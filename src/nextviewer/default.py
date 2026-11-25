import xbmcgui
window = xbmcgui.Window(10000)
data = window.getProperty("tvstreaming.nextdiagnostic")
xbmcgui.Dialog().textviewer("Next Episode Diagnostic", data or "No snapshot captured. Restart Kodi, play an episode for 60 seconds, stop and reopen this viewer.")
