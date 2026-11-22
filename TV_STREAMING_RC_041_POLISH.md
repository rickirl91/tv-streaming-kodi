# TV Streaming — Cricky Personalisation v0.1.1 RC polish

**22 November 2026**. **Status:** Offline logic tested (10 passes); Xbox v0.1.1 artwork and cleanup still await verification. Initial 0.1.0 three mixed feeds, posters, movie/TV navigation and required Home order were shown working on Xbox.

## Update

- ZIP: `plugin.video.tvstreaming.homepersonalisation-0.1.1-RC.zip`; SHA-256: `c30b8e0ed33446d7147b158903f8917ff100b369c03526df7928a3002552d72a`.
- Same add-on ID as v0.1.0, upgrades in place. Installing alone makes no Home changes.
- The previous See All tile incorrectly reused the first movie/TV title's **poster**. New version uses the **exact existing StreamRow Miami neutral SEE ALL artwork** at `resources/media/see_all_miami_neutral_v024.png`, found through Kodi's installed StreamRow add-on path. Retains first title's fanart for Home hero. Falls back to neutral skin folder image, never to a programme poster.
- Two new menu actions (5 Preview, 6 Cleanup) for **old separate Home rows only**. Labels: Your TV Show Watchlist; Your Movie Watchlist; Recommended Movies for You; Recommended Shows for You (plus limited exact plural TV aliases). The read-only preview shows *actual* matched row names.
- Cleanup refuses unless the approved first four rows and exact personalisation source paths exist. It never removes Up Next Episodes, Continue Watching, the new 3 combined feeds, Trending, genres, providers, new releases, or other hubs.
- Cleanup creates a fresh byte-exact SHA-256 Home backup; restore refuses to clobber later manual edits.
- No Trakt writes, credentials, catalog rebuild, altered playback or changes in other Kodi profiles.

## Xbox sequence

1. Open **Cricky** and install `plugin.video.tvstreaming.homepersonalisation-0.1.1-RC.zip` from Kodi **Settings → Add-ons → Install from ZIP file → rickirl91**. Do not rerun Bulk Setup.
2. **Fully quit and restart Kodi**; focus first tile in Recommended For You, Because You Watched and From Your Watchlist. Confirm each now shows standard neutral **SEE ALL** tile (not a film/TV poster). Hero backdrop may still reflect first recommendation by design.
3. Open **TV Streaming - Cricky Home Personalisation** → **5. Preview redundant-row cleanup**. Confirm exactly the old separate watchlist/recommendation rows appear. If labels differ, stop and send the preview rather than guessing.
4. Choose **6. Remove redundant Home rows**, read the preview, confirm once. Restart Kodi.
5. Verify the order: Continue Watching; Recommended For You; Because You Watched; From Your Watchlist; **Up Next Episodes**; then remaining sections, minus only the overlapping old watchlist and recommendations.
6. Verify See All, a film and a TV show still open correctly. If any issue occurs, use **7. Restore latest automatic backup** *before any new Home edits*, and restart Kodi.

**Only initial RC display and routing are Xbox-confirmed**. This release is not considered fully accepted until the artwork and optional cleanup test above pass.
