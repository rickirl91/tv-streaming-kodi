TV STREAMING KODI — v0.2.2
==========================

Latest change: each streaming provider now has a Movies row directly followed by a Series row. 12 provider rows total. Prime Video's discover query includes multiple regional/ad-supported TMDb provider IDs, to address the empty Prime Video Series row in v0.2.1.

UPDATE ON XBOX
1. Add-ons > Install from zip file > rickirl91 > plugin.video.tvstreaming.catalogue-0.2.2.zip
2. Video add-ons > TV Streaming Catalogue & Preset > Install / Update Standard Arctic Fuse 3 Preset.
3. Select Back up + apply only when the adult Kodi profile is active.
4. Rebuild Arctic Fuse 3 Shortcuts & Widgets if needed; return Home.
5. Open Streaming Services. Expect Netflix Movies, Netflix Series, Disney+ Movies, Disney+ Series, Prime Video Movies, Prime Video Series, Apple TV+ Movies, Apple TV+ Series, Paramount+ Movies, Paramount+ Series, HBO Max Movies, HBO Max Series.

RESTORE: Video add-on > Restore Latest Backup.

Use existing direct ZIP source. Kodi repository automatic updates were unreliable in v0.1.0; direct ZIP method is already tested on Xbox. The package does not modify account tokens, playback sources, theme, Kids profile, or other hub widget JSON.

UNVERIFIED: the new Prime Video query may still return empty results if TMDb has no IE streaming records or if your installed TMDb Helper interprets provider IDs differently. Do not treat it as a confirmed fix until verified in Kodi.
