# Track Almanac

Formula 1 results, standings & history — an unofficial fan site.

- **Live site:** https://trackalmanac.com
- **What's on it:** 2026 race calendar with next-race countdown, drivers' and constructors' standings, race-by-race results with circuit maps, and a past-seasons archive.
- **How it updates:** results are added to the data in `src/master.html`, then `python3 build.py` regenerates the site and the change is pushed here. GitHub Pages republishes automatically.

## How the site is built

- `src/master.html` is the single source: design, app script and all data (`SCHED`, `SEASON`, `RACES`, `DRIVERS`, `CONSTRUCTORS`, `ARCHIVE`, …).
- `build.py` (plain Python 3, no npm or packages) turns it into the static site:
  - one folder + `index.html` per page (`/`, `/championship/`, `/drivers/`, `/teams/`, `/calendar/`, `/races/2026/<slug>/`, `/archive/<year>/`, `/about/` …) and `404.html`, each with its own title, description, canonical, Open Graph tags, JSON-LD and prerendered HTML content
  - shared, cached `style.css`, `app.js` and `data.js`, and images extracted to `img/`
  - `sitemap.xml` with a per-page `lastmod` (tracked in `.automation/build-state.json`)
- Run `python3 build.py` after any change to `src/master.html`, then commit everything. `python3 build.py --check` builds into a temp folder and only reports.
- Don't edit generated files by hand; they are overwritten on every build. CNAME, .nojekyll, robots.txt, icons, og-image.png, site.webmanifest and `.automation/` are never touched by the build.

Track Almanac is not associated with the Formula 1 companies. F1, Formula 1 and related marks are trademarks of Formula One Licensing B.V.
