"""Candidate monitor adapter, injected Kodi dependencies for testing."""
from time import monotonic
from continue_watching_playback import Viewing, playing_key
from continue_watching_store import DismissalStore

def run(xbmc, xbmcvfs, rpc, refresh):
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    viewing = Viewing()
    while not monitor.abortRequested():
        try:
            profile = xbmcvfs.translatePath('special://profile/')
            name = xbmc.getInfoLabel('System.ProfileName')
            if name.strip().casefold() != 'cricky' or not player.isPlayingVideo():
                viewing.reset()
            else:
                key = playing_key(player.getVideoInfoTag())
                file = player.getPlayingFile()
                position = player.getTime()
                result = rpc('Player.GetProperties', {'playerid': 1, 'properties': ['speed']})
                if (profile != xbmcvfs.translatePath('special://profile/') or
                    name != xbmc.getInfoLabel('System.ProfileName') or
                    not player.isPlayingVideo() or file != player.getPlayingFile()):
                    viewing.reset()
                elif viewing.sample(profile, key, file, position, monotonic(), result.get('speed'), DismissalStore(profile)):
                    refresh()
        except Exception:
            viewing.reset()
        if monitor.waitForAbort(1):
            break
