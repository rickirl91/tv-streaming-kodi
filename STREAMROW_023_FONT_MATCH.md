# StreamRow v0.2.3 RC — Arctic Fuse 3 font + Miami-friendly artwork

## Confirmed Xbox baseline
- StreamRow v0.2.2: See All select launches Lazy Wall correctly on Xbox.
- Lazy Wall v0.2.1 RC: movie details display is visibly readable; scrolling works.
- User reports that the original See All poster itself still appeared blue.

## Targeted changes in StreamRow v0.2.3
- Repainted the 600×900 See All poster as **neutral charcoal + off-white** (no blue/purple tint).
- Re-rendered its "SEE ALL" lettering in **Inter Bold**, matching Arctic Fuse 3's installed `font_main_bold`/Inter family.
- The active Kodi skin continues to draw the Miami pink selection border; we do not hard-code accent colours into the poster.
- The text is part of a raster artwork asset because Kodi's home widget renders this tile as a poster. The font follows the installed Arctic Fuse 3 design but would not automatically change when switching to a different skin.
- **Exact, byte-for-byte unchanged StreamRow default.py compared with v0.2.2**: no change to See All click handling, direct fallback, catalogue, playback, Trakt, or profiles. Lazy Wall v0.2.1 RC is untouched.
- **No font files bundled.** Lazy Wall's details XML already references active-skin font names (`font_title_main`, `font_main`, `font_mini`).

## Xbox test
Install only **plugin.video.streamrow-0.2.3-RC.zip** from **Settings → Add-ons → Install from zip file → rickirl91**. Open Video add-ons → TV Streaming StreamRow → Action — See All First and verify the first tile is neutral dark with white Inter Bold "SEE ALL" and the Miami pink focus border. Press A once to confirm Lazy Wall still opens.

If old blue artwork persists, reload the widget / reopen Kodi to invalidate skin artwork cache; do not reinstall Lazy Wall.

ZIP SHA-256: `9e02ce12853bb5b4204151a7721b74426b8703931ad09ab98fa21465ee5c497c`.

Future phase: final Play/Watch Trailer test and replacement of the working Cricky Action homepage widget only after acceptance.
