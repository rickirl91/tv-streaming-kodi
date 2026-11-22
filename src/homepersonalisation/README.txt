Cricky Home Personalisation — v0.1.0 RC
======================================

INSTALLING THE ZIP DOES NOT CHANGE KODI.

Open Add-ons > Video Add-ons > TV Streaming - Cricky Home Personalisation.

1. Inspect current Home (read only)
2. Preview planned Home order (read only)
3. Test six Family Trakt sources (read only)
4. Apply personalisation (preview and one confirmation)
5. Restore latest backup (conflict checked)

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
