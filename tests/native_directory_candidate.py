from catalogue import normalize, same_title


def directory_successor(rpc, current, report=lambda reason: None):
    """Conservative native directory fallback: same-season adjacency only."""
    from urllib.parse import urlencode
    from datetime import date
    series = str(current.get("series_id") or "")
    if not series.isdecimal() or not current.get("parent_verified") or current.get("group"):
        return report("directory_parent_unverified_or_grouped")
    season, episode = current["season"], current["episode"]
    url = "plugin://plugin.video.themoviedb.helper/?" + urlencode(
        dict(info="episodes", tmdb_type="tv", tmdb_id=series, season=season))
    response = rpc("Files.GetDirectory", {"directory": url, "media": "video",
        "properties": ["title", "showtitle", "season", "episode", "firstaired", "uniqueid"]})
    rows = response.get("files", []) if isinstance(response, dict) else []
    if not rows or response.get("limits", {}).get("total", len(rows)) != len(rows):
        return report("directory_empty_or_partial")
    normalized = normalize(series, rows)
    if not normalized:
        return report("directory_invalid_rows")
    if any(r.get("showtitle", "").casefold().strip() != current["show"].casefold().strip() for r in rows):
        return report("directory_show_mismatch")
    ordered = sorted(normalized["episodes"], key=lambda r: r["episode"])
    if any(r["season"] != season for r in ordered) or [r["episode"] for r in ordered] != list(range(1, len(ordered)+1)):
        return report("directory_noncontiguous")
    if episode < 1 or episode >= len(ordered):
        return report("directory_boundary_unverified")
    if not same_title(current["title"], ordered[episode-1], "title"):
        return report("directory_current_title_mismatch")
    target = ordered[episode]
    try:
        if not target["title"] or date.fromisoformat(target["air_date"]) > date.today():
            return report("directory_successor_unaired")
    except (ValueError, TypeError):
        return report("directory_airdate_missing")
    return target
