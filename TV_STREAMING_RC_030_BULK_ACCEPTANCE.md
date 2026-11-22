# TV Streaming — One-confirmation bulk widget setup (Release Candidate)

## Scope
Build on the Xbox-tested Action Movies setup: neutral Miami See All tile, first-film backdrop/description, Play, trailer/fullscreen/return, and rolling 200-item Lazy Wall. Preserve existing Movies / TV Shows / Documentaries / provider menus and current profile settings.

Three independent opt-in ZIPs; installation via **Settings > Add-ons > Install from ZIP file > rickirl91**:
1. `script.tvstreaming.lazywall-0.3.0-RC.zip`
2. `plugin.video.streamrow-0.3.0-RC.zip`
3. `script.tvstreaming.bulksetup-0.1.0-RC.zip`

The bulk setup is **not automatic** on installation. In Kodi Program add-ons, open **TV Streaming — Bulk Widgets Setup (RC)** > **Preview and apply compatible catalogue rows**, review count and example labels, and confirm. This operates only on the **current Kodi profile**.

## What gets converted
- Existing widget paths under `special://profile/addon_data/script.skinvariables/nodes/skin.arctic.fuse.3/skinvariables-shortcut-*widgets.json` that point to a static TMDb Helper catalogue URL with explicit `tmdb_type=movie` or `tmdb_type=tv`
- These can include Recently Released, Trending, genre rows, documentary rows, streaming-provider filtered TMDb catalogues, popular/new TV and other eligible lists
- Existing genre/category/sort/provider/list source strings are retained, encoded into a safe StreamRow wrapper URL; the corresponding Lazy Wall follows the original catalogue's TMDb Helper Next page links. No artificial full-catalogue claim where the source doesn't offer pagination
- Original row labels, order, IDs, target, style, icons, menus and other properties remain untouched except `path`; the already-tested `Action — See All First` row can be renamed `Action Movies` without altering its working path

## What is intentionally left alone
- Continue Watching, Next Up, In Progress, Trakt personal lists/watchlists/history and similar progress widgets
- Kodi native entries, unrelated plugins (including unsupported custom provider catalogue add-ons), dynamic `$INFO` paths not limited to a reload key, non-listing TMDb paths, and anything without explicit media type
- The installer reports skipped counts and never invents support for a source; those rows keep working unchanged

## Safety
- No network login, credentials, Trakt writing, or automatic modifications from add-on installation
- Before changing any file, captures a verified byte-exact copy of every affected JSON in the user's local Kodi profile, with SHA-256 manifest under `special://profile/addon_data/script.tvstreaming.bulksetup/backups/`
- Per-file atomic replacement. On failure it rolls back already-applied changes. **Restore latest automatic backup** is offered, but safely refuses if later edits conflict
- Refreshes SkinVariables cached properties and reload token. Fully quit and restart Kodi after an apply or restore
- No auto-updates of RC components; existing source packages and widgets remain available

## Xbox acceptance
1. Confirm the preview count includes Movies and TV rows and that provider rows with supported TMDb Helper paths are eligible
2. Apply once (after backup confirmation) and fully restart Kodi
3. Movies > Recently Released: focus See All, verify first-film hero preview; open wall; browse and Back
4. TV Shows > Trending: See All opens TV title wall; close and return; select TV title to browse episodes
5. Provider and Documentary rows: filters remain correct (no cross-provider leakage); return navigation works
6. Continue Watching / Next Up: unchanged position, entries and Trakt behaviour
7. If any row fails, launch Bulk Widgets Setup > Restore latest automatic backup, then restart Kodi

**Status:** local syntax, JSON round-trip, source token and backup/rollback tests passed; Xbox multi-category test remains required before declaring full production.
