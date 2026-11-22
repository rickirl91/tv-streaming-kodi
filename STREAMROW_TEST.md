# StreamRow — See All First (experimental)
 
**v0.1.0 / test only.** Adds a first-position "See All" tile ahead of the Action movie posters without modifying the existing TV Streaming Catalogue & Preset add-on, Kodi players, the Arctic Fuse 3 skin, Trakt, or TMDb Helper configuration.

## Install on Xbox

**Recommended on the current Xbox:** Open **Settings → Add-ons → Install from zip file → rickirl91 → plugin.video.streamrow-0.1.0.zip**. The existing `rickirl91` source is enough; you do not need to install a new Kodi repository. If the dedicated **TV Streaming Repository** is installed, the add-on can alternatively be found under **Install from repository → TV Streaming Repository → Video add-ons** after its index refreshes.

Open **Video add-ons → StreamRow - See All First (Test) → Action - See All First (test)**.

Verify that (1) See All appears first, (2) the movie posters and information load correctly, (3) See All opens the Action wall on page one, and (4) opening an individual movie follows normal TMDb Helper playback.

**Do not replace the working homepage Action widget until all four checks pass.** Kodi's JSON-RPC `Files.GetDirectory` may not return all artwork/metadata from nested TMDb Helper plugin paths. If the preview shows `[TEST NOT PASSED]`, keep the existing widget and report the screenshot.

The package is static and has no background tasks or API keys.

The ZIP is available at `https://rickirl91.github.io/tv-streaming-kodi/plugin.video.streamrow-0.1.0.zip`. Previous catalogue releases remain untouched.


## v0.2.1 RC: neutral first-position See All tile
- Replaces the old bright blue tile image with neutral charcoal 3x3 grid artwork. The highlight colour still comes from the active Arctic Fuse skin (Miami pink in current profile).
- Supports Action and other named movie categories; the first tile launches the v0.2.1 rolling Lazy Wall test.
- **Does not** automatically replace the working Cricky homepage widget. Install directly from ZIP: `plugin.video.streamrow-0.2.1-RC.zip` after Lazy Wall v0.2.1 RC.
- SHA256: `56f1d14f5ae2fe63e6b126b4b73f5c7f88c77fe0b6df1282bcd0008e8d7fa16a`.
