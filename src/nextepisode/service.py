import xbmc
from diagnostic import snapshot

monitor = xbmc.Monitor()
previous = None
while not monitor.abortRequested():
    try:
        current = snapshot()
        if current != "No active video" and current != previous:
            xbmc.log("[TV Streaming diagnostic] " + current, xbmc.LOGINFO)
        previous = current
    except Exception:
        xbmc.log("[TV Streaming diagnostic] metadata unavailable", xbmc.LOGWARNING)
    if monitor.waitForAbort(30):
        break
