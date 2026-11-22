# TV Streaming Lazy Wall — v0.1.4 (Xbox experiment)

The v0.1.3 user video proves progressive loading from 20 to 159 posters without losing browsing position during appends. At the **160-poster safety cap**, pressing Down wraps Kodi's panel back to the first poster.

## Narrow v0.1.4 fix
- Replace the panel's explicit self-target navigation (up/down/left/right control ID 100) with `noop` edge targets. This should prevent the end-of-list focus wrap.
- Preserve TMDb Helper paging, poster artwork, selection restoration, original playback handoff and the deliberately retained 160-poster safety cap.
- The included two small PNG assets are palette-optimised **without pixel changes**.

## Xbox installation
Settings → Add-ons → Install from zip file → **rickirl91** → **script.tvstreaming.lazywall-0.1.4.zip**.
Then Program add-ons → TV Streaming Lazy Wall (EXPERIMENT). Scroll to the 160-poster safety limit and press Down one more time: focus should remain at the end.

This is an **unverified Xbox behaviour fix**; the ZIP, Python/XML syntax, and Git blob integrity were checked before publishing. The current Cricky homepage and StreamRow widget are not changed.

SHA-256: `af9b0e2038e8119ca9d43e3d96fe52578753aade0622620ec9cd17101dfd4ec8`. Prior packages remain available for rollback.
