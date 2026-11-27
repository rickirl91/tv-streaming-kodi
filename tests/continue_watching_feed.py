"""Candidate adapter. Preserve source records and fail open on storage failure."""
from continue_watching_candidate import filter_rows, identity

SOURCE = 'plugin://plugin.video.themoviedb.helper/?info=sync_currentlywatching&tmdb_type=both&widget=true&reload='
PROPERTIES = ['title', 'showtitle', 'season', 'episode', 'year', 'plot', 'art',
              'thumbnail', 'fanart', 'rating', 'playcount', 'uniqueid',
              'resume', 'runtime', 'file', 'mediatype']

def fetch_visible(rpc, store):
    response = rpc('Files.GetDirectory', {'directory': SOURCE, 'media': 'video',
                                          'properties': PROPERTIES})
    if not isinstance(response, dict) or not isinstance(response.get('files'), list):
        raise ValueError('Continue Watching directory unavailable')
    rows = response['files']
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError('Invalid directory records')
    try:
        hidden = store.read()
    except Exception:
        return rows
    return filter_rows(rows, hidden)

def dismissal_key(record):
    key = identity(record.get('file', ''))
    if key is None:
        return None
    ids = record.get('uniqueid') or {}
    if not isinstance(ids, dict):
        return None
    expected = ids.get('tvshow.tmdb') if key.startswith('tv:') else ids.get('tmdb')
    if expected is None or str(expected) != key.split(':')[1]:
        return None
    return key
