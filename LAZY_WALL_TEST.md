# TV Streaming Lazy Wall — v0.1.0 (Xbox experiment)

A standalone experimental Kodi **Program add-on** to test progressively appending TMDb Helper Action Movies posters while navigating a single custom wall.

## Install using your existing Xbox Kodi source

1. Kodi > Settings > Add-ons > Install from zip file > **rickirl91**.
2. Select **script.tvstreaming.lazywall-0.1.0.zip**.
3. Open **Add-ons > Program add-ons > TV Streaming Lazy Wall (EXPERIMENT)**.
4. Scroll downward and check that additional posters appear without a blue Next Page tile.

An alternative route after the repository updates is **Install from repository > TV Streaming Repository > Program add-ons**.

## Safety and limitations

- Does **not** replace the existing working StreamRow See All tile, Kodi homepage widgets, playback players, TMDb Helper settings, profiles or Trakt.
- Experimental cap: **160 posters**. Back from movie details does not yet restore scroll position.
- The custom wall is inspired by the Arctic Fuse look but is not its native view. Its focus colour reads the active skin string.
- Kodi/Xbox behaviour has **not yet been validated**. The preview must pass on Xbox before it is integrated into the See All entry.
- The add-on requests its batches while the window is open and stores no account credentials.

Original package ZIP SHA-256: `63c2e259c41c2336d490cc46978a9cb8c88258876928333a56e46d2a3ec8fa25`.
