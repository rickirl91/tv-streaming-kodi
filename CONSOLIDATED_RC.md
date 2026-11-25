# Cricky consolidated Xbox release candidate

Target test setup is Xbox Series S, Kodi 22.0 RC2 (21.90.902), Arctic Fuse 3 3.5.11, TMDb Helper 6.22.7 or later, and the existing TMDb Movies and family Trakt setup. Fire TV Stick acceptance is deferred.

## Install and configure in one session

1. Stop playback and switch to **Cricky**. In **Settings → Add-ons → My add-ons → Services → Up Next**, disable the official Up Next add-on if installed.
2. In **TMDb Movies → Settings**, turn off **Auto-Play Next Episode** and **TMDb UP NEXT**. Keep the automatic source, resume and Trakt settings used by the family. In **TMDb Helper → Settings → Players**, confirm **Episode player** is the existing TMDb Movies *Play* player. Under **Configure players**, select that player and disable its **Make playlist** option if enabled. For initial testing use **Default** in TMDb Helper's episode-group setting. Leave other players as configured.
3. In **Settings → Add-ons → Install from zip file → rickirl91**, install these three files in order. The source URL is `https://rickirl91.github.io/tv-streaming-kodi/`.
   - `plugin.video.streamrow-0.3.2-RC.zip`
   - `plugin.video.tvstreaming.homepersonalisation-0.1.5-RC.zip`
   - `service.tvstreaming.nextepisode-0.2.0-RC.zip`
4. Open **TV Streaming - Cricky Home Personalisation (RC)** from Video add-ons. Run **Rename Hidden Gems**, review the file and label in the preview, then confirm. This finds the saved AF3 widget file in the active profile. If the exact row is absent, uses another source, or appears in more than one hub file, inspect the row in AF3's widget editor before making any changes.
5. Open **Settings → Add-ons → My add-ons → Services → TV Streaming Next Episode → Configure**. Enable **Enable for Cricky (disable other autoplay controllers first)**. Fully quit and reopen Kodi as Cricky. If needed, rebuild widgets in Arctic Fuse 3 settings. Leave the legacy Bulk Setup installer unused.

## Xbox acceptance checklist

- Start a regular released episode through the usual TMDb Helper → TMDb Movies route. Check that automatic source selection, resume and Trakt recognise the same episode. Confirm there is a single Next Episode panel and the show, episode, number and artwork are correct. Check a 30+ minute episode at 2:00 remaining and a shorter episode at 1:00 remaining.
- Use the D-pad, A and B. Check that playback continues underneath the panel, the countdown follows playback, seeking back dismisses it, and playback can be paused and resumed. Confirm **Next Episode** launches once and Trakt keeps the unfinished episode's actual progress.
- Let an episode end after the credits. Confirm autoplay launches the correct episode once. Repeat with a season boundary and verify the next season's first catalogue episode. At a series finale or before an unaired successor, expect no launch.
- Test **Cancel**, a manual stop, a failed stream, a switch to another programme and a profile switch. Expect no automatic successor from the abandoned episode. After three consecutive episodes, test no response, Cancel and Continue Watching in separate runs. Check the 45-second post-end confirmation timeout and one launch after Continue Watching.
- In the hub identified by Preview, confirm **Hidden Gems** appears on the row and See All hero. Check the same artwork, titles, filters and ordering and page beyond the first batch. Spot-check Continue Watching, movie and episode resume, Trakt history, mixed Home rows, provider categories, poster walls, search, trailers and normal movie and TV playback.

## Compatibility and limits

The service uses VideoInfoTag and VideoPlayer labels. An unscoped TMDb identifier is corroborated with IMDb, show title and the exact catalogue episode. The TMDb Helper API module supplies public catalogue data via its existing configuration. Season and episode counts must agree, and unexpected paging, missing records, specials as a starting episode, unaired successors and ambiguous identities suppress the action. Group order requires the `group_tmdb` identifier to survive playback and TMDb Helper to use **Group**. The group, order and counts must verify before virtual episode numbering is passed to the player. An interactive numbering selector suppresses the service.

Manual and automatic playback use TMDb Helper's configured episode player with playlist creation disabled for the request. The service detects official Up Next, Helper playlist configuration and a populated Kodi queue. It relies on the installation settings above to disable TMDb Movies' internal controller. The addon is opt-in and checks the active profile before dispatch. Live Xbox identifier scope, player definition and source routing, AF3 panel render and focus, callback ordering and Trakt behaviour require physical acceptance. The optional `script.tvstreaming.nextviewer-0.1.0-RC.zip` reads the captured diagnostic while testing the enabled service. The service's executable diagnostic also supports inspecting current playback.

## Rollback

1. Disable **TV Streaming Next Episode** before re-enabling a previous autoplay controller. To revert to the read-only service, install `service.tvstreaming.nextepisode-0.1.2-RC.zip` from the archive.
2. While on **Cricky**, run **Restore Hidden Gems widget backup** in Home Personalisation 0.1.5 before downgrading. The restore verifies the backup and refuses to overwrite newer widget edits. Fully restart Kodi after restoring.
3. Install `plugin.video.streamrow-0.3.1-RC.zip` and `plugin.video.tvstreaming.homepersonalisation-0.1.4-RC.zip` from [Archived releases](archive/). If Kodi's source browser omits the archive folder, add `https://rickirl91.github.io/tv-streaming-kodi/archive/` as a temporary file source. If Kodi rejects an older ZIP over a newer version, remove only the corresponding add-on and keep its settings and data before installing the archived ZIP. Restore the original native autoplay settings only if desired, and enable one controller at a time.
