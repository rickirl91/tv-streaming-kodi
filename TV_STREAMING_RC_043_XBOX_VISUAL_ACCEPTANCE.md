# Cricky Home Personalisation v0.1.3 — Xbox visual acceptance

Date: 24 November 2026. Evidence: user-supplied 27-second Xbox video `IMG_4258.mp4` inspected in current conversation. The video is not stored in this repository.

## Observed passes
- The three personalised Home rows — Recommended For You, Because You Watched, From Your Watchlist — have narrow portrait poster tiles matching the existing Trending Movies and Trending TV Shows rows.
- The neutral square-grid **See All** artwork is present in all three personalised rows, with corresponding narrow tile size.
- Their large background art still displays.
- The approved first four Home rows appear in order, beginning with Continue Watching.
- Up Next Episodes and other original Home sections remain visible below the personalised sections.

## Outstanding
- Old separate Home sections including Your Movie Watchlist, Recommended Movies For You and Recommended Shows For You are still visible. The four-row redundant cleanup has **not** been demonstrated complete. Use the existing v0.1.3 actions **5 Preview redundant-row cleanup** then **6 Remove redundant Home rows**, only after reviewing the exact proposed removals. Backup and restart.
- Hero preview mismatch: on a personalised See All tile, the left hero title and description say `See All - Recommended For You` with a generic browse description, while an existing Trending Movies See All tile displays the *first actual film title and synopsis*. This should be corrected in a separate, testable future polish without changing the actual See All callback or artwork.
- Mixed-feed See All pagination/return, correct Family Trakt account selection in TMDb Helper, watched progress/scrobble sync and final portable Cricky backup still need acceptance. Film and show routing was verified in earlier tests but not exercised in this video.

**Scope:** This note records observed results only. It does not mark unfinished features accepted and does not change any installed add-ons or Xbox files.
