"""Bounded, profile-local directory cache. No services, network or skin edits."""
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from contextlib import contextmanager

TTL = 300
SLOTS = 64
MAX_BYTES = 1024 * 1024

@contextmanager
def slot_lock(path, wait=4.0):
    # OS locks are released on process exit, including a Kodi crash.
    f = None
    unlock = None
    try:
        f = open(path, 'a+b')
        if f.tell() == 0:
            f.write(b'\0')
            f.flush()
        f.seek(0)
        if os.name == 'nt':
            import msvcrt
            lock = lambda: msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            unlock = lambda: msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            lock = lambda: fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            unlock = lambda: fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except (OSError, ImportError, AttributeError):
        if f:
            f.close()
        yield False
        return
    acquired = False
    try:
        deadline = time.monotonic() + wait
        while True:
            try:
                lock()
                acquired = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
        yield acquired
    finally:
        if acquired:
            try:
                f.seek(0)
                unlock()
            except OSError:
                pass
        f.close()

def valid(records):
    return isinstance(records, list) and bool(records) and all(
        isinstance(row, dict) for row in records)

def read(path, key, now):
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        with path.open(encoding='utf-8') as f:
            obj = json.load(f)
        if obj['key'] == key and 0 <= now - obj['created'] < TTL and valid(obj['rows']):
            return obj['rows']
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return None

def write(path, key, rows):
    data = json.dumps({'key': key, 'created': time.time(), 'rows': rows},
                      ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if len(data) > MAX_BYTES:
        return
    tmp = None
    try:
        # Fixed temp name under the held OS lock, so crash leftovers stay bounded.
        tmp = path.with_suffix('.tmp')
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            try:
                tmp.unlink()
            except OSError:
                pass

def cached(root, uri, fetch, active=lambda: True, log=lambda msg: None):
    if not active():
        return fetch()
    key = hashlib.sha256(uri.encode('utf-8')).hexdigest()
    folder = Path(root) / 'addon_data' / 'tvstreaming-widget-cache-v1'
    path = folder / ('%02d.json' % (int(key[:8], 16) % SLOTS))
    def note(status):
        log('[WidgetCache] ' + status + ' ' + key[:12])
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError:
        note('unavailable')
        return fetch()
    rows = read(path, key, time.time())
    if rows is not None and active():
        note('hit')
        return rows
    with slot_lock(path.with_suffix('.lock')) as acquired:
        if not acquired:
            note('lock-bypass')
            return fetch()
        rows = read(path, key, time.time())
        if rows is not None and active():
            note('coalesced')
            return rows
        note('miss')
        start = time.monotonic()
        rows = fetch()
        note('fetched %.2fs' % (time.monotonic() - start))
        if valid(rows) and active():
            try:
                write(path, key, rows)
            except (OSError, ValueError, TypeError):
                note('write-bypass')
        return rows
