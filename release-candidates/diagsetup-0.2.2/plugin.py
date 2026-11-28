import sys
import xbmc
import xbmcgui
import xbmcplugin
from urllib.parse import parse_qs
import core
from guard import root
from default import run, OPTIONS

BASE='plugin://script.tvstreaming.diagsetup/'
def directory(argv=None):
    argv=sys.argv if argv is None else argv
    handle=int(argv[1])
    success=False
    try:
        profile=root()
        query=parse_qs(argv[2].lstrip('?')) if len(argv)>2 else {}
        if not query:
            # Kodi can open the add-on as a video directory rather than a script.
            for i,label in enumerate(OPTIONS):
                item=xbmcgui.ListItem(label=label)
                item.setArt({'icon':'DefaultFolder.png','thumb':'DefaultFolder.png'})
                xbmcplugin.addDirectoryItem(handle,BASE+'?action='+str(i),item,isFolder=True)
            success=True
        elif set(query)=={'action'}:
            action=int(query['action'][0])
            if action not in range(5):
                raise ValueError('Invalid action')
            run(action)
            success=True
        elif set(query)=={'row'}:
            i=int(query['row'][0])
            if not 0<=i<10 or core.mode(profile) not in ('staggered','lazy'):
                raise ValueError('Invalid placeholder')
            item=xbmcgui.ListItem(label='Load '+core.ROWS[i][0])
            item.setArt({'icon':'DefaultFolder.png','thumb':'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(handle,core.native(i),item,isFolder=True)
            success=True
        else:
            raise ValueError('Invalid route')
        xbmcplugin.setContent(handle,'videos')
    except Exception as exc:
        xbmc.log('[DiagSetup] directory stopped: '+type(exc).__name__,xbmc.LOGERROR)
    finally:
        xbmcplugin.endOfDirectory(handle,succeeded=success,cacheToDisc=False)

if __name__=='__main__':
    directory()
