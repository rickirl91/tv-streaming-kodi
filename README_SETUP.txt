TV STREAMING — KODI REPOSITORY PUBLISHING KIT v0.1.0

NOT YET PUBLISHED. Your public Kodi source URL will only work AFTER creating the repository, uploading these files and enabling GitHub Pages.

GitHub username: rickirl91
Recommended GitHub repository name: tv-streaming-kodi
Expected Kodi source (AFTER publishing): https://rickirl91.github.io/tv-streaming-kodi/

PUBLIC REPOSITORY SETUP
1. In your GitHub account, create a new PUBLIC repository named tv-streaming-kodi, using 'main' as the default branch.
2. Download and EXTRACT the publishing-kit ZIP.
3. Upload all extracted CONTENTS (not the outer directory and not the ZIP itself) into the root of the GitHub repository.
   This includes the hidden .nojekyll file, addons.xml, addons.xml.md5, index.html, the repository ZIP, and the zips/ directory with nested add-on ZIPs.
   You can use GitHub Desktop to clone, copy the files, Commit, and Push if browser upload of folders is awkward.
4. On GitHub: repository Settings → Pages → Build and deployment → Deploy from a branch → main / (root) → Save.
5. Once Pages says the site is live, open https://rickirl91.github.io/tv-streaming-kodi/ in Safari. It should show a link to repository.tvstreaming.catalogue-1.0.0.zip.
6. Only then, on Xbox Kodi: Settings → File manager → Add source → https://rickirl91.github.io/tv-streaming-kodi/; name it TV Streaming.
7. Kodi Add-ons → Install from zip file → TV Streaming → repository.tvstreaming.catalogue-1.0.0.zip. You may be asked to enable Unknown Sources to proceed.
8. Kodi Add-ons → Install from repository → TV Streaming Repository → Video add-ons → TV Streaming Catalogue & Preset.
9. In the Standard profile, open the add-on, back up and apply the preset; Kids remains separate.

WARNING: this is an OFFLINE VALIDATED PREVIEW RELEASE. NOT YET XBOX TESTED.
Do not overwrite your existing Kodi installation or install in Kids profile.
If your GitHub username or repository name differs, the repository add-on's URLs must be rebuilt before publishing.

UPDATE PROCESS
For later releases, upload the new add-on ZIP under zips/plugin.video.tvstreaming.catalogue/ and update addons.xml plus addons.xml.md5 accordingly.
Kodi can then discover a newer add-on package through the installed repository. Applying its navigation preset is still an explicit user action.
