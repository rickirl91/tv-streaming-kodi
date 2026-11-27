"""Capture playback only; catalogue verification is explicitly user-triggered."""
from time import monotonic
import json
import re
import xbmcgui
from continue_watching_playback import Viewing, playing_key
from continue_watching_store import DismissalStore
from continue_watching_feed import SOURCE, PROPERTIES, dismissal_key

def resolve(report, rpc):
    if report['key']:
        return report['key']
    candidate = report['tmdb']
    show = report['show']
    if report['media'] not in ('episode','video','') or not re.fullmatch(r'[1-9][0-9]*', candidate or '') or not show or report['season'] < 0 or report['episode'] < 1:
        return None
    rows = rpc('Files.GetDirectory', {'directory': SOURCE, 'media':'video','properties':PROPERTIES}).get('files', [])
    matches = {dismissal_key(r) for r in rows if dismissal_key(r) == 'tv:'+candidate and str(r.get('showtitle','')).strip().casefold() == show.strip().casefold()}
    return next(iter(matches)) if len(matches)==1 else None

def process_pending(store, rpc, safe):
    """Only call from an explicit foreground action, never from the service."""
    count = 0
    for i, report in store.pending():
        if not safe():
            break
        store.journal('Manual identity verification')
        key = resolve(report, rpc)
        if not safe():
            break
        if key and store.commit_pending(i, key):
            count += 1
            store.journal('Manual activity committed; no Home refresh')
        elif not key:
            store.journal('Manual identity unverified')
    return count

class Capture:
    def __init__(self, store, report):
        self.store, self.report = store, report
    def record_viewing(self, key):
        self.store.queue(self.report)
        self.store.journal('Viewing queued')

def run(xbmc, xbmcvfs, rpc):
    monitor, player, viewing = xbmc.Monitor(), xbmc.Player(), Viewing()
    window = xbmcgui.Window(10000)
    prefix = 'TVStreaming.CW.Diagnostics.'
    last_profile = None
    while not monitor.abortRequested():
        try:
            profile = xbmcvfs.translatePath('special://profile/')
            name = xbmc.getInfoLabel('System.ProfileName')
            window.setProperty(prefix+'heartbeat', str(monotonic()))
            if profile != last_profile:
                viewing.reset()
                last_profile = profile
            if name.strip().casefold() != 'cricky':
                viewing.reset()
            elif player.isPlayingVideo():
                tag = player.getVideoInfoTag()
                key = playing_key(tag)
                report = {'key':key,'media':tag.getMediaType(),'show':tag.getTVShowTitle() or xbmc.getInfoLabel('VideoPlayer.TVShowTitle'),'tmdb':tag.getUniqueID('tmdb'),'season':tag.getSeason(),'episode':tag.getEpisode()}
                file = player.getPlayingFile()
                position = player.getTime()
                speed = rpc('Player.GetProperties', {'playerid':1,'properties':['speed']}).get('speed')
                if profile == xbmcvfs.translatePath('special://profile/') and name == xbmc.getInfoLabel('System.ProfileName') and player.isPlayingVideo() and file == player.getPlayingFile():
                    token = key or 'unverified:'+str(report['tmdb'])+':'+report['show']
                    viewing.sample(profile,token,file,position,monotonic(),speed,Capture(DismissalStore(profile),report))
                    window.setProperty(prefix+'last',json.dumps(dict(report,elapsed=viewing.elapsed,done=viewing.done)))
                else:
                    viewing.reset()
            else:
                viewing.reset()
        except Exception as exc:
            window.setProperty(prefix+'error',type(exc).__name__)
            xbmc.log('TVStreaming CW monitor: '+type(exc).__name__,xbmc.LOGWARNING)
            viewing.reset()
        if monitor.waitForAbort(1):
            break
