# TV Streaming Lazy Wall — v0.1.1 (Xbox experiment)

**v0.1.1 startup fix:** Uses Kodi's supported `xbmc.getSkinDir()` API rather than `Skin.CurrentSkin`, which was incorrectly displayed literally and blocked Arctic Fuse 3.5.7. The lazy-wall operation remains unverified on Xbox.

A standalone experimental Kodi **Program add-on** to test progressively appending TMDb Helper Action Movies posters while navigating a single custom wall.

## Install using your existing Xbox Kodi source

1. Kodi > Settings > Add-ons > Install from zip file > **rickirl91**.
2. Select **script.tvstreaming.lazywall-0.1.1.zip**.
3. Open **Add-ons > Program add-ons > TV Streaming Lazy Wall (EXPERIMENT)**.
4. Scroll downward and check that additional posters appear without a blue Next Page tile.

An alternative route after the repository updates is **Install from repository > TV Streaming Repository > Program add-ons**.

## Safety and limitations

- Does **not** replace the existing working StreamRow See All tile, Kodi homepage widgets, playback players, TMDb Helper settings, profiles or Trakt.
- Experimental cap: **160 posters**. Back from movie details does not yet restore scroll position.
- The custom wall is inspired by the Arctic Fuse look but is not its native view. Its focus colour reads the active skin string.
- Kodi/Xbox behaviour has **not yet been validated**. The preview must pass on Xbox before it is integrated into the See All entry.
- The add-on requests its batches while the window is open and stores no account credentials.

v0.1.1 package ZIP SHA-256: `264b806ac6e2c200c271b1f3e7107dbf14a6efef5dd60bbfdb76874303908f3f`.

Previous v0.1.0 package remains on the source for rollback.
