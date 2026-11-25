import xbmc
import xbmcgui
from diagnostic import snapshot

monitor = xbmc.Monitor()
previous = None
while not monitor.abortRequested():
    try:
        current = snapshot()
        if current != "No active video" and current != previous:
            xbmcgui.Window(10000).setProperty("tvstreaming.nextdiagnostic", current)
        previous = current
    except Exception:
        xbmc.log("[TV Streaming diagnostic] metadata unavailable", xbmc.LOGWARNING)
    if monitor.waitForAbort(30):
        break

xbmcgui.Window(10000).clearProperty('tvstreaming.nextdiagnostic')
