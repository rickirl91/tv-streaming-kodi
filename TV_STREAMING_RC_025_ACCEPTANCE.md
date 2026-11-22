# TV Streaming StreamRow v0.2.5 RC — first-title preview for See All

## Observation from Xbox video
In the Action Movies row, selecting a movie such as The Odyssey shows a rich hero panel (movie title, synopsis, poster/backdrop). Focusing the first See All tile instead shows a nearly empty preview with a generic purple-blue gradient. The row was already installed as a Cricky homepage widget, and See All launches Lazy Wall successfully.

## Targeted change
- The first **valid title** returned by TMDb Helper for the widget category becomes the **preview donor** for the See All item.
- Supply its title, plot, year, rating and available backdrop via the See All Kodi ListItem metadata and artwork; the poster remains the custom **charcoal SEE ALL** tile (Inter Bold).
- Keep **label='See All'**, the exact working **mode=launch** URL, `IsPlayable=false`, context-menu direct launch, existing 30-item widget size and all Kodi playback/Trakt settings unchanged.
- Do not copy any playable URLs, media IDs or watched status from the preview donor.
- If the first title has no backdrop, don't invent one. If TMDb Helper fails, still render the See All launcher with the original generic text.
- All 12 StreamRow categories share this behaviour; no new remote requests beyond the existing TMDb Helper catalogue fetch.
- Fix the add-on manifest's icon path to the existing packaged charcoal art.

## Xbox acceptance test
1. Kodi > Settings > Add-ons > Install from zip file > **rickirl91** > **plugin.video.streamrow-0.2.5-RC.zip**.
2. On the existing Cricky homepage: highlight the **See All** tile at the beginning of the Action widget.
3. **Expected:** the background and hero preview reflect the first movie in that row, while the poster remains the charcoal **See All** tile.
4. Press **A**: the working Lazy Wall Action Movies grid must still open. Press Back: return to the same homepage widget.
5. Move to a regular movie: its own synopsis/background should replace the borrowed preview normally.
6. If the skin shows the wrong title, omits the backdrop or opens a film rather than Lazy Wall, roll back StreamRow to **v0.2.4 RC**; do not modify Lazy Wall.

## Status
Tested locally with mocked Kodi APIs: first-item metadata and fanart, launcher semantics, TMDb error fallback, and all 12 categories. Kodi/Arctic Fuse rendering itself remains to be verified on Xbox. This is an opt-in RC; no Kodi repository automatic-update metadata or homepage layout is changed.

SHA-256: `13869153f00a35fba724e93a894fd5ff02e36868a9a9e193ba44dc9b5c501e9a`.
