"""Candidate monitor adapter, injected Kodi dependencies for testing."""
from time import monotonic
import json
import xbmcgui
from continue_watching_playback import Viewing, playing_key, verified_episode_key
from continue_watching_store import DismissalStore

def run(xbmc, xbmcvfs, rpc, refresh):
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    viewing = Viewing()
    window = xbmcgui.Window(10000)
    prefix = 'TVStreaming.CW.Diagnostics.'
    probe = None
    fallback = None
    while not monitor.abortRequested():
        try:
            profile = xbmcvfs.translatePath('special://profile/')
            name = xbmc.getInfoLabel('System.ProfileName')
            window.setProperty(prefix + 'heartbeat', str(monotonic()))
            if name.strip().casefold() != 'cricky' or not player.isPlayingVideo():
                viewing.reset()
                probe = fallback = None
            else:
                tag = player.getVideoInfoTag()
                report = {'media': tag.getMediaType(), 'show': tag.getTVShowTitle(), 'title': tag.getTitle(), 'season': tag.getSeason(), 'episode': tag.getEpisode(), 'tmdb': tag.getUniqueID('tmdb'), 'tvshow.tmdb': tag.getUniqueID('tvshow.tmdb'), 'imdb': tag.getUniqueID('imdb')}
                window.setProperty(prefix + 'last', json.dumps(report))
                key = playing_key(tag)
                file = player.getPlayingFile()
                if not key:
                    signature = (profile, file, tag.getUniqueID('tmdb'), tag.getUniqueID('imdb'), tag.getSeason(), tag.getEpisode())
                    if probe != signature:
                        probe = signature
                        fallback = verified_episode_key(tag, rpc, xbmc.getInfoLabel)
                        xbmc.log('TVStreaming CW: fallback ' + ('verified' if fallback else 'unverified'), xbmc.LOGINFO)
                    key = fallback
                report.update(key=key, fallback=fallback, hidden=list(DismissalStore(profile).read()))
                window.setProperty(prefix + 'last', json.dumps(report))
                position = player.getTime()
                result = rpc('Player.GetProperties', {'playerid': 1, 'properties': ['speed']})
                if (profile != xbmcvfs.translatePath('special://profile/') or
                    name != xbmc.getInfoLabel('System.ProfileName') or
                    not player.isPlayingVideo() or file != player.getPlayingFile()):
                    viewing.reset()
                else:
                    cleared = viewing.sample(profile, key, file, position, monotonic(), result.get('speed'), DismissalStore(profile))
                    report.update(speed=result.get('speed'), elapsed=round(viewing.elapsed,2), done=viewing.done, cleared=cleared, hidden_after=list(DismissalStore(profile).read()))
                    if cleared:
                        window.setProperty(prefix + 'cleared', str(key))
                        xbmc.log('TVStreaming CW: dismissal cleared', xbmc.LOGINFO)
                        refresh()
                    window.setProperty(prefix + 'last', json.dumps(report))
        except Exception as exc:
            window.setProperty(prefix + 'error', type(exc).__name__)
            xbmc.log('TVStreaming CW monitor: ' + type(exc).__name__, xbmc.LOGWARNING)
            viewing.reset()
        if monitor.waitForAbort(1):
            break
