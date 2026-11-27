"""Candidate action: revalidate active profile and native feed before writing."""
from continue_watching_feed import dismissal_key, fetch_visible

def remove(key, *, profile, current_profile, rpc, store, refresh):
    if not profile or current_profile() != profile:
        return False
    matches = [row for row in fetch_visible(rpc, store) if dismissal_key(row) == key]
    if not matches or current_profile() != profile:
        return False
    label = matches[0].get('showtitle') or matches[0].get('title') or matches[0].get('label') or ''
    store.hide(key, label)
    refresh()
    return True
