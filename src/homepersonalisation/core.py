# -*- coding: utf-8 -*-
"""Pure, unit-testable Home layout planner and lossless backup/restore helpers.

Widget writes are confined to the active Cricky profile.
No automatic edits on addon installation, startup or widget browsing.
"""
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlencode

ADDON_ID = 'plugin.video.tvstreaming.homepersonalisation'
TMDB = 'plugin.video.themoviedb.helper'
TARGET_NAME = 'skinvariables-shortcut-homewidgets.json'
LABELS = (
    ('recommended', 'Recommended For You', 'trakt_recommendations'),
    ('because', 'Because You Watched', 'sync_becauseyouwatched'),
    ('watchlist', 'From Your Watchlist', 'sync_watchlist'),
)
LABEL_BY_KIND = {kind: label for kind, label, _ in LABELS}
INFO_BY_KIND = {kind: endpoint for kind, _, endpoint in LABELS}


def canonical_label(value):
    if not isinstance(value, str):
        return ''
    return ' '.join(re.sub(r'\[[^\]]+\]', '', value).split()).casefold()


def source_url(kind, media):
    if kind not in INFO_BY_KIND or media not in ('movie', 'tv'):
        raise ValueError('Unsupported feed or media type')
    return 'plugin://{}/?{}'.format(TMDB, urlencode({'info': INFO_BY_KIND[kind], 'tmdb_type': media}))


def valid_source(path, kind, media):
    if not isinstance(path, str) or len(path) > 3072:
        return False
    parsed = urlparse(path)
    if parsed.scheme != 'plugin' or parsed.netloc != TMDB or parsed.path not in ('', '/'):
        return False
    query = parse_qs(parsed.query)
    return (query.get('info') == [INFO_BY_KIND.get(kind)]
            and query.get('tmdb_type') == [media]
            and not parsed.fragment)


def widget_path(kind):
    return 'plugin://{}/?{}'.format(ADDON_ID, urlencode({'action': 'feed', 'kind': kind, 'mode': 'widget'}))


def plan_home(original):
    if not isinstance(original, list) or not original or not all(isinstance(r, dict) for r in original):
        raise ValueError('Unsupported Home JSON: expected a non-empty list of widget objects')
    if not all(isinstance(row.get('label'), str) for row in original):
        raise ValueError('Cannot safely edit Home: an existing row has no string label')
    watching = [r for r in original if canonical_label(r['label']) == 'continue watching']
    if len(watching) != 1:
        raise ValueError('Expected exactly one Continue Watching row; found {}'.format(len(watching)))
    progress_row = watching[0]
    customised = {canonical_label(label) for _, label, _ in LABELS}
    remaining = [r for r in original if r is not progress_row and canonical_label(r['label']) not in customised]
    new_rows = [{
        'label': label,
        'icon': '',
        'path': widget_path(kind),
        'target': 'videos',
        'widget_style': 'Poster',
    } for kind, label, _ in LABELS]
    result = [progress_row] + new_rows + remaining
    assert len(result) == len(remaining) + 4
    assert result[0] is progress_row
    return result


# Exact labels from the old, separate recommendations/watchlist widgets. The
# new blended rows supersede these on Cricky Home only. Do not use substrings:
# a different user's custom label must never be removed accidentally.
OBSOLETE_LABELS = frozenset({
    'your movie watchlist',
    'your tv show watchlist',
    'your tv shows watchlist',
    'recommended movies for you',
    'recommended shows for you',
    'recommended tv shows for you',
})


def cleanup_candidates(original):
    """Return exact-index obsolete rows only after verifying the new Home hub."""
    if not isinstance(original, list) or len(original) < 4 or not all(isinstance(r, dict) for r in original):
        raise ValueError('Unsupported or incomplete Cricky Home widgets')
    expected = ['continue watching'] + [canonical_label(label) for _, label, _ in LABELS]
    actual = [canonical_label(row.get('label')) for row in original[:4]]
    if actual != expected:
        raise ValueError('Home first four rows are not the approved Cricky layout; cleanup refused')
    for idx, (kind, _, _) in enumerate(LABELS, 1):
        if original[idx].get('path') != widget_path(kind):
            raise ValueError('Personalised widget source differs from installed RC; cleanup refused')
    return [(index, row) for index, row in enumerate(original)
            if index >= 4 and canonical_label(row.get('label')) in OBSOLETE_LABELS]


def plan_cleanup(original):
    """Keep all objects byte-for-byte semantically, except exact obsolete rows."""
    drop = {index for index, _ in cleanup_candidates(original)}
    return [row for index, row in enumerate(original) if index not in drop]


def poster_style_candidates(original):
    """Select just the three active Cricky mixed-feed rows needing Poster style.

    The existing exact-path + first-four validation used by cleanup ensures
    no similarly named unrelated widgets or other hubs can be modified.
    """
    cleanup_candidates(original)  # Validates target profile Home layout.
    return [(i, original[i]) for i in (1, 2, 3)
            if original[i].get('widget_style') != 'Poster']


def plan_poster_style(original):
    """Preserve every Home row and field except three target style properties."""
    candidates = poster_style_candidates(original)
    result = list(original)
    for i, row in candidates:
        result[i] = dict(row)
        result[i]['widget_style'] = 'Poster'
    return result


def load_home(raw):
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, list):
        raise ValueError('Home widget JSON is not a list')
    return data


def serialize_home(rows):
    return (json.dumps(rows, indent=4, ensure_ascii=False) + '\n').encode('utf-8')


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _atomic_replace(path, content):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix='.cricky-home-', dir=str(path.parent))
    try:
        try:
            os.fchmod(fd, path.stat().st_mode & 0o777)
        except (AttributeError, OSError):
            pass
        with os.fdopen(fd, 'wb') as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def apply_home(homepath, backup_root, expected_hash, profile='Cricky', planner=None, *, filename=TARGET_NAME):
    if profile.casefold() != 'cricky':
        raise ValueError('Only the Cricky profile may be changed')
    homepath = Path(homepath)
    if homepath.name != filename:
        raise ValueError('Refusing unexpected widget filename')
    old = homepath.read_bytes()
    if sha256(old) != expected_hash:
        raise RuntimeError('Home widgets changed after preview; no changes applied')
    original = load_home(old)
    planned = (planner or plan_home)(original)
    if planned == original:
        return None
    edited = serialize_home(planned)
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = Path(backup_root) / name
    folder.mkdir(parents=True, exist_ok=False)
    # Original bytes are kept exactly, including original encoding and newline style.
    backup = folder / filename
    with open(backup, 'xb') as out:
        out.write(old)
        out.flush()
        os.fsync(out.fileno())
    if backup.read_bytes() != old:
        raise RuntimeError('Backup verification failed; original Home file untouched')
    manifest = {
        'version': 1,
        'profile': profile,
        'filename': filename,
        'before_sha256': sha256(old),
        'after_sha256': sha256(edited),
        'created_utc': name,
    }
    with open(folder / 'manifest.json', 'x', encoding='utf-8') as out:
        json.dump(manifest, out, indent=2)
        out.flush()
        os.fsync(out.fileno())
    if sha256(homepath.read_bytes()) != expected_hash:
        raise RuntimeError('Home widgets changed during backup; no changes applied')
    _atomic_replace(homepath, edited)
    if sha256(homepath.read_bytes()) != manifest['after_sha256']:
        raise RuntimeError('Home write integrity check failed; original backup is at ' + str(folder))
    return folder


def latest_backup(backup_root):
    root = Path(backup_root)
    if not root.is_dir():
        return None
    folders = sorted((p for p in root.iterdir() if p.is_dir() and (p / 'manifest.json').is_file()), reverse=True)
    return folders[0] if folders else None


def restore_home(homepath, folder, profile='Cricky', *, filename=TARGET_NAME):
    if profile.casefold() != 'cricky':
        raise ValueError('Only the Cricky profile may be changed')
    homepath, folder = Path(homepath), Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text('utf-8'))
    if (manifest.get('profile', '').casefold() != profile.casefold()
            or manifest.get('filename') != filename
            or homepath.name != filename):
        raise ValueError('Backup belongs to a different profile/file')
    before = (folder / filename).read_bytes()
    if sha256(before) != manifest['before_sha256']:
        raise RuntimeError('Backup checksum mismatch')
    current = homepath.read_bytes()
    if sha256(current) == manifest['before_sha256']:
        return 'already-restored'
    if sha256(current) != manifest['after_sha256']:
        raise RuntimeError('Home has newer manual changes. Restore blocked to protect those changes.')
    _atomic_replace(homepath, before)
    if sha256(homepath.read_bytes()) != manifest['before_sha256']:
        raise RuntimeError('Restore integrity check failed')
    return 'restored'


def summary(original, proposed):
    old_names = [r['label'] for r in original]
    new_names = [r['label'] for r in proposed]
    return ('Current Home widgets: {}\nProposed Home widgets: {}\n\n'
            'New order (first eight):\n{}\n\n'
            'No change to other hubs or Kodi profiles.\n'
            'Existing Continue Watching object is preserved verbatim.\n'
            'Other existing widgets retain their original relative order and properties.\n'
            'Movie and TV lists are merged live without changing Trakt history.\n\n'
            'IMPORTANT: Sync History/Watchlist providers in TMDb Helper must point '
            'to your Family Trakt account; a login in another add-on is not proof.\n'
            'A full Kodi restart / SkinVariables widget rebuild may be required.') .format(
                len(old_names), len(new_names), '\n'.join('{}. {}'.format(i + 1, name) for i, name in enumerate(new_names[:8])))


HIDDEN_GEMS_OLD = 'Hidden Gems (Highly Rated, Less Popular)'
WIDGET_FILE = re.compile(r'skinvariables-shortcut-(?:home|[0-9]+)widgets\.json')


def plan_hidden_gems(original):
    """Rename the literal legacy widget label, including nested widget groups."""
    if not isinstance(original, list) or not all(isinstance(row, dict) for row in original):
        raise ValueError('Unsupported widget configuration')
    result = []
    for row in original:
        updated = dict(row)
        if row.get('label') == HIDDEN_GEMS_OLD:
            source = urlparse(row.get('path') or '')
            if source.scheme != 'plugin' or source.netloc != 'plugin.video.streamrow':
                raise ValueError('Hidden Gems widget uses an unexpected catalogue source')
            updated['label'] = 'Hidden Gems'
        if isinstance(row.get('widgets'), list):
            updated['widgets'] = plan_hidden_gems(row['widgets'])
        result.append(updated)
    return result


def hidden_gems_snapshot(skin_dir):
    """Locate the actual AF3 widget file before planning or writing any edit."""
    matches = []
    for path in sorted(Path(skin_dir).iterdir()):
        if not WIDGET_FILE.fullmatch(path.name) or path.is_symlink() or not path.is_file():
            continue
        raw = path.read_bytes()
        if HIDDEN_GEMS_OLD.encode() not in raw:
            continue
        original = load_home(raw)
        planned = plan_hidden_gems(original)
        if original != planned:
            matches.append((path, raw))
    if len(matches) > 1:
        raise ValueError('Hidden Gems occurs in multiple hub files. Use the skin widget editor to identify the active hub.')
    return matches[0] if matches else None
