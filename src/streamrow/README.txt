TV Streaming StreamRow v0.2.0 — consolidated release candidate

Requires TV Streaming Lazy Wall v0.2.0 (included dependency in our repo).
Select the Video add-on, then Action — See All First. Tile one will
attempt to open the scroll-loading wall; other 20 posters remain Kodi items.

This folder-launch handoff has NOT yet passed an Xbox test. Keep your existing
Action widget unchanged until both tile and movie Play tests pass.

See All artwork is neutral and inherits Arctic Fuse focus highlighting. Actual
pixel recolouring of the poster based on Miami requires changing the skin,
so this package avoids claiming full live palette inheritance.

Other genres are exposed for future rollout without rebuilding code.


v0.2.1 RC: replaced fixed blue See All poster with a neutral charcoal tile.
Arctic Fuse supplies the currently selected focus colour to its poster frame.
This is theme-compatible but the tile interior is intentionally neutral.


0.2.2 Xbox See All click repair:
- Treat See All as a non-playable action callback, not as a directory.
- Use RunAddon to hand off to Lazy Wall by category; avoid failed endOfDirectory.
- Context-menu fallback: Open Full Wall (direct) if Kodi still intercepts select.
- This is a targeted integration change only; movie artwork, widgets and
  the separate v0.2.1 Lazy Wall build are otherwise unchanged.


0.2.3: neutral artwork (charcoal/white) in place of the navy/lavender See All
image. Active Arctic Fuse 3/Miami skin still provides focus selection colour.
No change to Kodi list item type, direct launch callback, movie source
selection, wall content, Trakt, or on-Xbox profiles.


v0.2.4 RC — ARTWORK CACHE-BUST FIX
Kodi texture caching kept displaying the obsolete blue See All icon in v0.2.3.
The existing fully grayscale Inter Bold / charcoal poster has a new physical filename, see_all_miami_neutral_v024.png.
No changes to video list, See All click, context fallback, Lazy Wall, Trakt or player settings.
Selecting the tile still gets the Miami pink border from Arctic Fuse.

0.2.5 focused home-widget preview improvement:
- While See All remains selected as the first poster, borrow the first listed
  film/show's title, plot, year, rating and fanart for Arctic Fuse's hero
  preview. The tile itself keeps its neutral poster, label and proven launcher.
- If the first item has no fanart, background remains skin default; no
  artwork is invented or fetched from another film. When the catalogue query
  fails the launcher remains visible.
- Works for all 12 categories, including TV, without altering playback.
- Xbox acceptance still required for Arctic Fuse 3 rendering and click action.

v0.3.0 RC: Generic source wrapper adds the existing See All tile to static
TMDb Helper movie and TV catalogue paths while retaining each original sort,
provider, list source and filter. Playback and first movie preview are unchanged.
After source tokens are installed in widget paths using Bulk Setup, selecting
See All opens the matching Lazy Wall v0.3.0 source. Existing tested Action
widget mode remains available as before.

0.3.1 RC: Category-only hero title on every StreamRow See All tile across its supported hubs; first-title fanart, layout, sources, Lazy Wall and movie/TV callbacks remain unchanged.
