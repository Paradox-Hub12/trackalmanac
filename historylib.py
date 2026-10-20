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
    # newest races first, so "Schumacher" or "Verstappen" means the most recent driver of that name
    for R in reversed(base["races"]):
        for row in R["rows"]:
            d = drv[row[0]]; team.setdefault(row[0], row[7])
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
                if t not in base["cons"]: base["cons"].append(t)
                team[i] = base["cons"].index(t)
            rows.append([i, pos, code, num(x[5]) or 0, num(x[6]), num(x[3]), 0, team[i]])
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
            i, pos, code, pts, grid, laps, pole, ci = row
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
    return {"source": base["source"], "upto": [races[-1]["y"], races[-1]["r"]], "races": len(races), "now": year_now, "done": season_done,
            "drivers": out, "champs": champs, "records": rec, "countries": countries,
            "ccn": {k: v[0] for k, v in cc_name.items()}}
