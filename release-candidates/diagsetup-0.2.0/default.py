import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from urllib.parse import parse_qs
import core
from guard import root

def run():
    dlg=xbmcgui.Dialog()
    try:
        profile=root()
        xbmcaddon.Addon('plugin.video.themoviedb.helper')
        if xbmc.Player().isPlaying():
            raise ValueError('Stop playback first.')
        action=dlg.select('Diag Widget Loading',[
            'Standard - all ten native rows',
            'Staggered - two rows at a time',
            'Lazy - first two, then near focus',
            'Restore original diag Home'])
        if action<0:
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

def directory():
    handle=int(sys.argv[1])
    try:
        profile=root()
        i=int(parse_qs(sys.argv[2].lstrip('?'))['row'][0])
        if not 0<=i<10 or core.mode(profile) not in ('staggered','lazy'):
            raise ValueError('Invalid placeholder')
        label='Load '+core.ROWS[i][0]
        item=xbmcgui.ListItem(label=label)
        item.setArt({'icon':'DefaultFolder.png','thumb':'DefaultFolder.png'})
        # A selectable folder keeps an unloaded row navigable. Clicking opens the native list.
        xbmcplugin.addDirectoryItem(handle,core.native(i),item,isFolder=True)
        xbmcplugin.setContent(handle,'videos')
        xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
    except Exception:
        xbmcplugin.endOfDirectory(handle,succeeded=False,cacheToDisc=False)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1].isdigit():
        directory()
    else:
        run()
