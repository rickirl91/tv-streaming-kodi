# -*- coding: utf-8 -*-
"""StreamRow proof-of-concept: See All first, then Kodi TMDb Helper movie entries.

No remote API credentials, background tasks, filesystem changes, or playback code.
Metadata fidelity and nested plugin listing are deliberately tested BEFORE replacing
an existing home widget.
"""
import json
import base64
import re
import sys
from urllib.parse import parse_qs, urlparse

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

ADDON_ID = "plugin.video.streamrow"
TMDB_ID = "plugin.video.themoviedb.helper"
ACTION_DIR = (
    "plugin://plugin.video.themoviedb.helper/?"
    "info=discover&tmdb_type=movie&with_genres=28&with_id=True"
)
# Match the user's existing Action widget exactly, including widget=true.
ACTION_WIDGET = ACTION_DIR + "&widget=true&reload="
CATEGORIES = {
    'action': ('Action', 'movie', 28),
    'comedy': ('Comedy', 'movie', 35),
    'thriller': ('Thriller', 'movie', 53),
    'horror': ('Horror', 'movie', 27),
    'scifi': ('Science Fiction', 'movie', 878),
    'drama': ('Drama', 'movie', 18),
    'documentary': ('Documentaries', 'movie', 99),
    'family': ('Family', 'movie', 10751),
    'animation': ('Animation', 'movie', 16),
    'tvcomedy': ('Comedy TV Shows', 'tv', 35),
    'tvdrama': ('Drama TV Shows', 'tv', 18),
    'tvdocumentary': ('Documentary TV Shows', 'tv', 99),
}
MAX_MOVIES = 30

# A source token is an opaque URL-safe representation of an existing static
# TMDb Helper catalogue URL, its label and media type. Only this specific
# plugin and media-list paths are accepted: never execute arbitrary commands.
MAX_TOKEN = 4096
UNSAFE_INFO = {'play', 'details', 'seasons', 'episodes', 'videos', 'search',
               'directory', 'context', 'players', 'settings', 'nextpage'}

def unpack_source(token):
    if not token or len(token) > MAX_TOKEN or not re.fullmatch(r'[A-Za-z0-9_-]+', token):
        raise ValueError('Invalid widget source token')
    raw = base64.urlsafe_b64decode(token + ('=' * (-len(token) % 4)))
    data = json.loads(raw.decode('utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Expected catalogue metadata')
    path = data.get('url', '')
    parsed = urlparse(path)
    info = parse_qs(parsed.query).get('info', [''])[0].lower()
    if (len(path) > 2048 or parsed.scheme != 'plugin'
            or parsed.netloc != TMDB_ID or parsed.path not in ('', '/')
            or not info or info in UNSAFE_INFO):
        raise ValueError('Unsupported catalogue URL')
    media = data.get('media')
    if media not in ('movie', 'tv'):
        raise ValueError('Unsupported catalogue type')
    return {'url': path, 'title': str(data.get('title') or 'Catalogue')[:120],
            'media': media}


def category_directory(category):
    _, media, genre = CATEGORIES[category]
    return ('plugin://plugin.video.themoviedb.helper/?info=discover&tmdb_type={}'
            '&with_genres={}&with_id=True').format(media, genre)

def log(message, level=xbmc.LOGINFO):
    xbmc.log("[StreamRow] " + message, level)

def get_items(category=None, source=None):
    # Kodi's own Files.GetDirectory API delegates to TMDb Helper. On some Kodi
    # builds it does not preserve artwork/metadata; this is why we preview first.
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "Files.GetDirectory",
        "params": {
            "directory": (source or (category_directory(category) + "&widget=true&reload=")),
            "media": "files",
            "properties": [
                "title", "year", "plot", "thumbnail", "fanart",
                "art", "rating", "playcount", "uniqueid", "imdbnumber"
            ],
        },
    }
    response = json.loads(xbmc.executeJSONRPC(json.dumps(payload)))
    if "error" in response:
        raise RuntimeError(str(response["error"].get("message", "Kodi JSON-RPC error")))
    return response.get("result", {}).get("files", [])

def is_pagination(entry):
    label = str(entry.get("label") or "").strip().lower()
    path = str(entry.get("file") or "")
    if label in ("next page", "nextpage", "next page >>", "next page >"):
        return True
    parsed = urlparse(path)
    query = parse_qs(parsed.query)
    info = str(query.get("info", [""])[0]).lower()
    return info in ("nextpage", "next_page")

def featured_info(entry, category):
    """Borrow the first movie's preview, never its click/play action.

    The See All directory item remains a non-playable launcher. Its custom
    poster, label, and callback are not replaced by this featured movie.
    """
    if not entry:
        return {}, {}
    art = entry.get('art') or {}
    if not isinstance(art, dict):
        art = {}
    result_art = {}
    backdrop = entry.get('fanart') or art.get('fanart') or art.get('landscape')
    if backdrop:
        result_art['fanart'] = backdrop
        result_art['landscape'] = backdrop
    title = entry.get('title') or entry.get('label') or ''
    info = {'title': str(title)} if title else {}
    for key in ('plot', 'year', 'rating', 'duration', 'runtime', 'premiered'):
        if entry.get(key) is not None:
            info[key] = entry[key]
    # Do not copy playable paths, identifiers, playcount, mediatype or watched
    # flags: "See All" must stay an action, not become a proxy film.
    return info, result_art


def category_hero_title(source_meta, category):
    """Clean the row/category name for the See All hero title."""
    title = str((source_meta or {}).get('title') or CATEGORIES[category][0]).strip()
    title = re.sub(r'\[[^\]]*\]', '', title).strip()
    title = re.sub(r'(?i)^see all\s*[-:–—]\s*', '', title).strip()
    title = re.sub(r'(?i)\s*[-:–—]\s*see all(?: first)?$', '', title).strip()
    if title.casefold() == 'hidden gems (highly rated, less popular)':
        title = 'Hidden Gems'
    return title or CATEGORIES[category][0]


def add_see_all(handle, icon, category, featured=None, source_token=None, source_meta=None):
    item = xbmcgui.ListItem(label="See All", offscreen=True)
    featured_metadata, featured_art = featured_info(featured, category)
    item.setArt({"poster": icon, "thumb": icon, "icon": icon, **featured_art})
    description = (source_meta or {}).get('title') or CATEGORIES[category][0]
    # Retain cinematic backdrop but do not borrow the first film/show metadata.
    info = {"title": category_hero_title(source_meta, category), "plot": ""}
    item.setInfo("video", info)
    # This is a direct TMDb Helper folder, so the existing TMDb Helper movie
    # directory view (the tested poster wall) handles the destination.
    item.setProperty('SpecialSort', 'top')
    item.setProperty('streamrow.type', 'see_all')
    # Kodi distinguishes folders (directory-navigation) from action callbacks.
    # This tile does NOT lead to another Kodi directory: it opens the Lazy Wall
    # script. A false folder + endOfDirectory(succeeded=False) cancelled the
    # handoff on the user's Xbox, appearing to do nothing.
    item.setProperty('IsPlayable', 'false')
    args = ('source=' + source_token) if source_token else ('category=' + category)
    item.addContextMenuItems([
        ('Open Full Wall (direct)',
         'RunAddon(script.tvstreaming.lazywall,' + args + ')')
    ])
    xbmcplugin.addDirectoryItem(
        handle, 'plugin://plugin.video.streamrow/?mode=launch&' + args,
        item, isFolder=False)

def add_movie(handle, entry, category, media=None):
    path = entry.get("file", "")
    if not path or not isinstance(path, str) or not path.startswith("plugin://"):
        return False
    label = entry.get("label") or entry.get("title") or "Movie"
    artwork = entry.get("art") or {}
    if not isinstance(artwork, dict):
        artwork = {}
    thumb = entry.get("thumbnail") or artwork.get("poster") or artwork.get("thumb")
    fanart = entry.get("fanart") or artwork.get("fanart")
    if thumb:
        artwork.setdefault("poster", thumb)
        artwork.setdefault("thumb", thumb)
        artwork.setdefault("icon", thumb)
    if fanart:
        artwork.setdefault("fanart", fanart)
    item = xbmcgui.ListItem(label=str(label), offscreen=True)
    if artwork:
        item.setArt(artwork)
    info = {"title": str(entry.get("title") or label), "mediatype": "movie" if (media or CATEGORIES[category][1]) == "movie" else "tvshow"}
    for field in ("year", "plot", "playcount", "rating"):
        if entry.get(field) is not None:
            info[field] = entry[field]
    item.setInfo("video", info)
    ids = entry.get("uniqueid")
    if not isinstance(ids, dict):
        ids = {}
    if entry.get("imdbnumber"):
        ids["imdb"] = entry["imdbnumber"]
    if not ids:
        tmdb_id = parse_qs(urlparse(path).query).get("tmdb_id", [None])[0]
        if tmdb_id:
            ids["tmdb"] = str(tmdb_id)
    if ids:
        try:
            item.getVideoInfoTag().setUniqueIDs({str(k): str(v) for k, v in ids.items()})
        except (AttributeError, TypeError, ValueError):
            pass
    is_folder = entry.get("filetype") == "directory"
    if not is_folder:
        item.setProperty("IsPlayable", "true")
    xbmcplugin.addDirectoryItem(handle, path, item, isFolder=is_folder)
    return True

def listing(handle, category, source_token=None):
    icon = xbmcaddon.Addon(ADDON_ID).getAddonInfo("path") + "/resources/media/see_all_miami_neutral_v024.png"
    meta = unpack_source(source_token) if source_token else None
    media = meta['media'] if meta else CATEGORIES[category][1]
    xbmcplugin.setContent(handle, 'movies' if media == 'movie' else 'tvshows')
    first_tile_added = False
    try:
        entries = get_items(category, source=meta['url'] if meta else None)
        movies = [x for x in entries if not is_pagination(x)]
        first_title = next((e for e in movies if isinstance(e.get('file'), str)
                            and e['file'].startswith('plugin://')), None)
        add_see_all(handle, icon, category, first_title, source_token, meta)
        first_tile_added = True
        movie_count = 0
        posters = 0
        for entry in movies:
            if movie_count >= MAX_MOVIES:
                break
            art = entry.get("art") or {}
            if not isinstance(art, dict):
                art = {}
            if entry.get("thumbnail") or art.get("poster") or art.get("thumb"):
                posters += 1
            if add_movie(handle, entry, category, media):
                movie_count += 1
        log("Fetched {0} entries; displayed {1} movies; artwork on {2}".format(
            len(entries), movie_count, posters))
        if movie_count < 5 or posters < max(3, movie_count // 2):
            label = "[TEST NOT PASSED] Kodi did not return enough movie posters"
            status = xbmcgui.ListItem(label=label, offscreen=True)
            status.setArt({"icon": "DefaultWarning.png"})
            xbmcplugin.addDirectoryItem(handle, category_directory(category), status, isFolder=True)
            log("Do not replace the existing Action widget: missing metadata", xbmc.LOGWARNING)
    except Exception as exc:
        log("Preview failed: " + repr(exc), xbmc.LOGERROR)
        if not first_tile_added:
            add_see_all(handle, icon, category, source_token=source_token, source_meta=meta)
        item = xbmcgui.ListItem(label="[TEST NOT PASSED] Could not retrieve Action movie list")
        item.setArt({"icon": "DefaultWarning.png"})
        xbmcplugin.addDirectoryItem(handle, meta['url'] if meta else category_directory(category), item, isFolder=True)
    finally:
        xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)

def home(handle, base):
    xbmcplugin.setContent(handle, "files")
    for key, (label, media, genre) in CATEGORIES.items():
        item = xbmcgui.ListItem(label=label + ' — See All First')
        xbmcplugin.addDirectoryItem(handle, base + '?mode=widget&category=' + key,
                                    item, isFolder=True)
    xbmcplugin.endOfDirectory(handle)

if __name__ == "__main__":
    base = sys.argv[0]
    handle = int(sys.argv[1])
    query = parse_qs(sys.argv[2].lstrip("?")) if len(sys.argv) > 2 else {}
    mode = query.get('mode', [''])[0]
    category = query.get('category', ['action'])[0]
    if category not in CATEGORIES:
        category = 'action'
    source_token = query.get('source', [None])[0]
    if mode in ('action', 'widget', 'wrap'):
        listing(handle, category, source_token=source_token)
    elif mode == 'launch':
        # Action callback from the non-playable See All tile. RunAddon is Kodi's
        # supported script launcher. Keep the directory result successful:
        # the previous succeeded=False explicitly cancelled the navigation
        # while the asynchronous script window was being opened.
        xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)
        try:
            xbmcaddon.Addon('script.tvstreaming.lazywall')
        except Exception as exc:
            log('Lazy Wall unavailable: ' + repr(exc), xbmc.LOGERROR)
            xbmcgui.Dialog().ok('TV Streaming',
                               'TV Streaming Lazy Wall is not installed or enabled.')
        else:
            args = ('source=' + source_token) if source_token else ('category=' + category)
            if source_token:
                unpack_source(source_token)  # fail closed before launch
            command = 'RunAddon(script.tvstreaming.lazywall,' + args + ')'
            log('Launching ' + command)
            xbmc.executebuiltin(command)
    else:
        home(handle, base)
