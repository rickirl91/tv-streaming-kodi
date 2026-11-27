"""Candidate widget integration; no production configuration changes."""
from time import monotonic_ns
from urllib.parse import urlparse, parse_qs
from html import unescape
from core import canonical_label
from continue_watching_feed import SOURCE

PROPERTY = 'TVStreaming.ContinueWatching.Reload'
WIDGET = 'plugin://plugin.video.tvstreaming.homepersonalisation/?action=continue_watching&reload=$INFO[Window(Home).Property(' + PROPERTY + ')]'

def refresh(xbmcgui):
    xbmcgui.Window(10000).setProperty(PROPERTY, str(monotonic_ns()))

def native_source(path):
    if not isinstance(path, str) or len(path) > 3072:
        return False
    parsed = urlparse(unescape(path))
    if parsed.scheme != 'plugin' or parsed.netloc != 'plugin.video.themoviedb.helper' or parsed.path not in ('', '/') or parsed.fragment:
        return False
    query = parse_qs(parsed.query, keep_blank_values=True)
    return (query.get('info') == ['sync_currentlywatching']
            and query.get('tmdb_type') == ['both']
            and query.get('widget', ['true']) == ['true']
            and len(query.get('reload', [''])) == 1
            and set(query) <= {'info', 'tmdb_type', 'widget', 'reload'})

def plan_widget(rows, enable=True, original_source=None):
    if not isinstance(rows,list) or not all(isinstance(r,dict) for r in rows):
        raise ValueError('Invalid Home widgets')
    matches = [i for i,r in enumerate(rows) if canonical_label(r.get('label')) == 'continue watching']
    if matches != [0]:
        raise ValueError('Expected exactly one first-row Continue Watching widget')
    row = rows[0]
    path = row.get('path')
    if path != WIDGET and not native_source(path):
        raise ValueError('Unrecognised Continue Watching source: ' + repr(path)[:500])
    if not enable and path != WIDGET:
        return rows
    if not enable and not native_source(original_source):
        raise ValueError('Original source unavailable; use verified Home backup.')
    target = WIDGET if enable else original_source
    if row['path'] == target:
        return rows
    return [dict(row,path=target), *rows[1:]]
