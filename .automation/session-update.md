# Track Almanac: after-session update

Instructions for the scheduled run that fires ~10 minutes after each F1 session. The run's prompt names the target round and session.

## The setup
- **Master copy:** claude.ai artifact https://claude.ai/artifact/T8jvvRzGei1kTSk42oJcxS. The owner designs it in another chat. Always start from its latest version and never change design, layout, branding or features. Only change data.
- **Live site:** `index.html` in GitHub repo `Paradox-Hub12/trackalmanac` (branch `main`), served by GitHub Pages at https://trackalmanac.com. The repo also holds CNAME, README.md, .nojekyll, robots.txt, sitemap.xml, site.webmanifest, og-image.png and the favicon/icon files. Leave those alone, except for the sitemap date in step 7.

## Steps
1. **Read the master.** Use the Artifact tool: `read` with only the url (this registers the version you will publish onto), then `read` with the url and path `index.html` to save the full page locally. Work on that copy.
2. **Know the data.** In the page `<script>`:
   - `SCHED` holds session names, UTC start times and durations per round.
   - `SEASON["<round>"]` holds session tables. The keys are `fp1`, `fp2`, `fp3`, `sq` (sprint qualifying), `sprint`, `quali` and `race`, plus `tyres`, `wx`/`wxnote` and anything else earlier rounds have.
   - `RACES` holds rounds. A completed round has a `res` object.
   - `DRIVERS` and `CONSTRUCTORS` hold championship points.
   Before writing anything, study the most recent round (and the most recent sprint round, for sprint sessions) and match their format exactly.
3. **Wait for results.** Check whether the target session's official classification is published, using formula1.com first, then FIA documents, then reputable outlets. If it isn't out yet (the session may have been delayed or red-flagged), run `sleep 540` and check again, up to 5 times. If it's still not out, change nothing and finish with a one-line message saying so.
4. **Add the session.** Fill that session's table in `SEASON[round]`. Also add any other session of this round or the previous round that has finished but is still missing.
   - **Sprint:** also update `DRIVERS` and `CONSTRUCTORS` with the sprint points.
   - **Grand Prix:**
     - Add the round's `res` object (time, podium, pole, fastest lap, fastest pit stop and the `cls` note) in the same shape as earlier rounds.
     - Fill `SEASON[round].race`, plus `tyres` and weather if earlier rounds have them.
     - Set `DRIVERS` and `CONSTRUCTORS` to the championship totals after the race, re-sorted by points. Cross-check the sums.
     - Race results this soon are provisional. Mention that in the `cls` note only if a stewards' investigation is still open.
     - If round 23 (Abu Dhabi) is complete, also add a 2026 entry to `ARCHIVE` in the same format as other years.
   - Use only facts verified from sources. Where a detail can't be confirmed, use the same "not available" form earlier rounds use.
5. **Check the script parses.** Extract the script and run `node --check` on it.
6. **Publish the master.** Republish the master artifact to the same url (Artifact `publish`, with `url` set and `file_path` pointing to your copy). If the publish is refused because the owner changed the page in the meantime, merge your data changes into the version the refusal returns, then publish again. Never discard the owner's design changes.
7. **Sync the live site.**
   1. Attach the repo (`add_repo` with owner `Paradox-Hub12`, repo `trackalmanac`, access `push`) and clone it once (`git clone --depth 1`, generous timeout).
   2. Build `index.html` from the master page. The master's first line is a platform wrapper, and its second line is the `<title>` line; drop both.
   3. Keep the repo's current `<head>` opening block exactly as it is. That is everything in the repo's `index.html` before its `<style>html,body` line: title, canonical link, icons, manifest, Open Graph and Twitter tags.
   4. Assemble the file in this order:
      - that kept block
      - `<style>html,body{margin:0;padding:0}[hidden]{display:none!important}img{max-width:100%}</style>`
      - the master content up to `<div class="page">`
      - `</head>`, a newline, `<body>`, a newline
      - the rest of the master content
   5. Make sure `<head>` contains no `<title>`, `<link rel="icon"…>` or `<meta name="description"…>` lines other than the kept block's. Delete any that came in from the master.
   6. Run `node --check` again.
   7. If `index.html` changed, set `<lastmod>` in `sitemap.xml` to today's date. Commit with author `Paradox-Hub12 <Paradox-Hub12@users.noreply.github.com>` and message `R<round> <short name>: <session> results`, then push to `main`.
8. **Report.** Finish with one or two lines via SendUserMessage. For example: "Singapore Sprint added: Antonelli won; Russell P2. Standings updated." or "Singapore Practice 1 added." If a publish, push or lookup failed, say so plainly.
