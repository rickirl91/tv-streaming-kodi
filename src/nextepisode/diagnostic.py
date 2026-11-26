"""Read-only Xbox playback diagnostic. No playback commands or network requests."""
import json
import xbmc
import xbmcgui

def rpc(method, params):
    result = json.loads(xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})))
    return result.get("result", {})

def snapshot():
    players = rpc("Player.GetActivePlayers", {})
    video = next((p for p in players if p.get("type") == "video"), None)
    if not video:
        return "No active video"
    pid = video["playerid"]
    item = rpc("Player.GetItem", {"playerid":pid,"properties":["title","showtitle","season","episode","uniqueid"]}).get("item", {})
    props = rpc("Player.GetProperties", {"playerid":pid,"properties":["time","totaltime","speed"]})
    safe = {k:item.get(k) for k in ("type","title","showtitle","season","episode")}
    ids = item.get("uniqueid") or {}
    safe["identifier_types"] = [k for k in ("tmdb","tvdb","imdb","trakt") if ids.get(k)]
    labels = {}
    for key in ("Title", "TVShowTitle", "Season", "Episode", "IMDBNumber"):
        value = xbmc.getInfoLabel("VideoPlayer." + key)
        # Only expose numeric season/episode and presence of identifiers.
        if key in ("Season", "Episode"):
            labels[key] = value if value.isdigit() else ""
        elif key == "IMDBNumber":
            labels[key] = bool(value)
        else:
            # Titles may fall back to stream URLs; never display those.
            labels[key] = value[:160] if value and not any(x in value for x in ("://", "/", "\\", "?")) else ""
    safe["video_labels"] = labels
    try:
        tag = xbmc.Player().getVideoInfoTag()
        safe["video_tag"] = {"season": tag.getSeason(), "episode": tag.getEpisode(),
                             "show_present": bool(tag.getTVShowTitle()),
                             "identifier_types": [k for k in ("tmdb", "tvdb", "imdb") if tag.getUniqueID(k)]}
    except Exception:
        safe["video_tag"] = "unavailable"
    safe["playback"] = props
    return json.dumps(safe, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    try:
        current = xbmcgui.Window(10000).getProperty("tvstreaming.nextdiagnostic") or snapshot()
        dialog = xbmcgui.Dialog()
        choice = dialog.select("TV Streaming diagnostic", ["Playback report", "Overlay preview", "Independent Supernatural catalogue test"])
        if choice == 2:
            from service import resolve
            reasons = []
            identity = dict(show="Supernatural", title="Dead in the Water", season=1, episode=3, series_id="1622", parent_verified=False, imdb="tt0460681", group="")
            try:
                target = resolve(identity, "preview.json", reasons.append)
                result = {"verified": bool(target), "requests": reasons}
                if target:
                    result["next"] = {k: target[k] for k in ("season", "episode", "title")}
            except Exception as exc:
                result = {"error": type(exc).__name__, "requests": reasons}
            dialog.textviewer("Independent catalogue test", json.dumps(result, indent=2))
        elif choice == 1:
            if xbmc.Player().isPlaying():
                dialog.ok("Preview", "Stop playback before previewing.")
            else:
                import xbmcaddon
                from overlay import Overlay
                preview = Overlay("NextEpisode.xml", xbmcaddon.Addon().getAddonInfo("path"), "Default", "1080i")
                preview.display(dict(show="Preview only", season=1, episode=2, title="Sample next episode", art=""), False, 120)
                preview.show()
                try:
                    monitor = xbmc.Monitor()
                    for _ in range(60):
                        if preview.choice is not None or monitor.waitForAbort(0.25):
                            break
                finally:
                    preview.close()
        elif choice == 0:
            dialog.textviewer("TV Streaming playback diagnostic", current)
    except Exception:
        xbmcgui.Dialog().ok("TV Streaming playback diagnostic", "Could not read playback metadata.")
