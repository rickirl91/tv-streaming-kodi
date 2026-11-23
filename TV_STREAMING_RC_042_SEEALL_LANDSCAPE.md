# TV Streaming — Cricky See All horizontal tile correction (v0.1.2 RC)

**Built:** 23 November 2026. **Status:** Offline tests pass (4 targeted mocked-Kodi tests); Xbox confirmation pending.

## Observed fault and cause

An Xbox screenshot showed **See All - Because You Watched** with **Get Fast** artwork on the small horizontal tile, even after v0.1.1 had supplied the neutral Miami image for poster/thumb/icon. The SkinVariables `Image_Landscape` resolver in Arctic Fuse 3 takes `Art(landscape)` first and falls back to `Art(fanart)` before the poster. Because v0.1.1 set the first title's fanart for the large Home hero, the skin used that fanart on the horizontal tile.

This was an artwork selection error, not a Trakt or list-fetch error. v0.1.1's installed version on the Xbox was not independently inspected; the screenshot and v0.1.1 source are consistent with this mechanism.

## Scoped change

- Installer: `plugin.video.tvstreaming.homepersonalisation-0.1.2-RC.zip`
- SHA256: `87a04551a433fb73219d066bf9a3b35f5bfdf82c3b862319aebc842649ebd0f4`
- Add-on ID unchanged, version changed from `0.1.1` to `0.1.2`.
- The See All `ListItem` sets the existing StreamRow neutral Miami artwork as `poster`, `thumb`, `icon`, **`landscape`**, and as `override_landscape`. The first title's `fanart` remains for the large preview.
- If StreamRow's asset isn't accessible, the fallback is the skin's neutral folder icon, not a programme poster.
- No changes to Home widget JSON, categories, pagination, Trakt account, watched state, playback, duplicate cleanup, or backup/restore. **No Home reapplication required.**
- Reproducible builder: `tools/build-homepersonalisation-012.py`. Regression tests: `tests/test_home_personalisation_v012.py`.

## Xbox verification

1. With the **Cricky** profile active, in Kodi **Settings → Add-ons → Install from zip file → rickirl91**, install `plugin.video.tvstreaming.homepersonalisation-0.1.2-RC.zip`. If Kodi asks to update the existing add-on, accept. The version should be **0.1.2** in Add-on information.
2. **Fully quit Kodi** and relaunch (not just Back to Home). No Bulk Setup and no Apply Home required.
3. In Home, focus the first tile of **Recommended For You**, **Because You Watched**, and **From Your Watchlist**. Each **See All** horizontal tile should display the standard neutral Miami artwork, while the large hero can still show the first film/show's backdrop.
4. Open one See All tile and Back. Existing film and TV routing and list behaviour should remain unchanged.
5. If a tile still displays a programme image, capture the add-on version and the selected row screenshot **before any more changes**, so we can distinguish old version/cache from skin styling. Do not use **Restore latest automatic backup** for an artwork-only problem.
6. The optional redundant-row cleanup remains a separate preview-and-confirm operation; perform only if the old overlapping rows remain.

Only after the Xbox tests should v0.1.2 be marked accepted.
