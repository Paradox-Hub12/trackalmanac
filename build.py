#!/usr/bin/env python3
"""
Track Almanac site builder.

The GitHub repo is the master copy of the site. Sources:

  src/data.json   all race data (RACES, SCHED, SEASON, LAPS, DRIVERS, CONSTRUCTORS,
                  ARCHIVE, ...). Edited by hand and by scripts/update.py.
  src/media.json  driver portraits and flags (design assets)
  src/app.html    design and app: CSS, page markup and the app script.
                  Its script holds a /*DATA*/ marker where data.js is loaded.

build.py turns them into the static site served by GitHub Pages:

  /index.html, /championship/, /drivers/, /teams/, /calendar/,
  /races/2026/<slug>/, /archive/, /archive/<year>/,
  /about/ /contact/ /privacy/ /terms/ /disclaimer/ /site-map/, /404.html
  /style.css, /data.js, /app.js, /img/*   (shared, cached assets)
  /sitemap.xml                             (every page, per-page <lastmod>)

Every page gets its own title, description, canonical, Open Graph tags,
JSON-LD (WebSite/Organization, SportsEvent, BreadcrumbList) and its main
content as plain HTML before any JavaScript runs. The app (app.js) then takes
over and routes on real paths because each page sets window.TA_PATHS=1.

Data names and formats are unchanged; data.js declares each top-level key of
data.json (and media.json) as a JavaScript const. Pure Python 3, no dependencies.

Usage:  python3 build.py            (reads src/, writes the site)
        python3 build.py --check    (build into a temp dir and report only)
"""
import base64, datetime, hashlib, html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "app.html")
DATA = os.path.join(ROOT, "src", "data.json")
MEDIA = os.path.join(ROOT, "src", "media.json")
WORLD = os.path.join(ROOT, "src", "world.json")
HISTBASE = os.path.join(ROOT, "src", "history.json")
sys.path.insert(0, ROOT)
import historylib
SITE = "https://trackalmanac.com"
STATE = os.path.join(ROOT, ".automation", "build-state.json")
YEAR = 2026
KEEP = {".git", ".github", ".automation", "src", "scripts", "build.py", "CNAME", ".nojekyll", "README.md", "robots.txt",
        "site.webmanifest", "og-image.png", "favicon.svg", "favicon.ico", "favicon-16.png", "favicon-32.png",
        "apple-touch-icon.png", "icon-192.png", "icon-512.png", ".gitignore"}

esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)


# ---------------------------------------------------------------- JS literal parser
class JSParse:
    """Parses JavaScript object/array literals (bare keys, trailing commas, ' or " strings)."""
    def __init__(self, s): self.s, self.i = s, 0
    def ws(self):
        s = self.s
        while self.i < len(s):
            if s[self.i] in " \t\r\n": self.i += 1
            elif s.startswith("//", self.i): self.i = s.index("\n", self.i)
            elif s.startswith("/*", self.i): self.i = s.index("*/", self.i) + 2
            else: break
    def val(self):
        self.ws(); c = self.s[self.i]
        if c == "{": return self.obj()
        if c == "[": return self.arr()
        if c in "\"'": return self.string()
        m = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?").match(self.s, self.i)
        if m: self.i = m.end(); t = m.group(); return float(t) if re.search(r"[.eE]", t) else int(t)
        for w, v in (("true", True), ("false", False), ("null", None), ("undefined", None)):
            if self.s.startswith(w, self.i): self.i += len(w); return v
        raise ValueError("unexpected %r at %d" % (self.s[self.i:self.i + 40], self.i))
    def string(self):
        q = self.s[self.i]; self.i += 1; out = []
        while True:
            c = self.s[self.i]
            if c == "\\":
                n = self.s[self.i + 1]
                if n == "u": out.append(chr(int(self.s[self.i + 2:self.i + 6], 16))); self.i += 6; continue
                out.append({"n": "\n", "t": "\t", "r": "\r"}.get(n, n)); self.i += 2; continue
            if c == q: self.i += 1; return "".join(out)
            out.append(c); self.i += 1
    def key(self):
        self.ws(); c = self.s[self.i]
        if c in "\"'": return self.string()
        m = re.compile(r"[A-Za-z_$][\w$]*|\d+").match(self.s, self.i); self.i = m.end(); return m.group()
    def obj(self):
        self.i += 1; o = {}
        while True:
            self.ws()
            if self.s[self.i] == "}": self.i += 1; return o
            k = self.key(); self.ws(); assert self.s[self.i] == ":"; self.i += 1
            o[k] = self.val(); self.ws()
            if self.s[self.i] == ",": self.i += 1
    def arr(self):
        self.i += 1; a = []
        while True:
            self.ws()
            if self.s[self.i] == "]": self.i += 1; return a
            a.append(self.val()); self.ws()
            if self.s[self.i] == ",": self.i += 1


def const(js, name):
    m = re.search(r"\bconst %s\s*=\s*" % re.escape(name), js)
    if not m: return None
    p = JSParse(js); p.i = m.end(); return p.val()


# ---------------------------------------------------------------- data files
def fmt_json(v, ind=0, width=120):
    """JSON laid out for readable diffs: short values and lists of plain values on one
    line, everything else one entry per line."""
    flat = json.dumps(v, ensure_ascii=False, separators=(", ", ": "))
    if not isinstance(v, (list, dict)) or not v or len(flat) + ind <= width or \
            (isinstance(v, list) and not any(isinstance(x, (list, dict)) for x in v)):
        return flat
    pad, pad1 = " " * ind, " " * (ind + 1)
    if isinstance(v, list):
        return "[\n" + ",\n".join(pad1 + fmt_json(x, ind + 1, width) for x in v) + "\n" + pad + "]"
    return "{\n" + ",\n".join(pad1 + json.dumps(k, ensure_ascii=False) + ": " + fmt_json(x, ind + 1, width) for k, x in v.items()) + "\n" + pad + "}"


def load_data(path=DATA):
    return json.load(open(path, encoding="utf-8"))


def save_data(d, path=DATA):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: f.write(fmt_json(d) + "\n")
    os.replace(tmp, path)


def data_js(*dicts):
    """const NAME=<json>; for every top-level key, in file order."""
    return "".join("const %s=%s;\n" % (k, json.dumps(v, ensure_ascii=False, separators=(",", ":")))
                   for d in dicts for k, v in d.items())


# ---------------------------------------------------------------- read sources
def read_master(data_path=DATA):
    s = open(SRC, encoding="utf-8").read()
    s = s[s.index("<title>"):] if "<title>" in s else s
    s = re.sub(r"\s*</body>\s*</html>\s*$", "", s)
    head_end = s.index('<div class="page">')
    head = s[:head_end]
    css = re.search(r"<style>(.*?)</style>", head, re.S).group(1)
    fonts = "\n".join(re.findall(r'<link rel="(?:preconnect|stylesheet)" href="https://fonts[^"]*"[^>]*>', head))
    body = s[head_end:s.index("<script>", head_end)]
    script = s[s.index("<script>", head_end) + 8:s.rindex("</script>")]
    pre, app = script.split("/*APP*/", 1)
    assert pre.strip() == "/*DATA*/", "src/app.html: the script must start with /*DATA*/ then /*APP*/"
    D = load_data(data_path)
    # season archive data is not in data.js: each season is its own file, loaded when its page opens
    data = data_js({k: v for k, v in D.items() if k != "ARCHDATA"}, load_data(MEDIA))
    return css, fonts, body, data, app, D


def extract_images(text, imgdir, written):
    def sub(m):
        ext = {"svg+xml": "svg", "jpeg": "jpg"}.get(m.group(1), m.group(1))
        raw = base64.b64decode(m.group(2))
        name = hashlib.sha1(raw).hexdigest()[:12] + "." + ext
        if name not in written:
            os.makedirs(imgdir, exist_ok=True)
            open(os.path.join(imgdir, name), "wb").write(raw); written.add(name)
        return "/img/" + name
    return re.sub(r"data:image/(png|webp|jpeg|svg\+xml);base64,([A-Za-z0-9+/=]+)", sub, text)


def vhash(text): return hashlib.sha1(text.encode()).hexdigest()[:10]


# ---------------------------------------------------------------- helpers on data
def slug(r): return re.sub(r"[^a-z0-9]+", "-", r["short"].replace(" (Sepang)", "").lower()).strip("-")
def norm(s):
    import unicodedata
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", s).lower())
RACECC = {"albert": "AU", "shanghai": "CN", "suzuka": "JP", "miami": "US", "montreal": "CA", "monaco": "MC", "catalunya": "ES",
          "rbring": "AT", "silverstone": "GB", "spa": "BE", "hungaro": "HU", "zandvoort": "NL", "monza": "IT", "madring": "ES",
          "baku": "AZ", "sepang": "MY", "marina": "SG", "cota": "US", "mexico": "MX", "interlagos": "BR", "vegas": "US",
          "lusail": "QA", "yas": "AE"}
COUNTRY = {"AU": "Australia", "CN": "China", "JP": "Japan", "US": "United States", "CA": "Canada", "MC": "Monaco", "ES": "Spain",
           "AT": "Austria", "GB": "United Kingdom", "BE": "Belgium", "HU": "Hungary", "NL": "Netherlands", "IT": "Italy",
           "AZ": "Azerbaijan", "MY": "Malaysia", "SG": "Singapore", "MX": "Mexico", "BR": "Brazil", "QA": "Qatar",
           "AE": "United Arab Emirates", "BH": "Bahrain", "SA": "Saudi Arabia", "PT": "Portugal", "TR": "Türkiye"}
def fmt_date(iso, year=True):
    d = datetime.date.fromisoformat(iso[:10]); return d.strftime("%-d %B %Y" if year else "%-d %B")
def gp_name(r): return r["gp"].replace(" (Sepang)", "")


class Site:
    def __init__(self, D, app_js):
        g = lambda n: D.get(n)
        self.RACES, self.SEASON, self.SCHED = g("RACES"), g("SEASON") or {}, g("SCHED") or {}
        self.DRIVERS, self.CONS = g("DRIVERS"), g("CONSTRUCTORS")
        self.ARCHIVE, self.ARCHDATA = g("ARCHIVE") or {}, g("ARCHDATA") or {}
        self.ARCHIVE = dict(self.ARCHIVE)
        for y, t in (g("ARCHTXT") or {}).items(): self.ARCHIVE[y] = t
        if g("CAL2027"): self.ARCHIVE.setdefault("2027", {"next": True})
        self.CAL2027, self.ENT2027 = g("CAL2027") or [], g("ENTRIES2027") or []
        self.PREWAR = g("PREWAR")
        self.HIST = None
        self.BIO, self.TEAMBIO, self.GRIDNOTES = g("BIO") or {}, g("TEAMBIO") or {}, g("GRIDNOTES") or {}
        self.SITEINFO = const(app_js, "SITE") or {"name": "Track Almanac", "email": "", "domain": "trackalmanac.com", "updated": ""}
        self.full = {}
        for d in self.DRIVERS: self.full[norm(d[0].split()[-1])] = d[0]
        self.done = [r for r in self.RACES if r.get("res")]
        self.next = next((r for r in self.RACES if not r.get("res")), None)
        self.app_js = app_js

    def fullname(self, s): return self.full.get(norm(s), s)
    def team_of(self, name):
        for d in self.DRIVERS:
            if d[0] == name or norm(d[0].split()[-1]) == norm(name.split()[-1]): return d[2]
        return ""
    def path(self, key):
        if key == "season": return "/"
        if key.startswith("detail-"):
            r = next(x for x in self.RACES if x["r"] == int(key[7:])); return "/races/%d/%s/" % (YEAR, slug(r))
        if key.startswith("archive-"): return "/archive/%s/" % key[8:]
        if key == "sitemap": return "/site-map/"
        if key == "hcons": return "/history/constructors/"
        if key == "hcirc": return "/history/circuits/"
        if key == "hregs": return "/history/regulations/"
        if key.startswith("game-"): return {"game-picks": "/game/picks/", "game-lb": "/game/leaderboard/", "game-leagues": "/game/leagues/", "game-account": "/game/account/"}[key]
        return "/%s/" % key
    def a(self, key, text): return '<a href="%s">%s</a>' % (self.path(key), text)
    def dlink(self, name):
        b = next((x for x in self.BIO.values() if norm(x["last"]) == norm(name.split()[-1])), None)
        return '<a href="/drivers/?driver=%s">%s</a>' % (b["code"], esc(name)) if b else esc(name)


# ---------------------------------------------------------------- page content (plain HTML, read before JS)
def table(head, rows, cls="t"):
    return ('<div class="tw"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' %
            (cls, "".join("<th>%s</th>" % h for h in head), "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in row) for row in rows)))
def sec(title, inner, sub=""):
    return '<section class="dsec"><div class="sec"><h2>%s</h2>%s</div>%s</section>' % (title, '<span class="lbl">%s</span>' % sub if sub else "", inner)
def pagehead(h1, lead, lbl="2026 Formula 1 World Championship"):
    return '<div class="pagehead"><div><span class="lbl">%s</span><h1>%s</h1><p>%s</p></div></div>' % (lbl, h1, lead)


def standings_tables(S, n=None):
    d = [[i + 1, S.dlink(x[0]), esc(x[2]), x[3]] for i, x in enumerate(S.DRIVERS[:n] if n else S.DRIVERS)]
    c = [[i + 1, esc(x[0]), x[1]] for i, x in enumerate(S.CONS)]
    return (sec("Drivers' standings", table(["Pos", "Driver", "Team", "Pts"], d), "After round %d" % len(S.done)) +
            sec("Constructors' standings", table(["Pos", "Team", "Pts"], c)))


def gp_rows(S):
    rows = []
    for r in S.RACES:
        se = S.SEASON.get(str(r["r"]), {})
        res = r.get("res")
        pole = S.fullname(se["quali"][0][2]) if se.get("quali") else "—"
        sw = r["sprint"] if isinstance(r.get("sprint"), str) else ("Sprint" if r.get("sprint") else "—")
        if res:
            w = res["pod"][0][0]; rows.append([r["r"], S.a("detail-%d" % r["r"], esc(gp_name(r))), fmt_date(r["date"], False), esc(pole), esc(res["fl"][0]), "<b>%s</b>" % esc(w), esc(S.team_of(w)), esc(sw)])
        else:
            rows.append([r["r"], S.a("detail-%d" % r["r"], esc(gp_name(r))), fmt_date(r["date"], False), esc(pole), "—", "—", "—", esc(sw)])
    return table(["Rd", "Grand Prix", "Date", "Pole position", "Fastest lap", "Winning driver", "Winning constructor", "Sprint"], rows, "t gpt")


def session_rows(S, r):
    sc = S.SCHED.get(str(r["r"]))
    if not sc: return ""
    rows = [[esc(n if n != "Grand Prix" else "Race"), datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).strftime("%a %-d %b, %H:%M UTC")] for n, t, *_ in sc[1]]
    return table(["Session", "Start (UTC)"], rows)


def class_table(S, rows, grid=False):
    out = []
    for x in rows:
        pos = x[0] if x[0] not in ("NC", "DQ") else ("DSQ" if x[0] == "DQ" else "Ret")
        line = [pos, x[1], esc(S.fullname(x[2])), esc(S.team_of(S.fullname(x[2]))), x[3], esc(x[4])]
        if grid: line.append("Pit lane" if x[6] == "PL" else x[6])
        line.append(x[5]); out.append(line)
    head = ["Pos", "No", "Driver", "Team", "Laps", "Time / retired"] + (["Grid"] if grid else []) + ["Pts"]
    return table(head, out)


def quali_table(S, rows, labels):
    return table(["Pos", "No", "Driver"] + labels, [[x[0], x[1], esc(S.fullname(x[2])), esc(x[3]), esc(x[4]), esc(x[5])] for x in rows])


def practice_table(S, rows):
    return table(["Pos", "No", "Driver", "Time / gap", "Laps"], [[x[0], x[1], esc(S.fullname(x[2])), esc(x[3]) or "No time", x[4]] for x in rows])


NEUTRAL = {"SC": "Safety car", "VSC": "Virtual safety car", "RF": "Red flag", "PIT": "Field through the pit lane"}
TYRES = {"S": "Soft", "M": "Medium", "H": "Hard", "I": "Intermediate", "W": "Wet", "?": "Unknown"}


def laps_txt(a, b): return "lap %d" % a if a == b else "laps %d–%d" % (a, b)


def race_extras_html(S, se):
    """Safety cars and tyre strategy as plain HTML (the app draws the charts)."""
    out = []
    nz = se.get("neutral")
    if nz is not None:
        txt = "; ".join("%s: %s" % (NEUTRAL[k], laps_txt(a, b)) for k, a, b in nz) or "No safety car, virtual safety car or red flag."
        out.append(sec("How the race went", "<p>%s</p>" % esc(txt), "Safety cars and red flags"))
    st = se.get("stints")
    if st:
        rows = []
        for y in se["race"]:
            v = st.get(str(y[1]))
            if v: rows.append([esc(y[0]), esc(S.fullname(y[2])), esc(" · ".join("%s %s" % (TYRES.get(c, c), laps_txt(a, b)) for c, a, b, age in v)), len(v) - 1])
        out.append(sec("Tyre strategy", table(["Pos", "Driver", "Stints", "Stops"], rows), "Every stint, lap by lap"))
    return "".join(out)


def race_page(S, r):
    se = S.SEASON.get(str(r["r"]), {}); res = r.get("res"); name = gp_name(r)
    cc = RACECC.get(r["track"], ""); ctry = COUNTRY.get(cc, "")
    parts = ['<section class="dhero"><div class="info"><span class="lbl">Round %d of %d · %s</span><h1>%s %d</h1><p>%s, %s, %s. %d laps of %.3f km (%.1f km).</p>' %
             (r["r"], len(S.RACES), esc(r.get("days") or fmt_date(r["date"])), esc(name), YEAR, esc(r["circuit"]), esc(r["city"]), esc(ctry), r["laps"], r["len"], r["laps"] * r["len"])]
    if res:
        w, p2, p3 = res["pod"][0][0], res["pod"][1][0], res["pod"][2][0]
        parts.append("<p><b>%s</b> won the %s %d for %s, ahead of %s and %s. Pole position: %s. Fastest lap: %s, %s on lap %s.%s</p>" %
                     (esc(w), esc(name), YEAR, esc(S.team_of(w)), esc(p2), esc(p3), esc(res["pole"]), esc(res["fl"][0]), esc(res["fl"][1]), res["fl"][2], (" " + esc(res["cls"])) if res.get("cls") else ""))
    else:
        parts.append("<p>Session times, results and the starting grid are added after each session of the weekend.</p>")
    parts.append("</div></section>")
    if se.get("race"): parts.append(sec("Race classification", class_table(S, se["race"], grid=True), "%d laps" % r["laps"]))
    if se.get("race"): parts.append(race_extras_html(S, se))
    parts.append(wa_card(S, "race"))
    if S.GRIDNOTES.get(str(r["r"])): parts.append(sec("Starting grid", "<p>%s</p>" % esc(S.GRIDNOTES[str(r["r"])]), "Penalties and pit lane starts"))
    if se.get("quali"): parts.append(sec("Qualifying", quali_table(S, se["quali"], ["Q1", "Q2", "Q3"]), "Q1 · Q2 · Q3"))
    if se.get("sprint"): parts.append(sec("Sprint", class_table(S, se["sprint"]), "Sprint classification"))
    if se.get("sq"): parts.append(sec("Sprint qualifying", quali_table(S, se["sq"], ["SQ1", "SQ2", "SQ3"]), "SQ1 · SQ2 · SQ3"))
    for k, lab in (("fp1", "Practice 1"), ("fp2", "Practice 2"), ("fp3", "Practice 3")):
        if se.get(k): parts.append(sec(lab, practice_table(S, se[k]), "Best lap per driver"))
    sr = session_rows(S, r)
    if sr: parts.append(sec("Weekend schedule", sr, "All times UTC"))
    if se.get("tyres"):
        t = se["tyres"]; parts.append(sec("Tyres", "<p>Pirelli compounds: C%s (hard), C%s (medium), C%s (soft).</p>" % (t[0], t[1], t[2])))
    i = S.RACES.index(r); nav = []
    if i > 0: nav.append("Previous: " + S.a("detail-%d" % S.RACES[i - 1]["r"], esc(gp_name(S.RACES[i - 1]))))
    if i < len(S.RACES) - 1: nav.append("Next: " + S.a("detail-%d" % S.RACES[i + 1]["r"], esc(gp_name(S.RACES[i + 1]))))
    parts.append('<p class="note2">%s</p>' % " · ".join(nav))
    return "".join(parts)


def home_page(S):
    nr = S.next; out = []
    lead = ("%d of %d rounds run. %s leads the drivers' championship with %s points; %s lead the constructors' standings." %
            (len(S.done), len(S.RACES), S.DRIVERS[0][0], S.DRIVERS[0][3], S.CONS[0][0]))
    out.append(pagehead("2026 Formula 1 season", esc(lead), "Track Almanac · Races. Drivers. Teams. Numbers."))
    if nr:
        out.append(sec("Next race: " + esc(gp_name(nr)), "<p>Round %d · %s · %s, %s. %s</p>%s" % (nr["r"], esc(nr.get("days", "")), esc(nr["circuit"]), esc(nr["city"]), S.a("detail-%d" % nr["r"], "Weekend schedule and session results"), session_rows(S, nr))))
    if nr and wa_url(S):
        out.append('<p class="waline">Get session times and results on WhatsApp <a class="wabtn wasm" href="%s" target="_blank" rel="noopener" data-wa="home">%s<span>Follow</span></a></p>' % (esc(wa_url(S)), WA_ICON))
    out.append(standings_tables(S, 10))
    rows = [[r["r"], S.a("detail-%d" % r["r"], esc(gp_name(r))), fmt_date(r["date"], False), esc(r["res"]["pod"][0][0]) if r.get("res") else "—"] for r in reversed(S.RACES)]
    out.append(sec("Race results", table(["Rd", "Grand Prix", "Date", "Winner"], rows), "Latest first"))
    return "".join(out)


def championship_page(S):
    return (pagehead("2026 F1 Championship standings", "Drivers' and constructors' points after round %d of %d, with every Grand Prix winner, pole position and fastest lap." % (len(S.done), len(S.RACES))) +
            sec("Grands Prix", gp_rows(S), "%d rounds" % len(S.RACES)) + standings_tables(S) + wa_card(S, "championship"))


def drivers_page(S):
    rows = []
    for i, d in enumerate(S.DRIVERS):
        b = next((x for x in S.BIO.values() if norm(x["last"]) == norm(d[0].split()[-1])), None)
        rows.append([i + 1, esc(d[0]), b["num"] if b else "", esc(b["nationality"]) if b else "", esc(d[2]), d[3],
                     ("Born %s, %s. F1 debut: %s." % (fmt_date(b["dob"]), esc(b["birthplace"]), esc(b["debut"]))) if b else ""])
    return pagehead("2026 F1 drivers", "Every driver on the 2026 Formula 1 grid with team, nationality, points and career profile.") + \
        table(["Pos", "Driver", "No", "Nationality", "Team", "Pts", "Profile"], rows)


def teams_page(S):
    rows = []
    for i, (team, pts) in enumerate(S.CONS):
        tb = S.TEAMBIO.get(team, {}); ds = [d[0] for d in S.DRIVERS if d[2] == team]
        rows.append([i + 1, "<b>%s</b>" % esc(tb.get("name", team)), esc(tb.get("entry", "")), esc(tb.get("base", "")), esc(tb.get("principal", "")),
                     esc(tb.get("chassis", "")), esc(tb.get("power", "")), esc(", ".join(ds)), pts])
    return pagehead("2026 F1 teams", "All %d Formula 1 constructors in 2026 with drivers, chassis, power unit, base and team principal." % len(S.CONS)) + \
        table(["Pos", "Team", "Entrant", "Base", "Team principal", "Chassis", "Power unit", "Drivers", "Pts"], rows)


def calendar_page(S):
    rows = [[r["r"], S.a("detail-%d" % r["r"], esc(gp_name(r))), esc("%s, %s" % (r["circuit"], r["city"])), esc(r.get("days") or fmt_date(r["date"], False)),
             "Sprint" if r.get("sprint") else "Standard", esc(r["res"]["pod"][0][0]) if r.get("res") else "—"] for r in S.RACES]
    return pagehead("2026 F1 calendar", "All %d rounds of the 2026 Formula 1 season with dates, circuits, sprint weekends and winners." % len(S.RACES)) + \
        table(["Rd", "Grand Prix", "Circuit", "Weekend", "Format", "Winner"], rows, "t gpt")


def race_day_2027(days):
    """'12–14 Mar' or '30 Apr–2 May' -> 'Sun 14 Mar' (the last day of the weekend is race day)."""
    import datetime
    last = days.split("–")[-1].strip().split()
    mon = last[1] if len(last) > 1 else days.strip()[-3:]
    d = datetime.date(2027, ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(mon) + 1, int(last[0]))
    return "%s %d %s" % (d.strftime("%a"), d.day, mon)


def archive_year_page(S, y):
    a = S.ARCHIVE.get(str(y), {}); A = S.ARCHDATA.get(str(y))
    if a.get("next"):
        rows = [[c[0], esc(c[1]), esc(c[3]), esc(c[4]), esc(c[5]), race_day_2027(c[5]), "Sprint" if c[6] else "Standard"] for c in S.CAL2027]
        ent = [[esc(e[0]), esc(" · ".join(x or "TBC" for x in e[1]))] for e in S.ENT2027]
        return pagehead("2027 F1 calendar", "The confirmed 2027 Formula 1 calendar: %d Grands Prix, %d sprint weekends." % (len(rows), sum(1 for c in S.CAL2027 if c[6])), "Season 2027") + \
            sec("2027 calendar", table(["Rd", "Grand Prix", "Circuit", "Location", "Weekend", "Race day", "Format"], rows, "t gpt"), "Provisional") + \
            sec("Confirmed line-ups", table(["Team", "Drivers"], ent))
    if a.get("live"):
        lead = S.DRIVERS[0] if S.DRIVERS else None
        intro = "The 2026 season is in progress: %d of %d rounds complete." % (len(S.done), len(S.RACES))
        if lead: intro += " %s leads the drivers' championship on %s points; %s top the constructors' table." % (esc(lead[0]), lead[3], esc(S.CONS[0][0]))
        intro += " See the %s and %s for the full picture." % (S.a("championship", "championship standings"), S.a("calendar", "calendar"))
        return pagehead("2026 Formula 1 season", intro, "Season archive") + \
            sec("Grands Prix", gp_rows(S), "%d rounds" % len(S.RACES)) + standings_tables(S)
    out = [pagehead("%s Formula 1 season" % y, esc(a.get("sum", "")), "Season archive")]
    if a.get("keys"): out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(k) for k in a["keys"]))
    if A:
        D, C = A["D"], A["C"]; cname = {k: v[0] for k, v in (A.get("cn") or {}).items()}; cname.update({c[0]: c[1] for c in C})
        nm = lambda i: esc(D[i][0]) if i is not None and i >= 0 else "—"
        has_sprint = any(r[9] is not None for r in A["R"])
        rows = [[r[0], esc(r[1]), fmt_date(r[3], False), nm(r[5]), nm(r[6]), "<b>%s</b>" % nm(r[7]), esc(cname.get(r[8], r[8] or "—"))] + ([nm(r[9]) if r[9] is not None else "—"] if has_sprint else []) for r in A["R"]]
        out.append(sec("Grands Prix", table(["Rd", "Grand Prix", "Date", "Pole position", "Fastest lap", "Winning driver", "Winning constructor"] + (["Sprint winner"] if has_sprint else []), rows, "t gpt"), "%d rounds" % len(rows)))
        out.append(sec("Drivers' championship", table(["Pos", "Driver", "Team", "Pts"], [[d[4], esc(d[0]), esc(cname.get(d[2], d[2])), d[3]] for d in D])))
        if C: out.append(sec("Constructors' championship", table(["Pos", "Constructor", "Pts"], [[c[3], esc(c[1]), c[2]] for c in C])))
        else: out.append("<p>There was no constructors' championship until 1958.</p>")
    else:
        for k, lab in (("champ", "Champion"), ("p2", "Runner-up"), ("p3", "Third")):
            if a.get(k): out.append("<p>%s: %s (%s), %s points.</p>" % (lab, esc(a[k][0]), esc(a[k][1]), a[k][2]))
    return "".join(out)


def prewar_page(S):
    P = S.PREWAR
    out = [pagehead("Grand Prix racing 1946–1949", esc(P["sum"]), "Before the World Championship"),
           "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(k) for k in P["keys"])]
    head = ["Date", "Race", "Circuit", "Winner", "Car"]
    ge = [[y, fmt_date(r[0], False), "<b>%s</b>" % esc(r[1]), esc(r[3]), esc(r[4]), esc(r[6])] for y in sorted(P["years"]) for r in P["years"][y]["races"] if r[7]]
    ge_note = ("<p>In motorsport history, <i>Grandes Épreuves</i> (French for &ldquo;great trials&rdquo; or &ldquo;major events&rdquo;) "
               "was a term used from 1906 to 1949 to designate the most prestigious and important international motor racing events. "
               "There were none in 1946.</p>")
    out.append(sec("Grandes Épreuves", ge_note + table(["Year"] + head, ge, "t gpt"), "The most prestigious races, 1947–1949"))
    for y in sorted(P["years"]):
        Y = P["years"][y]
        rows = [[fmt_date(r[0], False), ("<b>%s</b> (Grande Épreuve)" % esc(r[1])) if r[7] else esc(r[1]), esc(r[3]), esc(r[4]), esc(r[6])] for r in Y["races"]]
        out.append(sec(y, "<p>%s</p><ul>%s</ul>" % (esc(Y["sum"]), "".join("<li>%s</li>" % esc(k) for k in Y.get("keys", []))) + table(head, rows, "t gpt"), "%d races" % len(rows)))
    out.append("<p>There were no points and no champion before 1950. Race lists: the 1946–1949 Grand Prix season pages on Wikipedia (CC BY-SA 4.0).</p>")
    return "".join(out)


def archive_index_page(S):
    rows = []
    for y in sorted((int(k) for k in S.ARCHIVE), reverse=True):
        A = S.ARCHDATA.get(str(y)); a = S.ARCHIVE[str(y)]
        champ = A["D"][0][0] if A else (a.get("champ") or ["—"])[0] if not a.get("live") and not a.get("next") else ("In progress" if a.get("live") else "Calendar")
        cons = (A["C"][0][1] if A["C"] else "—") if A else (a.get("cons") or ["—"])[0] if not a.get("live") and not a.get("next") else "—"
        rows.append([S.a("archive-%d" % y, str(y)), esc(champ), esc(cons), len(A["R"]) if A else ""])
    if S.PREWAR:
        rows.append([S.a("archive-1946-1949", "1946–1949"), "No championship", "—", sum(len(Y["races"]) for Y in S.PREWAR["years"].values())])
    return pagehead("Formula 1 season archive", "Every Formula 1 World Championship season since the first in 1950, with full results, standings and charts, plus the Grand Prix seasons of 1946–1949 before the championship began.", "Season archive") + \
        table(["Season", "Drivers' champion", "Constructors' champion", "Races"], rows)


def static_page(S, key):
    m = re.search(r"\n%s:\{t:\"([^\"]*)\",b:`(.*?)`\}" % key, S.app_js, re.S)
    t, b = m.group(1), m.group(2)
    info = S.SITEINFO
    b = re.sub(r"\$\{SITE\.(\w+)\}", lambda mm: esc(info.get(mm.group(1), "")), b)
    b = re.sub(r'\$\{H\("([\w-]+)"\)\}', lambda mm: S.path(mm.group(1)), b)
    b = b.replace("${new Date().getFullYear()}", str(datetime.date.today().year))
    b = re.sub(r"\$\{[^}]*\}", "", b)
    return t, '<article class="doc"><span class="lbl">Track Almanac</span><h1>%s</h1>%s</article>' % (esc(t), b)


def history_page(S):
    H = S.HIST; dv = {d["i"]: d for d in H["drivers"]}; nm = lambda i: esc(dv[i]["n"]) if i in dv else ""
    lead = ("Every driver to start or enter a Formula 1 World Championship race since 1950: %d drivers across %d races. "
            "World champions by year, every champion's titles, all-time records and stats by country." % (len(H["drivers"]), H["races"]))
    out = [pagehead("Formula 1 history: drivers", lead, "Formula 1 history")]
    rows = []
    for c in reversed(H["champs"]):
        t = c["top"]
        won = ("%s Grand Prix" % esc(c["dec"][0]) if c["dec"] and not c["dec"][0].endswith(("Prix", "500")) else esc(c["dec"][0]) if c["dec"] else "In progress")
        rows.append([c["y"], "<b>%s</b> (%s)" % (nm(t[0][0]), esc(t[0][1])), fmtn(t[0][2]), "%s (%s)" % (nm(t[1][0]), fmtn(t[1][2])) if len(t) > 1 else "",
                     "%s (%s)" % (nm(t[2][0]), fmtn(t[2][2])) if len(t) > 2 else "", won])
    out.append(sec("World champions by year", table(["Year", "Champion", "Pts", "Runner-up", "Third", "Title won at"], rows)))
    ch = sorted((d for d in H["drivers"] if d["t"]), key=lambda d: (-d["t"], d["ty"][0]))
    out.append(sec("All world champions", table(["Driver", "Titles", "Years"], [[esc(d["n"]), d["t"], ", ".join(map(str, d["ty"]))] for d in ch])))
    for c in H["records"]:
        items = "".join("<h3>%s</h3><ol>%s</ol>" % (esc(it["t"]), "".join("<li>%s: %s%s</li>" % (nm(r[0]), fmtn(r[1]) if not isinstance(r[1], str) else esc(r[1]), (" (%s)" % esc(r[2])) if r[2] else "") for r in it["rows"][:5])) for it in c["items"])
        out.append(sec("Records: %s" % esc(c["cat"].lower()), items))
    ds = sorted(H["drivers"], key=lambda d: d["n"])
    out.append(sec("All Formula 1 drivers", table(["Driver", "Nationality", "Years", "Starts", "Wins", "Podiums", "Poles", "Titles"],
               [[esc(d["n"]), esc(H["ccn"].get(d["cc"], d["cc"] or "")), "%d–%d" % tuple(d["y"]) if d["y"] else "", d["s"], d["w"], d["p"], d["pl"], d["t"]] for d in ds])))
    out.append(sec("Drivers by country", table(["Country", "Drivers", "Wins", "Titles"], [[esc(c["n"]), c["d"], c["w"], c["t"]] for c in H["countries"]])))
    return "".join(out)


def history_cons_page(S):
    H = S.HIST; tb = {t["i"]: t for t in H["teams"]}; dv = {d["i"]: d for d in H["drivers"]}; eb = {e["i"]: e for e in H["engines"]}
    tn = lambda i: esc(tb[i]["n"]) if i in tb else ""
    lead = ("Every constructor to enter a Formula 1 World Championship race since 1950: %d teams and %d engine makers. "
            "Constructors' champions since 1958, every champion team, team and engine records, and stats by country." % (len(H["teams"]), len(H["engines"])))
    out = [pagehead("Formula 1 history: constructors", lead, "Formula 1 history")]
    rows = []
    for c in reversed(H["cchamps"]):
        t = c["top"]
        won = (esc(c["dec"][0]) if c["dec"] else "In progress")
        d = c.get("d") or {}
        drivers = ", ".join("%s%s%s" % ("(" if x[3] else "", esc(dv[x[0]]["n"]), ")" if x[3] else "") for x in d.get("drv", []) if x[0] in dv)
        clinched = ("Race %d of %d (%s)" % (c["dec"][1], c["rounds"], esc(c["dec"][0]))) if c["dec"] else "In progress"
        rows.append([c["y"], "<b>%s</b>" % esc(tb[t[0][0]]["n"] if t[0][0] in tb else t[0][1]), esc(c["eng"][0]) if c.get("eng") else "", drivers,
                     d.get("poles", ""), d.get("wins", ""), d.get("pod", ""), d.get("fl", ""), fmtn(t[0][2]), "%.2f" % d["pct"] if d.get("pct") is not None else "",
                     clinched, fmtn(c["margin"]) if c["margin"] is not None else "",
                     "%s (%s)" % (esc(t[1][1]), fmtn(t[1][2])) if len(t) > 1 else "", "%s (%s)" % (esc(t[2][1]), fmtn(t[2][2])) if len(t) > 2 else ""])
    out.append(sec("Constructors' champions by year", table(["Season", "Chassis", "Engine", "Drivers", "Poles", "Wins", "Podiums", "Fastest laps", "Points", "% points", "Clinched", "Margin", "Runner-up", "Third"], rows)))
    ch = sorted((t for t in H["teams"] if t["t"]), key=lambda t: (-t["t"], t["ty"][0]))
    out.append(sec("All constructors' champions", table(["Team", "Titles", "Years"], [[esc(t["n"]), t["t"], ", ".join(map(str, t["ty"]))] for t in ch])))
    for c in H["crec"]:
        nm = (lambda i: esc(eb[i]["n"]) if i in eb else "") if c["cat"] == "Engines" else tn
        items = "".join("<h3>%s</h3><ol>%s</ol>" % (esc(it["t"]), "".join("<li>%s: %s%s</li>" % (nm(r[0]), fmtn(r[1]) if not isinstance(r[1], str) else esc(r[1]), (" (%s)" % esc(r[2])) if r[2] else "") for r in it["rows"][:5])) for it in c["items"])
        out.append(sec("Records: %s" % esc(c["cat"].lower()), items))
    ts = sorted(H["teams"], key=lambda t: t["n"])
    out.append(sec("All Formula 1 constructors", table(["Team", "Country", "Years", "Races", "Wins", "Poles", "Titles"],
               [[esc(t["n"]), esc(H["ccn"].get(t["cc"], t["cc"] or "")), ("%d–%d" % tuple(t["y"])) if t["y"] else "", t["s"], t["w"], t["pl"], t["t"]] for t in ts])))
    out.append(sec("Engine makers", table(["Engine", "Country", "Years", "Races", "Wins", "Constructors' titles", "Drivers' titles"],
               [[esc(e["n"]), esc(H["ccn"].get(e["cc"], e["cc"] or "")), ("%d–%d" % tuple(e["y"])) if e["y"] else "", e["s"], e["w"], e["t"], e["dt"]] for e in sorted(H["engines"], key=lambda e: -e["w"])])))
    return "".join(out)


def history_circ_page(S, D):
    H = S.HIST; cb = {c["i"]: c for c in H["circuits"]}; dv = {d["i"]: d for d in H["drivers"]}
    raced = [c for c in H["circuits"] if c["r"]]
    lead = ("Every circuit to host a Formula 1 World Championship race since 1950: %d circuits in %d countries, with track maps, lap records, "
            "most wins and every race held there, plus calendar changes and planned future circuits." % (len(raced), len({c["cc"] for c in raced})))
    out = [pagehead("Formula 1 history: circuits", lead, "Formula 1 history")]
    ch = "".join("<h3>%s season</h3><p>In: %s. Out: %s.</p>" % (y, ", ".join(esc(cb[i]["n"]) for i in [x[0] for x in v["add"]]) or "none", ", ".join(esc(cb[i]["n"]) for i in v["drop"]) or "none") for y, v in sorted(H["calchanges"].items(), reverse=True))
    fut = "".join("<h3>%s (%s)</h3><p>%s: %s</p>" % (esc(f["n"]), esc(f["status"]), esc(f["when"]), esc(f["note"])) for f in D.get("FUTURECIRC", []))
    out.append(sec("Calendar changes", ch + fut))
    for it in H["crecords"][0]["items"]:
        out.append(sec(esc(it["t"]), "<ol>%s</ol>" % "".join("<li>%s: %s%s</li>" % (esc(cb[r[0]]["n"]), fmtn(r[1]) if not isinstance(r[1], str) else esc(r[1]), (" (%s)" % esc(r[2])) if r[2] else "") for r in it["rows"][:5])))
    rows = [[esc(c["n"]), esc(c["place"]), esc(H["ccn"].get(c["cc"], c["cc"])), ("%d–%d" % tuple(c["y"])) if c["y"] else "", c["r"], ("%.3f km" % c["len"]) if c["len"] else "",
             ("%s (%s, %d)" % (c["rec"][1], esc(dv[c["rec"][2]]["n"]) if c["rec"][2] in dv else "", c["rec"][4])) if c["rec"] else ""] for c in sorted(H["circuits"], key=lambda c: -c["r"])]
    out.append(sec("All Formula 1 circuits", table(["Circuit", "Location", "Country", "Years", "Grands Prix", "Length", "Lap record"], rows)))
    return "".join(out)


def fmtn(x):
    if isinstance(x, float) and x.is_integer(): x = int(x)
    return "{:,}".format(x) if isinstance(x, int) else ("%g" % x)


def game_page(S):
    out = [pagehead("Track Almanac Predictor", "A free Formula 1 prediction game: pick the top five finishers and the pole sitter for every Grand Prix.", "Predictor")]
    out.append(sec("Points", "<ul><li>P1 exactly right: 5</li><li>P2: 3</li><li>P3: 2</li><li>P4: 1</li><li>P5: 1</li><li>Pole sitter right: 3</li><li>Perfect weekend: 15</li></ul>"))
    out.append(sec("Rules", "<ul><li>Picks lock at the scheduled start of qualifying and can be changed freely until then.</li><li>Pole is P1 in the qualifying classification, before grid penalties.</li>"
                   "<li>Races are scored against the official classification; if it changes, the round is scored again.</li><li>No picks means 0 points for that round.</li>"
                   "<li>Ties: most correct winners, then most exact positions, then the earliest final submission.</li><li>Free to play. No prizes and no money.</li><li>Minimum age 13 (16 in the EEA and the UK).</li>"
                   "<li>Questions about the game: <a href=\"mailto:%s\">%s</a>.</li></ul>" % ((game_contact(),) * 2)))
    return "".join(out)


def game_contact():
    p = os.path.join(ROOT, "src", "game.json")
    return esc((json.load(open(p, encoding="utf-8")).get("contact") if os.path.exists(p) else "") or "contact@trackalmanac.com")


def game_lb_page(S):
    f = os.path.join(ROOT, "data", "game", "leaderboard-%d.json" % YEAR)
    out = [pagehead("Predictor leaderboard", "Season standings of the Track Almanac Predictor, the free F1 prediction game.", "Predictor")]
    if os.path.exists(f):
        j = json.load(open(f, encoding="utf-8"))
        out.append(table(["Pos", "Player", "Points", "Correct winners", "Exact positions", "Races"], [[r["pos"], esc(r["name"]), r["points"], r["winners"], r["exact"], r["races"]] for r in j["top"]]))
    else:
        out.append("<p>No scores yet: the table starts after the first Grand Prix of the game.</p>")
    return "".join(out)


def regs_page(R):
    out = [pagehead("History of F1 regulations", " ".join(R["intro"][:1]), "Formula 1 history")]
    out.append("".join("<p>%s</p>" % esc(p) for p in R["intro"][1:]))
    A = R["areas"]
    for e in R["eras"]:
        y = "%d–%d" % tuple(e["y"]) if e["y"][0] != e["y"][1] else str(e["y"][0])
        body = "<p>%s</p><ul>%s</ul><p>%s</p>%s" % (esc(e["plain"]), "".join("<li><b>%s:</b> %s</li>" % (esc(A[a]), esc(t)) for a, t in e["changes"]),
                                                    esc(e["meant"]), ("<p><b>Who got it right:</b> %s</p>" % esc(e["nailed"])) if e.get("nailed") else "")
        out.append(sec("%s: %s" % (y, esc(e["name"])), body))
    out.append(sec("Sources", "<ul>%s</ul>" % "".join('<li><a href="%s">%s</a></li>' % (esc(u), esc(t)) for t, u in R["sources"])))
    return "".join(out)


def dictionary_page(DI):
    """Every term, A to Z, as plain HTML (the app replaces it with the searchable version)."""
    cats = dict((k, n) for k, n in DI["cats"])
    terms = sorted(DI["terms"], key=lambda t: norm_sort(t[0]))
    out, letter = [], None
    for t, c, d, aka in terms:
        L = first_letter(t)
        if L != letter:
            if letter is not None: out.append("</dl>")
            out.append('<h2 id="l-%s">%s</h2><dl>' % (L.lower() if L != "#" else "num", L)); letter = L
        out.append("<dt>%s%s</dt><dd>%s <small>(%s)</small></dd>" % (esc(t), (" <small>also: %s</small>" % esc(", ".join(aka))) if aka else "", esc(d), esc(cats.get(c, c))))
    out.append("</dl>")
    return pagehead("F1 dictionary", "%d Formula 1 terms, from aerodynamics and tyres to flags, radio codes and fan slang." % len(terms)) + "".join(out)


def norm_sort(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"^[^a-z0-9]+", "", t)


def first_letter(t):
    c = norm_sort(t)[:1].upper()
    return c if c.isalpha() else "#"


def sitemap_page(S, pages):
    groups = [("2026 season", [p for p in pages if p["path"] in ("/", "/championship/", "/drivers/", "/teams/", "/calendar/")]),
              ("2026 races", [p for p in pages if p["path"].startswith("/races/")]),
              ("Season archive", [p for p in pages if p["path"].startswith("/archive/")]),
              ("History", [p for p in pages if p["path"].startswith("/history/")]),
              ("About the site", [p for p in pages if p["key"] in ("about", "contact", "privacy", "terms", "disclaimer")])]
    body = "".join("<h3>%s</h3><ul class=\"smap\">%s</ul>" % (g, "".join('<li><a href="%s">%s</a></li>' % (p["path"], esc(p["h1"])) for p in ps)) for g, ps in groups)
    return '<article class="doc"><span class="lbl">Track Almanac</span><h1>Site map</h1>%s</article>' % body


# ---------------------------------------------------------------- structured data
def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(items)]}


def race_finish(start, hours=2):
    """Expected race finish: lights out + 2 h, same ISO format as the input."""
    if "T" not in start: return start
    t = datetime.datetime.fromisoformat(start.replace("Z", "+00:00")) + datetime.timedelta(hours=hours)
    return t.isoformat().replace("+00:00", "Z") if start.endswith("Z") else t.isoformat()


def sports_event(S, r):
    sc = S.SCHED.get(str(r["r"])); cc = RACECC.get(r["track"], "")
    gp = r.get("start") or (next((x[1] for x in sc[1] if x[0] == "Grand Prix"), sc[1][-1][1]) if sc else None)
    start = sc[1][0][1] if sc else (datetime.date.fromisoformat(r["date"]) - datetime.timedelta(days=2)).isoformat()
    end = race_finish(gp) if gp else r["date"]
    ev = {"@context": "https://schema.org", "@type": "SportsEvent", "name": "%d %s" % (YEAR, gp_name(r)),
          "description": "Round %d of the %d Formula 1 World Championship at %s." % (r["r"], YEAR, r["circuit"]),
          "sport": "Formula One", "startDate": start, "endDate": end,
          "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "location": {"@type": "Place", "name": r["circuit"], "address": {"@type": "PostalAddress", "addressLocality": r["city"], "addressCountry": cc}},
          "url": SITE + S.path("detail-%d" % r["r"]), "image": SITE + "/og-image.png",
          "organizer": {"@type": "Organization", "name": "Formula One World Championship"}}
    return ev


WA_ICON = ('<svg class="waic" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.8a9.2 9.2 0 0 0-7.9 13.9L2.8 21.2l4.6-1.2A9.2 9.2 0 1 0 12 2.8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>'
           '<path d="M8.7 7.3c.3-.3.8-.3 1 .1l1 1.9c.2.3.1.7-.1 1l-.6.6c.6 1.3 1.6 2.3 2.9 2.9l.6-.6c.3-.3.7-.3 1-.1l1.9 1c.4.2.4.7.1 1l-.8.9c-.5.5-1.3.7-2 .4-2.6-1-4.7-3.1-5.7-5.7-.3-.7-.1-1.5.4-2z" fill="currentColor"/></svg>')


def wa_url(S): return (S.SITEINFO or {}).get("whatsapp", "")      # the one place it is set: const SITE in src/app.html


def wa_card(S, placement):
    """Same card as waCard() in the app, for the prerendered pages."""
    if not wa_url(S): return ""
    return ('<aside class="wacard" aria-label="WhatsApp channel"><p><b>Results, session times and stats after every session</b><span>Follow the Track Almanac channel on WhatsApp</span></p>'
            '<a class="wabtn" href="%s" target="_blank" rel="noopener" data-wa="%s">%s<span>Follow on WhatsApp</span></a></aside>' % (esc(wa_url(S)), placement, WA_ICON))


def org_ld(same_as=()):
    return [{"@context": "https://schema.org", "@type": "WebSite", "name": "Track Almanac", "url": SITE + "/",
             "description": "Races. Drivers. Teams. Numbers. Formula 1 calendar, results, standings and lap-by-lap charts."},
            dict({"@context": "https://schema.org", "@type": "Organization", "name": "Track Almanac", "url": SITE + "/", "logo": SITE + "/icon-512.png"},
                 **({"sameAs": [u for u in same_as if u]} if any(same_as) else {}))]


# ---------------------------------------------------------------- page shell
# ---------------------------------------------------------------- Google Analytics 4 (Consent Mode v2)
GA_ID = "G-E8LPNWHWRT"
GA_HOST = "trackalmanac.com"          # gtag.js only loads on the live site, never on local/test builds
GA_STRICT = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
             "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "GB", "CH"]   # EEA, UK, Switzerland


def ga_snippet():
    """Consent defaults, the stored cookie choice and the gtag.js loader. window.taConsent(choice) is
    called by the cookie banner; window.TA_GA is set only when analytics actually loads."""
    return ("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}\n"
            "(function(){var D='denied',G='granted';"
            "gtag('consent','default',{analytics_storage:D,ad_storage:D,ad_user_data:D,ad_personalization:D,region:%s,wait_for_update:500});"
            "gtag('consent','default',{analytics_storage:G,ad_storage:D,ad_user_data:D,ad_personalization:D,wait_for_update:500});"
            "window.taConsent=function(c){if(c!=='accept'&&c!=='reject')return;var v=c==='accept'?G:D;"
            "gtag('consent','update',{analytics_storage:v,ad_storage:v,ad_user_data:v,ad_personalization:v});};"
            "var c=null;try{c=localStorage.getItem('ta-consent');}catch(e){}window.taConsent(c);"
            "if(location.hostname!==%s)return;"
            "var legacy=location.pathname==='/'&&/^#(season|championship|drivers|teams|calendar|archive|about|contact|privacy|terms|disclaimer|sitemap|race-|detail-|driver-|team-)/.test(location.hash);"
            "window.TA_GA=%s;window.TA_GA_FIRST=legacy?null:location.pathname+location.search;"
            "var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+window.TA_GA;document.head.appendChild(s);"
            "gtag('js',new Date());gtag('config',window.TA_GA,legacy?{send_page_view:false}:{});})();</script>"
            % (json.dumps(GA_STRICT, separators=(",", ":")), json.dumps(GA_HOST), json.dumps(GA_ID)))


def head(p, assets, fonts):
    t, d, url = esc(p["title"]), esc(p["desc"]), SITE + p["path"]
    ld = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") for x in p["ld"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
{'<meta name="robots" content="noindex">' if p.get("noindex") else f'<link rel="canonical" href="{url}">'}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#000000">
<script>try{{if(localStorage.getItem("ta-theme")==="light"){{document.documentElement.setAttribute("data-theme","light");document.querySelector('meta[name="theme-color"]').content="#f3f5f8";}}}}catch(e){{}}</script>
{ga_snippet()}
<meta property="og:type" content="{'article' if p['path'].startswith('/races/') else 'website'}">
<meta property="og:site_name" content="Track Almanac">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{SITE}/og-image.png">
{fonts}
<link rel="stylesheet" href="/style.css?v={assets['css']}">
<style>html,body{{margin:0;padding:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
{ld}</head>
<body>
"""


NAVKEY = {"/": "season", "/championship/": "championship", "/drivers/": "drivers", "/teams/": "teams", "/history/": "history", "/history/constructors/": "history", "/history/circuits/": "history", "/history/regulations/": "history"}


def page_html(p, body_tpl, assets, fonts):
    body = body_tpl.replace('<main id="app"></main>', '<main id="app">%s</main>' % p["main"])
    body = re.sub(r'(<span class="mono" id="sheetname">)[^<]*(</span>)', lambda m: m.group(1) + esc(p["sheet"]) + m.group(2), body)
    nk = "archive" if p["path"].startswith("/archive/") else ("season" if p["path"].startswith("/races/") else NAVKEY.get(p["path"]))
    if nk: body = body.replace('data-go="%s" id="n-%s"' % (nk, nk), 'data-go="%s" id="n-%s" aria-current="page"' % (nk, nk))
    return head(p, assets, fonts) + body + ('<script>window.TA_PATHS=1</script>\n<script src="/data.js?v=%s"></script>\n<script src="/app.js?v=%s"></script>\n</body>\n</html>\n' % (assets["data"], assets["app"]))


# ---------------------------------------------------------------- build
def build(out, data_path=DATA):
    css, fonts, body, data, app, D = read_master(data_path)
    written = set(); imgdir = os.path.join(out, "img")
    if os.path.isdir(imgdir): shutil.rmtree(imgdir)
    body = extract_images(body, imgdir, written)
    # one file per archive season: /data/archive/<year>.json, versioned in ARCHV
    adir = os.path.join(out, "data", "archive")
    if os.path.isdir(adir): shutil.rmtree(adir)
    os.makedirs(adir)
    archv = {}
    for y, season in D.get("ARCHDATA", {}).items():
        txt = json.dumps(season, ensure_ascii=False, separators=(",", ":"))
        open(os.path.join(adir, "%s.json" % y), "w", encoding="utf-8").write(txt)
        archv[y] = vhash(txt)
    data += "const ARCHDATA={};const ARCHV=%s;\n" % json.dumps(archv, separators=(",", ":"))
    # history page data (all drivers, champions, records), loaded only on /history/
    HIST = historylib.compute(load_data(HISTBASE), D) if os.path.exists(HISTBASE) else None
    htxt = json.dumps(HIST, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(out, "data", "history.json"), "w", encoding="utf-8").write(htxt)
    data += "const HISTV=%s;\n" % json.dumps(vhash(htxt))
    # Predictor game: public Firebase web config and the Firebase bundle (loaded only on /game/ pages)
    gpath = os.path.join(ROOT, "src", "game.json")
    data += "const GAMECFG=%s;\n" % json.dumps(load_data(gpath) if os.path.exists(gpath) else {}, separators=(",", ":"))
    vpath = os.path.join(ROOT, "src", "vendor", "firebase-game.js")
    if os.path.exists(vpath):
        vtxt = open(vpath, encoding="utf-8").read()
        os.makedirs(os.path.join(out, "js"), exist_ok=True)
        open(os.path.join(out, "js", "firebase-game.js"), "w", encoding="utf-8").write(vtxt)
        data += "const FBV=%s;\n" % json.dumps(vhash(vtxt))
    else:
        data += "const FBV='';\n"
    # F1 dictionary, loaded only on /dictionary/
    dpath = os.path.join(ROOT, "src", "dictionary.json")
    dtxt = json.dumps(load_data(dpath), ensure_ascii=False, separators=(",", ":")) if os.path.exists(dpath) else '{"cats":[],"terms":[]}'
    open(os.path.join(out, "data", "dictionary.json"), "w", encoding="utf-8").write(dtxt)
    data += "const DICTV=%s;\n" % json.dumps(vhash(dtxt))
    # regulations history, loaded only on /history/regulations/
    rpath = os.path.join(ROOT, "src", "regulations.json")
    rtxt = json.dumps(load_data(rpath), ensure_ascii=False, separators=(",", ":")) if os.path.exists(rpath) else "{}"
    open(os.path.join(out, "data", "regulations.json"), "w", encoding="utf-8").write(rtxt)
    data += "const REGV=%s;\n" % json.dumps(vhash(rtxt))
    # circuit outlines for the circuits page, loaded only there
    cm = os.path.join(ROOT, "src", "circuitmaps.json")
    ctxt = open(cm, encoding="utf-8").read().strip() if os.path.exists(cm) else "{}"
    open(os.path.join(out, "data", "circuitmaps.json"), "w", encoding="utf-8").write(ctxt)
    data += "const CMAPV=%s;\n" % json.dumps(vhash(ctxt))
    # world map for the 2027 calendar page, loaded only on that page
    wtxt = json.dumps(load_data(WORLD), separators=(",", ":"))
    open(os.path.join(out, "data", "world.json"), "w", encoding="utf-8").write(wtxt)
    data += "const WORLDV=%s;\n" % json.dumps(vhash(wtxt))
    # track diagrams: src/tracks/<circuit id>.svg (drawn in the site's style, classes styled by style.css),
    # copied under a content hash and fetched by the circuit card when it opens
    ti = {}
    tdir = os.path.join(os.path.dirname(MEDIA), "tracks")
    if os.path.isdir(tdir):
        os.makedirs(imgdir, exist_ok=True)
        tnotes = json.load(open(os.path.join(tdir, "notes.json"), encoding="utf-8")) if os.path.exists(os.path.join(tdir, "notes.json")) else {}
        for f in sorted(os.listdir(tdir)):
            if not f.endswith(".svg"): continue
            raw = open(os.path.join(tdir, f), "rb").read(); name = "t-" + hashlib.sha1(raw).hexdigest()[:12] + ".svg"
            open(os.path.join(imgdir, name), "wb").write(raw); written.add(name)
            ti[f[:-4]] = ["/img/" + name] + ([tnotes[f[:-4]]] if f[:-4] in tnotes else [])
    data += "const TRACKIMG=%s;\n" % json.dumps(ti, separators=(",", ":"))
    data_x = extract_images(data, imgdir, written)
    app_x = extract_images(app, imgdir, written)
    css_x = extract_images(css, imgdir, written)
    body = body.replace('<img src="/img/', '<img fetchpriority="high" src="/img/', 1)
    open(os.path.join(out, "style.css"), "w", encoding="utf-8").write(css_x)
    open(os.path.join(out, "data.js"), "w", encoding="utf-8").write(data_x)
    open(os.path.join(out, "app.js"), "w", encoding="utf-8").write(app_x)
    assets = {"css": vhash(css_x), "data": vhash(data_x), "app": vhash(app_x)}
    S = Site(D, app); S.HIST = HIST
    assert wa_url(S), "src/app.html: const SITE needs whatsapp (the channel address)"
    body = body.replace("__WHATSAPP__", esc(wa_url(S)))           # footer link

    home = [("Home", "/")]
    pages = []
    def add(key, title, desc, h1, main, sheet, bc, ld=None, path=None, noindex=False):
        pages.append({"key": key, "path": path or S.path(key), "title": title, "desc": desc, "h1": h1, "main": main, "sheet": sheet,
                      "ld": (ld or []) + [crumbs(bc)], "noindex": noindex})
    nr = S.next
    add("season", "Track Almanac · Races. Drivers. Teams. Numbers.",
        "Formula 1 2026: calendar with session times, live standings, race results, qualifying, grids and lap-by-lap charts.%s" %
        (" Next: %s, %s." % (gp_name(nr), nr.get("days", "")) if nr else ""),
        "2026 Formula 1 season", home_page(S), "2026 WORLD CHAMPIONSHIP", home, org_ld([wa_url(S)]))
    add("championship", "2026 F1 Championship Standings & Points Breakdown | Track Almanac",
        "2026 Formula 1 drivers' and constructors' standings after round %d, results grid for every Grand Prix, points progression and season statistics." % len(S.done),
        "2026 F1 Championship standings", championship_page(S), "2026 CHAMPIONSHIP · POINTS", home + [("2026 Championship", "/championship/")])
    add("drivers", "2026 F1 Drivers: Profiles, Stats & Standings | Track Almanac",
        "All %d drivers on the 2026 Formula 1 grid: team, nationality, age, career wins, podiums, poles and 2026 points." % len(S.BIO),
        "2026 F1 drivers", drivers_page(S), "2026 DRIVERS", home + [("2026 Drivers", "/drivers/")])
    add("teams", "2026 F1 Teams: Line-ups, Cars & Standings | Track Almanac",
        "All %d Formula 1 teams in 2026: drivers, chassis, power unit, base, team principal, titles and points." % len(S.CONS),
        "2026 F1 teams", teams_page(S), "2026 TEAMS", home + [("2026 Teams", "/teams/")])
    add("calendar", "2026 F1 Calendar: Dates, Circuits & Results | Track Almanac",
        "The 2026 Formula 1 calendar: all %d rounds with dates, circuits, sprint weekends and winners." % len(S.RACES),
        "2026 F1 calendar", calendar_page(S), "2026 CALENDAR", home + [("2026 Calendar", "/calendar/")])
    for r in S.RACES:
        name = gp_name(r); res = r.get("res")
        if res:
            title = "%s %d: Results, Grid & Lap Chart | Track Almanac" % (name, YEAR)
            desc = "%s %d results: %s won from %s on the grid. Full classification, qualifying, starting grid, fastest lap and lap-by-lap chart." % (
                name, YEAR, res["pod"][0][0], next((("P%s" % x[6]) for x in S.SEASON.get(str(r["r"]), {}).get("race", []) if x[0] == "1"), "the front"))
        else:
            title = "%s %d: Schedule, Session Times & Results | Track Almanac" % (name, YEAR)
            desc = "%s %d (%s, %s): session times, tyre compounds, circuit map and results from every session of the weekend." % (name, YEAR, r.get("days", fmt_date(r["date"])), r["circuit"])
        add("detail-%d" % r["r"], title, desc, "%s %d" % (name, YEAR), race_page(S, r), "R%d · %s" % (r["r"], name.upper()),
            home + [("2026 Season", "/calendar/"), (name, S.path("detail-%d" % r["r"]))], [sports_event(S, r)])
    if S.HIST:
        add("history", "F1 History: Every Driver, World Champion & All-Time Record | Track Almanac",
            "Every Formula 1 driver since 1950 (%d drivers) with career stats, world champions by year, all-time records like most wins and consecutive titles, and stats by country." % len(S.HIST["drivers"]),
            "Formula 1 history: drivers", history_page(S), "F1 HISTORY", home + [("History", "/history/")])
        add("hcirc", "F1 Circuits: Every Track, Lap Records & Calendar Changes | Track Almanac",
            "Every Formula 1 circuit since 1950 (%d tracks) with track maps, lap records, most wins and every race held there, plus 2026 and 2027 calendar changes and planned future circuits." % len([c for c in S.HIST["circuits"] if c["r"]]),
            "Formula 1 history: circuits", history_circ_page(S, D), "F1 HISTORY", home + [("History", "/history/"), ("Circuits", "/history/circuits/")])
        rpath = os.path.join(ROOT, "src", "regulations.json")
        if os.path.exists(rpath):
            add("hregs", "History of F1 Regulations 1946–2026 and Beyond, Explained | Track Almanac",
                "Every era of Formula 1 rules from 1946 to 2026 and the plans after, explained in plain words: engines, aerodynamics, tyres, safety and points, what each change meant and which teams dominated.",
                "History of F1 regulations", regs_page(load_data(rpath)), "F1 HISTORY", home + [("History", "/history/"), ("Regulations", "/history/regulations/")])
        add("hcons", "F1 Constructors History: Every Team, Champion, Engine & Record | Track Almanac",
            "Every Formula 1 constructor since 1950 (%d teams, %d engine makers): constructors' champions by year, team and engine records like most wins and consecutive titles, and team histories." % (len(S.HIST["teams"]), len(S.HIST["engines"])),
            "Formula 1 history: constructors", history_cons_page(S), "F1 HISTORY", home + [("History", "/history/"), ("Constructors", "/history/constructors/")])
    add("archive", "F1 Season Archive 1946–2025: Results & Champions | Track Almanac",
        "Every Formula 1 World Championship season since 1950: champions, Grand Prix winners, poles, fastest laps, sprint results and full standings, plus Grand Prix racing from 1946 to 1949.",
        "Formula 1 season archive", archive_index_page(S), "SEASON ARCHIVE", home + [("Archive", "/archive/")])
    for y in sorted((int(k) for k in S.ARCHIVE), reverse=True):
        a = S.ARCHIVE[str(y)]; A = S.ARCHDATA.get(str(y))
        if a.get("next"):
            title, desc, h1 = "2027 F1 Calendar: All %d Races & Sprint Dates | Track Almanac" % len(S.CAL2027), \
                "The confirmed 2027 Formula 1 calendar: %d Grands Prix from Bahrain to Abu Dhabi, %d sprint weekends and the line-ups announced so far." % (len(S.CAL2027), sum(1 for c in S.CAL2027 if c[6])), "2027 F1 calendar"
        elif a.get("live"):
            title, desc, h1 = "2026 Formula 1 Season | Track Almanac", "The 2026 Formula 1 season in progress: standings, calendar and results.", "2026 Formula 1 season"
        else:
            ch = A["D"][0] if A else a.get("champ")
            title = "%d Formula 1 Season: Results, Standings & Champion | Track Almanac" % y
            desc = "%d F1 season: %s won the title with %s points. Every Grand Prix winner, pole, fastest lap and full standings." % (y, ch[0], ch[3] if A else ch[2])
            h1 = "%d Formula 1 season" % y
        add("archive-%d" % y, title, desc, h1, archive_year_page(S, y), "SEASON ARCHIVE", home + [("Archive", "/archive/"), (str(y), "/archive/%d/" % y)])
    if S.PREWAR:
        n = sum(len(Y["races"]) for Y in S.PREWAR["years"].values())
        add("archive-1946-1949", "Grand Prix Racing 1946–1949: Before the F1 World Championship | Track Almanac",
            "Grand Prix racing from 1946 to 1949, before the Formula 1 World Championship: %d races with winners and cars, the Grandes Épreuves, and the most successful drivers and makes." % n,
            "Grand Prix racing 1946–1949", prewar_page(S), "SEASON ARCHIVE", home + [("Archive", "/archive/"), ("1946–1949", "/archive/1946-1949/")])
    dpath = os.path.join(ROOT, "src", "dictionary.json")
    if os.path.exists(dpath):
        DI = load_data(dpath)
        add("dictionary", "F1 Dictionary: %d Formula 1 Terms, Slang & Radio Calls Explained | Track Almanac" % len(DI["terms"]),
            "A to Z of %d Formula 1 words: aerodynamics, power units, tyres, strategy, flags and penalties, team radio codes, commentary catchphrases and fan slang." % len(DI["terms"]),
            "F1 dictionary", dictionary_page(DI), "F1 DICTIONARY", home + [("F1 dictionary", "/dictionary/")])
    # Predictor game: /game/ and /game/leaderboard/ are indexed; the signed-in pages are not
    gb = home + [("Predictor", "/game/")]
    add("game", "Track Almanac Predictor: Free F1 Prediction Game | Track Almanac",
        "Free Formula 1 prediction game: pick the top five and the pole sitter for every 2026 Grand Prix, score points for exact hits and play in leagues with friends. No prizes, no money.",
        "Track Almanac Predictor", game_page(S), "PREDICTOR", gb)
    add("game-lb", "Predictor Leaderboard %d | Track Almanac" % YEAR, "Season standings and race-by-race tables of the Track Almanac Predictor, the free F1 prediction game.",
        "Predictor leaderboard", game_lb_page(S), "PREDICTOR", gb + [("Leaderboard", "/game/leaderboard/")], path="/game/leaderboard/")
    for k, pth, t in (("game-picks", "/game/picks/", "My picks"), ("game-leagues", "/game/leagues/", "Leagues"), ("game-account", "/game/account/", "Account")):
        add(k, "%s · Predictor | Track Almanac" % t, "Track Almanac Predictor: %s." % t.lower(), t, pagehead(t, "Sign in to the Track Almanac Predictor to use this page.", "Predictor"),
            "PREDICTOR", gb + [(t, pth)], path=pth, noindex=True)
    for key in ("about", "contact", "privacy", "terms", "disclaimer"):
        t, main = static_page(S, key)
        add(key, "%s | Track Almanac" % t, "%s for Track Almanac, an unofficial Formula 1 results and statistics site." % t, t, main, t.upper(), home + [(t, S.path(key))])
    add("sitemap", "Site Map | Track Almanac", "Every page on Track Almanac: 2026 season, race pages, season archive and site information.", "Site map", "", "SITE MAP", home + [("Site map", "/site-map/")])
    pages[-1]["main"] = sitemap_page(S, pages)

    # write pages
    generated = []
    for p in pages:
        f = os.path.join(out, p["path"].strip("/"), "index.html") if p["path"] != "/" else os.path.join(out, "index.html")
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(page_html(p, body, assets, fonts)); generated.append(p["path"])
    nf = {"key": "notfound", "path": "/404.html", "title": "Page not found | Track Almanac", "desc": "This page does not exist on Track Almanac.", "h1": "Page not found",
          "main": '<article class="doc"><span class="lbl">404</span><h1>Page not found</h1><p>That page does not exist. Try the <a href="/">2026 season</a>, the <a href="/calendar/">calendar</a> or the <a href="/archive/">season archive</a>.</p></article>',
          "sheet": "NOT FOUND", "ld": [], "noindex": True}
    open(os.path.join(out, "404.html"), "w", encoding="utf-8").write(page_html(nf, body, assets, fonts))

    # sitemap with per-page lastmod (changes only when the page's own content changes)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    today = datetime.date.today().isoformat(); lm = {}
    for p in pages:
        h = hashlib.sha1((p["title"] + p["desc"] + p["main"]).encode()).hexdigest()
        old = state.get("pages", {}).get(p["path"])
        lm[p["path"]] = {"hash": h, "lastmod": old["lastmod"] if old and old["hash"] == h else today}
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in [x for x in pages if not x.get("noindex")]:
        pr = "1.0" if p["path"] == "/" else "0.8" if p["path"] in ("/championship/", "/calendar/", "/drivers/", "/teams/") or p["path"].startswith("/races/") else "0.6"
        xml.append("  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (SITE, p["path"], lm[p["path"]]["lastmod"], pr))
    xml.append("</urlset>")
    open(os.path.join(out, "sitemap.xml"), "w").write("\n".join(xml) + "\n")
    return pages, generated, lm, written


def main():
    check = "--check" in sys.argv
    if check:
        import tempfile; out = tempfile.mkdtemp()
    else:
        out = ROOT
        old = json.load(open(STATE)) if os.path.exists(STATE) else {}
        for path in old.get("generated", []):   # remove pages that no longer exist
            d = os.path.join(ROOT, path.strip("/"))
            if path != "/" and os.path.isfile(os.path.join(d, "index.html")): os.remove(os.path.join(d, "index.html"))
    pages, generated, lm, imgs = build(out)
    if not check:
        for dp, dn, fn in os.walk(ROOT, topdown=False):   # tidy empty folders left by removed pages
            if ".git" in dp or dp == ROOT: continue
            if not os.listdir(dp): os.rmdir(dp)
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump({"generated": generated, "pages": lm}, open(STATE, "w"), indent=1)
    sizes = sorted(((os.path.getsize(os.path.join(out, p.strip("/"), "index.html") if p != "/" else os.path.join(out, "index.html")), p) for p in generated), reverse=True)
    print("pages: %d  images: %d  largest page: %d KB (%s)  data.js: %d KB  app.js: %d KB  style.css: %d KB" % (
        len(generated), len(imgs), sizes[0][0] // 1024, sizes[0][1], os.path.getsize(os.path.join(out, "data.js")) // 1024,
        os.path.getsize(os.path.join(out, "app.js")) // 1024, os.path.getsize(os.path.join(out, "style.css")) // 1024))
    if check: print("checked into", out)


if __name__ == "__main__":
    main()
