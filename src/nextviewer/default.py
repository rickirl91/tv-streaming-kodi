"""Launch the service diagnostic through the visible program add-on."""
import os
import xbmc
import xbmcaddon
import xbmcgui
try:
    path = xbmcaddon.Addon("service.tvstreaming.nextepisode").getAddonInfo("path")
    xbmc.executebuiltin("RunScript(" + os.path.join(path, "diagnostic.py") + ")")
except Exception:
    xbmcgui.Dialog().ok("Next Episode Viewer", "Next Episode 0.2.3 is required.")
