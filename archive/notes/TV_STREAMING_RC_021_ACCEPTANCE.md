# TV Streaming — v0.2.1 RC Xbox acceptance

**Scope:** only visual fixes over v0.2.0 RC. These direct-ZIP installs are opt-in and don't change the existing Cricky home widgets or the repository's automatic-update metadata.

1. Install `script.tvstreaming.lazywall-0.2.1-RC.zip`, then `plugin.video.streamrow-0.2.1-RC.zip` from **Kodi → Settings → Add-ons → Install from zip file → rickirl91**.
2. Program add-ons → **TV Streaming Lazy Wall** → Action Movies. Select 2–3 posters and verify readable matte details: no transparent text over posters, and Play/Watch Trailer/Back accessible.
3. Test **Watch Trailer** for a movie with an available trailer. Requires enabled YouTube add-on; if missing, expect a clear message. Back should return without changing the selected movie or marking it watched.
4. Test **Play** on a known working title with a valid stream. It must use the current TMDb Helper default player. Confirm successful playback and return to selected poster.
5. Scroll far beyond the old 160-posters test limit, then backwards. Expect about 200 items held at a time, consistent poster navigation, no pagination tile, and no reset to the first row.
6. Video add-ons → **TV Streaming StreamRow** → Action — See All First: verify the first tile is neutral charcoal with Miami focus, not bright blue. Open it and ensure it launches Lazy Wall.

Only after these checks, configure one **test homepage row** using StreamRow, preserve the original row, then promote other categories.

Deferred: richer metadata (age rating, runtime, rating source etc.) in issue #1. Keep old v0.1.4 ZIP and prior v0.2.0 RC ZIPs available for rollback.
