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
        if url.scheme != "plugin" or url.netloc != "plugin.video.themoviedb.helper":
            return None
        if q.get("tmdb_id") != [series_id] or q.get("tmdb_type") != ["tv"]:
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
