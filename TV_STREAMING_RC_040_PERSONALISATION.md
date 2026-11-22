# TV Streaming — Cricky Home Personalisation v0.1.0 RC

**Built:** 22 November 2026. **Status:** Offline tests pass; Xbox acceptance pending. **No automatic changes on installation.**

## Package

- `plugin.video.tvstreaming.homepersonalisation-0.1.0-RC.zip` (SHA-256 `8e3994fe49e66591f69115fde572ecce00de18c406720e4832ca639bfd94e1bf`)
- Full reviewable source in `src/homepersonalisation/`; pure-Python tests in `tests/`.
- Install from existing Kodi source **rickirl91**. Open **Add-ons → Video Add-ons → TV Streaming - Cricky Home Personalisation (RC)**.
- Menu has Inspect, Preview, Test six feeds, Apply with one confirmation, Restore latest backup.

## Scope

Only `special://profile/addon_data/script.skinvariables/nodes/skin.arctic.fuse.3/skinvariables-shortcut-homewidgets.json` while current Kodi profile name is **Cricky** and active skin is **skin.arctic.fuse.3**.

Preserve the exact existing Continue Watching widget first, then insert Recommended For You, Because You Watched and From Your Watchlist; preserve all other existing row objects and their original relative order. No Trakt writes/tokens and no other hubs/profiles touched.

Each personalised row queries separate `movie` and `tv` TMDb Helper paths and alternates source-ranked titles, preserving each TMDb Helper returned callback. A native Kodi **See All** tile and **Next Page** folder are included; **this is not yet the validated custom Lazy Wall**. Only native next-page URLs are followed; it does not claim endless paging if unsupported.

The installer refuses to apply without one unambiguous Continue Watching row and successful access to six source directories. It cannot prove which Trakt account TMDb Helper sync settings selected. Confirm Family Trakt in its History and Watchlist settings before applying. No source feed list should be assumed to contain titles if its account watchlist is legitimately empty.

An immutable SHA-256 manifest and byte-for-byte backup are written under `special://profile/addon_data/plugin.video.tvstreaming.homepersonalisation/backups/` before an atomic Home replacement. Restore is refused after newer edits; preserve those newer edits manually.

## Xbox acceptance (must pass before marking complete)

1. Enter Cricky; inspect and preview the Home file. Do not apply from another profile.
2. Check TMDb Helper sync History and Watchlist providers are set to **Family Trakt**, not merely logged in to another Trakt addon.
3. Use **Test six Family Trakt film/TV sources** and test the **three mixed feeds** for posters, movie/TV navigation and watched badges.
4. Only if feed checks pass, select **Apply**; read preview and confirm once.
5. Fully quit and restart Kodi. If Home appearance is unchanged, rebuild shortcuts/widgets in Arctic Fuse 3. Check Continue Watching remains first and intact, then three personalised rows, then every other existing row.
6. Test selecting a film and a TV series, Play/Back, Home spotlight focus and See All/Next Page; watch for slowness or missing posters.
7. If any issue arises use **Restore latest automatic backup** before making further Home edits, then restart.

**Known limits:** Exact Xbox rendering of See All, mixed-source metadata and Native Next Page remains untested. Live source availability and Family-account isolation have not been verified. None of the existing Lazy Wall, StreamRow or bulk-setup ZIPs is replaced.
