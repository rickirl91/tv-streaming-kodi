# TV Streaming — Cricky narrow Poster tile correction (v0.1.3 RC)

**Built 23 November 2026.** Offline tests: 8 passed. Xbox confirmation pending.

## Symptom and proven source

The top three personalised mixed movie/TV rows appeared as **wide Landscape tiles**, while the original Movie/TV catalogue rows below used **narrow Poster tiles**, including their See All buttons. The original personalised row definitions lack the `widget_style` property. In Arctic Fuse 3 upstream `shortcuts/generator/data/setup/widgets_include_row.xml`, `widget_style=Poster` selects `List_Poster_Row`, and a missing/unknown style defaults to `List_Landscape_Row`.

This is independent of the See All asset choice fixed in v0.1.2. The mixed feed itself and media navigation already work.

## New installer

- `plugin.video.tvstreaming.homepersonalisation-0.1.3-RC.zip`, SHA-256 `999bbccbe04147d9f37f48dfbde20fd24ec0366a88da87de30855c429ac78b5f`.
- Same add-on ID; upgrades v0.1.2. Installing alone does not alter Home JSON.
- Future generated mixed Home widgets explicitly set `widget_style=Poster`.
- New menu action **8. Preview standard Poster tile style (read-only)** checks the installed Cricky Home rows and shows exactly which 3 `widget_style` values would change.
- New menu action **9. Apply standard Poster tile style (one confirmation)** only writes `widget_style=Poster` to the three personalised rows and refreshes SkinVariables includes; first verifies the four fixed Home labels and three exact feed URLs. Does not change any other row or other existing attributes.
- The existing SHA-256 byte-exact backup, atomic replacement and conflict-safe restoration are reused. Existing Duplicate Cleanup (5/6), Restore (7) and feed testing actions are retained.

## Xbox acceptance

1. Enter **Cricky** and install `plugin.video.tvstreaming.homepersonalisation-0.1.3-RC.zip` from **Settings → Add-ons → Install from ZIP file → rickirl91**. Check version 0.1.3 in add-on info.
2. Open **TV Streaming - Cricky Home Personalisation**, choose **8. Preview standard Poster tile style**. Ensure it identifies just **Recommended For You**, **Because You Watched**, **From Your Watchlist** and no other rows.
3. Choose **9. Apply standard Poster tile style**, review the preview and confirm once. A byte-exact backup is created.
4. **Fully quit and restart Kodi**. Check that all three personalised sections use the same narrow Poster card dimensions as the standard movie/TV catalogue rows, with See All tile appropriately narrow. Large hero backdrops should remain.
5. Check that selecting a movie and TV series still follows the tested playback/episode path. Do not rerun legacy Bulk Setup or the original Apply Home action.
6. If the result is wrong, before making further Home edits choose **7. Restore latest automatic backup**, then restart Kodi. Do not delete user data or settings.
7. Any remaining old duplicated separate watchlist and recommendation rows can be removed independently via **5 Preview** and **6 Remove**, if not already cleaned up.

**Status:** reasoned from exact Arctic Fuse 3 generator source and existing Home planner; local tests pass, but the resulting visual layout needs Xbox validation.
