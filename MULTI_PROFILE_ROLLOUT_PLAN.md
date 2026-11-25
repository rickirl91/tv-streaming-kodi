# TV Streaming — Multi-profile rollout and child controls (agreed design)

Status: **design approved; not implemented**. This document stores the reusable technical requirements, intentionally using generic person identifiers because the repository may be public. Profile names and children's private viewing histories must stay local to Kodi, Trakt, and any private project notes; do not publish credentials, children's names, histories, or ratings overrides here.

## Implementation sequence
1. Complete and accept **Cricky** Family master Home. Final test of Home Personalisation 0.1.1 RC (neutral See All tile; optional duplicate-row cleanup); check Family Trakt selection, progression, See All pagination, profile recovery/backup.
2. Produce a stable, portable, profile-aware baseline from the accepted master.
3. Clone for two **adult personal profiles**, then **Guest**, then two **children's profiles**, checking per-profile isolation.
4. Maintain common add-on code and version-controlled configuration, with private per-profile credentials, content decisions and history stored separately; updates must not overwrite profile-specific state.

## Profile layout contract
| Profile role | Trakt | Home and navigation |
| --- | --- | --- |
| Family master (Cricky) | Existing shared Family Trakt | Full catalog, Continue Watching and mixed personalised feeds; source of template |
| Adult A | New personal Trakt | Copy baseline; own progress, watchlist, recommendations and service sync |
| Adult B | Separate personal Trakt | Copy baseline; own progress, watchlist, recommendations and service sync |
| Guest | None | Discovery-first Home: trending and popular film/TV, new releases, provider/genre exploration; no personal recommendations or watch-progress assumption |
| Child A | Dedicated separate Trakt if available and appropriate | **One visible Home tab only**; restricted movie/TV categories, Continue Watching, approved favourites, personalised recommendations only after child policy filtering |
| Child B | Initially small parent-curated catalogue | **One visible Home tab only**, expandable from parent-curated infant content into age-appropriate categories over time |

For the two adults, match Cricky's working UI, artwork, Lazy Wall/See All, source selection, navigation and playback; only profile-specific Trakt data, customisations and allowed feeds differ. Never cross-wire the account used by TMDb Helper Sync with another user's watch activity; verify each integration and scrobble target rather than assuming one Trakt login controls every add-on.

## Child Home principles
- Single Home navigation tab, with all permitted browsing organized into horizontal sections and optional See All filtered poster walls.
- Suggested Child A section order: Continue Watching; Favourites; Recommended For You; Because You Watched; parent-approved Watchlist; Cartoons; Movies; age-appropriate provider collections; Learning & Educational; Discover Something New. Adjust for age and actual interests.
- Child B begins with a small parent-curated selection; no unrestricted discovery or autoplay. Add categories only as parents approve.
- Preference signal for Child A: examine available Netflix, Disney+ and YouTube viewing histories where permitted, identify liked shows, themes and characters, optionally rebuild matching film/TV history in a dedicated child Trakt account. YouTube videos do not directly imply Trakt items. No raw children's browsing history or credentials in the public repo.
- Trakt is a preference signal only, never the safety authority.

## Parent controls and allow/deny policy
- Each child has independent age stage, **whitelist**, **blacklist**, favourites and recommendations; the policy is parent-controlled.
- Decision precedence: **explicit blacklist always denies; else explicit whitelist may allow out-of-age content after parent review; else age-appropriate permitted content; else denied.** Missing/ambiguous content rating is denied until approved.
- Support rules for an individual film, whole TV series, and optionally specific seasons/episodes; define precedence clearly (e.g., blocked episode within an allowed series remains blocked).
- Use stable provider title IDs and media types rather than name matching alone. Include reason, parent approval and change history locally. Never auto-remove blacklists because a child gets older.
- Apply policy to Home feeds, suggestions, Continue Watching, favourites, watchlist, search, See All, detail views, direct URLs and every permitted playback entrypoint, not only cosmetic widget filtering.
- Hidden tabs by themselves are not effective access control. Restrict Kodi settings, Add-ons, unrestricted search, shortcuts, input/URL routes and profile switching with a parent-access mechanism; test bypass attempts before asserting protections.
- Introduce parent **PIN-protected Search** in child profiles: child cannot invoke it; parents enter PIN to search any title, then can preview/play under supervision, whitelist or blacklist. Relock when closing, timing out or switching profiles. Parent PIN must not be embedded in public files or logs.
- The parental safety model should be designed as defense-in-depth and evaluated against Kodi's actual add-on boundaries; do not represent unsupported Kodi profile locks as airtight.
- Age eligibility and Home sections should be configurable and grow with each child without destroying favourites/history. No automatic unlock of disallowed content on birthdays.

## Rollout acceptance and rollback
- Preserve current profile data, bookmark/progress, skin configuration and source settings using verified byte-exact backups with conflict-safe restore.
- Test one profile at a time; test actual Kodi profile switching, TMDb Helper's selected account, Kodi/Trakt scrobbling, watched indicators and source isolation.
- Confirm children cannot reach blocked titles via alternatives (genre/provider rows, search via contextual actions, native add-ons, recommendations, direct playback).
- A family-safe master template does not mean credentials or watch histories are duplicated.
- **No implementation/deployment of these additional profiles has occurred yet.**

## Immediate Xbox checkpoint

Cricky's duplicate-row cleanup was confirmed working. Install **StreamRow v0.3.1 RC** and **Home Personalisation v0.1.4 RC** in Cricky to test **category-only hero headings on all See All tiles** across Home, Movies, TV Shows, streaming providers, genres and documentaries. Fully restart Kodi. No original Apply Home or legacy Bulk Setup run is needed. Then verify See All pagination/return, Family Trakt sync and final profile backup. The universal hero change remains **Xbox acceptance pending**. See `TV_STREAMING_RC_044_UNIVERSAL_HERO.md`.


## Adult B (Christine) — Reality TV main hub (approved, pending profile build)

Christine enjoys reality television. Clone the finished Cricky adult foundation, connect **only her personal Trakt account** across TMDb Helper sync and watched-progress integrations, and replace the **top-level Documentaries navigation tab/hub with Reality TV** on Christine's profile only. This is a main navigation destination, **not merely an extra Home widget**. Retain the full adult viewing experience and working streaming providers/Movies/TV Shows hubs. Do **not** change Cricky, Ricky, Guest or children's navigation.

- **Top-level change:** `Documentaries` → `Reality TV` in Christine's adult tab/navigation lineup. This changes the hub entry and its content configuration, not the underlying shared add-on code or any existing catalogue data. Documentary titles can remain discoverable via normal Movies/TV search and suitable other genres; do not delete or globally block documentaries.
- **Dedicated Reality TV hub:** organize horizontal categories within the hub, such as **Trending Reality TV**, **Popular Reality Shows**, **New & Returning Reality Series**, **Dating & Relationships**, **Competition & Talent**, **Lifestyle & Makeovers**, and optionally **Reality Documentaries** or Ireland/UK reality categories if live catalogue sources support them. Apply useful deduplication and preserve serial episode routing.
- **Home:** keep the approved personalised order (**Continue Watching**, **Recommended For You**, **Because You Watched**, **From Your Watchlist**). A small **Reality TV** Home discovery row can be added near the top of the general discovery rows, linking to the full Reality TV hub; its existence should not substitute for the top-level tab.
- Use the same accepted neutral See All artwork, narrow Poster-style tiles, category-only hero headings on See All focus, full-wall/scrolling navigation and title-specific metadata when a real programme is selected.
- Use Christine's own Trakt history to shape her personal recommendations. The Reality TV hub must be usable for discovery even before substantial personal viewing history exists.
- Keep changes profile-scoped and reversible, with an original-documentaries-navigation backup and no cross-account Trakt scrobbling.
- **Design approved; no implementation or Xbox deployment yet.** Confirm working genre/provider feeds and catalogue coverage during Christine profile build.


## Playback continuity and next-episode automation — Cricky acceptance gate (research, not deployed)

The current Cricky playback path is **Arctic Fuse 3 → TMDb Helper → TMDb Movies**, with TMDb Movies selected as the automatic movie/episode player and source selection configured for a Windows 1080p profile. TMDb Helper is authenticated to the shared Family Trakt account. The custom StreamRow and Lazy Wall do not manage resume positions.

**Two independently required acceptance tests before cloning profiles:**

1. **Episode progression:** complete an episode through the configured player; it should be marked watched on the correct Trakt account and Up Next Episodes should advance to the next unwatched episode. Personal profiles must never scrobble to Family or each other.
2. **Exact timestamp resume:** stop a movie and a TV episode after several minutes using the Kodi Stop control; relaunch each and verify local resume, then repeat after fully quitting Kodi. Cross-device resume from Trakt is an additional test, not assumed to work.

**Add-on candidates — none installed automatically:**

- **TMDb Movies built-in AutoPlay Next Episode:** first option, because this is the existing playback add-on. Confirm the option actually applies when TMDb Helper launches TMDb Movies as its player; the add-on developer says the function is internal to TMDb Movies. Avoid a second auto-next service if it duplicates behaviour.
- **Official Kodi Up Next `service.upnext`:** good fallback for a Netflix-style next-episode countdown. Its upstream release **1.4.1 (24 Nov 2026)** follows **1.4.0 (15 Nov 2026)**, which explicitly fixed auto-next after an add-on launches playback using `Player.Open`, including TMDb Helper. Requires usable episode metadata / an integration to identify and open the next episode. Enable at most one competing auto-next controller.
- **Official Kodi Playback Resumer `script.service.playbackresumer`:** optional crash-resilience improvement, periodically saves Kodi's local resume points. Does **not** by itself guarantee reliable resume for plugin-provided streams with changing URLs, or cross-device Trakt playback-position synchronisation.
- **Trakt:** history and watched episode progression are distinct from reliable minute-accurate playback resume. Avoid simultaneously enabling multiple scrobblers to write the same state without a verified reason.

**Not guaranteed:** No add-on guarantees exact resume for every streaming source, nor automatic next episode from every title. Kodi local resume, the actual player add-on, Trakt metadata/scrobbling and any Up Next service need to work together. Do not replace the confirmed playback configuration or install extra services until an inspection or controlled Xbox test is available.

Sources: https://kodi.tv/addons/omega/script.service.playbackresumer/ , https://kodi.tv/addons/omega/service.upnext/ , https://github.com/im85288/service.upnext , https://kodi.tv/addons/omega/script.trakt/ .


## Cricky documentary redesign and heading correction — approved 25 November 2026

Xbox visual acceptance: category-only See All headings work in the user's tested sections except the long Hidden Gems (Highly Rated, Less Popular) heading is clipped. Rename both row and hero to Hidden Gems while preserving its source filters. Audit other long labels. Documentary Series and Popular Documentary Series show the same leading titles and unsuitable worldwide-language discovery. Inspect actual source URLs before replacing redundant rows.

Approved hub design: Recommended Documentaries for You; Because You Watched; New Documentaries; Trending Documentaries; True Crime; History & War; Sports Documentaries; Science & Technology; Nature & Wildlife; Highly Rated Documentaries. Default to English original language for discovery, retain search access to other languages. Use authenticated profile-specific Family Trakt history and ratings, weighting recent watches and highly rated titles; exclude already watched titles from recommendation discovery where supported. Do not guess tastes, embed credentials, or claim generic popularity is personalised. Use stable distinct feeds, deduplicate redundant rows, preserve movie/series routing, See All and pagination. Prefer adaptive topic order only after actual history is available. Preserve existing configuration with reversible migration and no unrelated profile changes. No installer or implementation yet; inspect source and test on Xbox before release acceptance.


## Continue Watching removal — approved Xbox follow-up

Iron Man appeared automatically in Continue Watching, offered Resume from 48m 36s, and resumed correctly. D-pad seeking works better than thumbstick. TMDb Helper Sync options > Reset resume position (Trakt) did not remove Iron Man from Continue Watching. Determine actual configured widget source and whether local resume, remote progress or cache supplies it before implementing. Add a direct Remove from Continue Watching context action, scoped to current profile and selected title/episode; preserve watched history, ratings and watchlist. Clear only relevant unfinished progress, refresh widget, verify persistence after restart and reappearance after new playback. Do not assume Trakt reset alone works; do not modify upstream add-ons blindly. Movie resume verified; episode resume and restart persistence pending. Implementation and Xbox acceptance pending.


## Xbox next-episode acceptance follow-up — 25 November 2026

User confirmed TV episode timestamp resume works. TMDb Movies settings show Auto-Play Next Episode, Show Skip Intro dialog and TMDb UP NEXT enabled. After Kaleidoscope episode ended including full credits, next-episode dialog correctly identified S01E05 Orange with Auto-Play, Not Now and Choose Source and ~60-second closing countdown. User confirmed timeout closed dialog and returned Home without starting next episode. True unattended autoplay therefore fails current acceptance test. Desired experience: nonintrusive Next Episode action visible 60–120 seconds before playback end (initial proposal 120 seconds), manual selection immediately loads next episode, no premature automatic skipping of actual story, automatic next episode on natural completion/countdown unless cancelled. Inspect existing settings and official Up Next compatibility with TMDb Helper/player routing before changing; test one controller at a time, no duplicate prompts, preserve correct Trakt watched state and resume. No new add-on installed or implementation yet. Playback Resumer unnecessary for normal resume based on current tests; restart persistence remains unverified.


## Custom next episode diagnostic gate
Kodi 22 RC2; Up Next 1.3.7 failed to show prompt; 1.4.1 installer unverified. Restore existing TMDb Movies prompt and disable Up Next. First test read-only episode metadata and player routing on Xbox. Never log stream URLs or credentials. Only implement autoplay after stable episode identity and next episode routing are verified. Target 60–120 second manual next button, natural-end autoplay, cancel, still-watching after three episodes, no advance on stop/error, profile isolation and watched sync.
