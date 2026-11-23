Cricky Home Personalisation — v0.1.1 RC
======================================

INSTALLING THE ZIP DOES NOT CHANGE KODI.

Open Add-ons > Video Add-ons > TV Streaming - Cricky Home Personalisation.

1. Inspect current Home (read only)
2. Preview planned Home order (read only)
3. Test six Family Trakt sources (read only)
4. Apply personalisation (preview and one confirmation)
5. Preview which older overlapping Home rows to remove (read only)
6. Remove older overlapping Home rows (one confirmation)
7. Restore latest backup (conflict checked)

Requirement: actively logged in to Kodi profile "Cricky" using Arctic Fuse 3.
TMDb Helper must be enabled and its History/Watchlist sync providers must
reference the shared Family Trakt account. This add-on cannot verify the
account's human-readable identity and never accesses or uploads tokens.

The three new rows mix live movie and TV results from TMDb Helper's separate
endpoints, preserving individual callback paths. More results are accessible
via the feed's Next Page folder (where supplied by the upstream source).
A lightweight See All-first tile opens Kodi's native listing for the mixed feed;
it is not yet the custom Lazy Wall and its exact Xbox styling is unverified.

Apply writes ONLY the Home widget JSON under the active profile's
script.skinvariables/nodes/skin.arctic.fuse.3 directory. Other profiles,
non-Home hubs and the source add-ons are untouched.

A byte-exact Home backup and SHA-256 manifest are saved locally, inside
special://profile/addon_data/plugin.video.tvstreaming.homepersonalisation/backups/.
Restoration refuses to overwrite any newer manual edits.

Completely quit/restart Kodi after Apply or Restore. If the Home rows do not
visually update, regenerate widgets in Arctic Fuse 3 shortcut customisation.

RELEASE STATUS: offline logic/backup tests passed; live Xbox feed performance,
artwork, widget navigation and Trakt provider identity remain to verify.

0.1.1 RC:
- Reuse the installed StreamRow neutral Miami SEE ALL tile instead of assigning
  the first recommendation's show/film poster to the launcher. Keep the first
  item's hero backdrop. If StreamRow artwork cannot be found, use a neutral
  skin folder icon, never a film/TV poster.
- Optional separate cleanup of 4 old overlapping Home sections, with exact
  labels, detailed preview, explicit confirmation and independent backup.
- Does not delete Up Next Episodes, existing unrelated rows or Trakt data.
- Installing this update alone DOES NOT modify Home widgets. Run menu action 6
  only after viewing the preview in action 5.

0.1.2 RC: Fix AF3 horizontal See All tile using title fanart despite 0.1.1 poster correction.
Set neutral Miami art as explicit landscape and override_landscape; preserve title fanart for Home hero.
This release does not change Home widget files, Trakt endpoints, navigation, playback, or cleanup logic.
Fully restart Kodi after installing, and check three new Home See All tiles.

v0.1.3 RC: Arctic Fuse 3 uses each Home widget's widget_style to choose the
row layout. The three personalised Home rows lacked widget_style and defaulted
to wider Landscape cards. Their correct matching style is widget_style=Poster.
New actions 8 Preview Poster tile style and 9 Apply Poster tile style update
ONLY those three rows with a separate one-confirmation, verified byte-exact
backup and conflict-safe restore. No change from installing the add-on alone.
Do NOT use Apply Home Personalisation or rerun Bulk Setup for this update.
After applying the poster style, fully quit/restart Kodi. Existing neutral
See All art (0.1.2), the large hero backdrop and playback are retained.
