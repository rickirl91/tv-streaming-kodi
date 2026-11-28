import sys
import xbmc
import xbmcgui
import xbmcaddon
import core
from guard import root

OPTIONS = ['Standard - all ten native rows', 'Staggered - two rows at a time', 'Lazy - first two, then near focus', 'Restore original diag Home']

def run(action=None):
    dlg=xbmcgui.Dialog()
    try:
        profile=root()
        xbmcaddon.Addon('plugin.video.themoviedb.helper')
        if xbmc.Player().isPlaying():
            raise ValueError('Stop playback first.')
        if action is None:
            action=dlg.select('Diag Widget Loading',OPTIONS)
        if action not in range(4):
            return
        previous=core.snapshot(core.safe_path(profile,core.REL))
        if not dlg.yesno('Diagnostics only','Change ONLY diag Home? All ten row labels are retained in each test mode. Restart Kodi after applying.'):
            return
        if root()!=profile or xbmc.Player().isPlaying():
            raise ValueError('Profile changed or playback started.')
        result=core.restore(profile) if action==3 else core.apply(profile,previous,core.MODES[action])
        xbmc.log('[DiagSetup] '+result,xbmc.LOGINFO)
        xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
        dlg.ok('Diagnostics',result+'\nFully quit Kodi and restart into diag.')
    except Exception as exc:
        xbmc.log('[DiagSetup] '+type(exc).__name__,xbmc.LOGERROR)
        dlg.ok('Diagnostics - stopped',str(exc)[:600])


if __name__=='__main__':
    run()
