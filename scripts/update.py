#!/usr/bin/env python3
"""
Track Almanac auto-update.

Adds missing session results to src/data.json from two free sources, then rebuilds
the site with build.py:

  Jolpica-F1  https://api.jolpi.ca/ergast/f1   race, sprint and qualifying results,
                                               standings, schedule
  OpenF1      https://api.openf1.org/v1        practice and sprint-qualifying
                                               classifications, lap-by-lap timing,
                                               pit stops, schedule

Rules
  * Only adds what is missing. A session table, result, lap chart or note that
    already exists is never changed, so hand corrections stay. Standings
    (DRIVERS, CONSTRUCTORS) only change by the points of a sprint or race the
    script adds itself.
  * Never writes race notes (res.cls) or archive text.
  * If a source has no data yet, that session is skipped and the next run tries again.
  * Checks before anything is saved: 20-22 cars per session; race and sprint
    finishing order agree between Jolpica-F1 and OpenF1; points add up to the
    published standings; standings sorted. A session that fails a check is not
    saved and the run exits with code 1, so GitHub emails the owner.
  * Schedule: for the current and next round, the time each source reports is
    remembered in .automation/schedule-seen.json. SCHED is only changed when a
    source's time CHANGES compared with what it reported before and both sources
    agree on the new time (more than 5 minutes from SCHED). A difference that was
    already there is left alone, so hand-entered times stick.
  * A check failure fails the run (GitHub emails the owner) only the first time it
    appears; repeats are logged as warnings and the run exits 0. Reported failures
    are remembered in .automation/check-failures.json and forgotten once resolved.

Usage
  python3 scripts/update.py                      normal run (writes data, rebuilds)
  python3 scripts/update.py --dry-run            report only, write nothing
  python3 scripts/update.py --selftest 17        rebuild round 17 from the APIs on a
                                                 copy of the data and compare
  options: --now 2026-10-11T15:00:00Z  --message-file F  --record DIR  --replay DIR

Plain Python 3, standard library only.
"""
import argparse, copy, datetime as dt, hashlib, json, os, subprocess, sys, time, unicodedata
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build  # noqa: E402  (load_data, save_data, DATA, YEAR)

YEAR = build.YEAR
JOLPICA = "https://api.jolpi.ca/ergast/f1"
OPENF1 = "https://api.openf1.org/v1"
UA = "TrackAlmanac-updater/1.0 (+https://trackalmanac.com)"

KEY = {"Practice 1": "fp1", "Practice 2": "fp2", "Practice 3": "fp3", "Sprint Qualifying": "sq",
       "Sprint": "sprint", "Qualifying": "quali", "Grand Prix": "race"}
OF1_NAMES = {"Practice 1": ("Practice 1",), "Practice 2": ("Practice 2",), "Practice 3": ("Practice 3",),
             "Sprint Qualifying": ("Sprint Qualifying", "Sprint Shootout"), "Sprint": ("Sprint",),
             "Qualifying": ("Qualifying",), "Grand Prix": ("Race",)}
JOL_KEYS = {"Practice 1": ("FirstPractice",), "Practice 2": ("SecondPractice",), "Practice 3": ("ThirdPractice",),
            "Sprint Qualifying": ("SprintQualifying", "SprintShootout"), "Sprint": ("Sprint",),
            "Qualifying": ("Qualifying",), "Grand Prix": None}
# Jolpica constructorId -> team name used on the site
TEAM_IDS = {"mercedes": "Mercedes", "ferrari": "Ferrari", "mclaren": "McLaren", "red_bull": "Red Bull Racing",
            "rb": "Racing Bulls", "racing_bulls": "Racing Bulls", "alpine": "Alpine", "haas": "Haas F1 Team",
            "audi": "Audi", "sauber": "Audi", "williams": "Williams", "aston_martin": "Aston Martin", "cadillac": "Cadillac"}
NATION = {"Italian": "ITA", "British": "GBR", "Dutch": "NED", "Monegasque": "MON", "Australian": "AUS", "French": "FRA",
          "New Zealander": "NZL", "Spanish": "ESP", "German": "GER", "Thai": "THA", "Argentine": "ARG", "Argentinian": "ARG",
          "Brazilian": "BRA", "Canadian": "CAN", "Mexican": "MEX", "Finnish": "FIN", "Japanese": "JPN", "American": "USA",
          "Danish": "DEN", "Chinese": "CHN", "Swiss": "SUI", "Belgian": "BEL", "Austrian": "AUT", "Polish": "POL",
          "Swedish": "SWE", "Estonian": "EST", "Indian": "IND", "Israeli": "ISR", "Irish": "IRL", "Russian": "RUS"}
SCHEDULE_SEEN = os.path.join(ROOT, ".automation", "schedule-seen.json")   # session times each source reported last
FAILURES_SEEN = os.path.join(ROOT, ".automation", "check-failures.json")  # check failures already reported by email
MIN_CARS, MAX_CARS = 20, 22
LIVE_GRACE = dt.timedelta(minutes=10)   # wait this long after a session's scheduled end


class NotReady(Exception):
    """A source has no (complete) data yet: skip quietly, the next run tries again."""


class CheckFailed(Exception):
    """Data disagree or look wrong: don't publish, fail the run."""


# ---------------------------------------------------------------- HTTP with cache, rate limits, record/replay
class Http:
    def __init__(self, record=None, replay=None, log=print):
        self.cache, self.record, self.replay, self.log = {}, record, replay, log
        self.last = {}
        self.gap = {"openf1": 2.1, "jolpica": 0.35, "github": 0.1}   # OpenF1 free: 30 req/min. Jolpica: 4 req/s, 500/h.

    def _file(self, url):
        return os.path.join(self.record or self.replay, hashlib.md5(url.encode()).hexdigest()[:16] + ".json")

    def get(self, url):
        if url in self.cache: return self.cache[url]
        if self.replay:
            f = self._file(url)
            if not os.path.exists(f): raise NotReady("no recorded response for " + url)
            data = json.load(open(f))
        else:
            data = self._fetch(url)
            if self.record:
                os.makedirs(self.record, exist_ok=True)
                json.dump(data, open(self._file(url), "w"))
                with open(os.path.join(self.record, "index.txt"), "a") as f: f.write(os.path.basename(self._file(url)) + " " + url + "\n")
        self.cache[url] = data
        return data

    def _fetch(self, url):
        host = "openf1" if "openf1" in url else "github" if "githubusercontent" in url else "jolpica"
        for attempt in range(4):
            wait = self.last.get(host, 0) + self.gap[host] - time.time()
            if wait > 0: time.sleep(wait)
            self.last[host] = time.time()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 404 and host == "openf1": return []        # OpenF1: 404 = "No results found"
                if e.code == 404 and host == "github": return None      # file not published (yet)
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * (attempt + 1)); continue
                raise NotReady("%s answered HTTP %d for %s" % (host, e.code, url))
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                if attempt < 3: time.sleep(5 * (attempt + 1)); continue
                raise NotReady("%s unreachable (%s) for %s" % (host, e, url))


# ---------------------------------------------------------------- small helpers
def parse_t(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
def iso_z(t): return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s or "").lower() if "a" <= c <= "z")
def ascii_name(s): return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
def num(v):
    f = float(v); return int(f) if f == int(f) else f


def fmt_lap(sec):
    ms = int(round(sec * 1000)); m, rest = divmod(ms, 60000)
    return "%d:%02d.%03d" % (m, rest // 1000, rest % 1000) if m else "%d.%03d" % (rest // 1000, rest % 1000)


def lap_secs(s):
    p = s.split(":"); return float(p[-1]) + (int(p[-2]) * 60 if len(p) > 1 else 0) + (int(p[-3]) * 3600 if len(p) > 2 else 0)


def plus_laps(n): return "+%d lap%s" % (n, "" if n == 1 else "s")


class People:
    """Maps car numbers to the names the site uses."""
    def __init__(self, D):
        self.D = D
        self.surname = {}                       # number -> surname as written in SEASON tables
        for r in sorted(D["SEASON"], key=int):
            for k, rows in D["SEASON"][r].items():
                if k in KEY.values():
                    for row in rows: self.surname[row[1]] = row[2]
        self.extra = {}                         # number -> {"full", "code", "nat"} for drivers new to the site

    def learn(self, number, given, family, code=None, nationality=None):
        if number not in self.surname: self.surname[number] = ascii_name(family)
        if not self.full_or_none(number):
            self.extra[number] = {"full": "%s %s" % (given, family), "code": code, "nat": NATION.get(nationality or "", "")}

    def sur(self, number):
        if number not in self.surname: raise CheckFailed("unknown car number %s (no name available)" % number)
        return self.surname[number]

    def full_or_none(self, number):
        s = norm(self.surname.get(number))
        for d in self.D["DRIVERS"]:
            if norm(d[0].split()[-1]) == s: return d[0]
        return None

    def full(self, number):
        return self.full_or_none(number) or (self.extra.get(number) or {}).get("full") or self.sur(number)


# ---------------------------------------------------------------- sources
class Sources:
    def __init__(self, http): self.h = http

    def jolpica(self, path):
        d = self.h.get("%s/%d%s.json?limit=100" % (JOLPICA, YEAR, "/" + path if path else ""))
        return d["MRData"]

    def race_table(self, rnd, kind, key):
        races = self.jolpica("%d/%s" % (rnd, kind))["RaceTable"]["Races"]
        return races[0].get(key, []) if races else []

    def schedule(self):
        return {int(r["round"]): r for r in self.jolpica("")["RaceTable"]["Races"]}

    def standings(self, rnd, kind):
        m = self.jolpica("%d/%s" % (rnd, kind))["StandingsTable"]
        lists = m.get("StandingsLists") or []
        if not lists or int(lists[0]["round"]) != rnd: raise NotReady("Jolpica-F1 standings after round %d not published yet" % rnd)
        return lists[0]["DriverStandings" if kind == "driverStandings" else "ConstructorStandings"]

    def of1(self, path):
        d = self.h.get("%s/%s" % (OPENF1, path))
        return d if isinstance(d, list) else []

    def of1_sessions(self): return self.of1("sessions?year=%d" % YEAR)

    def of1_session(self, name, start):
        """The OpenF1 session for a SCHED entry: same name, start within 36 h of the scheduled start."""
        best = None
        for s in self.of1_sessions():
            if s.get("session_name") not in OF1_NAMES[name] or s.get("is_cancelled"): continue
            gap = abs((parse_t(s["date_start"]) - start).total_seconds())
            if gap <= 36 * 3600 and (best is None or gap < best[0]): best = (gap, s)
        return best[1] if best else None


# ---------------------------------------------------------------- building rows in the site's formats
def of1_results(src, name, start):
    s = src.of1_session(name, start)
    if not s: raise NotReady("OpenF1 has no %s session near %s" % (name, iso_z(start)))
    res = src.of1("session_result?session_key=%d" % s["session_key"])
    if not res: raise NotReady("OpenF1 has no %s classification yet" % name)
    return s, res


def of1_order(res):
    """OpenF1 rows: numeric positions first, then the rest in API order."""
    isnum = lambda x: isinstance(x.get("position"), int)
    return sorted([x for x in res if isnum(x)], key=lambda x: x["position"]) + [x for x in res if not isnum(x)]


def learn_of1_drivers(src, people, session_key, numbers):
    if all(n in people.surname for n in numbers): return
    for d in src.of1("drivers?session_key=%d" % session_key):
        people.learn(d["driver_number"], d.get("first_name") or "", d.get("last_name") or d.get("broadcast_name") or "", d.get("name_acronym"))


def practice_rows(src, people, name, start):
    s, res = of1_results(src, name, start)
    learn_of1_drivers(src, people, s["session_key"], [x["driver_number"] for x in res])
    rows, lead = [], None
    for i, x in enumerate(of1_order(res)):
        d, gap = x.get("duration"), x.get("gap_to_leader")
        if isinstance(d, list) or isinstance(gap, list): raise CheckFailed("%s: unexpected OpenF1 format" % name)
        if i == 0 and d: t, lead = fmt_lap(d), d
        elif d and isinstance(gap, (int, float)): t = "+%.3fs" % gap
        elif d and lead: t = "+%.3fs" % (d - lead)
        else: t = ""
        rows.append([str(i + 1), x["driver_number"], people.sur(x["driver_number"]), t, str(x.get("number_of_laps") or 0)])
    if not rows[0][3]: raise NotReady("%s: no lap times in OpenF1 yet" % name)
    return rows


def q_cells(times, pos_i, n):
    """Q1/Q2/Q3 cells: a time, "No time" for a part the driver reached without a time, "" otherwise."""
    reach = [n, n - 6, 10] if n > 16 else [n, n - 5, 10]
    out = []
    for k in range(3):
        v = times[k] if k < len(times) else None
        out.append(v if v else ("No time" if isinstance(pos_i, int) and pos_i <= reach[k] else ""))
    return out


def sq_rows(src, people, start):
    s, res = of1_results(src, "Sprint Qualifying", start)
    learn_of1_drivers(src, people, s["session_key"], [x["driver_number"] for x in res])
    order, rows = of1_order(res), []
    for i, x in enumerate(order):
        dur = x.get("duration") if isinstance(x.get("duration"), list) else [x.get("duration")]
        times = [fmt_lap(v) if v else "" for v in dur]
        pos = "DQ" if x.get("dsq") else str(i + 1)
        rows.append([pos, x["driver_number"], people.sur(x["driver_number"])] + q_cells(times, i + 1, len(order)) + [str(x.get("number_of_laps") or 0)])
    if not rows[0][3] or rows[0][3] == "No time": raise NotReady("Sprint Qualifying: no times in OpenF1 yet")
    return rows


def learn_jolpica(people, rows):
    for x in rows:
        d = x["Driver"]; people.learn(int(x["number"]), d.get("givenName", ""), d.get("familyName", ""), d.get("code"), d.get("nationality"))


def quali_rows(src, people, rnd, start):
    q = src.race_table(rnd, "qualifying", "QualifyingResults")
    if not q: raise NotReady("Jolpica-F1 has no qualifying result yet")
    learn_jolpica(people, q)
    laps = {}
    try:
        _, res = of1_results(src, "Qualifying", start)
        laps = {x["driver_number"]: str(x.get("number_of_laps") or 0) for x in res}
    except NotReady:
        pass
    q = sorted(q, key=lambda x: int(x["position"]))
    rows = []
    for x in q:
        n, p = int(x["number"]), int(x["position"])
        rows.append([str(p), n, people.sur(n)] + q_cells([x.get("Q1", ""), x.get("Q2", ""), x.get("Q3", "")], p, len(q)) + [laps.get(n, "—")])
    return rows


def race_rows(src, people, rnd, start, sprint, grid_table=None):
    kind, key = ("sprint", "SprintResults") if sprint else ("results", "Results")
    label = "Sprint" if sprint else "Grand Prix"
    R = src.race_table(rnd, kind, key)
    if not R: raise NotReady("Jolpica-F1 has no %s result yet" % label)
    learn_jolpica(people, R)
    R = sorted(R, key=lambda x: int(x["position"]))
    wl = int(R[0]["laps"])
    pl = {g[1]: g[0] for g in (grid_table or [])}   # pit lane starts from the hand-entered starting grid, if any
    rows = []
    for i, x in enumerate(R):
        n, pt, laps, st = int(x["number"]), x["positionText"], int(x["laps"]), x.get("status", "")
        if pt.isdigit():
            pos = pt; t = (x.get("Time") or {}).get("time", "")
            if i == 0: t = t
            elif laps < wl: t = plus_laps(wl - laps)
            elif t: t = t if ":" in t else t + "s"
            else: raise CheckFailed("%s: no time for classified P%s" % (label, pt))
        elif pt == "D":
            pos, t = "DQ", "DSQ"
        elif pt == "W" or "start" in st.lower() or "withdr" in st.lower():
            pos, t = "NC", "DNS"
        elif pt == "N":
            pos, t = "NC", plus_laps(wl - laps) if laps < wl else "DNF"
        else:
            pos, t = "NC", "DNF"
        row = [pos, n, people.sur(n), laps, t, num(x.get("points", 0))]
        if not sprint:
            g = int(x.get("grid") or 0); row.append("PL" if g == 0 or pl.get(n) == "PL" else g)
        rows.append(row)
    return R, rows


def cross_check(src, label, name, start, R):
    """Jolpica-F1 finishing order must match OpenF1's final positions."""
    _, res = of1_results(src, name, start)
    of1 = {x["driver_number"]: x.get("position") for x in res}
    if len(of1) != len(R): raise CheckFailed("%s: Jolpica-F1 lists %d cars, OpenF1 %d" % (label, len(R), len(of1)))
    for x in R:
        if not x["positionText"].isdigit(): continue
        n, p = int(x["number"]), int(x["position"])
        if of1.get(n) is None: raise NotReady("%s: OpenF1 has no final position for car %d yet" % (label, n))
        if of1[n] != p:
            raise CheckFailed("%s: finishing order disagrees: car %d is P%d in Jolpica-F1 but P%s in OpenF1" % (label, n, p, of1[n]))


def team_name(D, cid, cname, people_team=None):
    names = {c[0] for c in D["CONSTRUCTORS"]}
    t = TEAM_IDS.get(cid)
    if t in names: return t
    for n in names:
        if norm(n) == norm(cname) or norm(n) in norm(cname) or norm(cname) in norm(n): return n
    if people_team in names: return people_team
    raise CheckFailed("unknown constructor %s (%s)" % (cname, cid))


def add_points(D, people, R, log):
    """Adds the session's points to DRIVERS and CONSTRUCTORS."""
    for x in R:
        p = num(x.get("points", 0)); n = int(x["number"])
        full = people.full(n)
        drv = next((d for d in D["DRIVERS"] if d[0] == full), None)
        team = team_name(D, x["Constructor"]["constructorId"], x["Constructor"]["name"], drv[2] if drv else None)
        if drv is None:
            e = people.extra.get(n) or {}
            drv = [full, e.get("nat", ""), team, 0]; D["DRIVERS"].append(drv)
            log("  new driver in standings: %s (%s)" % (full, team))
        if p:
            drv[3] = num(drv[3] + p)
            con = next(c for c in D["CONSTRUCTORS"] if c[0] == team)
            con[1] = num(con[1] + p)


def check_standings(D, src, people, rnd):
    js = src.standings(rnd, "driverStandings")
    jc = src.standings(rnd, "constructorStandings")
    order = {}
    for x in js:
        n = int(x["Driver"].get("permanentNumber") or 0)
        nm = people.full(n) if n in people.surname else "%s %s" % (x["Driver"]["givenName"], x["Driver"]["familyName"])
        d = next((d for d in D["DRIVERS"] if d[0] == nm or norm(d[0].split()[-1]) == norm(x["Driver"]["familyName"])), None)
        if d is None:
            if num(x["points"]): raise CheckFailed("standings: %s has %s points but is not on the site" % (nm, x["points"]))
            continue
        if num(d[3]) != num(x["points"]):
            raise CheckFailed("standings: %s has %s points on the site, %s in the published standings" % (d[0], d[3], x["points"]))
        order[d[0]] = int(x["position"])
    for x in jc:
        t = team_name(D, x["Constructor"]["constructorId"], x["Constructor"]["name"])
        c = next(c for c in D["CONSTRUCTORS"] if c[0] == t)
        if num(c[1]) != num(x["points"]):
            raise CheckFailed("standings: %s has %s points on the site, %s in the published standings" % (t, c[1], x["points"]))
        order[t] = int(x["position"])
    D["DRIVERS"].sort(key=lambda d: (-d[3], order.get(d[0], 99)))
    D["CONSTRUCTORS"].sort(key=lambda c: (-c[1], order.get(c[0], 99)))
    check_sorted(D)


def check_sorted(D):
    for k, i in (("DRIVERS", 3), ("CONSTRUCTORS", 1)):
        pts = [x[i] for x in D[k]]
        if pts != sorted(pts, reverse=True): raise CheckFailed("%s not sorted by points" % k)


def check_cars(label, rows):
    if not MIN_CARS <= len(rows) <= MAX_CARS: raise CheckFailed("%s: %d cars (expected %d-%d)" % (label, len(rows), MIN_CARS, MAX_CARS))
    nums = [r[1] for r in rows]
    if len(set(nums)) != len(nums): raise CheckFailed("%s: a car number appears twice" % label)


def race_res(D, src, people, rnd, rows, R, race_start):
    r = race_of(D, rnd)
    w = rows[0]
    if w[0] != "1": raise CheckFailed("Grand Prix: no winner")
    pod = [[people.full(rows[i][1]), "Winner" if i == 0 else rows[i][4]] for i in range(3)]
    S = D["SEASON"].get(str(rnd), {})
    if S.get("quali"): pole = people.full(S["quali"][0][1])
    else:
        q = src.race_table(rnd, "qualifying", "QualifyingResults")
        if not q: raise NotReady("Jolpica-F1 has no qualifying result (for pole) yet")
        pole = people.full(int(min(q, key=lambda x: int(x["position"]))["number"]))
    fl = next((x for x in R if (x.get("FastestLap") or {}).get("rank") == "1"), None)
    res = {"time": w[4], "pod": pod, "pole": pole}
    if fl:
        t = fl["FastestLap"]["Time"]["time"]
        res["fl"] = [people.full(int(fl["number"])), t, int(fl["FastestLap"]["lap"]), round(r["len"] * 3600 / lap_secs(t), 3)]
    else:
        raise NotReady("Jolpica-F1 has no fastest lap yet")
    try:   # fastest pit stop (stationary time), only when OpenF1 publishes it
        s = src.of1_session("Grand Prix", race_start)
        stops = [p for p in src.of1("pit?session_key=%d" % s["session_key"]) if p.get("stop_duration")] if s else []
        if stops:
            b = min(stops, key=lambda p: p["stop_duration"]); n = b["driver_number"]
            team = next((d[2] for d in D["DRIVERS"] if d[0] == people.full(n)), "")
            res["pit"] = [team, people.full(n), "%.2fs" % b["stop_duration"]]
    except NotReady:
        pass
    return res


def lap_chart(src, people, rows, race_start):
    """LAPS[round]: c = driver codes in race-table order; l[i] = indices of the cars in
    running order at the end of lap i+1."""
    s = src.of1_session("Grand Prix", race_start)
    if not s: raise NotReady("OpenF1 has no race session")
    laps = src.of1("laps?session_key=%d" % s["session_key"])
    if not laps: raise NotReady("OpenF1 has no lap data yet")
    codes = {}
    for d in src.of1("drivers?session_key=%d" % s["session_key"]): codes[d["driver_number"]] = d.get("name_acronym")
    idx = {row[1]: i for i, row in enumerate(rows)}
    by = {}
    for x in laps:
        if x.get("driver_number") in idx and x.get("lap_number") and x.get("date_start"):
            by.setdefault(x["driver_number"], {})[x["lap_number"]] = x
    nL = max(r[3] for r in rows if isinstance(r[3], int))
    if max((max(v) for v in by.values()), default=0) < nL: raise NotReady("OpenF1 lap data incomplete")
    ends = {}
    for n, L in by.items():
        for k, x in L.items():
            if x.get("lap_duration"): ends[(n, k)] = parse_t(x["date_start"]) + dt.timedelta(seconds=x["lap_duration"])
            elif (k + 1) in L: ends[(n, k)] = parse_t(L[k + 1]["date_start"])
    out = []
    for k in range(1, nL + 1):
        done = sorted((ends[(n, k)], n) for n in by if (n, k) in ends)
        out.append([idx[n] for _, n in done])
    c = []
    for row in rows:
        code = codes.get(row[1]) or (people.extra.get(row[1]) or {}).get("code")
        if not code: raise NotReady("no driver code for car %d" % row[1])
        c.append(code)
    return {"c": c, "l": out}


# ---------------------------------------------------------------- race extras: safety cars, tyre stints
COMPOUND = {"SOFT": "S", "MEDIUM": "M", "HARD": "H", "INTERMEDIATE": "I", "WET": "W"}
EXTRAS = ("neutral", "stints")
EXTRAS_DAYS = 7        # normal runs fill extras for races of the last 7 days; --backfill does every race


def neutral_periods(msgs, nL):
    """SEASON[r].neutral: [["SC"|"VSC"|"RF", first lap, last lap], ...] from OpenF1 race
    control messages, in lap order. [] means the race had none.
      SC   "SAFETY CAR DEPLOYED" ... "SAFETY CAR IN THIS LAP"
      VSC  "VSC DEPLOYED" / "VIRTUAL SAFETY CAR DEPLOYED" ... "VSC ENDING"; a VSC turned
           into a safety car ends the lap before the safety car comes out
      RF   "RED FLAG" (text or flag); ends any running SC/VSC; one lap: the lap it came out
      PIT  "ALL CARS / SAFETY CAR THROUGH THE PIT LANE": the field drove through the pit lane"""
    out, open_ = [], {}
    def lap(m): return max(1, min(nL, m.get("lap_number") or 1))
    def close(kind, l):
        if kind in open_: a = open_.pop(kind); out.append([kind, a, max(a, l)])
    for m in sorted(msgs, key=lambda x: x.get("date") or ""):
        t = (m.get("message") or "").upper(); flag = (m.get("flag") or "").upper(); L = lap(m)
        if flag == "CHEQUERED" or "CHEQUERED FLAG" in t: break
        if t.startswith(("INCIDENT", "FIA STEWARDS", "NOTED")) or any(w in t for w in ("INFRINGEMENT", "INVESTIGAT", "PENALTY")):
            continue   # stewards' notes ("RED FLAG INFRINGEMENT", "VSC INFRINGEMENT") are not track status
        if "RED FLAG" in t or (flag == "RED" and (m.get("scope") or "Track") == "Track"):
            close("SC", L); close("VSC", L)
            if "RF" not in open_: open_["RF"] = L
        elif "RF" in open_ and any(w in t for w in ("RESUME", "SESSION STARTED", "STANDING START", "ROLLING START")):
            close("RF", open_["RF"])
        elif "THROUGH THE PIT LANE" in t:
            out.append(["PIT", L, L])                  # field sent through the pit lane (no tyre change)
        elif t.startswith("VSC ") or "VIRTUAL SAFETY CAR" in t:
            if "DEPLOYED" in t and "VSC" not in open_: open_["VSC"] = L
            elif "ENDING" in t: close("VSC", L)
        elif "SAFETY CAR DEPLOYED" in t:
            close("VSC", L - 1)
            if "SC" not in open_: open_["SC"] = L
        elif "SAFETY CAR IN THIS LAP" in t:
            close("SC", L)
    for k in list(open_): close(k, nL if k != "RF" else open_[k])
    return sorted(out, key=lambda x: x[1])   # stable: same-lap periods keep the order they happened in


def race_extra(src, people, rnd, key, rows, start, D):
    nL = max(r[3] for r in rows if isinstance(r[3], int))
    s = src.of1_session("Grand Prix", start)
    if key == "neutral":
        if not s: raise NotReady("OpenF1 has no race session")
        msgs = src.of1("race_control?session_key=%d" % s["session_key"])
        if not msgs: raise NotReady("OpenF1 has no race control messages yet")
        if not any((m.get("flag") or "").upper() == "CHEQUERED" for m in msgs): raise NotReady("race control incomplete (no chequered flag)")
        return neutral_periods(msgs, nL)
    nums = [r[1] for r in rows]
    if key == "stints":
        return race_stints(src, rnd, rows, start, D, s)


# Tyre stints come from TracingInsights (github.com/TracingInsights/<year>, Apache-2.0): per-lap
# compound, stint and tyre life from the official F1 timing feed, processed with FastF1.
# OpenF1's own stints were checked against the official pit laps for all 2026 races and were
# often a lap early or scrambled (wet races, pit-lane starts), so OpenF1 is only used to name a
# compound the timing feed left unknown.
TI_BASE = "https://raw.githubusercontent.com/TracingInsights/%d/main/" % YEAR
TI_ALIASES = {"Barcelona-Catalunya Grand Prix": ["Barcelona Grand Prix", "Spanish Grand Prix"],
              "Spanish Grand Prix": ["Madrid Grand Prix"], "United States Grand Prix": ["United States Grand Prix"],
              "Mexico City Grand Prix": ["Mexican Grand Prix"], "Mexican Grand Prix": ["Mexico City Grand Prix"],
              "Brazilian Grand Prix": ["São Paulo Grand Prix"], "São Paulo Grand Prix": ["Brazilian Grand Prix"]}


def ti_url(*parts):
    import urllib.parse
    return TI_BASE + "/".join(urllib.parse.quote(p) for p in parts)


def ti_folder(src, rnd, D):
    r = race_of(D, rnd)
    cands = [r["gp"], r["gp"].replace(" (Sepang)", "")] + TI_ALIASES.get(r["gp"], [])
    try:
        jr = src.schedule().get(rnd)
        if jr: cands.append(jr["raceName"])
    except NotReady:
        pass
    for c in dict.fromkeys(cands):
        d = src.h.get(ti_url(c, "Race", "drivers.json"))
        if isinstance(d, dict) and d.get("drivers"): return c, d["drivers"]
    raise NotReady("TracingInsights has no race data for %s yet" % r["gp"])


def ti_driver_stints(L, done):
    """([[compound, first lap, last lap, laps on the set when fitted], ...], {pit lane laps without a tyre change})
    from one driver's laptimes.json. The timing feed starts a new stint on every trip down the pit
    lane; when the compound is the same and the tyre age just carries on, it's the same set, so the
    stints are joined (e.g. the field sent through the pit lane behind the safety car)."""
    def i(v):
        try: return int(float(v))
        except (TypeError, ValueError): return None
    laps = sorted((i(l), c, i(st), i(life)) for l, c, st, life in zip(L.get("lap", []), L.get("compound", []), L.get("stint", []), L.get("life", [])) if i(l))
    out, passes, last_life = [], set(), None
    for lap, comp, stint, life in laps:
        if lap > done: break
        c = COMPOUND.get((comp or "").upper(), "?")
        same_cmp = bool(out) and (out[-1][0] == c or "?" in (c, out[-1][0]))
        if out and (stint is None or out[-1][4] == stint) and same_cmp:
            out[-1][2] = lap
        elif out and same_cmp and life is not None and last_life is not None and life == last_life + 1:
            passes.add(out[-1][2]); out[-1][2] = lap; out[-1][4] = stint     # same set, carried on
        else:
            out.append([c, lap, lap, max(0, (life or 1) - 1), stint if stint is not None else (out[-1][4] + 1 if out else 1)])
        if out[-1][0] == "?" and c != "?": out[-1][0] = c
        last_life = life
    return [x[:4] for x in out], passes


def race_stints(src, rnd, rows, start, D, of1_session):
    folder, drivers = ti_folder(src, rnd, D)
    done = {r[1]: r[3] if isinstance(r[3], int) else 0 for r in rows}
    want = [n for n in done if done[n] > 0]
    out, passes = {}, {}
    for d in drivers:
        try: n = int(d.get("dn"))
        except (TypeError, ValueError): continue
        if n not in want: continue
        L = src.h.get(ti_url(folder, "Race", d["driver"], "laptimes.json"))
        if not isinstance(L, dict) or not L.get("lap"): raise NotReady("TracingInsights lap data for %s not published yet" % d["driver"])
        out[n], passes[n] = ti_driver_stints(L, done[n])
    missing = [n for n in want if not out.get(n)]
    if missing: raise NotReady("TracingInsights has no tyre data yet for cars %s" % missing)
    # name compounds the timing feed left unknown, from OpenF1, only when it gives one compound for those laps
    if any(x[0] == "?" for v in out.values() for x in v) and of1_session:
        o = src.of1("stints?session_key=%d" % of1_session["session_key"])
        for n, v in out.items():
            for x in v:
                if x[0] != "?": continue
                cs = {COMPOUND.get((y.get("compound") or "").upper()) for y in o if y.get("driver_number") == n and y.get("lap_start")
                      and y["lap_start"] <= x[2] and (y.get("lap_end") or 999) >= x[1]} - {None}
                if len(cs) == 1: x[0] = cs.pop()
    # check against the official pit laps: every stop starts a new stint on the next lap, and every
    # new stint follows a stop (or a red flag, when teams may change tyres in the pit lane)
    R = src.race_table(rnd, "results", "Results")
    ids = {x["Driver"]["driverId"]: int(x["number"]) for x in R}
    P = src.race_table(rnd, "pitstops", "PitStops")
    if not P: raise NotReady("Jolpica-F1 has no pit stops yet (needed to check the tyre data)")
    pits = {}
    for p in P:
        if ids.get(p["driverId"]) is not None: pits.setdefault(ids[p["driverId"]], set()).add(int(p["lap"]))
    nz = D["SEASON"].get(str(rnd), {}).get("neutral") or []
    rf = [a for k, a, b in nz if k == "RF"]
    pit_laps = [a for k, a, b in nz if k == "PIT"]   # field through the pit lane: counted as a stop, no tyre change
    bad = []
    for n, v in out.items():
        if v[0][1] != 1 or v[-1][2] != done[n] or any(v[k][2] + 1 != v[k + 1][1] for k in range(len(v) - 1)):
            bad.append("car %d: stints don't cover laps 1-%d" % (n, done[n])); continue
        b = {x[1] - 1 for x in v[1:]}
        stops = {l for l in pits.get(n, set()) if l < done[n]}
        nochange = stops - b - passes.get(n, set()) - set(pit_laps)
        if nochange: bad.append("car %d: stop on lap %s but no tyre change in the timing data" % (n, sorted(nochange)))
        extra = {l for l in b - stops if not any(abs(l - x) <= 1 for x in rf)}
        if extra: bad.append("car %d: tyre change after lap %s without a pit stop" % (n, sorted(extra)))
    if bad: raise CheckFailed("tyre stints disagree with the official pit stops: " + "; ".join(bad[:6]))
    return {str(r[1]): out[r[1]] for r in rows if r[1] in out}


def race_of(D, rnd): return next(r for r in D["RACES"] if r["r"] == rnd)


# ---------------------------------------------------------------- the update
class Updater:
    def __init__(self, D, src, now, log=print, seen=None, backfill=False):
        self.D, self.src, self.now, self.log, self.backfill = D, src, now, log, backfill
        self.seen = seen if seen is not None else {}   # {round: {session: {"jolpica": iso, "openf1": iso}}}
        self.added, self.failures, self.schedule_moves, self.schedule_notes = [], [], [], []

    def ended(self, start, dur): return self.now >= start + dt.timedelta(minutes=dur or 120) + LIVE_GRACE

    def run(self, rounds=None, schedule=True):
        D = self.D
        if schedule:
            try: self.check_schedule()
            except NotReady as e: self.log("schedule check skipped: %s" % e)
        for rk in sorted(D["SCHED"], key=int):
            rnd = int(rk)
            if rounds and rnd not in rounds: continue
            self.do_round(rnd)
        if self.backfill:
            try: self.backfill_rounds()
            except NotReady as e: self.log("backfill: %s" % e)
        return self

    # -- one round
    def do_round(self, rnd):
        D = self.D
        tz, sessions = D["SCHED"][str(rnd)]
        ended = [(n, parse_t(s), d) for n, s, d in sessions if self.ended(parse_t(s), d)]
        if not ended: return
        r = race_of(D, rnd)
        people = People(D)
        S = D["SEASON"].get(str(rnd), {})
        # sessions without points: each on its own
        for name, start, dur in ended:
            k = KEY.get(name)
            if k in ("sprint", "race") or k is None or k in S: continue
            self.attempt(rnd, name, lambda: self.add_plain(rnd, name, k, start, people))
            S = D["SEASON"].get(str(rnd), {})
        # sprint and race: points and standings checked together
        pts = [(n, s) for n, s, d in ended if KEY.get(n) in ("sprint", "race") and KEY[n] not in S]
        if pts:
            self.attempt(rnd, " + ".join(n for n, _ in pts), lambda: self.add_points_sessions(rnd, pts, sessions))
            S = D["SEASON"].get(str(rnd), {})
        race_ended = next(((s, d) for n, s, d in ended if n == "Grand Prix"), None)
        if race_ended and S.get("race") and not r.get("res"):
            self.attempt(rnd, "Grand Prix result summary", lambda: self.add_res(rnd, race_ended[0]))
        if race_ended and S.get("race") and str(rnd) not in D["LAPS"]:
            self.attempt(rnd, "lap chart", lambda: self.add_laps(rnd, race_ended[0]))
        if race_ended and S.get("race") and (self.backfill or self.now - race_ended[0] < dt.timedelta(days=EXTRAS_DAYS)):
            self.do_extras(rnd, race_ended[0])

    def do_extras(self, rnd, start):
        for key in EXTRAS:
            if key not in self.season(rnd):
                self.attempt(rnd, {"neutral": "safety cars", "stints": "tyre stints"}[key],
                             lambda key=key: self.add_extra(rnd, key, start))

    def add_extra(self, rnd, key, start):
        S = self.season(rnd)
        v = race_extra(self.src, People(self.D), rnd, key, S["race"], start, self.D)
        S[key] = v
        self.added.append((rnd, "race extras")); self.log("R%d %s added (%s)" % (rnd, key, len(v)))

    def backfill_rounds(self):
        """--backfill: race extras for every finished race, including rounds without SCHED."""
        jol = None
        for r in self.D["RACES"]:
            if not r.get("res") or str(r["r"]) in self.D["SCHED"] or not self.D["SEASON"].get(str(r["r"]), {}).get("race"): continue
            start = r.get("start")
            if not start:
                if jol is None: jol = self.src.schedule()
                j = jol.get(r["r"])
                if not j or not j.get("time"): continue
                start = "%sT%s" % (j["date"], j["time"])
            self.do_extras(r["r"], parse_t(start))

    def attempt(self, rnd, what, fn):
        snap = copy.deepcopy(self.D)
        try:
            fn()
        except NotReady as e:
            self.D.clear(); self.D.update(snap)
            self.log("R%d %s: not available yet (%s)" % (rnd, what, e))
        except CheckFailed as e:
            self.D.clear(); self.D.update(snap)
            self.failures.append("R%d %s: %s" % (rnd, what, e))
            self.log("R%d %s: CHECK FAILED, not saved: %s" % (rnd, what, e))

    def season(self, rnd): return self.D["SEASON"].setdefault(str(rnd), {})

    def add_plain(self, rnd, name, k, start, people):
        if k in ("fp1", "fp2", "fp3"): rows = practice_rows(self.src, people, name, start)
        elif k == "sq": rows = sq_rows(self.src, people, start)
        else: rows = quali_rows(self.src, people, rnd, start)
        check_cars("R%d %s" % (rnd, name), rows)
        self.season(rnd)[k] = rows
        self.added.append((rnd, name))
        self.log("R%d %s added (P1 %s)" % (rnd, name, rows[0][2]))

    def add_points_sessions(self, rnd, pts, sessions):
        D = self.D
        people = People(D)
        did = []
        for name, start in pts:
            sprint = name == "Sprint"
            R, rows = race_rows(self.src, people, rnd, start, sprint, self.season(rnd).get("grid"))
            check_cars("R%d %s" % (rnd, name), rows)
            cross_check(self.src, "R%d %s" % (rnd, name), name, start, R)
            add_points(D, people, R, self.log)
            self.season(rnd)["sprint" if sprint else "race"] = rows
            if sprint:
                r = race_of(D, rnd)
                if not isinstance(r.get("sprint"), str) or not r.get("sprint"): r["sprint"] = people.full(rows[0][1])
            did.append(name)
        # standings must match the published ones once every finished points session is in
        try:
            check_standings(D, self.src, people, rnd)
        except (NotReady, CheckFailed) as e:
            missing_later = [n for n, s, d in sessions if KEY[n] in ("sprint", "race") and KEY[n] not in self.season(rnd) and n not in did]
            if isinstance(e, CheckFailed) and not missing_later: raise
            raise NotReady("standings not confirmed yet: %s" % e)
        for name in did:
            self.added.append((rnd, name)); self.log("R%d %s added (winner %s)" % (rnd, name, self.season(rnd)["sprint" if name == "Sprint" else "race"][0][2]))

    def add_res(self, rnd, start):
        D = self.D; people = People(D)
        R = self.src.race_table(rnd, "results", "Results")
        if not R: raise NotReady("Jolpica-F1 has no race result yet")
        learn_jolpica(people, R)
        res = race_res(D, self.src, people, rnd, D["SEASON"][str(rnd)]["race"], R, start)
        race_of(D, rnd)["res"] = res
        self.added.append((rnd, "Grand Prix summary")); self.log("R%d race summary added" % rnd)

    def add_laps(self, rnd, start):
        D = self.D; people = People(D)
        D["LAPS"][str(rnd)] = lap_chart(self.src, people, D["SEASON"][str(rnd)]["race"], start)
        self.added.append((rnd, "lap chart")); self.log("R%d lap chart added" % rnd)

    # -- schedule
    def current_rounds(self):
        out = []
        for rk in sorted(self.D["SCHED"], key=int):
            gp = next((s for n, s, d in self.D["SCHED"][rk][1] if n == "Grand Prix"), None)
            if gp and parse_t(gp) + dt.timedelta(hours=3) > self.now: out.append(int(rk))
        return out[:2]

    def check_schedule(self):
        """Moves a session in SCHED only when the sources' reported time CHANGES compared
        with what they reported on an earlier run, and both agree on the new time. A
        difference that was already there is left alone, so hand-entered times stick."""
        D = self.D
        rounds = self.current_rounds()
        for rk in list(self.seen):                       # forget finished rounds
            if int(rk) not in rounds: del self.seen[rk]
        if not rounds: return
        jol = self.src.schedule()
        for rnd in rounds:
            jr = jol.get(rnd)
            seen_r = self.seen.setdefault(str(rnd), {})
            for item in D["SCHED"][str(rnd)][1]:
                name, cur = item[0], parse_t(item[1])
                jt = None
                if jr:
                    keys = JOL_KEYS.get(name)
                    blk = jr if keys is None else next((jr[k] for k in keys if k in jr), None)
                    if blk and blk.get("time"): jt = parse_t("%sT%s" % (blk["date"], blk["time"]))
                os_ = self.src.of1_session(name, cur)
                ot = parse_t(os_["date_start"]) if os_ else None
                prev = dict(seen_r.get(name) or {})
                now_seen = {"jolpica": iso_z(jt) if jt else prev.get("jolpica"), "openf1": iso_z(ot) if ot else prev.get("openf1")}
                seen_r[name] = {k: v for k, v in now_seen.items() if v}
                if not jt or not ot: continue
                if abs((jt - ot).total_seconds()) > 60: continue          # sources disagree: leave SCHED alone
                if abs((jt - cur).total_seconds()) <= 300: continue       # within 5 minutes: no change
                changed = [k for k, t in (("jolpica", jt), ("openf1", ot)) if prev.get(k) and prev[k] != iso_z(t)]
                if not changed:
                    why = "first time seen" if not prev else "sources unchanged since last run"
                    self.schedule_notes.append("R%d %s: SCHED %s, both sources %s UTC; left alone (%s, so a hand-entered time stays)" % (
                        rnd, name, cur.strftime("%Y-%m-%d %H:%M"), jt.strftime("%Y-%m-%d %H:%M"), why))
                    continue
                new = iso_z(jt)
                r = race_of(D, rnd)
                if name == "Grand Prix" and r.get("start") == item[1]: r["start"] = new
                item[1] = new
                msg = "R%d %s moved to %s UTC" % (rnd, name, jt.strftime("%Y-%m-%d %H:%M"))
                self.schedule_moves.append(msg); self.log("Schedule: " + msg)
        for n in self.schedule_notes: self.log("Schedule: " + n)

    def message(self):
        lines = []
        by = {}
        for rnd, what in self.added: by.setdefault(rnd, []).append(what)
        if by and all(set(w) == {"race extras"} for w in by.values()):
            lines.append("Auto: safety cars and tyre stints for %s" % ", ".join("R%d" % r for r in sorted(by)))
            by = {}
        for rnd, whats in by.items():
            whats = list(dict.fromkeys(whats))
            names = [w for w in whats if w not in ("Grand Prix summary", "lap chart", "race extras")] or whats
            lines.append("Auto: R%d %s: %s results" % (rnd, race_of(self.D, rnd)["short"], ", ".join(names)))
        lines += ["Schedule: " + m for m in self.schedule_moves]
        if not lines: return ""
        body = [l for l in lines[1:]]
        return lines[0] + ("\n\n" + "\n".join(body) if body else "") + "\n"


# ---------------------------------------------------------------- self-test
def strip_round(D, rnd, log=print):
    """Removes a finished round's sessions, summary, lap chart and points (for --selftest)."""
    T = copy.deepcopy(D)
    S = T["SEASON"][str(rnd)]
    for k in KEY.values():
        S.pop(k, None)
    r = race_of(T, rnd)
    r.pop("res", None)
    if isinstance(r.get("sprint"), str): r.pop("sprint")
    T["LAPS"].pop(str(rnd), None)
    for k in EXTRAS: S.pop(k, None)
    return standings_before(T, D, rnd)


def standings_before(T, D, rnd):
    """Standings as they were before round rnd: subtract the site's own sprint and race
    points of round rnd and every later round (team = the driver's current team)."""
    team = {d[0]: d[2] for d in T["DRIVERS"]}
    full = {norm(d[0].split()[-1]): d[0] for d in T["DRIVERS"]}
    for rk, S in D["SEASON"].items():
        if int(rk) < rnd: continue
        for k in ("sprint", "race"):
            for row in S.get(k, []):
                if not row[5]: continue
                nm = full[norm(row[2])]
                d = next(d for d in T["DRIVERS"] if d[0] == nm); d[3] = num(d[3] - row[5])
                c = next(c for c in T["CONSTRUCTORS"] if c[0] == team[nm]); c[1] = num(c[1] - row[5])
    T["DRIVERS"].sort(key=lambda d: -d[3]); T["CONSTRUCTORS"].sort(key=lambda c: -c[1])
    return T


def compare(orig, new, rnd):
    """Core = positions, car numbers, names, points, grid, standings. Returns (core_diffs, other_diffs)."""
    core, other = [], []
    So, Sn = orig["SEASON"][str(rnd)], new["SEASON"].get(str(rnd), {})
    for k in [k for k in KEY.values() if k in So]:
        a, b = So[k], Sn.get(k)
        if b is None: core.append("%s: not rebuilt" % k); continue
        if len(a) != len(b): core.append("%s: %d rows on the site, %d rebuilt" % (k, len(a), len(b)))
        cols = {"race": (0, 1, 2, 5, 6), "sprint": (0, 1, 2, 5)}.get(k, (0, 1, 2))
        if k in ("race", "sprint"):   # not-classified cars: same cars, order is hand-entered on the site
            nca, ncb = sorted(x[1] for x in a if not str(x[0]).isdigit()), sorted(x[1] for x in b if not str(x[0]).isdigit())
            if nca != ncb: core.append("%s: not-classified cars differ: site %s, rebuilt %s" % (k, nca, ncb))
            key = lambda rows: sorted(rows, key=lambda x: (0, int(x[0])) if str(x[0]).isdigit() else (1, x[1]))
            if [x[1] for x in a] != [x[1] for x in b]: other.append("%s: order of not-classified cars differs (site is hand-entered)" % k)
            a, b = key(a), key(b)
        for i, (x, y) in enumerate(zip(a, b)):
            for c in range(max(len(x), len(y))):
                xv, yv = (x[c] if c < len(x) else None), (y[c] if c < len(y) else None)
                if xv != yv:
                    (core if c in cols else other).append("%s P%d col %d: site %r, rebuilt %r" % (k, i + 1, c, xv, yv))
    exp = standings_before(copy.deepcopy(orig), orig, rnd + 1)   # expected standings right after round rnd
    for key, pi in (("DRIVERS", 3), ("CONSTRUCTORS", 1)):
        if exp[key] != new[key] and sorted(map(json.dumps, exp[key])) == sorted(map(json.dumps, new[key])) and \
                [x[pi] for x in exp[key]] == [x[pi] for x in new[key]]:
            other.append("%s: same points, order of tied entries differs (rebuilt follows the published standings)" % key)
        elif exp[key] != new[key]:
            core.append("%s differ:\n    site    %s\n    rebuilt %s" % (key, exp[key], new[key]))
    ro, rn = race_of(orig, rnd), race_of(new, rnd)
    if ro.get("sprint") != rn.get("sprint"): core.append("sprint winner: site %r, rebuilt %r" % (ro.get("sprint"), rn.get("sprint")))
    a, b = ro.get("res") or {}, rn.get("res") or {}
    for f in ("time", "pod", "pole", "fl", "pit"):
        if a.get(f) != b.get(f): (core if f in ("pod", "pole") else other).append("res.%s: site %r, rebuilt %r" % (f, a.get(f), b.get(f)))
    for k in EXTRAS:
        a, b = So.get(k), Sn.get(k)
        if b is None: other.append("%s: not rebuilt" % k)
        elif a is not None and a != b: other.append("%s differs from the site's" % k)
        else: other.append("%s: %s" % (k, json.dumps(b)[:400] if k != "stints" else "%d cars, %d stints" % (len(b), sum(len(v) for v in b.values()))))
    La, Lb = orig["LAPS"].get(str(rnd)), new["LAPS"].get(str(rnd))
    if La and not Lb: other.append("lap chart: not rebuilt")
    elif La and Lb:
        if La["c"] != Lb["c"]: other.append("lap chart codes: site %s, rebuilt %s" % (La["c"], Lb["c"]))
        same = sum(1 for x, y in zip(La["l"], Lb["l"]) if x == y)
        moved = sum(sum(1 for p, q in zip(x, y) if p != q) for x, y in zip(La["l"], Lb["l"]))
        other.append("lap chart: %d laps on the site, %d rebuilt; %d laps identical; %d car-positions differ in total" % (len(La["l"]), len(Lb["l"]), same, moved))
    return core, other


def selftest(D, src, rnd, log):
    log("Self-test: rebuild round %d from the APIs on a copy of the data" % rnd)
    D = copy.deepcopy(D)
    if str(rnd) not in D["SCHED"]:   # older rounds have no SCHED entry: take session times from Jolpica-F1
        jr = src.schedule().get(rnd)
        if not jr: raise SystemExit("round %d not in the Jolpica-F1 schedule" % rnd)
        items = []
        for name, keys in JOL_KEYS.items():
            blk = jr if keys is None else next((jr[k] for k in keys if k in jr), None)
            if blk and blk.get("time"): items.append([name, iso_z(parse_t("%sT%s" % (blk["date"], blk["time"]))), 0 if keys is None else 60])
        D["SCHED"][str(rnd)] = ["UTC", sorted(items, key=lambda x: x[1])]
        log("(SCHED for round %d taken from Jolpica-F1: %s)" % (rnd, ", ".join(i[0] for i in items)))
    T = strip_round(D, rnd)
    gp = next(s for n, s, d in D["SCHED"][str(rnd)][1] if n == "Grand Prix")
    now = parse_t(gp) + dt.timedelta(hours=6)
    u = Updater(T, src, now, log).run(rounds=[rnd], schedule=False)
    core, other = compare(D, T, rnd)
    log("\nAdded: %s" % ", ".join("R%d %s" % a for a in u.added))
    log("Failures: %s" % (u.failures or "none"))
    log("\nCore differences (positions, numbers, names, points, grid, standings, podium, pole): %d" % len(core))
    for c in core: log("  - " + c)
    log("Other differences (times, laps, lap chart, fastest lap): %d" % len(other))
    for c in other: log("  - " + c)
    log("\nCommit message would be:\n" + u.message())
    # schedule check, report only
    # schedule check, report only: in-memory state, .automation/schedule-seen.json is not read or written
    S2 = copy.deepcopy(D); u2 = Updater(S2, src, dt.datetime.now(dt.timezone.utc), log, seen={})
    try: u2.check_schedule()
    except NotReady as e: log("schedule check: %s" % e)
    log("Schedule check (report only): %s" % ("; ".join(u2.schedule_notes) if u2.schedule_notes else "SCHED matches both sources"))
    ok = not core and not u.failures
    log("\nSELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return ok


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", type=int)
    ap.add_argument("--now")
    ap.add_argument("--message-file")
    ap.add_argument("--record"); ap.add_argument("--replay")
    ap.add_argument("--report")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--backfill", action="store_true", help="also add safety cars and tyre stints for every finished race")
    a = ap.parse_args()
    lines = []
    def log(s=""):
        print(s, flush=True); lines.append(s)
    src = Sources(Http(record=a.record, replay=a.replay, log=log))
    D = build.load_data()
    if a.selftest:
        ok = selftest(D, src, a.selftest, log)
        if a.report: open(a.report, "w").write("\n".join(lines) + "\n")
        sys.exit(0 if ok else 1)
    now = parse_t(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    seen = read_json(SCHEDULE_SEEN, {})
    seen_before = json.dumps(seen, sort_keys=True)
    before = json.dumps(D, sort_keys=True)
    u = Updater(D, src, now, log, seen=seen, backfill=a.backfill).run()
    changed = json.dumps(D, sort_keys=True) != before
    msg = u.message()
    # check failures: email (exit 1) only the first time a failure appears; repeats are warnings
    reported = read_json(FAILURES_SEEN, {})
    new_fail = [f for f in u.failures if f not in reported]
    repeat_fail = [f for f in u.failures if f in reported]
    failures_now = {f: reported.get(f, iso_z(now)) for f in u.failures}   # resolved failures drop out (reset)
    if not a.dry_run:
        state_changed = write_json(SCHEDULE_SEEN, seen, seen_before) | write_json(FAILURES_SEEN, failures_now, json.dumps(reported, sort_keys=True))
        if state_changed and not msg: msg = "Auto: update source state\n"
    if changed and not a.dry_run:
        check_sorted(D)
        build.save_data(D)
        if not a.no_build:
            subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True, cwd=ROOT)
        log("saved src/data.json and rebuilt the site")
    elif not changed:
        log("nothing new")
    if a.message_file: open(a.message_file, "w").write(msg)
    if msg: log(msg.strip())
    if repeat_fail:
        log("\nWARNING: still failing a check (already reported by email), NOT published:\n  " + "\n  ".join(repeat_fail))
        if os.environ.get("GITHUB_ACTIONS"):
            for f in repeat_fail: print("::warning::Still not published (already reported): " + f.replace("\n", " "))
    if new_fail:
        log("\nChecks failed, these were NOT published:\n  " + "\n  ".join(new_fail))
        sys.exit(1)


def read_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, value, before_dump):
    """Writes the file only when its content changed. Returns True if written."""
    if json.dumps(value, sort_keys=True) == before_dump and os.path.exists(path): return False
    if not value and not os.path.exists(path): return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(json.dumps(value, indent=1, sort_keys=True) + "\n")
    return True


if __name__ == "__main__":
    main()
