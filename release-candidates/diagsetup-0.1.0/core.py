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

def apply(root, expected):
    target, backup = safe_path(root, REL), safe_path(root, BACKUP)
    old = snapshot(target)
    if old != expected:
        raise ValueError('Home changed during confirmation.')
    new = planned()
    if old == new:
        return 'Already configured.'
    if backup.exists():
        raise ValueError('A previous diagnostic backup exists; restore it first.')
    record = {'original': None if old is None else base64.b64encode(old).decode('ascii')}
    atomic(backup, json.dumps(record).encode('utf-8'))
    atomic(target, new)
    if target.read_bytes() != new:
        raise IOError('Could not verify saved diagnostic widgets.')
    return 'Ten native widgets saved.'

def restore(root):
    target, backup = safe_path(root, REL), safe_path(root, BACKUP)
    if not backup.exists():
        raise ValueError('No diagnostic backup found.')
    record = json.loads(backup.read_bytes())
    raw = None if record['original'] is None else base64.b64decode(record['original'], validate=True)
    current = snapshot(target)
    if current != planned() and current != raw:
        raise ValueError('Home has newer edits; restore refused.')
    if current != raw:
        if raw is None:
            target.unlink()
        else:
            atomic(target, raw)
    backup.unlink()
    return 'Previous diagnostic Home restored.'
