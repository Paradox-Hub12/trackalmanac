#!/usr/bin/env python3
"""Make src/history.json (the History page's base data) from an F1DB JSON release.

    python3 scripts/history.py path/to/f1db-json-splitted [path/to/f1db/src/assets/circuits]

The first folder holds the f1db-*.json files of a release; the optional second one is the circuit SVG
folder of the F1DB repository (https://github.com/f1db/f1db/tree/main/src/assets/circuits), which makes
src/circuitmaps.json, the track outlines shown on the Circuits page.

Get the release from https://github.com/f1db/f1db/releases (f1db-json-splitted.zip, CC BY 4.0).
The file holds every World Championship race up to the newest race in that release, one row per
driver entry. build.py adds the newer 2026 rounds from src/data.json and computes all stats,
records and champions from these rows, so nothing here needs updating after a race weekend.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "history.json")

# entry results that are not race starts
NONSTART = {"DNQ": 1, "DNPQ": 2, "DNS": 3, "DNP": 4}
TEXTCODE = {"DNF": 5, "NC": 6, "DSQ": 7, "EX": 8}


def main(src):
    L = lambda n: json.load(open(os.path.join(src, "f1db-%s.json" % n), encoding="utf-8"))
    countries = {c["id"]: c for c in L("countries")}
    cons = {c["id"]: c["name"] for c in L("constructors")}
    gps = {g["id"]: g for g in L("grands-prix")}
    circ = {c["id"]: c for c in L("circuits")}
    races = sorted(L("races"), key=lambda r: (r["year"], r["round"]))
    results = L("races-race-results")
    # circuits and their layouts
    CIR = sorted(L("circuits"), key=lambda c: c["id"]); cirx = {c["id"]: k for k, c in enumerate(CIR)}
    LAY = {l["id"]: l for l in L("circuits-layouts")}
    # pole lap: the fastest lap of the driver qualifying first (overall time, or the best of Q1-Q3)
    plt = {}
    for x in L("races-qualifying-results"):
        if x["positionNumber"] == 1:
            ts = [t for t in (x.get("timeMillis"), x.get("q1Millis"), x.get("q2Millis"), x.get("q3Millis")) if t]
            if ts: plt[x["raceId"]] = min(ts)
    fl = {}  # race -> drivers with the fastest lap (shared in a few 1950s races)
    for x in L("races-fastest-laps"):
        if x["positionNumber"] == 1: fl.setdefault(x["raceId"], []).append(x)
    sprint = L("races-sprint-race-results")
    # keyed by car too: in a shared drive a driver can appear for two teams in one race
    grid = {(x["raceId"], x["driverId"], x["constructorId"]): x["positionNumber"] for x in L("races-starting-grid-positions")}
    drivers = L("drivers")

    # only races that have been run (results exist)
    run = {x["raceId"] for x in results}
    races = [r for r in races if r["id"] in run]
    dix = {}  # driver id -> index
    used = sorted({x["driverId"] for x in results}, key=lambda i: i)
    D = []
    byid = {d["id"]: d for d in drivers}
    for i in used:
        d = byid[i]
        cc = lambda k: countries[d[k]]["alpha2Code"] if d.get(k) else None
        dix[i] = len(D)
        D.append({"id": i, "n": d["name"], "fn": d["firstName"], "ln": d["lastName"], "full": d["fullName"],
                  "ab": d.get("abbreviation"), "no": d.get("permanentNumber"), "dob": d.get("dateOfBirth"),
                  "dod": d.get("dateOfDeath"), "pob": d.get("placeOfBirth"), "cob": cc("countryOfBirthCountryId"),
                  "cc": cc("nationalityCountryId"), "cc2": cc("secondNationalityCountryId"),
                  "gs": d.get("totalGrandSlams") or 0, "g": "F" if d.get("gender") == "FEMALE" else "M"})
    cix, CN = {}, []
    def ci(c):
        if c not in cix: cix[c] = len(CN); CN.append(cons.get(c, c))
        return cix[c]
    # engine makers and tyre suppliers, by index
    emk = {e["id"]: e for e in L("engine-manufacturers")}
    tmk = {t["id"]: t for t in L("tyre-manufacturers")}
    eix, EN, tix, TN = {}, [], {}, []
    def ei(e):
        if e not in eix: eix[e] = len(EN); EN.append(e)
        return eix[e]
    def ti(t):
        if t not in tix: tix[t] = len(TN); TN.append(t)
        return tix[t]
    byrace = {}
    for x in results: byrace.setdefault(x["raceId"], []).append(x)
    spr = {}
    for x in sprint: spr.setdefault(x["raceId"], []).append(x)
    R = []
    for r in races:
        rows = []
        for x in sorted(byrace[r["id"]], key=lambda x: x["positionDisplayOrder"]):
            t = x["positionText"]
            code = 0 if x["positionNumber"] else NONSTART.get(t, TEXTCODE.get(t, 5))
            if t == "EX" and not x["laps"]: code = 9   # excluded before the start: an entry, not a start
            g = grid.get((r["id"], x["driverId"], x["constructorId"]))
            # [driver, finishing position (0 = not classified), status code, points, grid, laps, pole, constructor]
            rows.append([dix[x["driverId"]], x["positionNumber"] or 0, code, x["points"] or 0, g or 0,
                         x["laps"] or 0, 1 if x.get("polePosition") else 0, ci(x["constructorId"]),
                         ei(x["engineManufacturerId"]), ti(x["tyreManufacturerId"]) if x.get("tyreManufacturerId") else -1,
                         int(x["driverNumber"]) if str(x.get("driverNumber") or "").isdigit() else 0])
        # [driver, position (0 = not classified), points, started (0 = did not start)]
        sp = [[dix[x["driverId"]], x["positionNumber"] or 0, x["points"] or 0, 0 if x["positionText"] in NONSTART else 1] for x in spr.get(r["id"], [])]
        g = gps[r["grandPrixId"]]
        R.append({"y": r["year"], "r": r["round"], "gp": g["fullName"], "cc": countries[g.get("countryId") or circ[r["circuitId"]]["countryId"]]["alpha2Code"],
                  "d": r["date"], "fl": [dix[x["driverId"]] for x in fl.get(r["id"], []) if x["driverId"] in dix],
                  "flc": [[ci(x["constructorId"]), ei(x["engineManufacturerId"])] for x in fl.get(r["id"], [])],
                  "c": cirx[r["circuitId"]], "lay": r.get("circuitLayoutId"), "plt": plt.get(r["id"]), "len": r.get("courseLength"), "laps": r.get("laps"),
                  "flt": min((x["timeMillis"] for x in fl.get(r["id"], []) if x.get("timeMillis")), default=None),
                  "gap": next((x["gapMillis"] for x in byrace[r["id"]] if x["positionNumber"] == 2 and x.get("gapMillis") and not x.get("gapLaps")), None), "dec": 1 if r.get("driversChampionshipDecider") else 0, "cdec": 1 if r.get("constructorsChampionshipDecider") else 0,
                  "rows": rows, "sp": sp})
    # season standings: top three of every season, official (counted) points
    ST = {}
    for x in L("seasons-driver-standings"):
        if x["positionNumber"] and x["positionNumber"] <= 3 and x["driverId"] in dix:
            ST.setdefault(str(x["year"]), []).append([x["positionNumber"], dix[x["driverId"]], x["points"]])
    for v in ST.values(): v.sort()
    # every driver's championship position each season: [year, position, points]
    for x in L("seasons-driver-standings"):
        if x["driverId"] in dix: D[dix[x["driverId"]]].setdefault("cs", []).append([x["year"], x["positionNumber"] or 0, x["points"] or 0])
    fam = [[dix[f["parentDriverId"]] if f["parentDriverId"] in dix else byid[f["parentDriverId"]]["name"], dix[f["driverId"]], f["type"]]
           for f in L("drivers-family-relationships") if f["driverId"] in dix]
    used_cc = {d[k] for d in D for k in ("cc", "cc2", "cob") if d.get(k)} | {r["cc"] for r in R}
    cont = {c["id"]: c["name"] for c in L("continents")}
    CC = {c["alpha2Code"]: [c["name"], c["demonym"], cont.get(c["continentId"])] for c in countries.values() if c["alpha2Code"] in used_cc}
    last = races[-1]
    # constructors' standings every season (from 1958): [position, constructor, engine, points]
    CST = {}
    for x in L("seasons-constructor-standings"):
        CST.setdefault(str(x["year"]), []).append([x["positionNumber"] or 0, ci(x["constructorId"]), ei(x["engineManufacturerId"]), x["points"] or 0])
    for v in CST.values(): v.sort(key=lambda r: (r[0] or 999))
    cfull = {c["id"]: c for c in L("constructors")}
    # team lineage: a team's history under earlier names, e.g. Tyrrell > BAR > Honda > Brawn > Mercedes
    CHR = {}
    for x in sorted(L("constructors-chronology"), key=lambda x: (x["parentConstructorId"], x["positionDisplayOrder"])):
        CHR.setdefault(str(ci(x["parentConstructorId"])), []).append([ci(x["constructorId"]), x["yearFrom"], x["yearTo"]])
    CI = [{"id": c, "full": cfull[c]["fullName"] if c in cfull else cons.get(c, c), "cc": countries[cfull[c]["countryId"]]["alpha2Code"] if c in cfull else None} for c in list(cix)]
    ENG = [{"id": e, "n": emk[e]["name"] if e in emk else e, "cc": countries[emk[e]["countryId"]]["alpha2Code"] if e in emk and emk[e].get("countryId") else None} for e in EN]
    TYR = [{"id": t, "n": tmk[t]["name"] if t in tmk else t, "cc": countries[tmk[t]["countryId"]]["alpha2Code"] if t in tmk and tmk[t].get("countryId") else None} for t in TN]
    for c in L("circuits"):
        a2 = countries[c["countryId"]]["alpha2Code"]
        if a2 not in CC: CC[a2] = [countries[c["countryId"]]["name"], countries[c["countryId"]]["demonym"], cont.get(countries[c["countryId"]]["continentId"])]
    for c in CI + ENG + TYR:
        if c["cc"] and c["cc"] not in CC:
            k = next(v for v in countries.values() if v["alpha2Code"] == c["cc"]); CC[c["cc"]] = [k["name"], k["demonym"], cont.get(k["continentId"])]
    out = {"source": "F1DB (github.com/f1db/f1db), CC BY 4.0", "upto": [last["year"], last["round"]],
           "drivers": D, "cons": CN, "cinfo": CI, "engines": ENG, "tyres": TYR, "cstand": CST, "chron": CHR, "countries": CC,
           "circuits": [{"id": c["id"], "n": c["name"], "full": c["fullName"], "prev": c.get("previousNames"), "type": c["type"], "dir": c["direction"],
                         "place": c["placeName"], "cc": countries[c["countryId"]]["alpha2Code"], "lat": c["latitude"], "lon": c["longitude"],
                         "len": c["length"], "turns": c["turns"]} for c in CIR],
           "layouts": {k: [cirx[l["circuitId"]], l["length"], l["turns"]] for k, l in LAY.items()}, "races": R, "standings": ST, "family": fam}
    txt = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
    print("wrote %s: %d drivers, %d races (to %d R%d), %d KB" % (OUT, len(D), len(R), last["year"], last["round"], len(txt) // 1024))


def maps(assets):
    """src/circuitmaps.json: every layout's outline (F1DB's circuit SVGs by Jules Roy, CC BY 4.0) as one path, 500 x 500 box."""
    import re
    d = {}
    folder = os.path.join(assets, "white")
    for f in sorted(os.listdir(folder)):
        if not f.endswith(".svg"): continue
        svg = open(os.path.join(folder, f), encoding="utf-8").read()
        paths = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
        if not paths: continue
        p = " ".join(paths)
        # two decimals in a 500 box (relative paths add up rounding errors); always keep them, because paths run numbers together ("12.04.5" = 12.04, .5)
        if not re.search(r"[aA]", p):   # arcs run their flags into the next number ("0 011.5"): leave those paths exactly as they are
            p = re.sub(r"-?\d+\.\d+", lambda m: "%.2f" % float(m.group()), p)
        d[f[:-4]] = p
    out = os.path.join(ROOT, "src", "circuitmaps.json")
    txt = json.dumps(d, separators=(",", ":"))
    open(out, "w", encoding="utf-8").write(txt + "\n")
    print("wrote %s: %d layouts, %d KB" % (out, len(d), len(txt) // 1024))


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3): sys.exit(__doc__)
    main(sys.argv[1])
    if len(sys.argv) == 3: maps(sys.argv[2])
