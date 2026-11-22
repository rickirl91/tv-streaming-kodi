# StreamRow v0.2.4 RC — grayscale artwork cache-bust

## Xbox observation
Despite installing the prior release, the first See All tile still appeared blue with a light blue icon. Miami's pink selection border was correctly shown. The old art filename (`resources/media/see_all.png`) stayed fixed across versions and may be cached by Kodi; a difference between the older locally produced and GitHub-hosted v0.2.3 ZIP also prevents attributing it to caching alone.

## Change
- Package the locally verified grayscale **Inter Bold** artwork, no blue or purple RGB pixels, as `resources/media/see_all_miami_neutral_v024.png`.
- Change only StreamRow's artwork reference to that exact new filename.
- Increase add-on version from 0.2.3 to 0.2.4.
- Keep the working See All non-folder click callback and `RunAddon(script.tvstreaming.lazywall,...)` handoff **byte-for-byte identical** apart from the one artwork path.
- Keep the previously verified Lazy Wall (v0.2.1 RC), playback, Trakt, Kodi profile settings and Cricky homepage unchanged.

## Focused Xbox check
1. Kodi > Settings > Add-ons > Install from zip file > rickirl91 > **plugin.video.streamrow-0.2.4-RC.zip**.
2. Video add-ons > TV Streaming StreamRow > Action — See All First.
3. First tile should have a **neutral charcoal background, white icon and white SEE ALL lettering** with **Miami pink focus border**.
4. Press A and confirm Lazy Wall opens. Then Back returns to the row.
5. If still blue, check installed StreamRow version is 0.2.4 and fully restart Kodi to discard stale plugin directory views. Do not clear the entire Kodi thumbnail cache unless absolutely necessary.

## Verification and rollback
This is a targeted visual-only change. Local checks: Python parses, add-on XML parses, ZIP integrity clean; all pixels in packed artwork are grayscale; only the art file path differs from the working v0.2.3 local source code. ZIP SHA-256: `9e3870582bd9b79efc477bec040a205dc64c6d264211f40292d93e3e3ebdf600`. The earlier v0.2.2 (working launcher) and v0.2.3 (previous style) ZIPs remain in the GitHub source. This new package is not added to automatic repository updates until Xbox acceptance.
