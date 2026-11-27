# -*- coding: utf-8 -*-
"""Cricky-only, opt-in AF3 Home editor and live film+TV mixed feed.

Widget/feed reads never touch Home files. Apply/restore always require a user
confirmation and protect current bytes with checksums. No Trakt writes/tokens.
"""
import base64
import json
import os
import sys
from urllib.parse import parse_qs, urlencode, urlparse

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import core

ADDON = xbmcaddon.Addon(core.ADDON_ID)
DIALOG = xbmcgui.Dialog()
HOME_REL = ('addon_data', 'script.skinvariables', 'nodes',
            'skin.arctic.fuse.3', core.TARGET_NAME)


def log(msg, level=xbmc.LOGINFO):
    xbmc.log('[Cricky Personalisation] ' + str(msg), level)


def current_profile():
    return xbmc.getInfoLabel('System.ProfileName').strip()


def verify_cricky():
    name = current_profile()
    if name.casefold() != 'cricky':
        raise RuntimeError('Active Kodi profile is {!r}, not Cricky. Nothing changed.'.format(name))
    if xbmc.getSkinDir() != 'skin.arctic.fuse.3':
        raise RuntimeError('Arctic Fuse 3 must be the active skin. Nothing changed.')


def translated(uri):
    return xbmcvfs.translatePath(uri)


def home_path():
    return os.path.join(translated('special://profile/'), *HOME_REL)


def backups_path():
    return os.path.join(translated('special://profile/'), 'addon_data',
                        core.ADDON_ID, 'backups')


def home_snapshot():
    verify_cricky()
    path = home_path()
    if not os.path.isfile(path):
        raise RuntimeError('Home widget file not found in current Cricky profile; refusing to invent its layout.')
    raw = open(path, 'rb').read()
    old = core.load_home(raw)
    new = core.plan_home(old)
    return path, raw, old, new


def tmdb_directory(uri):
    if not (urlparse(uri).scheme == 'plugin'
            and urlparse(uri).netloc == core.TMDB):
        raise ValueError('Unexpected source add-on')
    request = {'jsonrpc': '2.0', 'id': 1, 'method': 'Files.GetDirectory',
               'params': {'directory': uri, 'media': 'files',
                          'properties': ['title', 'year', 'plot', 'thumbnail', 'fanart',
                                         'art', 'rating', 'playcount', 'uniqueid', 'imdbnumber']}}
    response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
    if 'error' in response:
        raise RuntimeError('TMDb Helper returned an error for this feed')
    result = response.get('result', {})
    if not isinstance(result, dict):
        raise RuntimeError('TMDb Helper did not return a directory result')
    return result.get('files') or []


def split_source(records, kind, media):
    selected, next_url = [], None
    for record in records:
        if not isinstance(record, dict):
            continue
        path = str(record.get('file') or '')
        label = str(record.get('label') or record.get('title') or '').casefold()
        if 'next page' in label or 'nextpage' in label:
            if core.valid_source(path, kind, media):
                next_url = path
            continue
        if not path.startswith('plugin://plugin.video.themoviedb.helper/'):
            continue
        selected.append(record)
    return selected, next_url


def fetch_kind(kind, paths=None):
    paths = paths or {}
    rows = {}
    nexts = {}
    for media in ('movie', 'tv'):
        if paths.get(media) == 'END':
            rows[media], nexts[media] = [], None
            continue
        source = paths.get(media) or core.source_url(kind, media)
        if not core.valid_source(source, kind, media):
            raise ValueError('Invalid next-page source')
        items, next_url = split_source(tmdb_directory(source), kind, media)
        rows[media] = items
        nexts[media] = next_url
    return rows, nexts


def media_id(item, media):
    parsed = urlparse(str(item.get('file') or ''))
    ids = item.get('uniqueid') or {}
    if not isinstance(ids, dict):
        ids = {}
    params = parse_qs(parsed.query)
    return '{}:{}'.format(media, params.get('tmdb_id', [None])[0]
                          or ids.get('tmdb') or parsed.geturl())


def interleave_movie_tv(rows):
    """Stable 1:1 alternating mix, preserving order within each source."""
    result, seen = [], set()
    movies, shows = rows.get('movie', []), rows.get('tv', [])
    for i in range(max(len(movies), len(shows))):
        for media, source in (('movie', movies), ('tv', shows)):
            if i >= len(source):
                continue
            item = source[i]
            key = media_id(item, media)
            if key in seen:
                continue
            seen.add(key)
            result.append((media, item))
    return result


def token_encode(value):
    return base64.urlsafe_b64encode(value.encode('utf-8')).decode('ascii').rstrip('=')


def token_decode(token, kind, media):
    if not token or len(token) > 4200 or not all(c.isalnum() or c in '-_' for c in token):
        raise ValueError('Invalid source token')
    text = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode('utf-8')
    if not core.valid_source(text, kind, media):
        raise ValueError('Invalid or mismatched next-page token')
    return text


def feed_link(kind, mode='widget', nexts=None):
    query = {'action': 'feed', 'kind': kind, 'mode': mode}
    if nexts is not None:
        for media, key in (('movie', 'm'), ('tv', 't')):
            query[key] = token_encode(nexts[media]) if nexts.get(media) else 'END'
    return 'plugin://{}/?{}'.format(core.ADDON_ID, urlencode(query))


def add_folder(handle, label, url, art=None, plot='', properties=None, hero_title=None):
    item = xbmcgui.ListItem(label=label)
    if art:
        item.setArt(art)
    if properties:
        for key, value in properties.items():
            item.setProperty(key, value)
    item.setInfo('video', {'title': hero_title if hero_title is not None else label,
                           'plot': '' if hero_title is not None else plot})
    xbmcplugin.addDirectoryItem(handle, url, item, isFolder=True)


def show_movie_tv_item(handle, media, record):
    path = str(record.get('file') or '')
    name = str(record.get('label') or record.get('title') or '').strip()
    if not name or not path.startswith('plugin://plugin.video.themoviedb.helper/'):
        return
    item = xbmcgui.ListItem(label=name, path=path)
    art = record.get('art') or {}
    if not isinstance(art, dict):
        art = {}
    art = dict(art)
    thumb = record.get('thumbnail') or art.get('poster') or art.get('thumb')
    fanart = record.get('fanart') or art.get('fanart')
    if thumb:
        art.setdefault('poster', thumb)
        art.setdefault('thumb', thumb)
    if fanart:
        art.setdefault('fanart', fanart)
    if art:
        item.setArt(art)
    info = {'title': str(record.get('title') or name),
            'plot': str(record.get('plot') or ''),
            'mediatype': 'movie' if media == 'movie' else 'tvshow'}
    for key in ('year', 'rating', 'playcount'):
        if record.get(key) is not None:
            info[key] = record[key]
    item.setInfo('video', info)
    ids = record.get('uniqueid') or {}
    if isinstance(ids, dict) and ids:
        try:
            item.getVideoInfoTag().setUniqueIDs({str(k): str(v) for k, v in ids.items() if v})
        except (AttributeError, TypeError, ValueError):
            pass
    item.setProperty('tmdb_type', media)
    if record.get('playcount'):
        item.setProperty('Watched', 'true')
    # Preserve TMDb Helper's returned callback rather than constructing a new
    # details/play URL. This is critical for TV series and watched indicators.
    is_folder = record.get('filetype', 'directory') != 'file'
    xbmcplugin.addDirectoryItem(handle, path, item, isFolder=is_folder)



def neutral_see_all_art():
    """Reuse the exact standard StreamRow 'Miami' See All tile on Xbox.

    StreamRow is already installed for Cricky catalogue sections. Resolve its
    actual Kodi addon path (no hardcoded Xbox storage location). A skin folder
    icon is a neutral fallback, never a show/movie poster.
    """
    try:
        streamrow = xbmcaddon.Addon('plugin.video.streamrow')
        artwork = os.path.join(streamrow.getAddonInfo('path'), 'resources',
                               'media', 'see_all_miami_neutral_v024.png')
        if xbmcvfs.exists(artwork) or os.path.isfile(artwork):
            return artwork
    except Exception as exc:
        log('StreamRow See All asset unavailable: {}'.format(repr(exc)), xbmc.LOGWARNING)
    return 'special://skin/extras/icons/folder.png'


def handle_feed(handle, query):
    kind = query.get('kind', [''])[0]
    mode = query.get('mode', ['widget'])[0]
    if kind not in core.INFO_BY_KIND or mode not in ('widget', 'all'):
        raise ValueError('Unsupported feed')
    paths = {}
    for media, key in (('movie', 'm'), ('tv', 't')):
        token = query.get(key, [''])[0]
        if token == 'END':
            paths[media] = 'END'
        elif token:
            paths[media] = token_decode(token, kind, media)
    rows, nexts = fetch_kind(kind, paths)
    combined = interleave_movie_tv(rows)
    xbmcplugin.setContent(handle, 'videos')
    if mode == 'widget':
        # Keep the first title's fanart as the Home hero/backdrop, but do not
        # borrow its poster. The first tile must show the existing StreamRow
        # neutral SEE ALL image just like the established catalogue widgets.
        artwork = neutral_see_all_art()
        # Arctic Fuse 3's Image_Landscape prioritises landscape artwork,
        # then falls back to fanart BEFORE poster/thumb. See All must set
        # landscape explicitly, or it incorrectly displays the first title's
        # programme backdrop as the horizontal tile image.
        # The override property also works if users disable landscape art.
        picture = {'poster': artwork, 'thumb': artwork, 'icon': artwork,
                   'landscape': artwork}
        if combined:
            entry = combined[0][1]
            art = entry.get('art') or {}
            if not isinstance(art, dict):
                art = {}
            fanart = art.get('fanart') or entry.get('fanart')
            if fanart:
                # Keep the original first-title fanart for the large Home hero.
                picture['fanart'] = fanart
        add_folder(handle, 'See All - ' + core.LABEL_BY_KIND[kind],
                   feed_link(kind, 'all'), picture,
                   'Browse movies and TV series together. Follow Next Page to load additional titles.',
                   properties={'override_landscape': artwork},
                   hero_title=core.LABEL_BY_KIND[kind])
    for media, entry in combined:
        show_movie_tv_item(handle, media, entry)
    if nexts.get('movie') or nexts.get('tv'):
        add_folder(handle, 'Next Page', feed_link(kind, 'all', nexts))
    xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)


def preflight_sources():
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.themoviedb.helper)'):
        raise RuntimeError('TMDb Helper is not enabled')
    results = []
    for kind, label, _ in core.LABELS:
        rows, _ = fetch_kind(kind)
        results.append('{}: {} films / {} shows'.format(label, len(rows['movie']), len(rows['tv'])))
    return results


def preview_and_apply():
    path, raw, old, new = home_snapshot()
    if new == old:
        DIALOG.ok('Cricky Home', 'The layout is already in the requested order.')
        return
    feeds = preflight_sources()
    preview = (core.summary(old, new) + '\n\nFeed checks (source accessible, not proof of account identity):\n'
               + '\n'.join(feeds))
    DIALOG.textviewer('Cricky Home - preview only', preview)
    if not DIALOG.yesno('Apply Cricky Home?',
                        'Back up the exact Home widgets file and apply only the Home row order?\n'
                        'This does not write to Trakt or other Kodi profiles.'):
        return
    # Verify still on correct profile and unchanged since preview.
    verify_cricky()
    folder = core.apply_home(path, backups_path(), core.sha256(raw), current_profile())
    if folder is None:
        DIALOG.ok('Cricky Home', 'No changes were necessary.')
        return
    # Regenerate AF3 includes using the installed SkinVariables generator.
    # The user still needs to fully restart Kodi for a consistent fresh view.
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Cricky Home - saved', 'Home layout updated and byte-for-byte backup verified.\n'
              'Fully quit and restart Kodi, then check all three new rows.\n'
              'If needed, rebuild widgets from Arctic Fuse 3 skin settings.')


def preview_only():
    _, _, old, new = home_snapshot()
    DIALOG.textviewer('Cricky Home - preview only', core.summary(old, new))


def inspect_only():
    path, raw, old, _ = home_snapshot()
    message = ('Profile: {}\nSkin: {}\nHome rows: {}\nHome SHA-256: {}\n\n'
               'Current order:\n{}').format(current_profile(), xbmc.getSkinDir(), len(old),
                                         core.sha256(raw), '\n'.join(
                                             '{}. {}'.format(i + 1, r['label']) for i, r in enumerate(old)))
    DIALOG.textviewer('Cricky Home - current layout', message)


def restore_latest():
    verify_cricky()
    path = home_path()
    if not os.path.isfile(path):
        raise RuntimeError('Current Home widget file is missing; restore refused')
    folder = core.latest_backup(backups_path())
    if folder is None:
        DIALOG.ok('Cricky Home', 'There is no automatic backup to restore.')
        return
    # A blocked restore is desirable if anything has been edited since apply.
    if not DIALOG.yesno('Restore saved Home?',
                        'Restore the most recent backed-up Home widget file?\n'
                        'This will refuse to overwrite any newer edits.'):
        return
    result = core.restore_home(path, folder, current_profile())
    if result == 'already-restored':
        DIALOG.ok('Cricky Home', 'The original Home widgets file is already restored.')
        return
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Cricky Home', 'Original Home widgets restored exactly. Fully restart Kodi.')



def preview_cleanup():
    _, _, original, _ = home_snapshot()
    candidates = core.cleanup_candidates(original)
    if not candidates:
        DIALOG.ok('Cricky Home cleanup', 'No overlapping older rows were found. Nothing to change.')
        return
    remaining = core.plan_cleanup(original)
    details = ('Remove ONLY the following older Home widgets:\n\n' +
               '\n'.join('{}. {}'.format(index + 1, row['label']) for index, row in candidates)
               + '\n\n{} existing rows will remain in their original order.\n'
                 'Continue Watching, Up Next Episodes, the three personalised '
                 'widgets, all other Home sections, and other Kodi profiles are unchanged.'
                 .format(len(remaining)))
    DIALOG.textviewer('Preview duplicate cleanup - read only', details)


def cleanup_duplicates():
    path, raw, original, _ = home_snapshot()
    candidates = core.cleanup_candidates(original)
    if not candidates:
        DIALOG.ok('Cricky Home cleanup', 'No overlapping older rows were found. Nothing to change.')
        return
    labels = '\n'.join('• ' + row['label'] for _, row in candidates)
    DIALOG.textviewer('Duplicate cleanup preview - nothing changed',
                      'The following {} older Home rows will be removed:\n\n{}\n\n'
                      'All other widgets, including Up Next Episodes, remain unchanged.'
                      .format(len(candidates), labels))
    if not DIALOG.yesno('Remove redundant Home widgets?',
                        'Create a verified backup and remove exactly {} older rows?\n'
                        'All newer personalised and other Home widgets remain.'.format(len(candidates))):
        return
    verify_cricky()
    backup = core.apply_home(path, backups_path(), core.sha256(raw), current_profile(),
                             planner=core.plan_cleanup)
    if backup is None:
        DIALOG.ok('Cricky Home cleanup', 'No change necessary.')
        return
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Cricky Home cleanup', 'Redundant rows removed and a byte-exact backup saved.\n'
              'Fully restart Kodi to refresh the Home screen.')


def preview_poster_style():
    _, _, old, _ = home_snapshot()
    candidates = core.poster_style_candidates(old)
    if not candidates:
        DIALOG.ok('Cricky poster rows', 'All three personalised rows already have Poster style. No change needed.')
        return
    lines = ['The following personalised Home rows will use the SAME narrow Poster layout as other catalogue rows:', '']
    for index, row in candidates:
        lines.append('{}. {}: {} -> Poster'.format(index + 1, row['label'],
                         row.get('widget_style') or '(unspecified - Landscape fallback)'))
    lines.extend(['', 'Only these widget_style values change. The exact Home file is backed up.',
                  'Continue Watching, all existing rows, mixed Trakt feeds, artwork and playback are otherwise preserved.'])
    DIALOG.textviewer('Preview Poster tile style - no changes', '\n'.join(lines))


def apply_poster_style():
    path, raw, old, _ = home_snapshot()
    candidates = core.poster_style_candidates(old)
    if not candidates:
        DIALOG.ok('Cricky poster rows', 'Personalised rows already use Poster style. Nothing changed.')
        return
    description = '\n'.join('{}. {} ({}) -> Poster'.format(i + 1, row['label'],
                         row.get('widget_style') or 'default Landscape') for i, row in candidates)
    DIALOG.textviewer('Poster tile correction - preview only',
                      'Only the following Home widget style properties will change:\n\n' +
                      description + '\n\nNo title feeds, Trakt data, playback callbacks, or other rows change.')
    if not DIALOG.yesno('Use standard Poster tiles?',
                        'Back up the exact Cricky Home widget file and change ONLY the {} personalised widget styles to Poster?'.format(len(candidates))):
        return
    verify_cricky()
    folder = core.apply_home(path, backups_path(), core.sha256(raw),
                             current_profile(), planner=core.plan_poster_style)
    if folder is None:
        DIALOG.ok('Cricky poster rows', 'No change needed.')
        return
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Cricky poster rows', 'Saved and backed up. Fully quit and restart Kodi.\n'
              'The three personalised Home sections should now have standard narrow Poster tiles.')


def hidden_gems(action):
    verify_cricky()
    skin_dir = os.path.dirname(home_path())
    root = os.path.join(backups_path(), 'hidden-gems')
    if action == 'gems_restore':
        folder = core.latest_backup(root)
        if folder is None:
            DIALOG.ok('Hidden Gems', 'There is no Hidden Gems backup.')
            return
        filename = json.loads((folder / 'manifest.json').read_text('utf-8'))['filename']
        if not core.WIDGET_FILE.fullmatch(filename):
            raise RuntimeError('Unexpected widget backup filename')
        path = os.path.join(skin_dir, filename)
        if not DIALOG.yesno('Restore Hidden Gems?', 'Restore the saved widget file {}?'.format(filename)):
            return
        verify_cricky()
        if os.path.dirname(home_path()) != skin_dir or os.path.islink(path):
            raise RuntimeError('Widget folder or file changed during confirmation')
        core.restore_home(path, folder, current_profile(), filename=filename)
    else:
        match = core.hidden_gems_snapshot(skin_dir)
        if match is None:
            DIALOG.ok('Hidden Gems', 'No exact legacy label found in Cricky’s saved Arctic Fuse 3 widgets.')
            return
        path, raw = match
        DIALOG.textviewer('Hidden Gems preview', '{}\n\n{} → Hidden Gems'.format(
            path.name, core.HIDDEN_GEMS_OLD))
        if action == 'gems_preview' or not DIALOG.yesno(
                'Rename Hidden Gems?', 'Save a verified backup and rename the widget in {}?'.format(path.name)):
            return
        verify_cricky()
        if os.path.dirname(home_path()) != skin_dir or path.is_symlink():
            raise RuntimeError('Widget folder or file changed during confirmation')
        core.apply_home(path, root, core.sha256(raw), current_profile(),
                        planner=core.plan_hidden_gems, filename=path.name)
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Hidden Gems', 'Widget configuration saved. Fully quit and restart Kodi.')


def ai_suggestions(apply=False):
    verify_cricky()
    path = home_path()
    raw = open(path, 'rb').read()
    original = core.load_home(raw)
    planned = core.plan_ai_suggestions(original)
    if planned == original:
        DIALOG.ok('Your AI Suggestions', 'Already installed.')
        return
    records = tmdb_directory(core.AI_PATH)
    if not records:
        raise RuntimeError('AI list is empty or unavailable; Home unchanged.')
    DIALOG.textviewer('AI Suggestions preview', 'Insert Your AI Suggestions below Continue Watching.\\nAll existing rows preserved.\\nSource returned {} entries.'.format(len(records)))
    if not apply or not DIALOG.yesno('Add Your AI Suggestions?', 'Back up and update Cricky Home?'):
        return
    verify_cricky()
    if home_path() != path:
        raise RuntimeError('Profile path changed')
    core.apply_home(path, backups_path(), core.sha256(raw), current_profile(),
                    planner=core.plan_ai_suggestions)
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Your AI Suggestions', 'Saved. Fully restart Kodi.')



# Continue Watching integration candidate (opt-in).
import continue_watching_feed as cw_feed
import continue_watching_widget as cw_widget
from continue_watching_store import DismissalStore
from continue_watching_render import render as cw_render
from continue_watching_action import remove as cw_remove

def cw_rpc(method, params):
    response = json.loads(xbmc.executeJSONRPC(json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params})))
    if 'error' in response:
        raise RuntimeError('Kodi directory or player request failed')
    return response['result']

def cw_refresh():
    cw_widget.refresh(xbmcgui)

def cw_store():
    verify_cricky()
    return DismissalStore(translated('special://profile/'))

def cw_command(key):
    return 'RunPlugin(plugin://{}/?{})'.format(core.ADDON_ID, urlencode({'action':'cw_remove','key':key}))

def cw_listing(handle):
    rows = cw_feed.fetch_visible(cw_rpc, cw_store())
    xbmcplugin.setContent(handle,'videos')
    for row in rows:
        cw_render(row,xbmcgui,xbmcplugin,handle,cw_command)
    xbmcplugin.endOfDirectory(handle,succeeded=True,cacheToDisc=False)

def cw_dismiss(key):
    store = cw_store()
    profile = translated('special://profile/')
    def active():
        verify_cricky()
        return translated('special://profile/')
    if not cw_remove(key,profile=profile,current_profile=active,rpc=cw_rpc,store=store,refresh=cw_refresh):
        raise RuntimeError('Title or profile no longer matches')

def cw_configure(enable):
    verify_cricky()
    path = home_path()
    raw = open(path,'rb').read()
    rows = core.load_home(raw)
    planner = lambda rows: cw_widget.plan_widget(rows,enable)
    if planner(rows) == rows:
        DIALOG.ok('Continue Watching','Already configured.')
        return
    if enable:
        records = cw_feed.fetch_visible(cw_rpc,cw_store())
        if not records or not all(cw_feed.dismissal_key(row) for row in records):
            raise RuntimeError('Native feed identity preflight failed; original widget retained.')
    if not DIALOG.yesno('Continue Watching','Change only the Continue Watching source and save a backup?'):
        return
    verify_cricky()
    if path != home_path():
        raise RuntimeError('Profile changed')
    core.apply_home(path,backups_path(),core.sha256(raw),current_profile(),planner=planner)
    xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
    DIALOG.ok('Continue Watching','Saved. Fully restart Kodi.')

def handle_action(action):
    if action in ('cw_enable','cw_disable'):
        cw_configure(action == 'cw_enable')
        return
    if action in ('ai_preview', 'ai_apply'):
        ai_suggestions(action == 'ai_apply')
        return
    if action in ('gems_preview', 'gems_apply', 'gems_restore'):
        hidden_gems(action)
    elif action == 'inspect':
        inspect_only()
    elif action == 'preview':
        preview_only()
    elif action == 'preflight':
        verify_cricky()
        DIALOG.textviewer('Family Trakt feed preflight', '\n'.join(preflight_sources())
                          + '\n\nCheck account selection separately in TMDb Helper Sync settings.')
    elif action == 'apply':
        preview_and_apply()
    elif action == 'restore':
        restore_latest()
    elif action == 'cleanup_preview':
        preview_cleanup()
    elif action == 'cleanup':
        cleanup_duplicates()
    elif action == 'poster_preview':
        preview_poster_style()
    elif action == 'poster_apply':
        apply_poster_style()
    else:
        raise ValueError('Unknown action')


def list_menu(handle):
    xbmcplugin.setContent(handle, 'files')
    for label, action, desc in (
            ('1. Inspect current Cricky Home (read-only)', 'inspect', 'Shows live Home labels and checksum.'),
            ('2. Preview proposed Home order (read-only)', 'preview', 'Does not make changes.'),
            ('3. Test six Family Trakt film/TV sources (read-only)', 'preflight', 'Verifies all six endpoints respond.'),
            ('4. Apply Home personalisation (one confirmation)', 'apply', 'Backs up, verifies, then changes only Cricky Home.'),
            ('5. Preview redundant-row cleanup (read-only)', 'cleanup_preview', 'Show exactly which duplicate rows would be removed.'),
            ('6. Remove redundant Home rows (one confirmation)', 'cleanup', 'Backs up Cricky Home before removing the four older overlapping rows.'),
            ('7. Restore latest automatic backup', 'restore', 'Only if no newer Home edits exist.'),
            ('8. Preview standard Poster tile style (read-only)', 'poster_preview', 'Check the 3 personalised rows before changing their size.'),
            ('9. Apply standard Poster tile style (one confirmation)', 'poster_apply', 'Back up and match the smaller tiles of the catalogue rows.'),
            ('Test Continue Watching candidate', 'continue_watching', 'Read-only filtered listing.'),
            ('Enable Continue Watching dismissal', 'cw_enable', 'Back up and change only this row.'),
            ('Disable Continue Watching dismissal', 'cw_disable', 'Return to native feed.'),
            ('Preview Your AI Suggestions', 'ai_preview', 'Check the list and proposed Home insertion.'),
            ('Add Your AI Suggestions', 'ai_apply', 'Preview and confirm a backed-up Home update.'),
            ('Preview Hidden Gems rename', 'gems_preview', 'Find the exact label in a saved Cricky hub.'),
            ('Rename Hidden Gems', 'gems_apply', 'Preview and confirm a backed-up label change.'),
            ('Restore Hidden Gems widget backup', 'gems_restore', 'Restore the original label if the file has no newer edits.'),
    ):
        add_folder(handle, label,
                   'plugin://{}/?{}'.format(core.ADDON_ID, urlencode({'action': action})),
                   plot=desc)
    for kind, label, _ in core.LABELS:
        add_folder(handle, 'Test mixed feed: ' + label, feed_link(kind, 'all'))
    xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)


def run():
    handle = int(sys.argv[1])
    query = parse_qs(sys.argv[2].lstrip('?') if len(sys.argv) > 2 else '')
    action = query.get('action', ['menu'])[0]
    try:
        if action == 'menu':
            list_menu(handle)
        elif action == 'continue_watching':
            cw_listing(handle)
        elif action == 'cw_remove':
            cw_dismiss(query.get('key',[''])[0])
            xbmcplugin.endOfDirectory(handle,succeeded=True,cacheToDisc=False)
        elif action == 'feed':
            handle_feed(handle, query)
        else:
            handle_action(action)
            xbmcplugin.endOfDirectory(handle, succeeded=True, updateListing=False, cacheToDisc=False)
    except Exception as exc:
        log('Action {} failed: {}'.format(action, repr(exc)), xbmc.LOGERROR)
        DIALOG.ok('Cricky Home - no change', str(exc)[:900])
        xbmcplugin.endOfDirectory(handle, succeeded=False, cacheToDisc=False)


if __name__ == '__main__':
    run()
