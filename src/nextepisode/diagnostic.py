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
        current = snapshot()
        if current == "No active video":
            current = xbmcgui.Window(10000).getProperty("tvstreaming.nextdiagnostic") or current
        xbmcgui.Dialog().textviewer("TV Streaming playback diagnostic", current)
    except Exception:
        xbmcgui.Dialog().ok("TV Streaming playback diagnostic", "Could not read playback metadata.")
