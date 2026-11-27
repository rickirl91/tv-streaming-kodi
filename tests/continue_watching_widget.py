"""Candidate widget integration; no production configuration changes."""
from time import monotonic_ns
from continue_watching_feed import SOURCE

PROPERTY = 'TVStreaming.ContinueWatching.Reload'
WIDGET = 'plugin://plugin.video.tvstreaming.homepersonalisation/?action=continue_watching&reload=$INFO[Window(Home).Property(' + PROPERTY + ')]'

def refresh(xbmcgui):
    xbmcgui.Window(10000).setProperty(PROPERTY, str(monotonic_ns()))

def plan_widget(rows, enable=True):
    if not isinstance(rows,list) or not all(isinstance(r,dict) for r in rows):
        raise ValueError('Invalid Home widgets')
    matches = [i for i,r in enumerate(rows) if str(r.get('label','')).strip().casefold() == 'continue watching']
    if matches != [0]:
        raise ValueError('Expected exactly one first-row Continue Watching widget')
    row = rows[0]
    if row.get('path') not in (SOURCE,WIDGET):
        raise ValueError('Unrecognised Continue Watching source')
    target = WIDGET if enable else SOURCE
    if row['path'] == target:
        return rows
    return [dict(row,path=target), *rows[1:]]
