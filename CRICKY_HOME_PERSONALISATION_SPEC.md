# Cricky — Home tab personalisation and ordering (approved design)

Status: **RC installer packaged; live Xbox acceptance pending**. This file is not a deployed Xbox change. Do not claim the Home widgets are modified until the Kodi update has been installed and verified.

## Required order

1. **Continue Watching** — existing working widget, preserved in place as the first Home row; do not replace its underlying Trakt/Kodi endpoint.
2. **Recommended For You** — personalised recommendations from the **existing shared Family Trakt account**, including films and TV series.
3. **Because You Watched** — suggestions influenced by titles recently watched on that shared Family account, including films and TV series.
4. **From Your Watchlist** — titles saved to the shared Family watchlist, including films and TV series.
5. **All remaining existing Home rows**, unchanged in their current relative order (Trending, Recently Released, genres, streaming services, etc.).

Use **You / Your** on the interface — never **Us / Our**. Apply to the **Cricky Home hub only**, not the Movies, TV Shows, Documentaries or other profile hubs.

## Available native TMDb Helper source endpoints

Confirmed against upstream TMDb Helper's list-endpoint and Trakt docs (10 Nov 2026):

| Row | Movie feed | TV feed |
| --- | --- | --- |
| Recommended For You | `plugin://plugin.video.themoviedb.helper/?info=trakt_recommendations&tmdb_type=movie` | `plugin://plugin.video.themoviedb.helper/?info=trakt_recommendations&tmdb_type=tv` |
| Because You Watched | `plugin://plugin.video.themoviedb.helper/?info=sync_becauseyouwatched&tmdb_type=movie` | `plugin://plugin.video.themoviedb.helper/?info=sync_becauseyouwatched&tmdb_type=tv` |
| From Your Watchlist | `plugin://plugin.video.themoviedb.helper/?info=sync_watchlist&tmdb_type=movie` | `plugin://plugin.video.themoviedb.helper/?info=sync_watchlist&tmdb_type=tv` |

The `sync_*` routes use TMDb Helper's selected History/Watchlist sync source. On Cricky, confirm those sync providers are set to the existing **Family Trakt** account and not to another profile's account. An authorised Trakt login in another addon is not sufficient proof of which TMDb Helper sync provider is selected.

**Do not use `tmdb_type=both` for these three routes without first confirming support.** These documented endpoints use separate movie and TV routes. To meet the approved three-row layout, use a combined widget/adaptor or an independently tested mixed-source implementation which retains the correct per-item movie or TV navigation and watched indicators. Do not silently show only one media type.

## Safe rollout

- Take a verified, byte-for-byte backup of Cricky's Arctic Fuse 3 `skinvariables-shortcut-homewidgets.json` and any related file before applying edits.
- Discover the actual Home widget file and existing Continue Watching widget on the Xbox. Never guess another profile's path, overwrite the existing progress row, or reconstruct all existing Home rows from a template.
- Reorder **only** the Home row sequence; insert the three personalised sections immediately after Continue Watching, deduplicating any earlier copies by exact label. Preserve all other Home widgets' ordering, properties, paths, widget styling, fallback paths and IDs.
- A mixed-type widget must preserve original movie/TV item callback paths and poster information. Prefer our current See All/Lazy Wall presentation where validated; if multi-source pagination is unsupported, do not claim full-wall support.
- Provide a one-confirmation, preview-before-apply Kodi updater which can roll back without deleting newer user edits. Do not rerun the legacy bulk catalogue conversion.
- Use live Trakt/TMDb Helper lists, not snapshot exports and not hardcoded movie IDs. No Trakt writing or token transmission to the repository.
- Verify all three row contents, their titles, homepage focus/hero preview, view-all behaviour if included, refresh and account isolation. Once accepted, back up the final Cricky layout.

## Upstream references

- https://github.com/jurialmunkey/plugin.video.themoviedb.helper/wiki/Lists-Trakt
- https://github.com/jurialmunkey/plugin.video.themoviedb.helper/wiki/List-Endpoints
\n## Implementation candidate (22 Nov 2026)\n\nThe standalone `plugin.video.tvstreaming.homepersonalisation-0.1.0-RC.zip` provides six live TMDb Helper source reads, a movie/TV interleaved adapter, a See All-first launcher using Kodi's native directory view, one-confirmation Home apply, verified byte-exact backup and conflict-safe restore. This differs from the existing custom Lazy Wall; Xbox mixed-feed styling, item navigation, account identity, and generator refresh remain **unverified**. The other hubs and the Continue Watching widget object are never rebuilt.\n
## v0.1.1 RC — See All polish and approved cleanup (22 November 2026)

Live Xbox video confirmed the v0.1.0 mixed recommendation sections and Home row order. The first See All tile borrowed the first show's poster; v0.1.1 now uses the installed StreamRow neutral Miami See All image (fallback neutral folder icon), preserving the first show's backdrop. This requires Xbox retest before acceptance.

Older Home sections specifically **Your TV Show Watchlist**, **Your Movie Watchlist**, **Recommended Movies for You**, **Recommended Shows for You** overlap the three combined sections. A **separate preview/confirm** action will remove only the exact older section labels (including singular/plural TV alias) once the approved first four current rows and their new widget paths are verified. Preserve Up Next Episodes, all other Home rows/properties/order, separate profile hubs, and Trakt history. Backup/restore checks are identical to first release. Installing the update alone makes no edits.
