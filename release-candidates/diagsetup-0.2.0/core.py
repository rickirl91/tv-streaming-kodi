"""Pure helpers for a temporary, native-widget-only diagnostic profile."""
import base64
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlencode

ROWS = (
    ('Trending Movies', 'trending_week', 'movie', None),
    ('Trending TV Shows', 'trending_week', 'tv', None),
    ('Popular Movies', 'popular', 'movie', None),
    ('Popular TV Shows', 'popular', 'tv', None),
    ('In Cinemas Now', 'now_playing', 'movie', None),
    ('Upcoming Movies', 'upcoming', 'movie', None),
    ('Top Rated Movies', 'top_rated', 'movie', None),
    ('Top Rated TV Shows', 'top_rated', 'tv', None),
    ('Action Movies', 'discover', 'movie', 28),
    ('Comedy Movies', 'discover', 'movie', 35),
)
REL = ('addon_data', 'script.skinvariables', 'nodes', 'skin.arctic.fuse.3',
       'skinvariables-shortcut-homewidgets.json')
BACKUP = ('addon_data', 'script.tvstreaming.diagsetup', 'home-backup.json')

def verify(name, skin, profile, master):
    if name.strip().casefold() != 'diag' or skin != 'skin.arctic.fuse.3':
        raise ValueError('Only the diag profile with Arctic Fuse 3 is allowed.')
    p, m = Path(profile).resolve(), Path(master).resolve()
    if p == m or p.parent != m / 'profiles' or p.name.casefold() != 'diag':
        raise ValueError('Expected the separate default diag directory; refusing to write.')
    return p

def safe_path(root, parts):
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise ValueError('Unexpected symbolic link; refusing to write.')
    if p.resolve().parent != p.parent.resolve() or root not in p.resolve().parents:
        raise ValueError('Unexpected profile path.')
    return p

def planned():
    rows = []
    for label, info, media, genre in ROWS:
        params = {'info': info, 'tmdb_type': media}
        if genre is not None:
            params.update(with_genres=genre, with_id='True')
        uri = ('plugin://plugin.video.themoviedb.helper/?' + urlencode(params)
               + '&reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]&widget=true')
        rows.append({'label': label, 'icon': '', 'path': uri,
                     'target': 'videos', 'widget_style': 'Poster'})
    return (json.dumps(rows, ensure_ascii=False, indent=4) + '\n').encode('utf-8')

def snapshot(path):
    if not path.exists():
        return None
    raw = path.read_bytes()
    obj = json.loads(raw)
    if not isinstance(obj, list) or not all(isinstance(x, dict) for x in obj):
        raise ValueError('Unexpected existing Home widget format.')
    return raw

def atomic(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix='.diag-')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(raw)
            f.flush()
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


MODE = ('addon_data','script.tvstreaming.diagsetup','mode.json')
MODES = ('standard','staggered','lazy')
def prop(i):
    return 'TVStreaming.Diag.Row' + str(i+1)
def native(i, reload=''):
    row = json.loads(planned())[i]
    return row['path'].replace('$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]', reload)
def placeholder(i):
    return 'plugin://script.tvstreaming.diagsetup/?row=' + str(i)
def deferred():
    rows = json.loads(planned())
    for i, row in enumerate(rows):
        row['path'] = '$INFO[Window(Home).Property(' + prop(i) + ')]'
    return (json.dumps(rows, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
def same(a,b):
    return a == b or (a is not None and b is not None and json.loads(a)==json.loads(b))
def mode(root):
    p = safe_path(root, MODE)
    if not p.exists():
        return 'standard'
    value = json.loads(p.read_bytes())['mode']
    if value not in MODES:
        raise ValueError('Invalid diagnostic mode.')
    return value
def apply(root, expected, choice='standard'):
    if choice not in MODES:
        raise ValueError('Invalid mode.')
    target, backup, marker = [safe_path(root,p) for p in (REL,BACKUP,MODE)]
    old = snapshot(target)
    if old != expected:
        raise ValueError('Home changed during confirmation.')
    new = planned() if choice=='standard' else deferred()
    if backup.exists():
        original = json.loads(backup.read_bytes())['original']
        original = None if original is None else base64.b64decode(original,validate=True)
        if not any(same(old,x) for x in (planned(),deferred(),original)):
            raise ValueError('Diagnostic Home was edited; restore or review before changing mode.')
    else:
        atomic(backup,json.dumps({'original':None if old is None else base64.b64encode(old).decode('ascii')}).encode())
    atomic(target,new)
    atomic(marker,json.dumps({'mode':choice}).encode())
    if target.read_bytes()!=new or mode(root)!=choice:
        raise IOError('Could not verify diagnostic configuration.')
    return 'Ten widgets saved: '+choice
def restore(root):
    target, backup, marker = [safe_path(root,p) for p in (REL,BACKUP,MODE)]
    if not backup.exists():
        raise ValueError('No diagnostic backup found.')
    record=json.loads(backup.read_bytes())
    raw=None if record['original'] is None else base64.b64decode(record['original'],validate=True)
    current=snapshot(target)
    if not any(same(current,x) for x in (planned(),deferred(),raw)):
        raise ValueError('Home has newer edits; restore refused.')
    if current!=raw:
        if raw is None:
            target.unlink()
        else:
            atomic(target,raw)
    if marker.exists():
        marker.unlink()
    backup.unlink()
    return 'Previous diagnostic Home restored.'

class Scheduler:
    """At most two outstanding row activations; timeout pauses instead of piling up."""
    def __init__(self, mode):
        self.mode=mode
        self.started=set()
        self.pending={}
        self.done=set()
        self.failed=False
        self.highest=1
    def tick(self, now, home, focus, observed):
        if not home or self.failed:
            return []
        for i, since in list(self.pending.items()):
            if observed.get(i,False):
                self.done.add(i)
                del self.pending[i]
            elif now-since>=45:
                self.failed=True
                return []
        if self.mode=='lazy' and focus is not None and 0<=focus<10:
            self.highest=max(self.highest,min(9,focus+1))
        limit=9 if self.mode=='staggered' else self.highest
        batch=[i for i in range(limit+1) if i not in self.started][:max(0,2-len(self.pending))]
        for i in batch:
            self.started.add(i)
            self.pending[i]=now
        return batch
