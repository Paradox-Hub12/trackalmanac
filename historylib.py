"""History page: driver careers, champions, records and countries.

build.py calls compute(base, D). `base` is src/history.json (every World Championship race from F1DB,
see scripts/history.py); D is src/data.json, whose 2026 results are added for rounds newer than the
base file. Everything else is worked out here, so the page stays current after every race.
"""
import datetime, re, unicodedata

NONSTART = {1, 2, 3, 4, 9}       # DNQ, DNPQ, DNS, DNP, excluded before the start
TRACKCC = {"albert": "AU", "shanghai": "CN", "suzuka": "JP", "miami": "US", "montreal": "CA", "monaco": "MC",
           "catalunya": "ES", "rbring": "AT", "silverstone": "GB", "spa": "BE", "hungaro": "HU", "zandvoort": "NL",
           "monza": "IT", "madring": "ES", "baku": "AZ", "sepang": "BH", "marina": "SG", "cota": "US", "mexico": "MX",
           "interlagos": "BR", "vegas": "US", "lusail": "QA", "yas": "AE", "bahrain": "BH", "jeddah": "SA"}
REL = {"PARENT": ("Son", "Daughter"), "CHILD": ("Father", "Mother"), "SIBLING": ("Brother", "Sister"),
       "HALF_SIBLING": ("Half-brother", "Half-sister"), "PARENTS_SIBLING": ("Nephew", "Niece"),
       "SIBLINGS_CHILD": ("Uncle", "Aunt"), "GRANDPARENT": ("Grandson", "Granddaughter"),
       "GRANDCHILD": ("Grandfather", "Grandmother"), "PARENTS_SIBLINGS_CHILD": ("Cousin", "Cousin"),
       "SIBLING_IN_LAW": ("Brother-in-law", "Sister-in-law"), "CHILD_IN_LAW": ("Father-in-law", "Mother-in-law"),
       "PARENT_IN_LAW": ("Son-in-law", "Daughter-in-law"), "GRANDPARENTS_SIBLING": ("Great-nephew", "Great-niece"),
       "SIBLINGS_GRANDCHILD": ("Great-uncle", "Great-aunt"), "SIBLINGS_CHILD_IN_LAW": ("Relative by marriage", "Relative by marriage")}


# record titles as they read in a driver's facts
FACT = {"Most world titles": "most world titles", "Most race wins": "most race wins", "Most pole positions": "most pole positions",
        "Most podiums": "most podiums", "Most fastest laps": "most fastest laps", "Most race starts": "most race starts",
        "Most points": "most points", "Most grand slams": "most grand slams", "Highest win rate (25+ starts)": "highest win rate (25+ starts)",
        "Most consecutive titles": "most titles in a row", "Most consecutive race wins": "most race wins in a row",
        "Most consecutive pole positions": "most poles in a row", "Most consecutive podiums": "most podiums in a row",
        "Most wins in a season": "most wins in a season", "Highest share of a season's races won": "highest share of a season's races won",
        "Most poles in a season": "most poles in a season", "Most podiums in a season": "most podiums in a season",
        "Most points in a season": "most points in a season", "Biggest title-winning margin": "biggest title-winning margin",
        "Closest title fights": "closest title win", "Youngest race winners": "youngest ever race winner",
        "Oldest race winners": "oldest ever race winner", "Youngest world champions": "youngest ever world champion",
        "Oldest world champions": "oldest ever world champion", "Youngest pole sitters": "youngest ever pole sitter",
        "Youngest race starters": "youngest ever race starter", "Oldest race starters": "oldest ever race starter",
        "Most wins without a title": "most wins without a title", "Most starts without a win": "most starts without a win",
        "Most podiums without a win": "most podiums without a win", "Won races with the most teams": "race wins with the most teams",
        "Most wins at the same Grand Prix": "most wins at the same Grand Prix", "Most seasons raced": "most seasons raced"}
RANKED = {"Most world titles": "world titles", "Most race wins": "race wins", "Most pole positions": "pole positions",
          "Most podiums": "podiums", "Most fastest laps": "fastest laps", "Most race starts": "race starts", "Most points": "points"}


# 1958-1978: how many of a constructor's results counted towards its championship total
COUNTED = {1958: 6, 1959: 5, 1960: 6, 1961: 5, 1962: 5, 1963: 6, 1964: 6, 1965: 6, 1966: 5, 1967: 9, 1968: 10, 1969: 9, 1970: 11,
           1971: 9, 1972: 10, 1973: 13, 1974: 13, 1975: 12, 1976: 14, 1977: 15, 1978: 14}


def norm(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
def day(s): return datetime.date.fromisoformat(s)
def age(dob, on):
    if not dob: return None
    b, d = day(dob), day(on)
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day)), (d - b).days
def ord_(n): return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
def plural(n, w): return "%s %s%s" % (fmt(n), w, "" if n == 1 else "s")
def fmt(x):
    if isinstance(x, float) and x.is_integer(): x = int(x)
    return "{:,}".format(x) if isinstance(x, int) else ("%g" % x)


def add_site_rounds(base, D):
    """Append 2026 rounds that F1DB didn't have yet, from the site's own results."""
    y0, r0 = base["upto"]
    year = int(D["RACES"][0]["date"][:4])
    if year < y0: return
    drv = base["drivers"]
    cur = {}  # last name -> driver index, for drivers in this season
    team = {}
    kit = {}   # constructor -> (engine, tyres) in its latest race
    # newest races first, so "Schumacher" or "Verstappen" means the most recent driver of that name
    for R in reversed(base["races"]):
        for row in R["rows"]:
            d = drv[row[0]]; team.setdefault(row[0], row[7]); kit.setdefault(row[7], (row[8], row[9]))
            for key in (d["ln"], d["ln"].split()[0], d["n"]): cur.setdefault(norm(key), row[0])   # "Sainz" = "Sainz Jr."
    full = {norm(d[0]): d for d in D["DRIVERS"]}
    bio = {norm(b.get("last", "")): b for b in (D.get("BIO") or {}).values()}
    def who(name):
        n = norm(name)
        if n in cur: return cur[n]
        n2 = norm(name.split()[-1])
        if n2 in cur: return cur[n2]
        # a rookie the history file doesn't know yet: add them from the site's driver profile
        b = bio.get(n) or bio.get(n2)
        if not b: return None
        drv.append({"id": re.sub(r"[^a-z0-9]+", "-", norm(b["name"])).strip("-"), "n": b["name"], "fn": b.get("first"), "ln": b.get("last"),
                    "full": b["name"], "ab": b.get("code"), "no": str(b.get("num") or ""), "dob": b.get("dob"), "dod": None,
                    "pob": b.get("birthplace"), "cob": b.get("iso2"), "cc": b.get("iso2"), "cc2": None, "gs": 0, "g": "M"})
        i = len(drv) - 1
        for key in (b.get("last", ""), b["name"]): cur[norm(key)] = i
        return i
    for r in D["RACES"]:
        if not r.get("res") or (year == y0 and r["r"] <= r0): continue
        S = D["SEASON"].get(str(r["r"]), {})
        rows = []
        for x in S.get("race", []):
            i = who(x[2])
            if i is None: continue
            pos = int(x[0]) if str(x[0]).isdigit() else 0
            t = str(x[4]).upper()
            code = 0 if pos else (3 if "DNS" in t else 7 if ("DSQ" in t or "DQ" in t) else 5)
            num = lambda v: (int(v) if str(v).isdigit() else 0) if not isinstance(v, (int, float)) else v
            if i not in team:
                t = next((d[2] for d in D["DRIVERS"] if norm(d[0]) == norm(drv[i]["n"])), "")
                mate = next((who(d[0]) for d in D["DRIVERS"] if d[2] == t and norm(d[0]) != norm(drv[i]["n"]) and who(d[0]) in team), None)
                if mate is not None: team[i] = team[mate]
                else:
                    if t not in base["cons"]: base["cons"].append(t)
                    team[i] = base["cons"].index(t)
            e_, t_ = kit.get(team[i], (-1, -1))
            rows.append([i, pos, code, num(x[5]) or 0, num(x[6]), num(x[3]), 0, team[i], e_, t_, num(x[1])])
        pole = S.get("quali", [[None, None, None]])[0][2] if S.get("quali") else None
        pi = who(r["res"].get("pole") or pole or "")
        for row in rows:
            if row[0] == pi: row[6] = 1
        sp = [[who(x[2]), int(x[0]) if str(x[0]).isdigit() else 0, (x[5] if isinstance(x[5], (int, float)) else 0), 0 if "DNS" in str(x[4]).upper() else 1] for x in S.get("sprint", []) if who(x[2]) is not None]
        fl = [who(r["res"]["fl"][0])] if r["res"].get("fl") and who(r["res"]["fl"][0]) is not None else []
        base["races"].append({"y": year, "r": r["r"], "gp": r["gp"].replace(" Grand Prix", " Grand Prix"), "cc": TRACKCC.get(r["track"]),
                              "d": r["date"], "fl": fl, "dec": 0, "rows": rows, "sp": sp, "site": 1})


def compute(base, D):
    add_site_rounds(base, D)
    drv, CN, races = base["drivers"], base["cons"], base["races"]
    N = len(drv)
    year_now = int(D["RACES"][0]["date"][:4])
    season_done = all(r.get("res") for r in D["RACES"])
    st = [dict(entries=0, starts=0, wins=0, pod=0, poles=0, fl=0, pts=0.0, laps=0, sst=0, sw=0, front=0, pf=0,
               first=None, last=None, fwin=None, lwin=None, fpod=None, fpole=None, bres=None, bgrid=None,
               teams={}, wteams={}, years=set(), wins_at={}, seq=[], gs=drv[i].get("gs", 0)) for i in range(N)]
    # ---- race by race
    for k, R in enumerate(races):
        win = [row[0] for row in R["rows"] if row[1] == 1]
        R["win"] = win
        R["pole"] = next((row[0] for row in R["rows"] if row[6]), None)
        seen_e, seen_s, seen_p = set(), set(), set()   # shared drives: count each race once per driver
        for row in R["rows"]:
            i, pos, code, pts, grid, laps, pole, ci = row[:8]
            s = st[i]; s["pts"] += pts
            if i not in seen_e: s["entries"] += 1; seen_e.add(i)
            if pole:
                s["poles"] += 1
                if s["fpole"] is None: s["fpole"] = (k, R["y"], R["gp"])
            if grid and (s["bgrid"] is None or grid < s["bgrid"]): s["bgrid"] = grid
            if code in NONSTART: continue
            s["laps"] += laps; s["years"].add(R["y"])
            if i not in seen_s: s["starts"] += 1; seen_s.add(i)
            s["teams"][CN[ci]] = s["teams"].get(CN[ci], 0) + 1
            ref = (k, R["y"], R["gp"])
            if s["first"] is None: s["first"] = ref
            s["last"] = ref
            if pos == 1:
                s["wins"] += 1; s["wteams"][CN[ci]] = 1; s["lwin"] = ref
                if s["fwin"] is None: s["fwin"] = ref
                s["wins_at"][R["gp"]] = s["wins_at"].get(R["gp"], 0) + 1
            if 1 <= pos <= 3 and i not in seen_p:
                s["pod"] += 1; seen_p.add(i)
                if s["fpod"] is None: s["fpod"] = ref
            if pts > 0: s["pf"] += 1
            if grid == 1: s["front"] += 1
            if pos and (s["bres"] is None or pos < s["bres"]): s["bres"] = pos
            if s["seq"] and s["seq"][-1][0] == k:   # second car in the same race: keep the better result
                o = s["seq"][-1]; s["seq"][-1] = (k, min([x for x in (o[1], pos) if x] or [0]), o[2] or pole, o[3])
            else: s["seq"].append((k, pos, pole, i in R["fl"]))
        for i in set(R["fl"]): st[i]["fl"] += 1
        for i, pos, pts, ok in R["sp"]:
            st[i]["pts"] += pts
            if ok: st[i]["sst"] += 1
            if pos == 1: st[i]["sw"] += 1
    # grand slams for site-added rounds: pole, win, fastest lap and led every lap
    for R in races:
        if R.get("site") and R["win"] and R["pole"] == R["win"][0] and R["fl"] == [R["win"][0]]:
            led = D.get("LAPS", {}).get(str(R["r"]))
            if led and isinstance(led, dict) and led.get("lead") and all(x == led["lead"][0] for x in led["lead"]):
                st[R["win"][0]]["gs"] += 1
    # ---- seasons and champions
    stand = {int(y): v for y, v in base["standings"].items()}
    if year_now in stand or True:
        # current season from the site's standings (base may stop a few rounds earlier)
        cs = [[k + 1, None, d[3]] for k, d in enumerate(D["DRIVERS"][:3])]
        for c, d in zip(cs, D["DRIVERS"][:3]):
            n = norm(d[0]); c[1] = next((i for i in range(N) if norm(drv[i]["n"]) == n), None)
        if all(c[1] is not None for c in cs): stand[year_now] = cs
    titles = {}
    champs = []
    by_year = {}
    for k, R in enumerate(races): by_year.setdefault(R["y"], []).append(k)
    for y in sorted(stand):
        top = stand[y]
        done = y < year_now or season_done
        ks = by_year.get(y, [])
        def team_in(i):
            c = {}
            for k in ks:
                for row in races[k]["rows"]:
                    if row[0] == i and row[2] not in NONSTART: c[CN[row[7]]] = c.get(CN[row[7]], 0) + 1
            return max(c, key=c.get) if c else ""
        def wins_in(i): return sum(1 for k in ks if i in races[k]["win"])
        dec = next((k for k in ks if races[k]["dec"]), None)
        if done and dec is None and ks: dec = ks[-1]
        ch = top[0][1]
        if done: titles.setdefault(ch, []).append(y)
        a = age(drv[ch]["dob"], races[dec]["d"]) if dec is not None else None
        champs.append({"y": y, "done": done, "rounds": len(ks),
                       "top": [[i, team_in(i), p, wins_in(i)] for _, i, p in top],
                       "dec": [races[dec]["gp"], races[dec]["r"], races[dec]["d"], races[dec]["cc"]] if (done and dec is not None) else None,
                       "left": (len(ks) - races[dec]["r"]) if (done and dec is not None) else None,
                       "margin": round(top[0][2] - top[1][2], 1) if len(top) > 1 else None,
                       "age": a[0] if a else None})
    # ---- streaks per driver (over the races they started)
    def best_run(seq, test):
        best = cur = 0; start = bs = be = None
        for k, *v in seq:
            if test(*v):
                cur += 1
                if cur == 1: start = k
                if cur > best: best, bs, be = cur, start, k
            else: cur = 0
        return best, bs, be
    run = {}
    for i in range(N):
        s = st[i]
        run[i] = {"wins": best_run(s["seq"], lambda p, pl, f: p == 1), "poles": best_run(s["seq"], lambda p, pl, f: pl),
                  "pod": best_run(s["seq"], lambda p, pl, f: 1 <= p <= 3)}
    def runtxt(r):
        n, a, b = r
        return "%s %d – %s %d" % (short(races[a]["gp"]), races[a]["y"], short(races[b]["gp"]), races[b]["y"]) if n else ""
    def short(gp): return gp.replace(" Grand Prix", " GP")
    # consecutive titles
    title_run = {}
    for i, ys in titles.items():
        best = cur = 0; prev = None; s0 = None; bs = None
        for y in sorted(ys):
            cur = cur + 1 if prev == y - 1 else 1
            if cur == 1: s0 = y
            if cur > best: best, bs = cur, (s0, y)
            prev = y
        title_run[i] = (best, bs)
    # ---- records
    rec = []
    def top(key, title, unit, n=10, filt=lambda i: True, extra=lambda i: "", rev=True):
        rows = sorted((i for i in range(N) if filt(i) and key(i) is not None), key=lambda i: (-key(i) if rev else key(i), drv[i]["n"]))
        out = []
        for i in rows:
            if len(out) >= n and key(i) != out[-1][1]: break
            out.append([i, key(i), extra(i)])
        out = [r for r in out if r[1]]
        return {"t": title, "u": unit, "rows": out[:max(n, 0) + 5]}
    started = [i for i in range(N) if st[i]["starts"]]
    cat = lambda name, items: rec.append({"cat": name, "items": items})
    cat("Career", [
        top(lambda i: len(titles.get(i, [])), "Most world titles", "titles", extra=lambda i: ", ".join(map(str, titles.get(i, [])))),
        top(lambda i: st[i]["wins"], "Most race wins", "wins"),
        top(lambda i: st[i]["poles"], "Most pole positions", "poles"),
        top(lambda i: st[i]["pod"], "Most podiums", "podiums"),
        top(lambda i: st[i]["fl"], "Most fastest laps", "fastest laps"),
        top(lambda i: st[i]["starts"], "Most race starts", "starts"),
        top(lambda i: st[i]["pts"], "Most points", "points"),
        top(lambda i: st[i]["gs"], "Most grand slams", "grand slams", extra=lambda i: "pole, win, fastest lap and led every lap"),
        top(lambda i: round(100 * st[i]["wins"] / st[i]["starts"], 1) if st[i]["starts"] >= 25 and st[i]["wins"] else None, "Highest win rate (25+ starts)", "%",
            extra=lambda i: "%d wins from %d starts" % (st[i]["wins"], st[i]["starts"])),
    ])
    cat("In a row", [
        top(lambda i: title_run.get(i, (0,))[0] if title_run.get(i, (0,))[0] > 1 else None, "Most consecutive titles", "titles",
            extra=lambda i: "%d–%d" % title_run[i][1] if i in title_run else ""),
        top(lambda i: run[i]["wins"][0] if run[i]["wins"][0] > 2 else None, "Most consecutive race wins", "wins", extra=lambda i: runtxt(run[i]["wins"])),
        top(lambda i: run[i]["poles"][0] if run[i]["poles"][0] > 2 else None, "Most consecutive pole positions", "poles", extra=lambda i: runtxt(run[i]["poles"])),
        top(lambda i: run[i]["pod"][0] if run[i]["pod"][0] > 4 else None, "Most consecutive podiums", "podiums", extra=lambda i: runtxt(run[i]["pod"])),
    ])
    # seasons
    seas = {}
    for y, ks in by_year.items():
        for k in ks:
            R = races[k]
            for row in R["rows"]:
                i = row[0]; e = seas.setdefault((i, y), dict(w=0, p=0, pod=0, s=0, pts=0.0))
                if row[2] in NONSTART: continue
                e["s"] += 1; e["w"] += row[1] == 1; e["pod"] += 1 <= row[1] <= 3; e["p"] += row[6]; e["pts"] += row[3]
            for i, pos, pts, _ok in R["sp"]: seas.setdefault((i, y), dict(w=0, p=0, pod=0, s=0, pts=0.0))["pts"] += pts
    def season_top(key, title, unit, n=10, extra=lambda k, v: ""):
        rows = sorted(((k, v) for k, v in seas.items() if key(k, v)), key=lambda kv: (-key(*kv), kv[0][1]))
        out = []
        for (i, y), v in rows:
            val = key((i, y), v)
            if len(out) >= n and val != out[-1][1]: break
            out.append([i, val, ("%d" % y) + ((" · " + extra((i, y), v)) if extra((i, y), v) else "")])
        return {"t": title, "u": unit, "rows": out[:n + 5]}
    nrounds = {y: len(ks) for y, ks in by_year.items()}
    ch_rows = [c for c in champs if c["done"] and c["margin"] is not None]
    cat("In one season", [
        season_top(lambda k, v: v["w"], "Most wins in a season", "wins", extra=lambda k, v: "from %d races" % nrounds[k[1]]),
        season_top(lambda k, v: round(100 * v["w"] / nrounds[k[1]], 1) if v["w"] >= 3 else 0, "Highest share of a season's races won", "%",
                   extra=lambda k, v: "%d of %d" % (v["w"], nrounds[k[1]])),
        season_top(lambda k, v: v["p"], "Most poles in a season", "poles"),
        season_top(lambda k, v: v["pod"], "Most podiums in a season", "podiums"),
        season_top(lambda k, v: v["pts"], "Most points in a season", "points"),
        {"t": "Biggest title-winning margin", "u": "points", "rows": [[c["top"][0][0], c["margin"], "%d · over %s" % (c["y"], drv[c["top"][1][0]]["n"])] for c in sorted(ch_rows, key=lambda c: -c["margin"])[:10]]},
        {"t": "Closest title fights", "u": "points", "rows": [[c["top"][0][0], c["margin"], "%d · over %s" % (c["y"], drv[c["top"][1][0]]["n"])] for c in sorted(ch_rows, key=lambda c: c["margin"])[:10]]},
    ])
    # ages
    def age_at(i, ref):
        if ref is None or not drv[i]["dob"]: return None
        return age(drv[i]["dob"], races[ref[0]]["d"])
    def agetop(title, refkey, young=True, n=10):
        rows = []
        for i in started:
            a = age_at(i, st[i][refkey]) if refkey not in ("lastwin", "laststart") else age_at(i, st[i]["lwin"] if refkey == "lastwin" else st[i]["last"])
            if a: rows.append((a[1], i, a[0], st[i][refkey] if refkey in st[i] else (st[i]["lwin"] if refkey == "lastwin" else st[i]["last"])))
        rows.sort(key=lambda x: x[0] if young else -x[0])
        return {"t": title, "u": "years", "rows": [[i, "%d y %d d" % (yrs, days - yrs_days(drv[i]["dob"], yrs)), "%s %d" % (short(ref[2]), ref[1])] for days, i, yrs, ref in rows[:n]]}
    def yrs_days(dob, yrs):
        b = day(dob)
        try: return (b.replace(year=b.year + yrs) - b).days
        except ValueError: return (b.replace(year=b.year + yrs, day=28) - b).days
    champ_age = sorted(((c["age"], c) for c in champs if c["done"] and c["age"] is not None), key=lambda x: x[0])
    def champ_age_rows(young):
        rows = []
        for c in champs:
            if not c["done"] or not c["dec"]: continue
            i = c["top"][0][0]; a = age(drv[i]["dob"], c["dec"][2])
            if a: rows.append((a[1], i, a[0], c["y"]))
        rows.sort(key=lambda x: x[0] if young else -x[0])
        seen, out = set(), []
        for days, i, yrs, y in rows:
            if i in seen: continue
            seen.add(i); out.append([i, "%d y %d d" % (yrs, days - yrs_days(drv[i]["dob"], yrs)), "%d title" % y])
        return out[:10]
    cat("Age", [
        agetop("Youngest race winners", "fwin"), agetop("Oldest race winners", "lastwin", young=False),
        {"t": "Youngest world champions", "u": "years", "rows": champ_age_rows(True)},
        {"t": "Oldest world champions", "u": "years", "rows": champ_age_rows(False)},
        agetop("Youngest pole sitters", "fpole"), agetop("Youngest race starters", "first"),
        agetop("Oldest race starters", "laststart", young=False),
    ])
    cat("Other", [
        top(lambda i: st[i]["wins"] if not titles.get(i) else None, "Most wins without a title", "wins"),
        top(lambda i: st[i]["starts"] if not st[i]["wins"] else None, "Most starts without a win", "starts"),
        top(lambda i: st[i]["pod"] if not st[i]["wins"] else None, "Most podiums without a win", "podiums"),
        top(lambda i: len(st[i]["wteams"]) if len(st[i]["wteams"]) > 1 else None, "Won races with the most teams", "teams", extra=lambda i: ", ".join(st[i]["wteams"])),
        top(lambda i: max(st[i]["wins_at"].values()) if st[i]["wins_at"] else None, "Most wins at the same Grand Prix", "wins",
            extra=lambda i: max(st[i]["wins_at"], key=st[i]["wins_at"].get) if st[i]["wins_at"] else ""),
        top(lambda i: len(st[i]["years"]), "Most seasons raced", "seasons", extra=lambda i: "%d–%d" % (min(st[i]["years"]), max(st[i]["years"]))),
    ])
    # rank lookups for facts
    rank = {}
    for c in rec:
        for it in c["items"]:
            for pos, row in enumerate(it["rows"]):
                # equal values share a rank
                r = 1 + sum(1 for x in it["rows"] if x[1] != row[1] and ((x[1] > row[1]) if it["t"].startswith(("Most", "High", "Big", "Won")) else (str(x[1]) < str(row[1]))))
                rank.setdefault(row[0], []).append((it["t"], r, row[1], row[2], it["u"]))
    # ---- family
    fam = {}
    for p, d, t in base["family"]:
        if not isinstance(p, int): continue
        g = 1 if drv[p].get("g") == "F" else 0
        fam.setdefault(p, []).append("%s of %s" % (REL.get(t, ("Relative", "Relative"))[g], drv[d]["n"]))
    # ---- driver list for the page
    cc_name = base["countries"]
    women = [j for j in range(N) if drv[j].get("g") == "F" and st[j]["starts"]]
    out = []
    for i in range(N):
        s, d = st[i], drv[i]
        if not s["entries"]: continue
        ys = sorted(s["years"]) or sorted({races[k]["y"] for k in range(len(races)) for row in races[k]["rows"] if row[0] == i})
        cs = {c[0]: c for c in d.get("cs", [])}
        bcp = min((c[1] for y, c in cs.items() if c[1] and (y < year_now or season_done)), default=None)
        teams = sorted(s["teams"], key=lambda t: -s["teams"][t])
        facts = []
        t = titles.get(i)
        if t: facts.append("%s world champion: %s." % ({1: "One-time", 2: "Two-time", 3: "Three-time"}.get(len(t), "%d-time" % len(t)), ", ".join(map(str, t))))
        for title, r, val, ex, u in sorted(rank.get(i, []), key=lambda x: x[1]):
            vt = val if isinstance(val, str) else (fmt(val) + ("%" if u == "%" else " " + (u[:-1] if val == 1 and u.endswith("s") else u)))
            if r == 1 and title in FACT: facts.append("All-time record: %s (%s%s)." % (FACT[title], vt, (", " + ex) if ex else ""))
            elif 1 < r <= 10 and title in RANKED: facts.append("%s on the all-time list for %s." % (ord_(r), RANKED[title]))
        if s["fwin"]:
            a = age_at(i, s["fwin"])
            facts.append("First win: %d %s%s%s." % (s["fwin"][1], s["fwin"][2], " (aged %d)" % a[0] if a else "", ", on debut" if s["first"] and s["fwin"][0] == s["first"][0] else ""))
            if s["lwin"] and s["lwin"] != s["fwin"]: facts.append("Last win: %d %s." % (s["lwin"][1], s["lwin"][2]))
            fav = max(s["wins_at"], key=s["wins_at"].get)
            if s["wins_at"][fav] > 1: facts.append("Won the %s %s." % (fav, plural(s["wins_at"][fav], "time")))
        elif s["fpod"]:
            facts.append("Best result: %s, first podium at the %d %s." % (ord_(s["bres"]), s["fpod"][1], s["fpod"][2]))
        elif s["bres"]:
            facts.append("Best finish: %s." % ord_(s["bres"]))
        if len(s["wteams"]) > 1: facts.append("Won races with %d teams: %s." % (len(s["wteams"]), ", ".join(s["wteams"])))
        held = {t for t, r, *_ in rank.get(i, []) if r == 1}
        for k, lab in (("wins", "wins"), ("poles", "poles"), ("pod", "podiums")):
            n = run[i][k][0]
            if {"wins": "Most consecutive race wins", "poles": "Most consecutive pole positions", "pod": "Most consecutive podiums"}[k] in held: continue
            if n >= (3 if k != "pod" else 5): facts.append("Best run: %d %s in a row (%s)." % (n, lab, runtxt(run[i][k])))
        if s["first"]:
            a = age_at(i, s["first"])
            facts.append("Debut: %d %s%s." % (s["first"][1], s["first"][2], " (aged %d)" % a[0] if a else ""))
        if s["starts"] == 0 and s["entries"]: facts.append("Entered %s but never started one." % plural(s["entries"], "race"))
        if d.get("g") == "F" and s["starts"]:
            facts.append("One of %d women to start a World Championship race." % len(women))
            if s["pts"] > 0 and len([j for j in women if st[j]["pts"] > 0]) == 1: facts.append("The only woman to score World Championship points (%s)." % fmt(s["pts"]))
        facts += [f + "." for f in fam.get(i, [])]
        out.append({"i": i, "n": d["n"], "id": d["id"], "cc": d["cc"], "cc2": d.get("cc2"), "dob": d["dob"], "dod": d["dod"], "pob": d["pob"], "cob": d.get("cob"),
                    "ab": d.get("ab"), "no": d.get("no"), "y": [ys[0], ys[-1]] if ys else None, "ns": len(ys),
                    "e": s["entries"], "s": s["starts"], "w": s["wins"], "p": s["pod"], "pl": s["poles"], "fl": s["fl"], "pts": round(s["pts"], 2),
                    "laps": s["laps"], "sw": s["sw"], "ss": s["sst"], "gs": s["gs"], "t": len(t or []), "ty": t or [], "bcp": bcp,
                    "br": s["bres"], "bg": s["bgrid"], "teams": teams, "facts": facts, "act": bool(ys and ys[-1] == year_now)})
    # ---- countries
    C = {}
    for o in out:
        c = C.setdefault(o["cc"], {"cc": o["cc"], "n": cc_name.get(o["cc"], [o["cc"], o["cc"]])[0], "dem": cc_name.get(o["cc"], [o["cc"], o["cc"]])[1],
                                   "d": 0, "st": 0, "w": 0, "p": 0, "pl": 0, "t": 0, "winners": 0, "champs": [], "best": None, "first": None})
        c["d"] += 1; c["st"] += o["s"]; c["w"] += o["w"]; c["p"] += o["p"]; c["pl"] += o["pl"]; c["t"] += o["t"]; c["winners"] += o["w"] > 0
        if o["t"]: c["champs"].append([o["i"], o["t"]])
        if o["w"] and (c["best"] is None or o["w"] > c["best"][1]): c["best"] = [o["i"], o["w"]]
        if o["y"] and (c["first"] is None or o["y"][0] < c["first"][1]): c["first"] = [o["i"], o["y"][0]]
    countries = sorted(C.values(), key=lambda c: (-c["t"], -c["w"], -c["p"], -c["d"]))
    TM = team_history(base, D, races, champs, year_now, season_done, None)
    return {**TM, "source": base["source"], "upto": [races[-1]["y"], races[-1]["r"]], "races": len(races), "now": year_now, "done": season_done,
            "drivers": out, "champs": champs, "records": rec, "countries": countries,
            "ccn": {k: v[0] for k, v in cc_name.items()}}


# ================================================================ constructors and engines
def team_history(base, D, races, champs, year_now, season_done, rec_rank_fact):
    drv, CN, CI, EN = base["drivers"], base["cons"], base["cinfo"], base["engines"]
    while len(CI) < len(CN): CI.append({"id": norm(CN[len(CI)]).replace(" ", "-"), "full": CN[len(CI)], "cc": None})
    NC, NE = len(CN), len(EN)
    def blank(): return dict(entries=0, starts=0, wins=0, onetwo=0, pod=0, podr=0, poles=0, fl=0, pts=0.0, laps=0, sst=0, sw=0,
                             bres=None, bgrid=None, years=set(), first=None, fwin=None, lwin=None, drivers={}, winners={}, engines={}, teams={},
                             seq=[], bys={})
    T = [blank() for _ in range(NC)]; E = [blank() for _ in range(NE)]
    def ref(k, R): return (k, R["y"], R["gp"])
    for k, R in enumerate(races):
        per_c, per_e = {}, {}
        for row in R["rows"]:
            i, pos, code, pts, grid, laps, pole, ci, eng = row[:9]
            for X, key, bucket in ((T, ci, per_c), (E, eng, per_e)):
                if key is None or key < 0: continue
                b = bucket.setdefault(key, dict(st=False, pos=[], pole=False, drivers=set(), pts=0.0, sgrid=None))
                b["pts"] += pts; b["drivers"].add(i)
                s = X[key]
                if pole: b["pole"] = True
                if grid and code not in (1, 2) and (s["bgrid"] is None or grid < s["bgrid"]): s["bgrid"] = grid
                if code in NONSTART: continue
                b["st"] = True; s["laps"] += laps
                if pos:
                    b["pos"].append(pos)
                    if s["bres"] is None or pos < s["bres"]: s["bres"] = pos
                s["drivers"][i] = s["drivers"].get(i, 0) + 1
                if X is T: s["engines"][EN[eng]["n"] if 0 <= eng < NE else "?"] = s["engines"].get(EN[eng]["n"] if 0 <= eng < NE else "?", set()) | {R["y"]}
                else: s["teams"][CN[ci]] = s["teams"].get(CN[ci], set()) | {R["y"]}
        fl_list = [tuple(x) for x in R.get("flc", [])]
        if not fl_list:   # rounds added from the site: the team of the driver who set it
            for f in R["fl"]:
                row = next((r for r in R["rows"] if r[0] == f and r[2] not in NONSTART), None)
                if row: fl_list.append((row[7], row[8]))
        for X, bucket, idx in ((T, per_c, 0), (E, per_e, 1)):
            for key, b in bucket.items():
                s = X[key]; s["entries"] += 1; s["pts"] += b["pts"]
                if b["pole"]: s["poles"] += 1
                s["fl"] += sum(1 for x in fl_list if x[idx] == key)
                if not b["st"]: continue
                s["starts"] += 1; s["years"].add(R["y"])
                if s["first"] is None: s["first"] = ref(k, R)
                ps = sorted(set(b["pos"])); win = 1 in ps   # a shared car is one car
                if win:
                    s["wins"] += 1; s["lwin"] = ref(k, R)
                    if s["fwin"] is None: s["fwin"] = ref(k, R)
                    for row in R["rows"]:
                        if row[1] == 1 and (row[7] if idx == 0 else row[8]) == key: s["winners"][row[0]] = s["winners"].get(row[0], 0) + 1
                if 1 in ps and 2 in ps: s["onetwo"] += 1
                np_ = sum(1 for p in ps if 1 <= p <= 3)
                s["pod"] += np_; s["podr"] += np_ > 0
                s["seq"].append((k, win, b["pole"], 1 in ps and 2 in ps))
                y = s["bys"].setdefault(R["y"], dict(w=0, p=0, o=0, r=0, pts=0.0)); y["w"] += win; y["p"] += b["pole"]; y["o"] += 1 in ps and 2 in ps; y["r"] += 1
        sp_st = set()
        for i, pos, pts, ok in R["sp"]:
            row = next((r for r in R["rows"] if r[0] == i), None)
            if not row: continue
            for X, key, tag in ((T, row[7], "c"), (E, row[8], "e")):
                if key is None or key < 0: continue
                X[key]["pts"] += pts
                if ok and (tag, key) not in sp_st: X[key]["sst"] += 1; sp_st.add((tag, key))
                if pos == 1: X[key]["sw"] += 1
    # ---- constructors' championship (from 1958)
    cst = {int(y): v for y, v in base["cstand"].items()}
    by_name = {norm(n): k for k, n in enumerate(CN)}
    last_ci = {}
    for R in reversed(races):
        for row in R["rows"]: last_ci.setdefault(row[0], row[7])
    full = {norm(d["n"]): j for j, d in enumerate(drv)}
    def site_team(name):
        # "Red Bull Racing" / "Haas F1 Team" on the site = "Red Bull" / "Haas" in F1DB: go through the team's drivers
        for d in D.get("DRIVERS", []):
            j = full.get(norm(d[0]))
            if d[2] == name and j in last_ci: return last_ci[j]
        return by_name.get(norm(name))
    cur = []
    for k, c in enumerate(D.get("CONSTRUCTORS", [])):
        ci = site_team(c[0])
        if ci is None: continue
        e = next((row[8] for R in reversed(races) for row in R["rows"] if row[7] == ci), -1)
        cur.append([k + 1, ci, e, c[1]])
    if cur: cst[year_now] = cur
    by_year = {}
    for k, R in enumerate(races): by_year.setdefault(R["y"], []).append(k)
    dchamp = {c["y"]: c for c in champs}
    cchamps, ctitles, etitles, dtitles_t, dtitles_e = [], {}, {}, {}, {}
    def ename(ci, e): return CN[ci] if e < 0 or EN[e]["n"] == CN[ci] else "%s-%s" % (CN[ci], EN[e]["n"])
    for y in sorted(cst):
        top = cst[y]; done = y < year_now or season_done; ks = by_year.get(y, [])
        dec = next((k for k in ks if races[k].get("cdec")), None)
        if done and dec is None and ks: dec = ks[-1]
        c0 = top[0]
        if done:
            ctitles.setdefault(c0[1], []).append(y)
            if c0[2] >= 0: etitles.setdefault(c0[2], []).append(y)
        def wins_in(ci): return sum(1 for k in ks if any(r[1] == 1 and r[7] == ci for r in races[k]["rows"]))
        dc = dchamp.get(y)
        cchamps.append({"y": y, "done": done, "rounds": len(ks),
                        "top": [[ci, ename(ci, e), pts, wins_in(ci)] for _, ci, e, pts in top[:3]],
                        "dec": [races[dec]["gp"], races[dec]["r"], races[dec]["d"], races[dec]["cc"]] if (done and dec is not None) else None,
                        "left": (len(ks) - races[dec]["r"]) if (done and dec is not None) else None,
                        "margin": round(top[0][3] - top[1][3], 1) if len(top) > 1 else None,
                        "dch": [dc["top"][0][0], dc["top"][0][1]] if dc else None})
    # ---- the champion team's season in detail (as in Wikipedia's table of constructors' champions)
    TY = base.get("tyres", [])
    def season_detail(ci, y, pts):
        ks = by_year.get(y, [])
        drivers, nums, tyres = {}, {}, {}
        poles = wins = pod = fl = 0
        for k in ks:
            R = races[k]; mine = [r for r in R["rows"] if r[7] == ci]
            if not mine: continue
            if any(r[6] for r in mine): poles += 1
            if any(r[1] == 1 for r in mine): wins += 1
            pod += len({r[1] for r in mine if 1 <= r[1] <= 3})
            fl += sum(1 for x in R.get("flc", []) if x[0] == ci) if R.get("flc") else sum(1 for f in R["fl"] for r in mine if r[0] == f and r[2] not in NONSTART)
            for r in mine:
                if r[2] in NONSTART: continue
                drivers[r[0]] = drivers.get(r[0], 0) + 1
                if len(r) > 10 and r[10]: nums.setdefault(r[0], {}); nums[r[0]][r[10]] = nums[r[0]].get(r[10], 0) + 1
                if len(r) > 9 and r[9] is not None and r[9] >= 0: tyres[r[9]] = tyres.get(r[9], 0) + 1
        n = len(ks)
        dl = []
        for i, c in sorted(drivers.items(), key=lambda kv: (-kv[1], min(nums.get(kv[0], {0: 0})) if nums.get(kv[0]) else 999)):
            no = max(nums[i], key=nums[i].get) if nums.get(i) else None
            dl.append([i, no, c, 1 if c * 3 <= n else 0])   # last: a stand-in (a third of the races or fewer)
        dl.sort(key=lambda d: (d[3], d[1] if d[1] is not None else 999))
        # share of the points available: 1958-78 only a team's best car scored and only its best results counted;
        # from 1979 every car scores, so the most a team can get is 1st + 2nd in every race (+ sprints, + the fastest-lap point 2019-24)
        pct = gross = None
        if y >= 1958:
            if y <= 1978:
                win = 8 if y <= 1960 else 9
                table = {1958: [8, 6, 4, 3, 2], 1959: [8, 6, 4, 3, 2], 1960: [8, 6, 4, 3, 2, 1]}.get(y, [9, 6, 4, 3, 2, 1])
                gp = [k for k in ks if "Indianapolis" not in races[k]["gp"]]
                g = 0
                for k in gp:
                    best = min((r[1] for r in races[k]["rows"] if r[7] == ci and r[1]), default=0)
                    if best and best <= len(table): g += table[best - 1]
                cnt = COUNTED.get(y, len(gp))
                pct = round(100 * pts / (cnt * win), 2); gross = round(100 * g / (len(gp) * win), 2)
            else:
                per = 15 if y <= 1990 else 16 if y <= 2002 else 18 if y <= 2009 else 43
                win = 9 if y <= 1990 else 10 if y <= 2009 else 25
                mx = 0
                for k in ks:
                    # a shortened race gave half points (Monaco 1984, Adelaide 1991, Sepang 2009, Spa 2021); Abu Dhabi 2014 gave double
                    p1 = max((r[3] for r in races[k]["rows"] if r[1] == 1), default=win)
                    fl1 = 1 if (2019 <= y <= 2024 and any(r[1] == 1 and r[0] in races[k]["fl"] for r in races[k]["rows"]) and p1 > win * .75) else 0
                    f = round((p1 - fl1) / win * 2) / 2 if p1 else 1
                    f = f if f in (0.5, 2) else 1
                    mx += per * f + (1 if 2019 <= y <= 2024 and f >= 1 else 0)
                spr = sum(1 for k in ks if races[k]["sp"])
                mx += spr * (5 if y == 2021 else 15)
                pct = round(100 * pts / mx, 2)
        return {"drv": dl, "tyre": [TY[t]["n"] for t in sorted(tyres, key=lambda t: -tyres[t])] if TY else [],
                "poles": poles, "wins": wins, "pod": pod, "fl": fl, "pct": pct, "gross": gross}
    for c in cchamps:
        ci = c["top"][0][0]; e = next((r[2] for r in cst[c["y"]] if r[1] == ci), -1)
        c["d"] = season_detail(ci, c["y"], c["top"][0][2])
        c["eng"] = [EN[e]["n"], EN[e]["cc"]] if e >= 0 else None
        c["cc"] = CI[ci]["cc"]
        c["mpct"] = round(100 * c["margin"] / c["top"][0][2], 2) if c["margin"] is not None and c["top"][0][2] else None
    # drivers' titles by team and engine: the champion's car that season
    for c in champs:
        if not c["done"]: continue
        i, y = c["top"][0][0], c["y"]
        cnt = {}
        for k in by_year.get(y, []):
            for r in races[k]["rows"]:
                if r[0] == i and r[2] not in NONSTART: cnt[(r[7], r[8])] = cnt.get((r[7], r[8]), 0) + 1
        if cnt:
            ci, e = max(cnt, key=cnt.get)
            dtitles_t.setdefault(ci, []).append([y, i]); dtitles_e.setdefault(e, []).append([y, i])
    # ---- records
    cpts_all = {}
    for y, v in cst.items():
        for _, ci, e, pts in v: cpts_all[ci] = cpts_all.get(ci, 0) + pts
    rec = []
    def run(seq, j):
        best = cur_ = 0; a = bs = be = None
        for x in seq:
            if x[j]:
                cur_ += 1
                if cur_ == 1: a = x[0]
                if cur_ > best: best, bs, be = cur_, a, x[0]
            else: cur_ = 0
        return best, bs, be
    def runtxt(r):
        n, a, b = r
        sh = lambda g: g.replace(" Grand Prix", " GP")
        return "%s %d – %s %d" % (sh(races[a]["gp"]), races[a]["y"], sh(races[b]["gp"]), races[b]["y"]) if n else ""
    truns = [{"w": run(T[c]["seq"], 1), "p": run(T[c]["seq"], 2), "o": run(T[c]["seq"], 3)} for c in range(NC)]
    def trun_titles(ys):
        best = cur_ = 0; prev = s0 = bs = None
        for y in sorted(ys):
            cur_ = cur_ + 1 if prev == y - 1 else 1
            if cur_ == 1: s0 = y
            if cur_ > best: best, bs = cur_, (s0, y)
            prev = y
        return best, bs
    ctr = {c: trun_titles(v) for c, v in ctitles.items()}
    def top(X, key, title, unit, extra=lambda c: "", n=10, filt=lambda c: True):
        idx = sorted((c for c in range(len(X)) if filt(c) and key(c)), key=lambda c: (-key(c), CN[c] if X is T else EN[c]["n"]))
        out = []
        for c in idx:
            if len(out) >= n and key(c) != out[-1][1]: break
            out.append([c, key(c), extra(c)])
        return {"t": title, "u": unit, "rows": out[:n + 5]}
    def seasontop(X, f, title, unit, extra=lambda c, y, v: "", n=10):
        rows = sorted(((c, y, v) for c in range(len(X)) for y, v in X[c]["bys"].items() if f(y, v)), key=lambda t: (-f(t[1], t[2]), t[1]))
        out = []
        for c, y, v in rows:
            val = f(y, v)
            if len(out) >= n and val != out[-1][1]: break
            ex = extra(c, y, v); out.append([c, val, "%d%s" % (y, (" · " + ex) if ex else "")])
        return {"t": title, "u": unit, "rows": out[:n + 5]}
    nr = {y: len(ks) for y, ks in by_year.items()}
    cdone = [c for c in cchamps if c["done"] and c["margin"] is not None]
    rec.append({"cat": "Career", "items": [
        top(T, lambda c: len(ctitles.get(c, [])), "Most constructors' titles", "titles", extra=lambda c: ", ".join(map(str, ctitles.get(c, [])))),
        top(T, lambda c: len(dtitles_t.get(c, [])), "Most drivers' titles", "titles", extra=lambda c: ", ".join(str(y) for y, _ in dtitles_t.get(c, []))),
        top(T, lambda c: T[c]["wins"], "Most race wins", "wins"),
        top(T, lambda c: T[c]["poles"], "Most pole positions", "poles"),
        top(T, lambda c: T[c]["onetwo"], "Most 1-2 finishes", "1-2s"),
        top(T, lambda c: T[c]["pod"], "Most podiums", "podiums"),
        top(T, lambda c: T[c]["fl"], "Most fastest laps", "fastest laps"),
        top(T, lambda c: T[c]["starts"], "Most races", "races"),
        top(T, lambda c: cpts_all.get(c), "Most points", "points", extra=lambda c: "constructors' championship points"),
        top(T, lambda c: round(100 * T[c]["wins"] / T[c]["starts"], 1) if T[c]["starts"] >= 50 and T[c]["wins"] else None, "Highest win rate (50+ races)", "%",
            extra=lambda c: "%d wins from %d races" % (T[c]["wins"], T[c]["starts"])),
    ]})
    rec.append({"cat": "In a row", "items": [
        top(T, lambda c: ctr.get(c, (0,))[0] if ctr.get(c, (0,))[0] > 1 else None, "Most consecutive titles", "titles", extra=lambda c: "%d–%d" % ctr[c][1] if c in ctr else ""),
        top(T, lambda c: truns[c]["w"][0] if truns[c]["w"][0] > 3 else None, "Most consecutive race wins", "wins", extra=lambda c: runtxt(truns[c]["w"])),
        top(T, lambda c: truns[c]["p"][0] if truns[c]["p"][0] > 3 else None, "Most consecutive pole positions", "poles", extra=lambda c: runtxt(truns[c]["p"])),
        top(T, lambda c: truns[c]["o"][0] if truns[c]["o"][0] > 2 else None, "Most consecutive 1-2 finishes", "1-2s", extra=lambda c: runtxt(truns[c]["o"])),
    ]})
    rec.append({"cat": "In one season", "items": [
        seasontop(T, lambda y, v: v["w"], "Most wins in a season", "wins", extra=lambda c, y, v: "from %d races" % nr[y]),
        seasontop(T, lambda y, v: round(100 * v["w"] / nr[y], 1) if v["w"] >= 3 else 0, "Highest share of a season's races won", "%", extra=lambda c, y, v: "%d of %d" % (v["w"], nr[y])),
        seasontop(T, lambda y, v: v["o"], "Most 1-2 finishes in a season", "1-2s"),
        seasontop(T, lambda y, v: v["p"], "Most poles in a season", "poles"),
        {"t": "Most points in a season", "u": "points", "rows": [[ci, pts, "%d" % y] for y, ci, pts in sorted(((y, r[1], r[3]) for y, v in cst.items() for r in v[:1]), key=lambda t: -t[2])[:10]]},
        {"t": "Biggest title-winning margin", "u": "points", "rows": [[c["top"][0][0], c["margin"], "%d · over %s" % (c["y"], c["top"][1][1])] for c in sorted(cdone, key=lambda c: -c["margin"])[:10]]},
        {"t": "Closest title fights", "u": "points", "rows": [[c["top"][0][0], c["margin"], "%d · over %s" % (c["y"], c["top"][1][1])] for c in sorted(cdone, key=lambda c: c["margin"])[:10]]},
    ]})
    rec.append({"cat": "Other", "items": [
        top(T, lambda c: len(T[c]["winners"]), "Most different race winners", "drivers", extra=lambda c: ", ".join(drv[i]["ln"] for i in sorted(T[c]["winners"], key=lambda i: -T[c]["winners"][i])[:4]) + ("…" if len(T[c]["winners"]) > 4 else "")),
        top(T, lambda c: len(T[c]["drivers"]), "Most drivers raced", "drivers"),
        top(T, lambda c: len(T[c]["years"]), "Most seasons", "seasons", extra=lambda c: "%d–%d" % (min(T[c]["years"]), max(T[c]["years"]))),
        top(T, lambda c: T[c]["wins"] if not ctitles.get(c) else None, "Most wins without a constructors' title", "wins"),
        top(T, lambda c: T[c]["starts"] if not T[c]["wins"] else None, "Most races without a win", "races"),
    ]})
    rec.append({"cat": "Engines", "items": [
        top(E, lambda e: len(etitles.get(e, [])), "Most constructors' titles (engine)", "titles", extra=lambda e: ", ".join(map(str, etitles.get(e, [])))),
        top(E, lambda e: len(dtitles_e.get(e, [])), "Most drivers' titles (engine)", "titles", extra=lambda e: ", ".join(str(y) for y, _ in dtitles_e.get(e, []))),
        top(E, lambda e: E[e]["wins"], "Most race wins (engine)", "wins"),
        top(E, lambda e: E[e]["poles"], "Most pole positions (engine)", "poles"),
        top(E, lambda e: len(E[e]["teams"]), "Most teams supplied", "teams"),
        top(E, lambda e: len(E[e]["years"]), "Most seasons (engine)", "seasons", extra=lambda e: "%d–%d" % (min(E[e]["years"]), max(E[e]["years"]))),
    ]})
    for c in rec:
        for it in c["items"]: it["k"] = "e" if c["cat"] == "Engines" else "c"
    rank = {}
    for c in rec:
        for it in c["items"]:
            for row in it["rows"]:
                r = 1 + sum(1 for x in it["rows"] if x[1] != row[1] and (x[1] > row[1] if not it["t"].startswith("Closest") else x[1] < row[1]))
                rank.setdefault((it["k"], row[0]), []).append((it["t"], r, row[1], row[2], it["u"]))
    # ---- lineage
    chron = {int(p): v for p, v in base.get("chron", {}).items()}
    lineage = {}
    for p, v in chron.items():
        for ci, a, b in v: lineage.setdefault(ci, []).append(p)
    def years_txt(s):
        if not s["years"]: return ""
        a, b = min(s["years"]), max(s["years"]); return str(a) if a == b else "%d–%d" % (a, b)
    def vt(val, u):
        return val if isinstance(val, str) else (fmt(val) + ("%" if u == "%" else " " + (u[:-1] if val == 1 and u.endswith("s") else u)))
    # ---- output lists
    cpts, epts = {}, {}
    for y, v in cst.items():
        for _, ci, e, pts in v:
            cpts[ci] = cpts.get(ci, 0) + pts
            if e >= 0: epts[e] = epts.get(e, 0) + pts
    tout = []
    for c in range(NC):
        s = T[c]
        if not s["entries"]: continue
        facts = []
        ct = ctitles.get(c)
        if ct: facts.append("%s constructors' champion: %s." % (plural(len(ct), "time").split(" ")[0] + "-time" if len(ct) > 1 else "One-time", ", ".join(map(str, ct))))
        dt = dtitles_t.get(c)
        if dt: facts.append("Drivers' champions with the team: %s." % ", ".join("%s %d" % (drv[i]["n"], y) for y, i in dt))
        for title, r, val, ex, u in sorted(rank.get(("c", c), []), key=lambda x: x[1]):
            if r == 1: facts.append("All-time record: %s (%s%s)." % ("closest constructors' title win" if title.startswith("Closest") else title[0].lower() + title[1:], vt(val, u), (", " + ex) if ex else ""))
            elif r <= 10 and title in ("Most race wins", "Most pole positions", "Most 1-2 finishes", "Most podiums", "Most constructors' titles", "Most races", "Most points"):
                facts.append("%s on the all-time list for %s." % (ord_(r), title[5:].lower()))
        if s["fwin"]:
            w = next((drv[row[0]]["n"] for row in races[s["fwin"][0]]["rows"] if row[1] == 1 and row[7] == c), "")
            facts.append("First win: %d %s%s." % (s["fwin"][1], s["fwin"][2], " (%s)" % w if w else ""))
            if s["lwin"] != s["fwin"]:
                w = next((drv[row[0]]["n"] for row in races[s["lwin"][0]]["rows"] if row[1] == 1 and row[7] == c), "")
                facts.append("Most recent win: %d %s%s." % (s["lwin"][1], s["lwin"][2], " (%s)" % w if w else ""))
            if s["winners"]:
                tw = sorted(s["winners"], key=lambda i: -s["winners"][i])
                facts.append("Top race winner for the team: %s (%s)." % (drv[tw[0]]["n"], plural(s["winners"][tw[0]], "win")))
        elif s["bres"]: facts.append("Best race result: %s." % ord_(s["bres"]))
        best = max(s["bys"].items(), key=lambda kv: (kv[1]["w"], kv[1]["p"]), default=None)
        if best and best[1]["w"] > 1: facts.append("Best season: %d, with %d wins from %d races." % (best[0], best[1]["w"], best[1]["r"]))
        if s["first"]: facts.append("First race: %d %s." % (s["first"][1], s["first"][2]))
        for k, lab, mn in (("w", "wins", 4), ("o", "1-2 finishes", 3)):
            n = truns[c][k][0]
            if n >= mn and not any(t == {"w": "Most consecutive race wins", "o": "Most consecutive 1-2 finishes"}[k] and r == 1 for t, r, *_ in rank.get(("c", c), [])):
                facts.append("Best run: %d %s in a row (%s)." % (n, lab, runtxt(truns[c][k])))
        lin = []
        for p in lineage.get(c, []):
            chain = chron[p]
            if len(chain) > 1:
                lin.append(" → ".join("%s (%s)" % (CN[x], ("%d–%s" % (a, b if b else "")) if a != b else str(a)) for x, a, b in chain))
        if lin: facts.append("Team history: %s." % lin[0])
        tout.append({"i": c, "id": CI[c]["id"], "n": CN[c], "full": CI[c]["full"], "cc": CI[c]["cc"], "y": [min(s["years"]), max(s["years"])] if s["years"] else None,
                     "ns": len(s["years"]), "e": s["entries"], "s": s["starts"], "w": s["wins"], "o": s["onetwo"], "p": s["pod"], "pr": s["podr"],
                     "pl": s["poles"], "fl": s["fl"], "pts": round(cpts.get(c, 0), 2), "dpts": round(s["pts"], 2), "laps": s["laps"], "sw": s["sw"], "ss": s["sst"],
                     "t": len(ct or []), "ty": ct or [], "dt": len(dt or []), "dty": [[y, i] for y, i in (dt or [])],
                     "bcp": min((r[0] for y, v in cst.items() for r in v if r[1] == c and r[0] and (y < year_now or season_done)), default=None),
                     "br": s["bres"], "bg": s["bgrid"], "nd": len(s["drivers"]),
                     "top": [[i, n] for i, n in sorted(s["winners"].items(), key=lambda kv: -kv[1])[:6]],
                     "eng": [[n, min(ys), max(ys)] for n, ys in sorted(s["engines"].items(), key=lambda kv: min(kv[1]))],
                     "facts": facts, "act": bool(s["years"] and max(s["years"]) == year_now)})
    # two teams with the same name (e.g. Lotus 1958–94 and Lotus 2012–15): label them by their years
    seen = {}
    for o in tout: seen.setdefault(o["n"], []).append(o)
    for name, L in seen.items():
        if len(L) > 1:
            for o in L:
                if o["y"]: o["n2"] = "%s (%s)" % (name, str(o["y"][0]) if o["y"][0] == o["y"][1] else "%d–%s" % (o["y"][0], str(o["y"][1])[-2:]))
    eout = []
    for e in range(NE):
        s = E[e]
        if not s["entries"]: continue
        facts = []
        et, de = etitles.get(e), dtitles_e.get(e)
        if et: facts.append("Powered %s to the constructors' title: %s." % ("teams" if len({r[1] for y, v in cst.items() for r in v[:1] if r[2] == e}) > 1 else "its team", ", ".join(map(str, et))))
        if de: facts.append("Drivers' champions with this engine: %s." % ", ".join("%s %d" % (drv[i]["n"], y) for y, i in de))
        for title, r, val, ex, u in sorted(rank.get(("e", e), []), key=lambda x: x[1]):
            if r == 1: facts.append("All-time record: %s (%s%s)." % (title[0].lower() + title[1:].replace(" (engine)", ""), vt(val, u), (", " + ex) if ex else ""))
        if s["fwin"]: facts.append("First win: %d %s." % (s["fwin"][1], s["fwin"][2]))
        if s["first"]: facts.append("First race: %d %s." % (s["first"][1], s["first"][2]))
        eout.append({"i": e, "id": EN[e]["id"], "n": EN[e]["n"], "cc": EN[e]["cc"], "y": [min(s["years"]), max(s["years"])] if s["years"] else None, "ns": len(s["years"]),
                     "e": s["entries"], "s": s["starts"], "w": s["wins"], "p": s["pod"], "pr": s["podr"], "pl": s["poles"], "fl": s["fl"], "pts": round(epts.get(e, 0), 2), "laps": s["laps"], "sw": s["sw"], "ss": s["sst"],
                     "t": len(et or []), "ty": et or [], "dt": len(de or []), "dty": de or [], "br": s["bres"],
                     "teams": [[n, min(ys), max(ys)] for n, ys in sorted(s["teams"].items(), key=lambda kv: min(kv[1]))],
                     "facts": facts, "act": bool(s["years"] and max(s["years"]) == year_now)})
    C = {}
    for o in tout:
        c = C.setdefault(o["cc"], {"cc": o["cc"], "n": base["countries"].get(o["cc"], [o["cc"] or "", ""])[0], "c": 0, "w": 0, "pl": 0, "t": 0, "dt": 0, "best": None})
        c["c"] += 1; c["w"] += o["w"]; c["pl"] += o["pl"]; c["t"] += o["t"]; c["dt"] += o["dt"]
        if o["w"] and (c["best"] is None or o["w"] > c["best"][1]): c["best"] = [o["i"], o["w"]]
    return {"teams": tout, "engines": eout, "cchamps": cchamps, "crec": rec,
            "tcountries": sorted(C.values(), key=lambda c: (-c["t"], -c["w"], -c["c"]))}
