# TV Streaming Lazy Wall — v0.1.2 (Xbox experimental)

The user’s video of v0.1.1 proved the catalogue counter advanced from **20 to 39** posters while the wall itself stayed blank. The catalogue requests worked; the custom panel failed to render the items.

**v0.1.2 rendering fix:** Uses a non-media WindowXML and explicitly populates custom panel control ID 100 with `ControlList.addItems`, instead of populating the built-in media-window list. Adds a title label to the focused item as a visual diagnostic fallback. The scroll prefetch, 160-title safety cap and source TMDb Helper paths are unchanged.

### Install on Xbox

1. **Settings → Add-ons → Install from zip file → rickirl91**.
2. Select **script.tvstreaming.lazywall-0.1.2.zip**.
3. Open **Program add-ons → TV Streaming Lazy Wall (EXPERIMENT)**.
4. Check that posters appear, move the selection, and scroll down to see whether the counter advances past 39 without a Next Page tile.

This build **does not** replace the working StreamRow first-tile widget, Cricky homepage, Arctic Fuse 3, playback providers, Trakt or profiles. It is not proven on Xbox until the user tests this version. Back-to-position and full skin inheritance are not implemented.

Prior releases v0.1.0 and v0.1.1 remain available for rollback.

ZIP SHA-256: `54b3c2bdd4678b57f9c3df069de4fef863e28a9321c0bbd0c55907ef7079fb32`.
