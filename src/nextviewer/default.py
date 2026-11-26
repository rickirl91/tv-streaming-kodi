"""Independent read-only diagnostic menu."""
import json
import xbmc
import xbmcaddon
import xbmcgui

dialog = xbmcgui.Dialog()
choice = dialog.select("TV Streaming diagnostic", ["Playback report", "Overlay preview", "Independent Supernatural catalogue test", "Native directory test"])
if choice == 0:
    dialog.textviewer("Playback report", xbmcgui.Window(10000).getProperty("tvstreaming.nextdiagnostic") or "No snapshot captured.")
elif choice == 1:
    try:
        if xbmc.Player().isPlaying():
            dialog.ok("Overlay preview", "Stop playback first.")
        else:
            path = xbmcaddon.Addon("service.tvstreaming.nextepisode").getAddonInfo("path")
            from overlay import Overlay
            preview = Overlay("NextEpisode.xml", path, "Default", "1080i")
            preview.display(dict(show="Preview only", season=1, episode=2, title="Sample next episode", art=""), False, 120)
            preview.show()
            try:
                monitor = xbmc.Monitor()
                for _ in range(60):
                    if preview.choice is not None or monitor.waitForAbort(0.25):
                        break
            finally:
                preview.close()
    except Exception as exc:
        dialog.ok("Overlay preview error", type(exc).__name__)
elif choice == 2:
    report = {"helper_version": "unknown", "requests": []}
    stage = "import"
    try:
        report["helper_version"] = xbmcaddon.Addon("plugin.video.themoviedb.helper").getAddonInfo("version")
        from tmdbhelper_lib.api.tmdb.api import TMDb
        stage = "initialise"
        api = TMDb()
        for args, kwargs in [(("find", "tt0460681"), {"external_source": "imdb_id"}), (("tv", "1622"), {"append_to_response": "external_ids"}), (("tv", "1622", "season", "1"), {})]:
            stage = "/".join(args)
            entry = {"endpoint": stage}
            report["requests"].append(entry)
            try:
                payload = api.get_response_json(*args, **kwargs)
                entry["type"] = type(payload).__name__
                if isinstance(payload, dict):
                    entry["keys"] = sorted(k for k in payload if k in ("id", "status_code", "success", "tv_results", "tv_episode_results", "episodes", "seasons", "name"))
                    for key in ("id", "status_code", "success"):
                        if isinstance(payload.get(key), (int, bool)):
                            entry[key] = payload[key]
                    if isinstance(payload.get("tv_results"), list):
                        entry["parent_ids"] = [r.get("id") for r in payload["tv_results"] if isinstance(r.get("id"), int)]
                    if isinstance(payload.get("episodes"), list):
                        entry["episodes_3_4"] = [{"number": r.get("episode_number"), "name": r.get("name")} for r in payload["episodes"] if r.get("episode_number") in (3, 4)]
            except Exception as exc:
                entry["error"] = type(exc).__name__
    except Exception as exc:
        report["failure_stage"] = stage
        report["error"] = type(exc).__name__
    dialog.textviewer("Independent catalogue test", json.dumps(report, indent=2))

elif choice == 3:
    report = {}
    for label, query in [
        ("seasons", "info=seasons&tmdb_type=tv&tmdb_id=1622"),
        ("episodes", "info=episodes&tmdb_type=tv&tmdb_id=1622&season=1")]:
        try:
            result = json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc="2.0", id=1, method="Files.GetDirectory", params=dict(directory="plugin://plugin.video.themoviedb.helper/?"+query, media="video", properties=["title","showtitle","season","episode","firstaired","uniqueid"])))))
            data = result.get("result", {})
            rows = data.get("files", [])
            report[label] = dict(count=len(rows), limits=data.get("limits"), error=result.get("error", {}).get("code"), sample=[{k:r.get(k) for k in ("title","showtitle","season","episode","firstaired","uniqueid")} for r in rows[:4]])
        except Exception as exc:
            report[label] = dict(error=type(exc).__name__)
    dialog.textviewer("Native directory test", json.dumps(report, indent=2))
