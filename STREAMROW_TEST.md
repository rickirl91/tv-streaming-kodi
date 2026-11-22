# StreamRow — See All First (experimental)
 
**v0.1.0 / test only.** Adds a first-position "See All" tile ahead of the Action movie posters without modifying the existing TV Streaming Catalogue & Preset add-on, Kodi players, the Arctic Fuse 3 skin, Trakt, or TMDb Helper configuration.

## Install on Xbox

In Kodi's existing **TV Streaming Repository**, use **Install from repository → TV Streaming Repository → Video add-ons → StreamRow - See All First (Test)**. If it does not appear after Kodi refreshes the repository index, install the direct ZIP `plugin.video.streamrow-0.1.0.zip` from the existing `rickirl91` source (no new source needed).

Open **Video add-ons → StreamRow - See All First (Test) → Action - See All First (test)**.

Verify that (1) See All appears first, (2) the movie posters and information load correctly, (3) See All opens the Action wall on page one, and (4) opening an individual movie follows normal TMDb Helper playback.

**Do not replace the working homepage Action widget until all four checks pass.** Kodi's JSON-RPC `Files.GetDirectory` may not return all artwork/metadata from nested TMDb Helper plugin paths. If the preview shows `[TEST NOT PASSED]`, keep the existing widget and report the screenshot.

The package is static and has no background tasks or API keys.

The ZIP is available at `https://rickirl91.github.io/tv-streaming-kodi/plugin.video.streamrow-0.1.0.zip`. Previous catalogue releases remain untouched.
