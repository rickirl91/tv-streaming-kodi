"""Candidate monitor adapter, injected Kodi dependencies for testing."""
from time import monotonic
from continue_watching_playback import Viewing, playing_key, verified_episode_key
from continue_watching_store import DismissalStore

def run(xbmc, xbmcvfs, rpc, refresh):
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    viewing = Viewing()
    probe = None
    fallback = None
    while not monitor.abortRequested():
        try:
            profile = xbmcvfs.translatePath('special://profile/')
            name = xbmc.getInfoLabel('System.ProfileName')
            if name.strip().casefold() != 'cricky' or not player.isPlayingVideo():
                viewing.reset()
                probe = fallback = None
            else:
                tag = player.getVideoInfoTag()
                key = playing_key(tag)
                file = player.getPlayingFile()
                if not key:
                    signature = (profile, file, tag.getUniqueID('tmdb'), tag.getUniqueID('imdb'), tag.getSeason(), tag.getEpisode())
                    if probe != signature:
                        probe = signature
                        fallback = verified_episode_key(tag, rpc, xbmc.getInfoLabel)
                        xbmc.log('TVStreaming CW: fallback ' + ('verified' if fallback else 'unverified'), xbmc.LOGINFO)
                    key = fallback
                position = player.getTime()
                result = rpc('Player.GetProperties', {'playerid': 1, 'properties': ['speed']})
                if (profile != xbmcvfs.translatePath('special://profile/') or
                    name != xbmc.getInfoLabel('System.ProfileName') or
                    not player.isPlayingVideo() or file != player.getPlayingFile()):
                    viewing.reset()
                elif viewing.sample(profile, key, file, position, monotonic(), result.get('speed'), DismissalStore(profile)):
                    xbmc.log('TVStreaming CW: dismissal cleared', xbmc.LOGINFO)
                    refresh()
        except Exception as exc:
            xbmc.log('TVStreaming CW monitor: ' + type(exc).__name__, xbmc.LOGWARNING)
            viewing.reset()
        if monitor.waitForAbort(1):
            break
