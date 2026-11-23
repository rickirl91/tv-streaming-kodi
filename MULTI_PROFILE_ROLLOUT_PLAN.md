# TV Streaming — Multi-profile rollout and child controls (agreed design)

Status: **design approved; not implemented**. This document stores the reusable technical requirements, intentionally using generic person identifiers because the repository may be public. Profile names and children's private viewing histories must stay local to Kodi, Trakt, and any private project notes; do not publish credentials, children's names, histories, or ratings overrides here.

## Implementation sequence
1. Complete and accept **Cricky** Family master Home. Final test of Home Personalisation 0.1.1 RC (neutral See All tile; optional duplicate-row cleanup); check Family Trakt selection, progression, See All pagination, profile recovery/backup.
2. Produce a stable, portable, profile-aware baseline from the accepted master.
3. Clone for two **adult personal profiles**, then **Guest**, then two **children's profiles**, checking per-profile isolation.
4. Maintain common add-on code and version-controlled configuration, with private per-profile credentials, content decisions and history stored separately; updates must not overwrite profile-specific state.

## Profile layout contract
| Profile role | Trakt | Home and navigation |
| --- | --- | --- |
| Family master (Cricky) | Existing shared Family Trakt | Full catalog, Continue Watching and mixed personalised feeds; source of template |
| Adult A | New personal Trakt | Copy baseline; own progress, watchlist, recommendations and service sync |
| Adult B | Separate personal Trakt | Copy baseline; own progress, watchlist, recommendations and service sync |
| Guest | None | Discovery-first Home: trending and popular film/TV, new releases, provider/genre exploration; no personal recommendations or watch-progress assumption |
| Child A | Dedicated separate Trakt if available and appropriate | **One visible Home tab only**; restricted movie/TV categories, Continue Watching, approved favourites, personalised recommendations only after child policy filtering |
| Child B | Initially small parent-curated catalogue | **One visible Home tab only**, expandable from parent-curated infant content into age-appropriate categories over time |

For the two adults, match Cricky's working UI, artwork, Lazy Wall/See All, source selection, navigation and playback; only profile-specific Trakt data, customisations and allowed feeds differ. Never cross-wire the account used by TMDb Helper Sync with another user's watch activity; verify each integration and scrobble target rather than assuming one Trakt login controls every add-on.

## Child Home principles
- Single Home navigation tab, with all permitted browsing organized into horizontal sections and optional See All filtered poster walls.
- Suggested Child A section order: Continue Watching; Favourites; Recommended For You; Because You Watched; parent-approved Watchlist; Cartoons; Movies; age-appropriate provider collections; Learning & Educational; Discover Something New. Adjust for age and actual interests.
- Child B begins with a small parent-curated selection; no unrestricted discovery or autoplay. Add categories only as parents approve.
- Preference signal for Child A: examine available Netflix, Disney+ and YouTube viewing histories where permitted, identify liked shows, themes and characters, optionally rebuild matching film/TV history in a dedicated child Trakt account. YouTube videos do not directly imply Trakt items. No raw children's browsing history or credentials in the public repo.
- Trakt is a preference signal only, never the safety authority.

## Parent controls and allow/deny policy
- Each child has independent age stage, **whitelist**, **blacklist**, favourites and recommendations; the policy is parent-controlled.
- Decision precedence: **explicit blacklist always denies; else explicit whitelist may allow out-of-age content after parent review; else age-appropriate permitted content; else denied.** Missing/ambiguous content rating is denied until approved.
- Support rules for an individual film, whole TV series, and optionally specific seasons/episodes; define precedence clearly (e.g., blocked episode within an allowed series remains blocked).
- Use stable provider title IDs and media types rather than name matching alone. Include reason, parent approval and change history locally. Never auto-remove blacklists because a child gets older.
- Apply policy to Home feeds, suggestions, Continue Watching, favourites, watchlist, search, See All, detail views, direct URLs and every permitted playback entrypoint, not only cosmetic widget filtering.
- Hidden tabs by themselves are not effective access control. Restrict Kodi settings, Add-ons, unrestricted search, shortcuts, input/URL routes and profile switching with a parent-access mechanism; test bypass attempts before asserting protections.
- Introduce parent **PIN-protected Search** in child profiles: child cannot invoke it; parents enter PIN to search any title, then can preview/play under supervision, whitelist or blacklist. Relock when closing, timing out or switching profiles. Parent PIN must not be embedded in public files or logs.
- The parental safety model should be designed as defense-in-depth and evaluated against Kodi's actual add-on boundaries; do not represent unsupported Kodi profile locks as airtight.
- Age eligibility and Home sections should be configurable and grow with each child without destroying favourites/history. No automatic unlock of disallowed content on birthdays.

## Rollout acceptance and rollback
- Preserve current profile data, bookmark/progress, skin configuration and source settings using verified byte-exact backups with conflict-safe restore.
- Test one profile at a time; test actual Kodi profile switching, TMDb Helper's selected account, Kodi/Trakt scrobbling, watched indicators and source isolation.
- Confirm children cannot reach blocked titles via alternatives (genre/provider rows, search via contextual actions, native add-ons, recommendations, direct playback).
- A family-safe master template does not mean credentials or watch histories are duplicated.
- **No implementation/deployment of these additional profiles has occurred yet.**

## Immediate Xbox checkpoint
Upgrade **Home Personalisation v0.1.3 RC** while in Cricky; verify the neutral See All artwork and use **8 Preview Poster style** / **9 Apply Poster style** to match the narrow card dimensions of the other catalogue rows; preview duplicate cleanup and confirm only the four redundant old watchlist/recommendation rows; run cleanup with separate confirmation; restart; verify remaining row order and See All behaviour; confirm Family Trakt in TMDb Helper; final Cricky backup. Do **not** rerun legacy Bulk Setup.
