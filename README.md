# TV Streaming — Kodi Repository

Source: https://rickirl91.github.io/tv-streaming-kodi/

## v0.2.3 — Optional TMDb Movies playback-link setup

- TMDb Movies playback confirmed directly in Xbox Kodi by user. Other tested add-ons have not produced working playback.
- New *optional* action **Connect TMDb Movies Playback** is in TV Streaming Catalogue & Preset main menu.
- Adds a single validated JSON player mapping for movies and episodes to the active profile's TMDb Helper `players` folder only after confirmation.
- Based on upstream TMDb Movies `tmdb_resolve` endpoints from Angelitto; adapts title placeholders to TMDb Helper's documented keys and encodings.
- Verifies TMDb Helper and TMDb Movies are installed; blocks common Kids profile names; backs up pre-existing same-name file; verifies the write and attempts rollback on failure.
- **Does not** change default movie/episode player settings. Users set default via TMDb Helper > Configure > Players. Restart Kodi if player not listed.
- **Does not** modify any navigation, widget, skin, Trakt, source, or playback provider settings. All v0.2.2 Arctic Fuse 3 navigation JSON files are byte-identical.
- Installation and integrated playback remain to be tested on Xbox; no claims of successful TMDb Helper handoff yet.

### Xbox setup

1. Install `plugin.video.tvstreaming.catalogue-0.2.3.zip` from existing `rickirl91` Kodi source.
2. Open Video add-ons > TV Streaming Catalogue & Preset > Connect TMDb Movies Playback (optional).
3. Select Install player link in adult Kodi profile (TMDb Movies already installed).
4. In TMDb Helper > Configure > Players, choose TMDb Movies (TV Streaming) as movie and episode default if it appears, or choose it from Play With dialog first.
5. Test a permitted film and a TV episode from our current Arctic Fuse 3 lists. A Kodi restart may be necessary.

### Navigation base retained from v0.2.2

Home; Streaming Services paired provider movies/series; Movies; TV Shows; Documentaries; upcoming episodes calendar; Search. Other profiles are not changed by the playback-link action.

Previous version ZIPs are preserved for rollback.
