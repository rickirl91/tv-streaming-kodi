"""Pure episode selection; catalogue adapter and playback routing are separate."""
from datetime import date

def resolve_next(current, catalogue, today=None, *, grouped=False):
    """Require verified parent identity, complete ordered catalogue and current match."""
    today = today or date.today()
    if not current.get("series_id") or not current.get("episode_id"):
        return None
    if not catalogue.get("complete") or catalogue.get("series_id") != current["series_id"]:
        return None
    rows = catalogue.get("episodes", [])
    if any(not isinstance(r.get("season"), int) or not isinstance(r.get("episode"), int) for r in rows):
        return None
    rows = [r for r in rows if r["season"] > 0 and r["episode"] > 0]
    if not grouped:
        rows.sort(key=lambda r: (r["season"], r["episode"]))
    keys = [(r["season"], r["episode"]) for r in rows]
    if len(keys) != len(set(keys)):
        return None
    matches = [i for i,r in enumerate(rows) if r.get("episode_id") == current["episode_id"]
               and (r["season"],r["episode"]) == (current.get("season"),current.get("episode"))]
    if len(matches) != 1 or matches[0] + 1 >= len(rows):
        return None
    nxt = rows[matches[0]+1]
    try:
        if date.fromisoformat(nxt["air_date"]) > today:
            return None
    except (KeyError, TypeError, ValueError):
        return None
    if not nxt.get("episode_id") or nxt["episode_id"] == current["episode_id"]:
        return None
    return dict(nxt)
