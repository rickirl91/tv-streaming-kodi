"""Candidate only: no Kodi or Trakt writes."""
from urllib.parse import urlparse, parse_qs

def identity(path):
    p = urlparse(path)
    if p.scheme != 'plugin' or p.netloc != 'plugin.video.themoviedb.helper' or p.path not in ('', '/') or p.fragment:
        return None
    q = parse_qs(p.query)
    media, ids = q.get('tmdb_type', []), q.get('tmdb_id', [])
    if len(ids) != 1 or not ids[0].isascii() or not ids[0].isdigit() or int(ids[0]) < 1:
        return None
    if media == ['movie']:
        return 'movie:' + str(int(ids[0]))
    if media == ['tv']:
        return 'tv:' + str(int(ids[0]))
    return None

def dismiss(hidden, key, label):
    if not isinstance(key, str) or identity('plugin://plugin.video.themoviedb.helper/?tmdb_type=' + key.replace(':', '&tmdb_id=', 1)) != key:
        raise ValueError('Unverified identity')
    return dict(hidden, **{key: {'label': str(label)}})

def restore(hidden, key):
    return {k: v for k, v in hidden.items() if k != key}

def filter_rows(rows, hidden):
    return [row for row in rows if identity(row.get('file', '')) not in hidden]

def subsequent_viewing(hidden, key, *, verified=False):
    """Only a separately verified playback event can clear a dismissal."""
    return restore(hidden, key) if verified else dict(hidden)
