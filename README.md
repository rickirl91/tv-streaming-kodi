# TV Streaming — Kodi add-ons for the Cricky profile

**[Installers and status](https://rickirl91.github.io/tv-streaming-kodi/)** · **[Archive](https://rickirl91.github.io/tv-streaming-kodi/archive/)**

This project builds the shared **Cricky** streaming experience on Xbox Kodi with Arctic Fuse 3, TMDb Helper, StreamRow's See All-first home widgets, and Lazy Wall's continuous poster browsing.

## Current installers (direct ZIP)

| Component | Current ZIP | Purpose |
| --- | --- | --- |
| Home Personalisation (RC) | `plugin.video.tvstreaming.homepersonalisation-0.1.4-RC.zip` | Three mixed film/TV rows; clean category hero headings; preserved poster style, artwork and backups |
| Lazy Wall | `script.tvstreaming.lazywall-0.3.1-RC.zip` | Poster wall, paging, details, playback and trailers |
| StreamRow | `plugin.video.streamrow-0.3.1-RC.zip` | See All-first catalogue widgets; category-only hero headings across supported hubs |
| Bulk Setup | `script.tvstreaming.bulksetup-0.1.0-RC.zip` | One-time safe migration of supported homepage catalogue rows |
| Catalogue & Preset | `plugin.video.tvstreaming.catalogue-0.2.3.zip` | Original navigation preset and optional playback link |

Install through Kodi **Settings → Add-ons → Install from zip file → rickirl91**. Once Bulk Setup has been applied successfully, **do not rerun it** just because Lazy Wall is updated.

## Verified and outstanding

- Xbox: Action Movies and Netflix Movies now scroll beyond 20 titles on Lazy Wall 0.3.1 RC.
- Xbox: Disney Series, Apple Series and Trending TV pagination were tested beyond 20 titles.
- Earlier tests confirmed working poster-wall navigation, film details, Play, trailer viewing/return, the See All hero preview and Miami-style neutral poster.
- Before declaring Cricky complete: confirm shared Trakt behaviour, representative TV episode playback, remaining provider/genre filters, and final backup. Personalised feeds, poster artwork, and movie/TV routing passed initial Xbox tests. See All tile artwork correction and exact-label duplicate-row cleanup are packaged in v0.1.1 RC and await Xbox verification.
- No claims of production acceptance beyond tested paths.

## Repository layout

- Root: current direct-install ZIPs, selected rollback ZIPs, `index.html`, active release notes and repository metadata.
- `zips/`: legacy Kodi repository package URLs — **not moved**.
- `tools/` and `.github/workflows/`: reproducible v0.3.1 build tooling — retained.
- `archive/releases/`: older superseded direct-install versions.
- `archive/notes/`: historical readmes and release tests.
- `addons.xml` and `addons.xml.md5`: existing Kodi repository metadata — unchanged in this housekeeping pass.

The reorganisation changes **GitHub file locations only**. It does not change installed Xbox files or existing profiles and settings.

## Home personalisation v0.1.1 RC

- Upgrades existing plugin; installing **does not** change Home widgets.
- Reuses StreamRow's `see_all_miami_neutral_v024.png` artwork for the **See All** tile, retaining first-title backdrop, without changing source feeds or playback.
- New separate **Preview redundant-row cleanup** and **Remove redundant Home rows** actions, exactly four older overlapping label families only; retain Up Next Episodes and all other rows. Requires an explicit confirmation and makes a new byte-exact SHA-256 backup.
- The four older rows only disappear **after** selecting cleanup in Cricky. Do **not** rerun legacy Bulk Setup or reinstall Lazy Wall.
- [Release test guide](TV_STREAMING_RC_041_POLISH.md).

## v0.1.2 RC: Arctic Fuse 3 See All landscape artwork

- Initial Xbox report after v0.1.1: the See All tile in **Because You Watched** still displayed **Get Fast** background rather than the neutral Miami image.
- Root cause confirmed against Arctic Fuse 3's `Image_Landscape` precedence: `fanart` was selected for horizontal tiles because v0.1.1 did not set `landscape` (even though `poster` and `thumb` were neutral).
- v0.1.2 sets `landscape` and `override_landscape` to the installed StreamRow neutral artwork, while preserving source `fanart` for the Home hero preview. It does **not** edit widgets, feed logic, Trakt, playback, or cleanup.
- Upgrade just this add-on in Cricky; fully restart Kodi. Verify all three personalised See All tiles and compare with working catalogue rows. **Xbox verification pending.**
- Source, deterministic builder and regression tests: `src/homepersonalisation/`, `tools/build-homepersonalisation-012.py`, `tests/test_home_personalisation_v012.py`.

## v0.1.3 RC — Match standard Home tile dimensions

- Xbox video showed the **three personalised mixed film/TV Home rows** as wide Landscape tiles; the other film/TV catalogue rows use narrow Poster tiles.
- This is a **skin widget style** issue, not a TMDb Helper or Trakt feed issue. Arctic Fuse 3's `shortcuts/generator/data/setup/widgets_include_row.xml` chooses `List_Poster_Row` when `widget_style=Poster` and defaults to `List_Landscape_Row` for missing styles. The original personalised Home widgets did not set `widget_style`.
- v0.1.3 adds explicit Poster style for future new Home rows, plus separate **8. Preview standard Poster tile style** and **9. Apply standard Poster tile style** for existing Cricky installations. It checks the exact three Home paths and ordering, backs up the original Home widget file, changes only those three style properties and regenerates skin widgets.
- **Installing alone does not edit Home**. After installing, run #8 and #9 in Cricky, then fully restart Kodi. Do not rerun Bulk Setup or the original Home personalisation.
- Mixed movie/TV source feeds, artwork/backdrops, playback, watchlists, other Home rows, duplicate-row cleanup and other Kodi profiles are unchanged. **Xbox v0.1.3 tile dimensions still need confirmation.**
- [Test guide](TV_STREAMING_RC_043_POSTER_STYLE.md).

## Universal category hero headings — 0.3.1 / 0.1.4 RC

Two add-on upgrades make the **large hero heading show the category name whenever a See All tile is focused**, including Home, Movies, TV Shows, provider catalogues and documentary/genre hubs converted through StreamRow. The first film/show fanart is preserved as decorative backdrop but its title/plot is no longer copied to the category launcher. A real film/show selection retains its own details.

- **StreamRow 0.3.1 RC**: fixes catalogue See All tiles across all compatible hubs.
- **Home Personalisation 0.1.4 RC**: fixes the three mixed Trakt See All category headings.
- Both are installed as **ZIP upgrades** using existing Kodi source **rickirl91**; **no Apply Home, Bulk Setup, profile migration or widget regeneration is required by the installers**. Fully quit/restart Kodi, then verify different hubs.
- Exact old installers are retained in `archive/releases/`. Lazy Wall, Trakt, other hubs' raw configuration and all profile data are unchanged.
- [Release guide](TV_STREAMING_RC_044_UNIVERSAL_HERO.md) and [offline regression tests](tests/test_universal_hero_044.py). **Xbox acceptance pending.**
