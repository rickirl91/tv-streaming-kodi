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
