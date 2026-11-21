# thailand-moto-loop

Public GitHub Pages site for a future group motorcycle trip (Mae Hong Son Loop, 8 days from Chiang Mai). Live at https://andrewsouth.github.io/thailand-moto-loop/ (Pages serves `main`, repo root).

- Sources are `src/*.html`; `python3 build.py` writes `index.html`, `plan.html`, and `links.html` to the root. Always rebuild and commit the built pages with the sources.
- Placeholders: `{{nav}}`, `{{photo:name}}` (→ `images/name.jpg`), `{{map}}` (→ `map/map.svg` with `map/basemap.jpg`), `{{credits}}`. The build fails if one is left unfilled.
- Nav order and page list: `PAGES` in `build.py`.
- Map: run the scripts in `map/` from inside that folder. `map/tiles/` is git-ignored (re-download with `tiles.py`).
- python3 on Andrew's Macs has no HTTPS certificates set up; the map and photo scripts fetch through curl.
- **This repo is public.** No rider names, passports, flight details, phone numbers, or bookings. The tour page has no costs (Andrew's rule); costs live only on the plan page.
- Style: AJS (Georgia headings, Arial body, navy). Tour page palette: ink #18263a, gold #a5803c, road #9b3b2e.
- Trip decisions and open questions: `docs/claude-notes/trip-notes.md`.
- Before this repo existed, the trip was built as two Claude artifacts (flyer https://claude.ai/artifact/AjUs1UGkRGAYr7Ac5LsTzP, shared with outside people; planner https://claude.ai/artifact/47uoAV1oFdj8Bgt7ndSFNq). The website is now the main copy.
