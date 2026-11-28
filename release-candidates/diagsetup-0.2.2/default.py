import sys
import time
import json
import xbmc
import xbmcgui
import xbmcaddon
import core
from guard import root

OPTIONS = ['Standard - all ten native rows', 'Staggered - two rows at a time', 'Lazy - first two, then near focus', 'Restore original diag Home','Diagnostic status (read only)']

def run(action=None):
    dlg=xbmcgui.Dialog()
    try:
        profile=root()
        xbmcaddon.Addon('plugin.video.themoviedb.helper')
        if xbmc.Player().isPlaying():
            raise ValueError('Stop playback first.')
        if action is None:
            action=dlg.select('Diag Widget Loading',OPTIONS)
        if action not in range(5):
            return
        if action==4:
            actual=core.config_kind(core.snapshot(core.safe_path(profile,core.REL)))
            saved=core.mode(profile)
            s=core.read_status(profile)
            live=xbmc.getInfoLabel('Window(Home).Property(TVStreaming.Diag.Status)')
            if live:
                try:
                    s=json.loads(live)
                except ValueError:
                    pass
            age=round(max(0,time.time()-s.get('time',0))) if s.get('time') else None
            fresh=age is not None and age<=15 and s.get('mode')==saved and bool(live)
            message=('Saved mode: %s\nHome paths: %s\nScheduler: %s\nLoaded: %s / 10 | Pending: %s | Deferred: %s\nLast update: %s\nReason: %s' %
                (saved,actual,s.get('state','not started') if fresh else 'not verified active',
                 s.get('loaded','?'),s.get('pending','?'),s.get('deferred','?'),
                 str(age)+' sec ago' if age is not None else 'none',s.get('reason','No runtime status')))
            dlg.ok('Diagnostic status',message)
            return
        previous=core.snapshot(core.safe_path(profile,core.REL))
        if not dlg.yesno('Diagnostics only','Change ONLY diag Home? All ten row labels are retained in each test mode. Restart Kodi after applying.'):
            return
        if root()!=profile or xbmc.Player().isPlaying():
            raise ValueError('Profile changed or playback started.')
        result=core.restore(profile) if action==3 else core.apply(profile,previous,core.MODES[action])
        xbmc.log('[DiagSetup] '+result,xbmc.LOGINFO)
        core.write_status(profile,{'state':'restart required','mode':core.mode(profile),'reason':'Configuration saved; native template rebuild requested','time':time.time()})
        xbmcgui.Window(10000).clearProperty('TVStreaming.Diag.Status')
        # The template parameter is a suffix, not a path. Use the native default generator.
        xbmc.executebuiltin('Skin.SetString(Shortcuts.RebuildDateTime,DiagSetup-%d)' % time.time())
        xbmc.executebuiltin('RunScript(script.skinvariables,action=buildtemplate,force=true,background=true)')
        dlg.ok('Diagnostics',result+'\nAfter skin rebuilding completes, fully quit Kodi and restart into diag. Check Diagnostic status before testing.')
    except Exception as exc:
        xbmc.log('[DiagSetup] '+type(exc).__name__,xbmc.LOGERROR)
        dlg.ok('Diagnostics - stopped',str(exc)[:600])


if __name__=='__main__':
    run()
