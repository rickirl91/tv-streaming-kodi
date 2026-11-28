import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import core

def root():
    return core.verify(xbmc.getInfoLabel('System.ProfileName'), xbmc.getSkinDir(),
                       xbmcvfs.translatePath('special://profile/'),
                       xbmcvfs.translatePath('special://masterprofile/'))

def run():
    dlg = xbmcgui.Dialog()
    try:
        profile = root()
        xbmcaddon.Addon('plugin.video.themoviedb.helper')
        if xbmc.Player().isPlaying():
            raise ValueError('Stop playback first.')
        action = dlg.select('Diag native widget setup', [
            'Apply ten native TMDb Helper widgets',
            'Restore previous diag Home'])
        if action < 0:
            return
        previous = core.snapshot(core.safe_path(profile, core.REL))
        if action == 0:
            msg = 'Replace ONLY diag Home widgets with these ten rows?\n\n' + '\n'.join(x[0] for x in core.ROWS)
        else:
            msg = 'Restore the original diag Home widget configuration?'
        if not dlg.yesno('Diagnostics only', msg):
            return
        if root() != profile or xbmc.Player().isPlaying():
            raise ValueError('Profile changed or playback started.')
        result = core.apply(profile, previous) if action == 0 else core.restore(profile)
        xbmc.log('[DiagSetup] ' + result, xbmc.LOGINFO)
        # Native skin generator, scoped by the active skin user. No installed skin edits.
        xbmc.executebuiltin('RunScript(script.skinvariables,template=special://skin/shortcuts/skinvariables-generator.json)')
        dlg.ok('Diagnostics', result + '\nFully quit Kodi and restart into diag.')
    except Exception as exc:
        xbmc.log('[DiagSetup] ' + type(exc).__name__, xbmc.LOGERROR)
        dlg.ok('Diagnostics - stopped', str(exc)[:600])

if __name__ == '__main__':
    run()
