# TV Streaming — Kodi add-ons for the Cricky profile

**[Installers and status](https://rickirl91.github.io/tv-streaming-kodi/)** · **[Archive](https://rickirl91.github.io/tv-streaming-kodi/archive/)**

This project builds the shared **Cricky** streaming experience on Xbox Kodi with Arctic Fuse 3, TMDb Helper, StreamRow's See All-first home widgets, and Lazy Wall's continuous poster browsing.

## Current installers (direct ZIP)

| Component | Current ZIP | Purpose |
| --- | --- | --- |
| Home Personalisation (RC) | `plugin.video.tvstreaming.homepersonalisation-0.1.1-RC.zip` | Three mixed film/TV rows; standard See All artwork and optional duplicate-row cleanup, with preview/backup |
| Lazy Wall | `script.tvstreaming.lazywall-0.3.1-RC.zip` | Poster wall, paging, details, playback and trailers |
| StreamRow | `plugin.video.streamrow-0.3.0-RC.zip` | Skin-friendly See All launcher and category widgets |
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
