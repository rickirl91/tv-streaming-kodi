# TV Streaming — Kodi Repository

Hosted Kodi file source: https://rickirl91.github.io/tv-streaming-kodi/

The add-on `plugin.video.tvstreaming.catalogue` installs a profile-scoped Arctic Fuse 3 navigation preset; it never applies that preset without an explicit backup-and-apply confirmation.

## v0.2.1 — navigation update (Xbox confirmation pending)

Horizontal menu: Search (magnifier), Home, **Streaming Services**, Movies, TV Shows, Documentaries, **Trakt - Upcoming Episodes** (calendar icon on the right), Power.

This is a layout-only change relative to 0.2.0. All existing movie, TV, documentary, provider, search and Trakt widget paths remain intact. No Kodi skin modification, account changes or Kids-profile changes.

### Xbox update instructions

1. Kodi → Add-ons → Install from zip file → existing `rickirl91` source.
2. Install `plugin.video.tvstreaming.catalogue-0.2.1.zip`.
3. Video add-ons → TV Streaming Catalogue & Preset → **Install / Update Standard Arctic Fuse 3 Preset**.
4. Confirm the adult profile name, then choose **Back up + apply**.
5. If navigation is stale, choose **Rebuild Arctic Fuse 3 Shortcuts & Widgets** in the same add-on, then return Home.
6. Restore prior menu if needed using **Restore Latest Backup**.

Earlier ZIPs are kept for rollback: [v0.2.0](plugin.video.tvstreaming.catalogue-0.2.0.zip) and [v0.1.0](plugin.video.tvstreaming.catalogue-0.1.0.zip).

Kodi repository metadata (`addons.xml` + `addons.xml.md5`) and versioned ZIP paths are also published for repository clients, although direct ZIP installation is the method already proven on Xbox.

### v0.2.0 history

Search people source, updated new/returning-show discovery, attempted empty provider/documentary row fixes and explicit rebuild action. Some metadata filters are still subject to Xbox validation.
