# TV Streaming Lazy Wall — v0.1.3 (Xbox experiment)

**Bug reproduced in v0.1.2:** Scrolling to the bottom and pressing Down while new TMDb Helper entries arrive jumps focus back to the beginning of the list.

## Changes in v0.1.3
- Remove the custom panel's self-referencing `<ondown>100</ondown>` navigation, which can wrap focus to the first item when at the end.
- Before appending a new batch, save the current absolute selected item index. Restore that index after appending and re-assert panel focus.
- Keep existing automatic next-batch retrieval, movie posters, Miami focus colour and 160-item experimental cap.

## Install
Kodi → Settings → Add-ons → Install from zip file → **rickirl91** → **script.tvstreaming.lazywall-0.1.3.zip**. Launch Program add-ons → TV Streaming Lazy Wall (EXPERIMENT).

Test pressing Down repeatedly at the last poster while the next batch loads. It should remain near the same scroll position and continue into the next batch, rather than jumping to the beginning.

This change has been source-validated and packaged but has **not yet passed an Xbox navigation test**. No edits to StreamRow, Cricky homepage, TMDb Helper, playback or profiles.

SHA-256: `831595e2f8ece69efbfe2062742205616f42b3d8ff9d7778d1b9cf7d524f6914`.

Prior v0.1.0–v0.1.2 releases remain for rollback.
