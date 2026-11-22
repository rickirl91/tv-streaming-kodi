# -*- coding: utf-8 -*-
"""Incremental TMDb Helper movie wall with a bounded, bidirectional poster window.

The panel retains only a small, fixed number of Kodi ListItems. When the user
scrolls forward, older pages are removed; scrolling back refetches those pages
using remembered TMDb Helper folder URLs. The URL/key index contains no artwork
or full movie metadata. The add-on runs only while its window is open.
"""
import json
import base64
import re
import threading
import sys
from urllib.parse import parse_qs, urlparse

import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon('script.tvstreaming.lazywall')
ROOT = ADDON.getAddonInfo('path')
BASE = 'plugin://plugin.video.themoviedb.helper/?'
# User-configurable catalogue sources. TMDb Helper is still authoritative.
CATEGORIES = {
    'action': ('Action Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=28&with_id=True'),
    'comedy': ('Comedy Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=35&with_id=True'),
    'thriller': ('Thriller Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=53&with_id=True'),
    'horror': ('Horror Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=27&with_id=True'),
    'scifi': ('Science Fiction Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=878&with_id=True'),
    'drama': ('Drama Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=18&with_id=True'),
    'documentary': ('Documentary Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=99&with_id=True'),
    'family': ('Family Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=10751&with_id=True'),
    'animation': ('Animated Movies', 'movie', 'info=discover&tmdb_type=movie&with_genres=16&with_id=True'),
    'tvcomedy': ('Comedy TV Shows', 'tv', 'info=discover&tmdb_type=tv&with_genres=35&with_id=True'),
    'tvdrama': ('Drama TV Shows', 'tv', 'info=discover&tmdb_type=tv&with_genres=18&with_id=True'),
    'tvdocumentary': ('Documentary TV Shows', 'tv', 'info=discover&tmdb_type=tv&with_genres=99&with_id=True'),
}
ACTION_DIRECTORY = BASE + CATEGORIES['action'][2]

# Same strict source format as StreamRow: only a TMDb Helper media-list URL.
def choose_source(argv):
    for arg in argv[1:]:
        if not arg.startswith('source='):
            continue
        token = arg.split('=', 1)[1]
        if len(token) > 4096 or not re.fullmatch(r'[A-Za-z0-9_-]+', token):
            raise ValueError('Invalid catalogue token')
        data = json.loads(base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode('utf-8'))
        if not isinstance(data, dict):
            raise ValueError('Invalid source metadata')
        path = data.get('url', '')
        parsed = urlparse(path)
        info = parse_qs(parsed.query).get('info', [''])[0].lower()
        if (len(path) > 2048 or parsed.scheme != 'plugin'
                or parsed.netloc != 'plugin.video.themoviedb.helper'
                or parsed.path not in ('', '/') or not info
                or info in ('play','details','seasons','episodes','videos','search','directory','context','settings','nextpage')):
            raise ValueError('Unsupported source')
        if data.get('media') not in ('movie', 'tv'):
            raise ValueError('Unsupported media type')
        return {'url': path, 'title': str(data.get('title') or 'Catalogue')[:120], 'media': data['media']}
    return None


def choose_category(argv):
    for arg in argv[1:]:
        if arg.startswith('category='):
            val = arg.split('=', 1)[1].strip().lower()
            return val if val in CATEGORIES else 'action'
    return 'action'

# Max number of *simultaneous* ListItems in Kodi's poster panel. This is not
# a catalogue-size limit. Individual pages are ~20 items, so memory use remains
# bounded even after browsing hundreds of pages.
WINDOW_POSTERS = 200
PREFETCH_AT = 15
ACTION_BACK = (9, 10, 92, 216, 247, 257)
ACTION_UP = (3, 5)
ACTION_DOWN = (4, 6)


def log(message, level=xbmc.LOGINFO):
    xbmc.log('[TV Lazy Wall] ' + str(message), level)


def get_remote_items(path):
    if not path.startswith('plugin://plugin.video.themoviedb.helper/'):
        raise ValueError('Unexpected plugin path')
    request = {'jsonrpc': '2.0', 'id': 1, 'method': 'Files.GetDirectory',
               'params': {'directory': path, 'media': 'files',
                          'properties': ['title', 'year', 'plot', 'thumbnail', 'fanart',
                                         'art', 'rating', 'playcount', 'uniqueid', 'imdbnumber']}}
    response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
    if 'error' in response:
        raise RuntimeError('TMDb Helper response: ' + str(response['error']))
    return response.get('result', {}).get('files', [])


def split_page(entries):
    movies = []
    next_path = None
    for item in entries:
        path = str(item.get('file') or '')
        label = str(item.get('label') or item.get('title') or '').strip().lower()
        if 'next page' in label or 'nextpage' in label:
            if path.startswith('plugin://plugin.video.themoviedb.helper/'):
                next_path = path
            continue
        if path.startswith('plugin://plugin.video.themoviedb.helper/'):
            movies.append(item)
    return movies, next_path


def item_id(item):
    path = str(item.get('file') or '')
    params = parse_qs(urlparse(path).query)
    for key in ('tmdb_id', 'imdb_id', 'id'):
        value = params.get(key, [None])[0]
        if value:
            return key + ':' + str(value)
    return path


def find_trailer(media_type, tmdb_id):
    """Retrieve the selected movie/show's official YouTube trailer from TMDb Helper."""
    if media_type not in ('movie', 'tv') or not str(tmdb_id).isdigit():
        return None
    url = (BASE + 'info=videos&tmdb_type={}&tmdb_id={}'
           .format(media_type, tmdb_id))
    videos = get_remote_items(url)
    official = []
    other = []
    for entry in videos:
        label = str(entry.get('label') or entry.get('title') or '').lower()
        path = str(entry.get('file') or '')
        parsed = urlparse(path)
        if parsed.scheme != 'plugin' or parsed.netloc != 'plugin.video.youtube':
            continue
        youtube_id = parse_qs(parsed.query).get('video_id', [''])[0]
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', youtube_id):
            continue
        youtube_url = 'plugin://plugin.video.youtube/play/?video_id=' + youtube_id
        if 'trailer' in label:
            (official if 'official' in label else other).append(youtube_url)
    return (official or other or [None])[0]


def launch_trailer(media_type, tmdb_id):
    """Only start trailer playback after the details dialog has been closed."""
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
        xbmcgui.Dialog().ok('Watch Trailer',
                            'Install and enable the Kodi YouTube add-on to play trailers.')
        return False
    try:
        trailer_url = find_trailer(media_type, tmdb_id)
    except Exception as exc:
        log('Trailer lookup failed: ' + repr(exc), xbmc.LOGWARNING)
        xbmcgui.Dialog().notification('Watch Trailer', 'Unable to retrieve trailer information.')
        return False
    if not trailer_url:
        xbmcgui.Dialog().notification('Watch Trailer', 'No trailer available for this title.')
        return False
    xbmc.executebuiltin('PlayMedia("{}")'.format(trailer_url))
    return True


def wait_for_trailer():
    """Wait for Kodi to finish foreground playback before restoring details.

    Short, abort-aware polls keep the Kodi player able to receive Back/Stop and
    do not change the film's Trakt playback/scrobbling path. The wall stays
    alive underneath the player. Playback errors time out cleanly.
    """
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    for _ in range(100):  # up to 10 seconds to start (YouTube may buffer)
        if monitor.abortRequested():
            return False
        if player.isPlayingVideo():
            break
        if monitor.waitForAbort(0.1):
            return False
    else:
        return False
    # Do not impose a trailer duration cap. Let Kodi handle Stop/Back.
    while not monitor.abortRequested() and player.isPlayingVideo():
        if monitor.waitForAbort(0.2):
            return False
    return not monitor.abortRequested()


def to_list_item(entry, media="movie"):
    name = str(entry.get('label') or entry.get('title') or 'Movie')
    item = xbmcgui.ListItem(label=name, offscreen=True)
    art = dict(entry.get('art') or {})
    poster = art.get('poster') or entry.get('thumbnail') or art.get('thumb')
    fanart = art.get('fanart') or entry.get('fanart')
    if poster:
        art['poster'] = poster
        art.setdefault('thumb', poster)
        art.setdefault('icon', poster)
    if fanart:
        art['fanart'] = fanart
    item.setArt(art)
    info = {'title': str(entry.get('title') or name), 'mediatype': 'movie' if media == 'movie' else 'tvshow'}
    for key in ('year', 'plot', 'rating', 'playcount'):
        if entry.get(key) is not None:
            info[key] = entry[key]
    item.setInfo('video', info)
    item.setProperty('streamrow.path', str(entry.get('file') or ''))
    item.setProperty('streamrow.label', name)
    item.setProperty('streamrow.plot', str(entry.get('plot') or ''))
    item.setProperty('streamrow.year', str(entry.get('year') or ''))
    item.setProperty('streamrow.rating', str(entry.get('rating') or ''))
    item.setProperty('streamrow.runtime', str(entry.get('runtime') or entry.get('duration') or ''))
    item.setProperty('streamrow.poster', str(poster or ''))
    item.setProperty('streamrow.fanart', str(fanart or ''))
    params = parse_qs(urlparse(str(entry.get('file') or '')).query)
    ids = entry.get('uniqueid') or {}
    if not isinstance(ids, dict):
        ids = {}
    tmdb_id = params.get('tmdb_id', [None])[0] or ids.get('tmdb')
    item.setProperty('streamrow.tmdb_id', str(tmdb_id or ''))
    return item


class LazyWall(xbmcgui.WindowXML):
    def onInit(self):
        # Kodi can call onInit each time this window becomes active, including
        # when YouTube playback ends. Never erase the already-loaded pages.
        if getattr(self, '_initialized', False):
            if not getattr(self, '_closed', False) and self._grid.size():
                selected = max(0, min(getattr(self, '_return_index', 0), self._grid.size()-1))
                self._grid.selectItem(selected)
                self.setFocus(self._grid)
            return
        self._initialized = True
        self._return_index = 0
        # Keep only page URLs, previously accepted IDs, and the visible pages.
        # Do not retain raw artwork or rich movie dictionaries for older pages.
        self._category = getattr(self, '_configured_category', 'action')
        source = getattr(self, '_configured_source', None)
        if source:
            self._title, self._media = source['title'], source['media']
            self._root_directory = source['url']
        else:
            self._title, self._media, query = CATEGORIES[self._category]
            self._root_directory = BASE + query
        self._paths = [self._root_directory]
        self._page_keys = {}
        self._known_ids = set()
        self._visible_pages = []  # ordered (page_index, number_of_posters)
        self._end_reached = False
        self._pending = None
        self._error = None
        self._lock = threading.Lock()
        self._thread = None
        self._loading_request = None
        self._closed = False
        self._selected_path = None
        self._loaded_pages = 0
        self._failed = False
        self._grid = self.getControl(100)
        self._grid.reset()
        self.setFocus(self._grid)
        self._status('Loading ' + self._title + '...')
        try:
            movies, next_path = split_page(get_remote_items(self._root_directory))
            fresh, keys = self._dedupe_new(movies)
            if not fresh:
                self._end_reached = True
                self._refresh_status()
                return
            self._grid.addItems(fresh)
            self._visible_pages.append((0, len(fresh)))
            self._page_keys[0] = keys
            self._loaded_pages = 1
            self._register_next(next_path)
            self._grid.selectItem(0)
            self._refresh_status()
            # Preserve the existing tested behaviour: prefetch page two early.
            self._request('forward')
        except Exception as exc:
            log('Initial load error: ' + repr(exc), xbmc.LOGERROR)
            self._status('Unable to load ' + self._title + '. Press Back.')

    def _status(self, message):
        self.setProperty('Status', message)
        self.setProperty('Title', self._title)

    def _dedupe_new(self, data):
        result, keys = [], []
        for entry in data:
            key = item_id(entry)
            if key not in self._known_ids:
                self._known_ids.add(key)
                result.append(to_list_item(entry, self._media))
                keys.append(key)
        return result, tuple(keys)

    def _rehydrate(self, index, data):
        """Refetch an older page and preserve its original poster order."""
        entries = {item_id(e): e for e in data}
        keys = self._page_keys.get(index, ())
        return [to_list_item(entries[k], self._media) for k in keys if k in entries]

    def _register_next(self, path):
        if not path or not path.startswith('plugin://plugin.video.themoviedb.helper/'):
            self._end_reached = True
        elif path in self._paths:
            # Guard plugin pagination loops; no artificial catalogue cap.
            self._end_reached = True
            log('Stopping repeated TMDb Helper page URL', xbmc.LOGWARNING)
        else:
            self._paths.append(path)

    def _refresh_status(self):
        visible = self._grid.size()
        found = len(self._known_ids)
        if not visible:
            self._status('No titles were returned')
            return
        if self._failed:
            self._status('{0} titles seen · next batch failed · Back to retry'.format(found))
        elif self._end_reached and self._visible_pages[-1][0] == len(self._paths) - 1:
            self._status('{0} titles · end of catalogue'.format(found))
        else:
            self._status('{0} titles explored · {1} posters active · scroll to explore'.format(found, visible))

    def _request(self, direction):
        if self._closed or self._failed or self._thread or self._pending or not self._visible_pages:
            return
        first, last = self._visible_pages[0][0], self._visible_pages[-1][0]
        if direction == 'backward':
            if first <= 0:
                return
            index = first - 1
        elif direction == 'forward':
            index = last + 1
            if index >= len(self._paths):
                return
        else:
            return
        path = self._paths[index]
        self._loading_request = (direction, index, path)

        def worker():
            try:
                batch = split_page(get_remote_items(path))
                with self._lock:
                    self._pending = (direction, index, path, batch)
            except Exception as exc:
                with self._lock:
                    self._error = repr(exc)
        thread = threading.Thread(target=worker, name='TVLazyWallPage')
        thread.daemon = True
        self._thread = thread
        thread.start()

    def _trim_far_edge(self, direction, selected):
        """Keep the Kodi GUI panel bounded, retaining the selected poster."""
        while self._grid.size() > WINDOW_POSTERS and len(self._visible_pages) > 1:
            if direction == 'forward':
                count = self._visible_pages[0][1]
                if selected < count:
                    break
                for _ in range(count):
                    self._grid.removeItem(0)
                selected -= count
                self._visible_pages.pop(0)
            else:
                count = self._visible_pages[-1][1]
                if selected >= self._grid.size() - count:
                    break
                for _ in range(count):
                    self._grid.removeItem(self._grid.size() - 1)
                self._visible_pages.pop()
        return selected

    def _accept_page(self, direction, index, data, next_path):
        if direction == 'forward':
            if index != self._visible_pages[-1][0] + 1:
                return
            revisiting = index in self._page_keys
            if revisiting:
                # When travelling forward again after scrolling backwards,
                # restore the page from its original IDs. Do not dedupe it
                # against the IDs discovered earlier in this same session.
                fresh = self._rehydrate(index, data)
            else:
                fresh, keys = self._dedupe_new(data)
            if not fresh:
                if revisiting:
                    self._failed = True
                    log('Previously viewed TMDb Helper page changed; cannot restore', xbmc.LOGWARNING)
                else:
                    self._end_reached = True
                self._refresh_status()
                return
            old_selection = self._grid.getSelectedPosition()
            self._grid.addItems(fresh)
            self._visible_pages.append((index, len(fresh)))
            if not revisiting:
                self._page_keys[index] = keys
                self._loaded_pages += 1
                if index == len(self._paths) - 1:
                    self._register_next(next_path)
            selected = self._trim_far_edge('forward', old_selection)
        elif direction == 'backward':
            if index != self._visible_pages[0][0] - 1:
                return
            fresh = self._rehydrate(index, data)
            if not fresh:
                self._failed = True
                self._refresh_status()
                log('Earlier TMDb Helper page changed; cannot restore', xbmc.LOGWARNING)
                return
            old_selection = self._grid.getSelectedPosition()
            # Kodi ControlList supports inserting at position 0. Reversing
            # insertion order leaves the original page in correct poster order.
            for item in reversed(fresh):
                self._grid.addItem(item, 0)
            self._visible_pages.insert(0, (index, len(fresh)))
            selected = self._trim_far_edge('backward', old_selection + len(fresh))
        else:
            return
        if self._grid.size():
            selected = max(0, min(selected, self._grid.size() - 1))
            self._grid.selectItem(selected)
            self._return_index = selected
        self._refresh_status()
        log('Fetch {0} page {1}; displayed {2}; discovered {3}; window {4}-{5}'.format(
            direction, index + 1, self._grid.size(), len(self._known_ids),
            self._visible_pages[0][0] + 1, self._visible_pages[-1][0] + 1))

    def _process_queue(self):
        with self._lock:
            pending = self._pending
            error = self._error
            self._pending = None
            self._error = None
        if error:
            log('Page load error: ' + error, xbmc.LOGERROR)
            self._thread = None
            self._failed = True  # No runaway retries on every keypress.
            self._refresh_status()
            return
        if pending:
            direction, index, path, (data, next_path) = pending
            if (direction, index, path) == self._loading_request and not self._closed:
                self._thread = None
                self._accept_page(direction, index, data, next_path)

    def _maybe_prefetch(self, action_id=None):
        if self._closed or not self._visible_pages or self._grid.size() == 0:
            return
        selected = self._grid.getSelectedPosition()
        if selected < 0:
            return
        start_dist = selected
        end_dist = self._grid.size() - selected - 1
        # When moving up near the trimmed edge, refetch the preceding page.
        if action_id in ACTION_UP and start_dist <= PREFETCH_AT:
            self._request('backward')
        elif action_id in ACTION_DOWN and end_dist <= PREFETCH_AT:
            self._request('forward')
        elif end_dist <= PREFETCH_AT:
            self._request('forward')
        elif start_dist <= PREFETCH_AT:
            self._request('backward')

    def onAction(self, action):
        if action.getId() in ACTION_BACK:
            self._closed = True
            self.close()
            return
        if not self._closed:
            self._process_queue()  # GUI controls modified only on Kodi UI callback.
            try:
                self._maybe_prefetch(action.getId())
            except RuntimeError:
                pass

    def onClick(self, control_id):
        if control_id != 100 or self._grid.size() == 0:
            return
        index = self._grid.getSelectedPosition()
        if index < 0:
            return
        item = self._grid.getListItem(index)
        self._return_index = index
        tmdb_id = item.getProperty('streamrow.tmdb_id')

        # Each modal dialog closes *before* a video starts. Keeping it open
        # traps the trailer underneath it (observed on Xbox v0.2.1).
        # When the viewer stops the trailer, we reopen the same title's
        # details. All existing poster ListItems and loaded pages are retained.
        while not self._closed:
            details = Details('TVStreamingDetails.xml', ROOT, 'default', '1080i')
            try:
                details.media_type = self._media
                details.tmdb_id = tmdb_id
                for key in ('label', 'plot', 'year', 'rating', 'runtime', 'poster', 'fanart', 'tmdb_id'):
                    details.setProperty(key.capitalize(), item.getProperty('streamrow.' + key))
                details.setProperty('MediaType', self._media)
                details.setProperty('PlayButton', 'Play' if self._media == 'movie' else 'Browse episodes')
                details.doModal()
                choice = details.choice
            finally:
                del details

            if choice != 'trailer':
                break
            if not launch_trailer(self._media, tmdb_id):
                # On a missing trailer, redisplay details rather than leaving
                # the viewer unexpectedly at the wall.
                continue
            if not wait_for_trailer():
                # Kodi couldn't start the clip or playback was aborted; keep
                # focus on the original poster with no navigation reset.
                break
            if self._grid.size():
                self._return_index = max(0, min(index, self._grid.size() - 1))
                self._grid.selectItem(self._return_index)
            # Loop restores the SAME film's details screen after Stop/Back.

        if self._grid.size():
            self._return_index = max(0, min(index, self._grid.size() - 1))
            self._grid.selectItem(self._return_index)
        if choice == 'play':
            if not tmdb_id.isdigit():
                xbmcgui.Dialog().notification('TV Streaming', 'Movie identifier not available')
                return
            if self._media == 'movie':
                xbmc.executebuiltin(
                    'RunScript(plugin.video.themoviedb.helper,play=movie,tmdb_id={})'
                    .format(tmdb_id))
            else:
                directory = BASE + 'info=seasons&tmdb_type=tv&tmdb_id=' + tmdb_id
                xbmc.executebuiltin('ActivateWindow(Videos,"{}",return)'.format(directory))


class Details(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(Details, self).__init__(*args, **kwargs)
        self.choice = None

    def onInit(self):
        self.setFocusId(301)

    def onClick(self, control_id):
        if control_id == 301:
            self.choice = 'play'
            self.close()
        elif control_id == 302:
            self.choice = 'trailer'
            self.close()
        elif control_id == 303:
            self.close()

    def onAction(self, action):
        if action.getId() in ACTION_BACK:
            self.close()


def main():
    skin = xbmc.getSkinDir()
    if not skin.lower().startswith('skin.arctic.fuse.3'):
        xbmcgui.Dialog().ok('TV Streaming Lazy Wall',
                            'This experiment targets Arctic Fuse 3. Your skin is: ' + skin)
        return
    ui = LazyWall('TVStreamingLazyWall.xml', ROOT, 'default', '1080i', False)
    try:
        ui._configured_source = choose_source(sys.argv)
    except (ValueError, TypeError, KeyError, UnicodeError) as exc:
        xbmcgui.Dialog().ok('TV Streaming', 'Unsupported catalogue source: ' + str(exc))
        del ui
        return
    ui._configured_category = choose_category(sys.argv)
    try:
        ui.doModal()
    finally:
        del ui

if __name__ == '__main__':
    main()
