import time
import xbmc
import xbmcgui
import core
from guard import root

def log(s):
    xbmc.log('[DiagLoader] '+s,xbmc.LOGINFO)
def focus():
    try:
        n=int(xbmc.getInfoLabel('System.CurrentControlID'))
        if 501<=n<=510:
            return n-501
        if 701<=n<=710:
            return n-701
    except (ValueError,TypeError):
        pass
    return None
def run():
    try:
        profile=root()
        mode=core.mode(profile)
        if mode=='standard' or not core.same(core.snapshot(core.safe_path(profile,core.REL)),core.deferred()):
            return
    except Exception:
        return
    monitor=xbmc.Monitor()
    home=xbmcgui.Window(10000)
    initialized=False
    sched=core.Scheduler(mode)
    was_home=False
    try:
        while not monitor.abortRequested():
            try:
                if root()!=profile or core.mode(profile)!=mode:
                    break
            except Exception:
                break
            active=xbmcgui.getCurrentWindowId()==10000 and not xbmc.Player().isPlaying()
            if active and not initialized:
                for i in range(10):
                    home.setProperty(core.prop(i),core.placeholder(i))
                initialized=True
                log('mode='+mode+' placeholders ready')
            if active and initialized:
                # Confirm the native content actually replaced the one-item placeholder.
                # NumItems > 1 and not updating are deliberately conservative.
                observed={}
                for i in sched.pending:
                    cid=501+i
                    count=xbmc.getInfoLabel('Container(%d).NumItems'%cid)
                    try:
                        observed[i]=int(count)>1 and not xbmc.getCondVisibility('Container(%d).IsUpdating'%cid)
                    except ValueError:
                        observed[i]=False
                before=set(sched.done)
                launch=sched.tick(time.monotonic(),True,focus(),observed)
                for i in sorted(sched.done-before):
                    log('ready row=%d'%(i+1))
                for i in launch:
                    home.setProperty(core.prop(i),core.native(i))
                    log('activate row=%d'%(i+1))
                if sched.failed:
                    log('timeout; further row activation paused')
                    break
                if not was_home:
                    log('Home entered; active rows=%d'%len(sched.started))
            elif was_home:
                log('Home left; scheduling paused')
            was_home=active
            if monitor.waitForAbort(0.5):
                break
    except Exception as exc:
        log('stopped '+type(exc).__name__)
    # Do not clear properties on a search transition or timeout. They are runtime-only.
if __name__=='__main__':
    run()
