# Continue Watching removal

Xbox Cricky / Arctic Fuse 3. Verified widget path from user screenshot:

`plugin://plugin.video.themoviedb.helper/?info=sync_currentlywatching&tmdb_type=both&widget=true&reload=`

Requirements: profile-local dismissal, immediate refresh, persistence across restart, reappearance after subsequent viewing, no writes to Trakt history, ratings or watchlist. Preserve original playback callbacks, resume metadata and widget properties. Investigate native sync dismissal semantics first; if unavailable, use a reversible profile-local adapter with verified identity and progress-change detection. Do not infer new viewing from cache refresh alone. Verify context menu availability in AF3 before release. No production changes until tests pass.
