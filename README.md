# TV Streaming — Kodi Repository

Source: https://rickirl91.github.io/tv-streaming-kodi/

## v0.2.2 — Streaming Services grouped by provider (Xbox validation pending)

Custom Arctic Fuse 3 Streaming Services hub now has **12 rows, grouped movie/series pairs**:

1. Netflix Movies / Netflix Series
2. Disney+ Movies / Disney+ Series
3. Prime Video Movies / Prime Video Series
4. Apple TV+ Movies / Apple TV+ Series
5. Paramount+ Movies / Paramount+ Series
6. HBO Max Movies / HBO Max Series

The previous Prime Video Series widget returned No Results on the user's Xbox. The filter now requests regional provider 9/119 plus ad-tier 2100 and free-with-ads 613, with Ireland region and flatrate/ads/free access models. This is an evidence-based *candidate fix*, not a verified live outcome.

The Streaming Services browse menu is aligned to the same provider/region queries. All other Arctic Fuse 3 hub files are unchanged. Existing Trakt upcoming-episodes/calendar icon, Search, Movies, TV Shows, Documentaries and Kids setup are left as before.

### Install on Xbox

1. Kodi → Add-ons → Install from zip file → existing `rickirl91` source.
2. Select `plugin.video.tvstreaming.catalogue-0.2.2.zip`.
3. Video add-ons → TV Streaming Catalogue & Preset → **Install / Update Standard Arctic Fuse 3 Preset**.
4. Verify current adult profile, then **Back up + apply**.
5. Run **Rebuild Arctic Fuse 3 Shortcuts & Widgets** from the same add-on if the old widget layout remains. Reload Home or fully restart Kodi.
6. Confirm 12 Streaming Services rows and whether both Prime Video lists populate.

If something is wrong, choose **Restore Latest Backup** within the add-on, then rebuild/restart. Previous 0.2.1, 0.2.0, and 0.1.0 package ZIPs are retained in the repository.

> TMDb availability data can be incomplete or stale and does not guarantee a working playback source. Provider queries and content cannot be verified without Xbox/TMDb live execution.

