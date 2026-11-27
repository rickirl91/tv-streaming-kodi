# Continue Watching removal

Xbox Cricky / Arctic Fuse 3. Verified widget path from user screenshot:

`plugin://plugin.video.themoviedb.helper/?info=sync_currentlywatching&tmdb_type=both&widget=true&reload=`

Requirements: profile-local dismissal, immediate refresh, persistence across restart, reappearance after subsequent viewing, no writes to Trakt history, ratings or watchlist. Preserve original playback callbacks, resume metadata and widget properties. Investigate native sync dismissal semantics first; if unavailable, use a reversible profile-local adapter with verified identity and progress-change detection. Do not infer new viewing from cache refresh alone. Verify context menu availability in AF3 before release. No production changes until tests pass.

## Scope clarification (27 November 2026)
Continue Watching dismissal affects only that row. No dedicated restore UI. Titles remain discoverable in search, categories and recommendations; verified subsequent viewing clears dismissal. Internal restoration logic remains useful for playback detection. Separately proposed Not Interested preference may suppress future recommendations and optionally general discovery rows, with search retained and reversible profile-local preferences. Exact scope and AI publisher integration require user agreement before implementation. Do not conflate the two stores or modify Trakt data.
