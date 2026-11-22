# TV Streaming StreamRow v0.2.2 RC — Xbox See All launcher acceptance

## Scope
A targeted fix for the reported **See All button does nothing** when selected under Video add-ons > TV Streaming StreamRow > Action — See All First. The matte details dialog and neutral See All artwork in v0.2.1 are confirmed visible on Xbox; the new wall launch from the first tile is not yet proven.

## Diagnosis and change
Earlier versions marked the See All tile as `isFolder=True` and then called `endOfDirectory(succeeded=False)` while asynchronously invoking a separate script window. Kodi's action-item guidance indicates that a non-playable callback item should not be represented as a folder. v0.2.2 sets `IsPlayable=false`, `isFolder=False`, hands off with `RunAddon(script.tvstreaming.lazywall,category=...)`, and ends the plugin response successfully. A **context-menu fallback** opens the same Lazy Wall directly. The installed Lazy Wall v0.2.1 is unchanged.

## Focused Xbox test
1. **Settings > Add-ons > Install from zip file > rickirl91 > plugin.video.streamrow-0.2.2-RC.zip**. No need to reinstall the Lazy Wall v0.2.1 RC.
2. Video add-ons > **TV Streaming StreamRow > Action — See All First**. Highlight the first See All poster and press **A** once.
3. **Expected:** Lazy Wall Action Movies poster grid opens, then pressing Back returns to the row. It must not start a movie or navigate to a broken/empty Kodi directory.
4. If pressing A still does nothing, use the **menu/context button** on See All and choose **Open Full Wall (direct)**. Report whether that opens the wall; this isolates skin click handling from script availability.
5. Only if A works, test a second category (**Comedy — See All First**) to verify category selection.
6. No change to Cricky homepage widgets, playback source selection, profiles, Trakt or Kodi repository automatic-update metadata.

## Status
ZIP and source passed local syntax/structure tests and all 12 category dispatch tests. Launch behavior requires physical Xbox confirmation before promoting this version to the homepage.

Known verified fallback: Lazy Wall v0.1.4 for its 160-poster scrolling test; RC v0.2.1 details visual layout.
