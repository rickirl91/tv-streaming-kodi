import json
import time
import xbmc
import xbmcgui
import core
from guard import root

KEY='TVStreaming.Diag.Status'
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
    log('v0.2.2 startup')
    monitor=xbmc.Monitor()
    profile=None
    # Kodi can invoke services before skin/profile initialization completes.
    for _ in range(40):
        name=xbmc.getInfoLabel('System.ProfileName')
        if name and name.strip().casefold()!='diag':
            log('inactive: not diag')
            return
        try:
            profile=root()
            break
        except Exception as exc:
            if monitor.waitForAbort(0.5):
                return
    if profile is None:
        log('inactive: diag profile/skin guard never became ready')
        return
    home=xbmcgui.Window(10000)
    mode='unknown'
    sched=None
    last=None
    last_write=0
    def report(state,reason):
        nonlocal last,last_write
        now=time.time()
        data={'mode':mode,'state':state,'reason':reason,
              'loaded':len(sched.done) if sched else 0,
              'pending':len(sched.pending) if sched else 0,
              'deferred':10-len(sched.started) if sched else 10}
        if data!=last or now-last_write>=5:
            if data!=last:
                log('%s mode=%s loaded=%s pending=%s deferred=%s reason=%s' %
                    (state,mode,data['loaded'],data['pending'],data['deferred'],reason))
            last=data.copy()
            last_write=now
            data['time']=now
            core.write_status(profile,data)
            home.setProperty(KEY,json.dumps(data,separators=(',',':')))
    try:
        mode=core.mode(profile)
        kind=core.config_kind(core.snapshot(core.safe_path(profile,core.REL)))
        log('saved mode='+mode+' home paths='+kind)
        if mode=='standard':
            report('inactive','Standard mode selected; scheduler not required')
            return
        if kind!='deferred':
            report('blocked','Saved mode requires deferred Home paths; found '+kind)
            return
        sched=core.Scheduler(mode)
        initialized=False
        was_home=False
        report('waiting','Awaiting Home')
        while not monitor.abortRequested():
            try:
                if root()!=profile or core.mode(profile)!=mode:
                    log('stopped: profile or mode changed')
                    return
            except Exception as exc:
                log('stopped: profile guard '+type(exc).__name__)
                return
            active=xbmcgui.getCurrentWindowId()==10000 and not xbmc.Player().isPlaying()
            if active and not initialized:
                for i in range(10):
                    home.setProperty(core.prop(i),core.placeholder(i))
                initialized=True
                log('mode='+mode+' placeholders ready')
            if active and initialized and not sched.failed:
                observed={}
                for i in sched.pending:
                    cid=501+i
                    try:
                        count=int(xbmc.getInfoLabel('Container(%d).NumItems'%cid))
                        observed[i]=count>1 and not xbmc.getCondVisibility('Container(%d).IsUpdating'%cid)
                    except ValueError:
                        observed[i]=False
                before=set(sched.done)
                launch=sched.tick(time.monotonic(),True,focus(),observed)
                for i in sorted(sched.done-before):
                    log('ready row=%d'%(i+1))
                for i in launch:
                    home.setProperty(core.prop(i),core.native(i))
                    log('activate row=%d'%(i+1))
                if not was_home:
                    log('Home entered; active rows=%d'%len(sched.started))
            elif was_home:
                log('Home left; scheduling paused')
            if sched.failed:
                report('blocked','Row readiness timeout; check generated paths and control IDs')
            elif not active:
                report('paused','Away from Home')
            elif len(sched.done)==10:
                report('complete','All ten rows reported ready')
            else:
                report('active','Native row activation; readiness inferred from container state')
            was_home=active
            if monitor.waitForAbort(0.5):
                break
    except Exception as exc:
        log('stopped: '+type(exc).__name__+': '+str(exc)[:200])
        try:
            report('blocked',type(exc).__name__)
        except Exception:
            pass
if __name__=='__main__':
    run()
