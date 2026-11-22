# TV Streaming Lazy Wall — v0.2.2 RC

## Purpose
Fix two bugs reported in Xbox video testing with v0.2.1 RC:
- Selecting **Watch Trailer** launches the YouTube video, but the movie details dialog remains on top and obscures playback.
- Returning from the trailer resets the Action Movies wall to its first poster, rather than preserving the selected film.

The `script.tvstreaming.lazywall-0.2.2-RC.zip` release candidate changes trailer handoff to close the details dialog before video starts, waits for playback to finish, then aims to restore the same film's details screen and browsing position. It also makes the custom wall's initialization idempotent on Kodi window reactivation. This version is **not yet verified on Xbox**.

## Install
Kodi > Settings > Add-ons > Install from zip file > **rickirl91** > `script.tvstreaming.lazywall-0.2.2-RC.zip`.

Only Lazy Wall needs updating. **StreamRow v0.2.4 RC stays installed**. Do not replace the current Cricky homepage widget yet.

## Acceptance test
1. Open Program add-ons > TV Streaming Lazy Wall, scroll well down the Action Movies list, and select an already released movie.
2. Select **Watch Trailer**. Confirm the video appears in front, full screen, without the details dialog obscuring it.
3. Stop or exit the trailer. Confirm the **same movie's details** reappears and Back returns to the original movie position, not the top of the Action Movies wall.
4. Check **Play** still starts the film normally.

If the new handoff fails, reinstall `script.tvstreaming.lazywall-0.2.1-RC.zip`, still available at the same source. This RC is intentionally not promoted in `addons.xml` until confirmed.

## Integrity
Source ZIP passed local archive integrity checks and has been uploaded to GitHub with a matching Git blob ID. SHA-256: `b6cad1676caf7c7be1c6808dac6c7de98cc5a66040545d30ecd099355028631c`.
