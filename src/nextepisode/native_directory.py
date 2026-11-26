from catalogue import normalize, same_title


def directory_successor(rpc, current, report=lambda reason: None):
    """Validate declared season counts and immediate default-order successor."""
    from urllib.parse import urlencode
    from datetime import date
    series = str(current.get("series_id") or "")
    if not series.isdecimal() or current.get("group"):
        return report("directory_parent_unverified_or_grouped")
    season, episode = current["season"], current["episode"]
    def directory(info, **extra):
        url = "plugin://plugin.video.themoviedb.helper/?" + urlencode(dict(info=info, tmdb_type="tv", tmdb_id=series, **extra))
        response = rpc("Files.GetDirectory", {"directory": url, "media": "video",
            "properties": ["title", "showtitle", "season", "episode", "firstaired", "premiered", "uniqueid"]})
        rows = response.get("files", []) if isinstance(response, dict) else []
        if not rows or response.get("limits") != {"start": 0, "end": len(rows), "total": len(rows)}:
            return None
        return rows
    summaries = directory("seasons")
    if not summaries:
        return report("directory_seasons_missing")
    def season_count(number):
        matches = [row for row in summaries if type(row.get("season")) is int
                   and row["season"] == number]
        if len(matches) != 1:
            report("directory_season_summary_missing_or_duplicate:" + str(number))
            return None
        row = matches[0]
        count = row.get("episode")
        if type(count) is not int or count < 1:
            report("directory_season_count_invalid:" + str(number))
            return None
        if str((row.get("uniqueid") or {}).get("tvshow.tmdb")) != series:
            report("directory_season_parent_mismatch:" + str(number))
            return None
        return count
    count = season_count(season)
    if count is None:
        return None
    url = "plugin://plugin.video.themoviedb.helper/?" + urlencode(
        dict(info="episodes", tmdb_type="tv", tmdb_id=series, season=season))
    response = rpc("Files.GetDirectory", {"directory": url, "media": "video",
        "properties": ["title", "showtitle", "season", "episode", "firstaired", "premiered", "uniqueid"]})
    rows = response.get("files", []) if isinstance(response, dict) else []
    if not rows or response.get("limits") != {"start": 0, "end": len(rows), "total": len(rows)}:
        return report("directory_empty_or_partial")
    for row in rows:
        ids = row.get("uniqueid") or {}
        if ids.get("tvshow.tmdb") != series:
            return report("directory_parent_mismatch")
    current_rows = [r for r in rows if r.get("season") == season and r.get("episode") == episode]
    if len(current_rows) != 1:
        return report("directory_current_missing")
    ids = current_rows[0].get("uniqueid") or {}
    if not current.get("parent_verified") and (not current.get("imdb") or current["imdb"] not in (ids.get("imdb"), ids.get("tvshow.imdb"))):
        return report("directory_imdb_mismatch")
    rows = [dict(r, firstaired=r.get("firstaired") or r.get("premiered")) for r in rows]
    normalized = normalize(series, rows)
    if not normalized:
        return report("directory_invalid_rows")
    if any(r.get("showtitle", "").casefold().strip() != current["show"].casefold().strip() for r in rows):
        return report("directory_show_mismatch")
    ordered = sorted(normalized["episodes"], key=lambda r: r["episode"])
    if any(r["season"] != season for r in ordered) or [r["episode"] for r in ordered] != list(range(1, len(ordered)+1)):
        return report("directory_noncontiguous")
    if len(ordered) != count:
        return report("directory_count_mismatch")
    if episode < 1 or episode > len(ordered):
        return report("directory_boundary_unverified")
    if not same_title(current["title"], ordered[episode-1], "title"):
        return report("directory_current_title_mismatch")
    if episode == len(ordered):
        following_count = season_count(season + 1)
        if following_count is None:
            return None
        following = directory("episodes", season=season+1)
        if not following or len(following) != following_count:
            return report("directory_following_incomplete")
        if any(str((r.get("uniqueid") or {}).get("tvshow.tmdb")) != series or r.get("showtitle","").casefold().strip() != current["show"].casefold().strip() for r in following):
            return report("directory_following_identity")
        parsed = normalize(series, [dict(r, firstaired=r.get("firstaired") or r.get("premiered")) for r in following])
        if not parsed:
            return report("directory_following_invalid")
        ordered = sorted(parsed["episodes"], key=lambda r:r["episode"])
        if any(r["season"] != season+1 for r in ordered) or [r["episode"] for r in ordered] != list(range(1,len(ordered)+1)):
            return report("directory_following_noncontiguous")
        target = ordered[0]
    else:
        target = ordered[episode]
    try:
        if not target["title"] or date.fromisoformat(target["air_date"]) > date.today():
            return report("directory_successor_unaired")
    except (ValueError, TypeError):
        return report("directory_airdate_missing")
    return target
