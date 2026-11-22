# TV Streaming Lazy Wall v0.3.1 RC — bulk source pagination

## Fault
After bulk rollout v0.3.0, some Apple TV+ Movies and Apple TV+ Series lists show exactly 20 titles and incorrectly say end of catalogue. Action Movies successfully pages.

## Scoped fix
For configured TMDb Helper source directories, remove widget-only restrictions but keep every source filter; retain Next Page links where present; cautiously try page 2 if page 1 has 20 results but no Next Page. Duplicate/empty results stop pagination. Native genre paths, 200-poster window, Play, trailer and return-position logic are unchanged.

## Xbox acceptance
Install script.tvstreaming.lazywall-0.3.1-RC.zip. Open Apple TV+ Movies, Apple TV+ Series and a Trending TV or Movie source, scroll after title 20, and confirm whether more titles load. Retest Action Movies, movie Play/Trailer and return-to-position. If no additional results, capture exact provider source URL for further diagnosis.

**Status:** Package and Python syntax/URL transformations verified in automated build; Xbox behaviour requires testing.
