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

## v0.1.2 RC artwork regression correction (23 Nov 2026)

The Xbox photo showed the first film backdrop **Get Fast** on the **See All - Because You Watched** horizontal tile after v0.1.1. Arctic Fuse 3's `Image_Landscape` variable prioritises `Art(landscape)`, then falls back to `Art(fanart)` before poster. v0.1.1 set only poster/thumb/icon, allowing title fanart to appear on the tile. v0.1.2 explicitly sets neutral StreamRow artwork as `landscape` plus `override_landscape`, while keeping first-title `fanart` for the large hero. The existing personalised Home paths, mix, playback, backup/restore and duplicate cleanup are unchanged. Four offline tests passed; Xbox validation remains pending. The relevant skin source is `shortcuts/skinvariables-images.xml` in `jurialmunkey/skin.arctic.fuse.3`.

## v0.1.3 RC: exact standard Poster row style (23 November 2026)

Xbox video revealed that the three personalised rows use wider Landscape cards, including the See All first tile, unlike the narrow Poster cards in standard movie and TV catalogue rows. Root cause: new rows were written without `widget_style`; upstream Arctic Fuse 3 `shortcuts/generator/data/setup/widgets_include_row.xml` defaults a missing style to `List_Landscape_Row`. A `widget_style` of `Poster` selects `List_Poster_Row`. v0.1.3 applies this property to new rows and adds a **separate preview/confirm correction** for the three existing mixed rows only, using exact path and first-four label checks. All other widget fields, sources, positions, settings, profiles, and previous See All artwork are preserved. Uses existing verified byte-for-byte backup and change-conflict refusal; requires a full Kodi restart. Eight offline tests pass; Xbox confirmation pending.

## Approved hero text behaviour (24 Nov 2026; pending implementation)

When focus is on the **See All** tile at the start of a personalised Home row, the large hero **heading must be the clean category label** — precisely **Recommended For You**, **Because You Watched**, or **From Your Watchlist**. It must **not** begin with `See All` and must **not** show the first film or TV programme's title. Use a short category-level description if a description is shown, not the generic See All navigation instruction or the first title's synopsis. The first recommendation's backdrop may remain as decorative hero artwork, as long as it does not cause its title to replace the category heading.

When focus moves to an **actual film or TV title**, retain the normal title-specific hero information and working movie/TV navigation; this decision concerns **category-level See All focus** only. Keep the approved narrow `Poster` layout, neutral See All artwork, mixed Trakt feeds, progress widgets, backup/restore and profile isolation intact.

**No code or Xbox settings have been changed for this hero-text decision yet.** Next step is to finish the existing v0.1.3 redundant-row cleanup (menu actions **5 Preview** and **6 Remove**), then deliver a separately tested hero-label update.

## Superseding scope — category-name hero heading on ALL See All tiles (24 Nov 2026)

**Approved requirement:** the category-only heading rule above applies to **every See All tile across the completed Cricky profile**, not only the three personalised Home rows. Include standard StreamRow catalogue widgets in Home, Movies, TV Shows, Documentaries, streaming-provider collections, genre sections, trending, new releases, and any other hub/row with a See All tile. Future adult and child profiles cloned from the approved master should inherit this consistent behaviour for their own allowed categories.

**When a See All tile is focused:**
- The large hero heading is the **exact clean category/row name** (e.g., `Trending Movies`, `Netflix Movies`, `Action Movies`, `Recommended For You`), never a `See All` prefix/suffix and never the first programme's title.
- If a subtitle/description is displayed, it must be **category-level text**, not the first programme's plot and not generic internal pagination instructions. For categories without a suitable description, omit it rather than invent a title synopsis.
- Preserve the agreed **neutral See All tile artwork**, current Poster widget styling, optional large cinematic fanart backdrop, existing See All destination and pagination.
- As focus moves to an actual movie or series tile, restore that item's normal title, plot, badges and navigation. Do not globally replace content metadata or alter Trakt/playback paths.

**Implementation / tests:** inspect both `plugin.video.streamrow` (existing catalogue See All widgets) and `plugin.video.tvstreaming.homepersonalisation` (three new mixed feeds), plus Arctic Fuse 3's hero metadata precedence. Fix **both** widget producers or an equivalent shared presentation layer; updating only Home Personalisation would leave old catalogue rows inconsistent. Use a separate versioned, reversible rollout and test a personalised Home row, a Trending row, a genre row, a streaming-provider row, and a TV series row, across Home and relevant hubs. Avoid touching native rows that do not have a See All tile.

**Checkpoint:** user's next action is still the existing v0.1.3 **5 Preview redundant-row cleanup** then **6 Remove redundant Home rows**, followed by Kodi restart. **No hero-text changes have been deployed to Xbox yet.**

## Universal hero-heading code release candidate (November 2026)

Prepared **StreamRow v0.3.1 RC** and **Home Personalisation v0.1.4 RC**. Both are opt-in plugin ZIP upgrades, not Xbox deployments. StreamRow sets the `ListItem` video `title` on its See All launcher to the clean row/category title rather than the first film/show `featured_metadata`; it leaves the callback and featured fanart alone. Home Personalisation sets an optional `hero_title` for its three mixed-feed See All entries, leaving actual film/show metadata unchanged. Both omit the first programme's plot for the See All launcher. Supports Home and other existing **StreamRow-wrapped** category hubs, including Movies, TV Shows, provider and documentary lists. Native/third-party See All tiles **not generated by these add-ons** have not been altered and must be separately assessed if encountered.

One automated regression suite validates source parity, Python compilation, ZIP integrity, a provider/genre label, featured backdrop, preserved launcher and personalised mixed feed. **Xbox visual checks are still required** for heading focus in representative Home, Movies, TV, streaming-provider, genre and documentary rows. No Kodi profile files or Trakt accounts have been edited by publication.
