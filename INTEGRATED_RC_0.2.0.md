# TV Streaming — integrated v0.2.0 release candidate (Xbox opt-in)

**Published as an explicit install-from-ZIP test only, not as an automatic Kodi repository upgrade.** The stable fallback remains Lazy Wall v0.1.4 and StreamRow v0.1.0. Neither Cricky homepage widgets, player preferences, Kodi profiles, nor Trakt settings are changed by merely publishing these files.

## What is included

- Lazy Wall: continuous TMDb Helper pagination without a 160-title catalogue cap. A rolling panel keeps approximately 200 poster items visible while refetching previously visited pages when scrolling backwards. Upstream TMDb discovery limits may still apply.
- Custom details popup with title, year, synopsis, rating, poster, background and Play/Browse Episodes.
- **Watch Trailer** asks TMDb Helper's `info=videos` directory for the selected TMDb ID and, if it finds an official trailer, plays it through the Kodi YouTube add-on. If YouTube is missing or no trailer is returned, it displays a message. No extra TMDb API key.
- Play uses TMDb Helper's `RunScript(plugin.video.themoviedb.helper,play=movie,tmdb_id=...)` route, reusing the user's default player. TV opens TMDb Helper seasons rather than guessing a next episode.
- StreamRow: 12 configured sample genre categories; a neutral See All first tile that gets the skin's active focus styling, and an experimental link to the lazy wall. The See All launcher requires a live Xbox test.
- There is no background crawling or account token storage in this package.

## Install from Xbox

1. **Settings → Add-ons → Install from zip file → rickirl91**.
2. First install `script.tvstreaming.lazywall-0.2.0-RC.zip`.
3. Then install `plugin.video.streamrow-0.2.0-RC.zip`.
4. **Program add-ons → TV Streaming Lazy Wall**: test scrolling, details, Play, Trailer, and return to prior selection.
5. **Video add-ons → TV Streaming StreamRow → Action — See All First**: test the first See All tile's handoff to the lazy wall, and normal movie posters.
6. Only after all pass, manually replace the Cricky Action widget path. Do **not** apply automatically.

## Acceptance criteria

1. Scroll beyond 160 without circular navigation or a Next Page tile; active panel stays bounded near 200.
2. Scroll back to older titles then forward; selection remains stable.
3. Selecting a poster opens our details modal, not a technical TMDb directory.
4. **Play** launches the configured working TMDb Helper provider.
5. **Watch Trailer** plays the correct official trailer (Kodi YouTube add-on required), or explains a missing dependency/trailer.
6. After trailer/movie playback, Return keeps wall selection.
7. See All first tile actually launches lazy wall and Back returns to the homepage normally.
8. Existing Cricky watch history and Trakt recommendations are unchanged by trailers.

## Known caveats

This is a release candidate tested by code inspection, Python/XML/ZIP checks, and simulated Kodi RPC responses. The new dialog, YouTube playback, and launcher have not yet passed an Xbox runtime test. Full native Miami-skin component inheritance is not implemented; the neutral artwork and focus colour are meant to blend with the skin.

### SHA-256

- `script.tvstreaming.lazywall-0.2.0-RC.zip`: `0572f9f4f1fe8c78ad9fb46ac45a8386922cd4f3f882b2827f66e1178f2d7d8f`
- `plugin.video.streamrow-0.2.0-RC.zip`: `6f6181205479a3e32e006482dc782194cf4de63d23ec8518bad023b2918ffa94`
