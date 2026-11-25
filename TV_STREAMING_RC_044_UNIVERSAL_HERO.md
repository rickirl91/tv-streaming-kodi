# TV Streaming — universal category-name See All hero (RC 044)

**Status: packaged for Xbox testing, not yet accepted on Xbox.**

## Why

Previously the neutral See All tile borrowed the first programme's **title and synopsis** in StreamRow-wrapped catalogue rows, while the three personalised feeds showed **See All - [category]**. The requested behaviour is the **category name only** as the large hero heading whenever the See All tile is selected. An actual selected film/TV entry should still show title-specific metadata.

## Packages

- `plugin.video.streamrow-0.3.1-RC.zip` (upgrade of `plugin.video.streamrow-0.3.0-RC.zip`).
- `plugin.video.tvstreaming.homepersonalisation-0.1.4-RC.zip` (upgrade of `plugin.video.tvstreaming.homepersonalisation-0.1.3-RC.zip`).
- Other installed ZIPs (Lazy Wall, bulk setup, catalogue) are intentionally untouched.
- Full sources and a no-network Python regression suite are committed in `src/streamrow/`, `src/homepersonalisation/` and `tests/test_universal_hero_044.py`.
- Earlier direct installers remain byte-exact under `archive/releases/`. These package upgrades do not change Home JSON, Trakt credentials, playback paths or Kodi profiles.

## Behaviour

- **StreamRow**: `add_see_all` still uses a neutral See All image and the first programme's backdrop; its *hero video title* is now the clean category label from the existing encoded source metadata (`source_meta.title`), with a fallback to the existing static category label. See All prefix/suffix and Kodi formatting tags are stripped. The first title's plot is **not** copied into the launcher. On a real poster, normal metadata remains unchanged.
- **Home Personalisation**: mixed-feed See All tiles show `Recommended For You`, `Because You Watched` and `From Your Watchlist` as large headings. First-title hero fanart, the poster-style rows, neutral tile image and film/TV callbacks remain intact.
- StreamRow is used for supported See All catalogue rows under **Home, Movies, TV Shows, Streaming Providers, genres and Documentaries** where previously converted by Bulk Setup. Existing native/third-party See All tiles outside these two plugins are out of scope and must be checked separately rather than assumed updated.

## Xbox steps

1. Switch to **Cricky**. In **Settings → Add-ons → Install from zip file → rickirl91**, install `plugin.video.streamrow-0.3.1-RC.zip`, then `plugin.video.tvstreaming.homepersonalisation-0.1.4-RC.zip`.
2. Check add-on information shows StreamRow **0.3.1** and Home Personalisation **0.1.4**. Fully quit Kodi and reopen it.
3. On **Home**, focus See All in **Recommended For You**, **Because You Watched**, **From Your Watchlist** and **Trending Movies**. Large hero heading must show the category name, **not** See All or a title of a film or series.
4. Repeat in **Movies (Action or Comedy)**, **TV Shows (a category)**, **Streaming Providers (Netflix/Disney/Apple)** and **Documentaries**, wherever a See All tile exists. The hero category title should match the row label.
5. Move right to a real movie/show: its own title, description and hero background should be shown. Open See All, test poster wall navigation and Back. Verify film Play and show episode selection in one representative category.
6. If the heading is stale, first confirm both versions and that Kodi was fully restarted. Capture one row + screenshot. **Do not rerun Bulk Setup, Apply Home, duplicate cleanup or restore backups for a presentation-only issue.**
7. If regression occurs, previous exact ZIPs are in `archive/releases/` for controlled rollback; inspect before reinstalling anything.

## Still pending before Cricky signoff

- Live Xbox verification of the universal category headings in all supported hubs.
- Mixed personalised See All pagination and return navigation.
- Confirmation of the Family Trakt provider in TMDb Helper and watched-progress sync.
- Final verified portable Cricky profile backup.

**The prior 8-row Home layout and completed cleanup are intentionally preserved.**

## Automated release verification

On 25 November 2026, [GitHub Actions regression run 45515749295](https://github.com/rickirl91/tv-streaming-kodi/actions/runs/45515749295) completed **SUCCESS**. All five tests passed: ZIP/source parity and syntax, category label normalisation, StreamRow hero behaviour, personalised hero behaviour and unchanged navigation anchors. The runner produced SHA-256 values:

- StreamRow 0.3.1 RC: `63664b5062ea4ab8c0aff0b8184f646886807a42ca216c15b8b84ad3a6070bb7`
- Home Personalisation 0.1.4 RC: `59a729f64475dcbc7488147f2ba285c2ddff076e3d8b7dff858bee2b6777d6a9`

These checks do not replace Xbox visual acceptance. The package content is fixed at this checksum; avoid recreating ZIPs under the same filename.

The 0.3.1 and 0.1.4 installers are now in the [archive](archive/). Follow the [consolidated RC guide](CONSOLIDATED_RC.md) for the latest installers.
