# Ride Northern Thailand

An 8-day adventure motorcycle tour of the Mae Hong Son Loop, from Chiang Mai.

**Site:** https://andrewsouth.github.io/thailand-moto-loop/

| Page | What |
|---|---|
| `index.html` | The tour: photos, the relief map, the day-by-day route, and the stops |
| `plan.html` | Riding times, roads, fuel, lodging, and the budget calculator |
| `links.html` | Each day in Google Maps, the stops, bike rentals, paperwork, and guides |

## Editing

Edit the pages in `src/`, then run `python3 build.py` to rebuild the three pages in this folder, and commit. GitHub Pages publishes from the `main` branch within a minute or two.

- **Add a link:** copy an `<li>` line in `src/links.html`.
- **Add a page:** create it in `src/` (start from `src/links.html`), then add it to `PAGES` in `build.py` so it appears in the top bar.
- **Swap a photo:** replace the JPEG in `images/` with the same name, and update its entry in `images/credits.json`.
- **Change the map:** see `map/` (`route.py` for roads, `tiles.py` for the relief, `build_map.py` for labels), then rebuild.

Photos are from Wikimedia Commons under CC BY and CC BY-SA (credited on the tour page). Map relief by Esri and USGS; roads and border © OpenStreetMap contributors.
