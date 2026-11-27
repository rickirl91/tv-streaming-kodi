"""Pure Search command builder, independent of the active skin."""
from urllib.parse import urlencode

ADDON_ID = 'script.tvstreaming.safesearch'
HELPER = 'plugin.video.themoviedb.helper'


def allowed_profile(name):
    return name.strip().casefold() == 'cricky'


def search_command(query):
    query = query.strip()
    if not query:
        return None
    params = urlencode({'info': 'search', 'tmdb_type': 'both', 'query': query,
                        'history': 'true'})
    return 'ActivateWindow(Videos,plugin://' + HELPER + '/?' + params + ',return)'
