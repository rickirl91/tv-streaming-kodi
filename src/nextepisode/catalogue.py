"""Normalize catalogue records without treating parent IDs as episode IDs."""
from urllib.parse import urlparse, parse_qs

def normalize(series_id, rows):
    series_id = str(series_id)
    if not series_id.isdigit() or not rows:
        return None
    episodes = []
    for row in rows:
        url = urlparse(row.get("file", ""))
        q = parse_qs(url.query)
        if (url.scheme != "plugin" or url.netloc != "plugin.video.themoviedb.helper"
                or url.path not in ("", "/") or url.fragment):
            return None
        if (q.get("tmdb_id") != [series_id] or q.get("tmdb_type") != ["tv"]
                or q.get("info") not in (["details"], ["play"])
                or len(q.get("season", [])) != 1 or len(q.get("episode", [])) != 1):
            return None
        try:
            season = int(q["season"][0])
            episode = int(q["episode"][0])
            if season != row["season"] or episode != row["episode"]:
                return None
        except (KeyError, ValueError, TypeError, IndexError):
            return None
        episodes.append(dict(season=season, episode=episode,
                             episode_id=f"{series_id}:{season}:{episode}",
                             air_date=row.get("firstaired"), title=row.get("title","")))
    return dict(series_id=series_id, episodes=episodes, complete=False)


def playback_url(series, target, player):
    from urllib.parse import urlencode

    params = {
        "info": "play", "tmdb_type": "tv", "tmdb_id": series,
        "season": target["season"], "episode": target["episode"],
        "player": player, "mode": "play", "allow_playlist": "false", "ignore_default": "true",
    }
    for field in ("virtual_season", "virtual_episode"):
        if field in target:
            params[field] = target[field]
    return "plugin://plugin.video.themoviedb.helper/?" + urlencode(params)


def verified_successor(fetch, current):
    """Use Helper's unpaginated TMDb detail endpoints and declared counts.

    Only the current season and the first following non-special season are
    needed to prove adjacency. Any missing or filtered records fail closed.
    """
    from resolver import resolve_next

    series, season, episode = (current[key] for key in ("series_id", "season", "episode"))
    group = current.get("group")
    append = "external_ids,episode_groups" if group else "external_ids"
    show = fetch("tv", series, append_to_response=append)
    if str(show.get("id")) != series or not same_title(current["show"], show, "name"):
        return None
    seasons = show.get("seasons")
    regular = sorted((row for row in seasons if row["season_number"] > 0),
                     key=lambda row: row["season_number"])
    numbers = [row["season_number"] for row in regular]
    if (numbers != list(range(1, show["number_of_seasons"] + 1))
            or sum(row["episode_count"] for row in regular) != show["number_of_episodes"]
            or season not in numbers):
        return None

    def load(summary):
        number = summary["season_number"]
        payload = fetch("tv", series, "season", number)
        rows = sorted(payload["episodes"], key=lambda row: row["episode_number"])
        count = summary["episode_count"]
        if (payload.get("page") or payload.get("total_pages", 1) != 1
                or payload.get("season_number") != number or payload.get("id") != summary["id"]
                or not count or len(rows) != count
                or [r["episode_number"] for r in rows] != list(range(1, count + 1))
                or len({r["id"] for r in rows if r.get("id")}) != count
                or any(r.get("season_number") != number for r in rows)):
            return None
        return rows

    index = numbers.index(season)
    raw = load(regular[index])
    if not raw or episode < 1 or episode > len(raw):
        return None
    item = raw[episode - 1]
    if not same_title(current["title"], item, "name"):
        return None
    # An unscoped TMDb tag is only a candidate parent ID. Check the IMDb
    # identifier against the show or this exact episode before trusting it.
    if not current.get("parent_verified"):
        imdb = current.get("imdb")
        if not imdb or not imdb.startswith("tt") or not imdb[2:].isdigit():
            return None
        if imdb != (show.get("external_ids") or {}).get("imdb_id"):
            detail = fetch("tv", series, "season", season, "episode", episode,
                           append_to_response="external_ids")
            if (item["id"] != detail.get("id")
                    or imdb != (detail.get("external_ids") or {}).get("imdb_id")):
                return None

    if group:
        declared = [row for row in (show.get("episode_groups") or {}).get("results", [])
                    if row.get("id") == group]
        if len(declared) != 1:
            return None
        raw = group_rows(fetch("tv", "episode_group", group), declared[0])
        if not raw or sum(row.get("id") == item["id"] and
                          (row.get("season_number"), row.get("episode_number")) == (season, episode)
                          for row in raw) != 1:
            return None
    elif episode == len(raw) and index + 1 < len(regular):
        following = load(regular[index + 1])
        if not following:
            return None
        raw += following

    rows = []
    for row in raw:
        s, e = row["season_number"], row["episode_number"]
        still = row.get("still_path") or ""
        rows.append(dict(season=s, episode=e, episode_id=f"{series}:{s}:{e}",
                         air_date=row.get("air_date"), title=row.get("name") or "",
                         art="https://image.tmdb.org/t/p/w500" + still
                         if still.startswith("/") else ""))
        if group:
            rows[-1].update(virtual_season=row["virtual_season"],
                            virtual_episode=row["virtual_episode"])
    result = resolve_next(dict(current, episode_id=f"{series}:{season}:{episode}"),
                          dict(series_id=series, episodes=rows, complete=True),
                          grouped=bool(group))
    return result if result and result["title"] else None


def group_rows(payload, summary):
    if (payload.get("id") != summary["id"] or payload.get("page")
            or payload.get("total_pages", 1) != 1):
        return None
    groups = sorted(payload["groups"], key=lambda row: row["order"])
    if (len(groups) != summary["group_count"] or len(groups) != payload["group_count"]
            or len({g["id"] for g in groups}) != len(groups)
            or [g["order"] for g in groups] != list(range(len(groups)))):
        return None
    rows = []
    for group in groups:
        episodes = sorted(group["episodes"], key=lambda row: row["order"])
        if [row["order"] for row in episodes] != list(range(len(episodes))):
            return None
        rows.extend(dict(row, virtual_season=group["order"], virtual_episode=row["order"] + 1)
                    for row in episodes)
    if (len(rows) != summary["episode_count"] or len(rows) != payload["episode_count"]
            or len({row["id"] for row in rows if row.get("id")}) != len(rows)):
        return None
    return rows


def same_title(playing, row, key):
    def canonical(title):
        return " ".join((title or "").casefold().split())

    return bool(canonical(playing)) and canonical(playing) in {
        canonical(row.get(key)), canonical(row.get("original_" + key))}
