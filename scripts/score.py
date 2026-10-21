#!/usr/bin/env python3
"""Track Almanac Predictor scorer. Runs in the results workflow after update.py.

  1. Keeps rounds/{round} in Firestore in step with SCHED: lock time (start of qualifying),
     Grand Prix name, status and the car numbers that may be picked.
  2. For every round with a race classification, scores every pick and writes scores/{round}_{uid}
     when the result or the pick changed (so stewards' changes re-score automatically).
  3. Publishes data/game/leaderboard-2026.json and data/game/round-<n>.json for the site.

Credentials: the service account JSON in the environment variable FIREBASE_SERVICE_ACCOUNT
(a GitHub secret). Without it the script does nothing and exits 0, so the workflow keeps working
before the game is set up. FIRESTORE_EMULATOR_HOST is honoured for tests.

Everything is computed before anything is written to data/game/, so a failure never publishes
half a table; the script then exits 1 and the run fails.

  python3 scripts/score.py                 normal run
  python3 scripts/score.py --replay R FILE score the picks in FILE (JSON list) for round R offline, print the table
"""
import argparse, datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build
import gamelib as G

OUT = os.path.join(ROOT, "data", "game")
UTC = datetime.timezone.utc


def load():
    return build.load_data(os.path.join(ROOT, "src", "data.json"))


def table_for_round(D, rnd, picks, names, banned):
    """picks: list of dicts {uid, top5, pole, updatedAt(datetime)}. Returns (official, rows)."""
    off = G.official(D, rnd); lock = G.lock_at(D, rnd); allowed = set(G.cars(D))
    if not off: return None, []
    rows = []
    for p in picks:
        if not G.valid_pick(p, allowed): continue
        if lock and p.get("updatedAt") and p["updatedAt"] >= lock: continue      # cannot happen through the rules; belt and braces
        s = G.score(p, off)
        lead = (lock - p["updatedAt"]).total_seconds() if lock and p.get("updatedAt") else 0
        rows.append({"uid": p["uid"], "name": G.public_name(p["uid"], names.get(p["uid"], ""), banned), "points": s["points"],
                     "winners": int(s["winner"]), "exact": s["exact"], "pole": s["pole"], "slots": s["slots"], "lead": round(lead),
                     "top5": p["top5"], "polePick": p["pole"], "h": G.result_hash(off, p)})
    return off, G.rank(rows)


def season_table(per_round):
    tot = {}
    for rnd, rows in per_round.items():
        for r in rows:
            t = tot.setdefault(r["uid"], {"uid": r["uid"], "name": r["name"], "points": 0, "winners": 0, "exact": 0, "races": 0, "leadSum": 0})
            t["points"] += r["points"]; t["winners"] += r["winners"]; t["exact"] += r["exact"]; t["races"] += 1; t["leadSum"] += r["lead"]; t["name"] = r["name"]
    rows = list(tot.values())
    for t in rows: t["lead"] = round(t["leadSum"] / t["races"]) if t["races"] else 0   # average time before the lock
    return G.rank(rows)


def publish_files(D, per_round, offs):
    """The static tables (top 100), as file name -> text."""
    files = {}
    season = season_table(per_round)
    files["leaderboard-%d.json" % G.SEASON] = {"season": G.SEASON, "players": len(season), "rounds": sorted(int(r) for r in per_round),
        "top": [{k: r[k] for k in ("pos", "name", "points", "winners", "exact", "races")} for r in season[:100]]}
    for rnd, rows in per_round.items():
        R = next(x for x in D["RACES"] if x["r"] == int(rnd))
        files["round-%s.json" % rnd] = {"round": int(rnd), "gp": R["gp"], "official": offs[rnd], "players": len(rows),
            "top": [{k: r[k] for k in ("pos", "name", "points", "winners", "exact", "pole", "slots")} for r in rows[:100]]}
    return {k: json.dumps(v, ensure_ascii=False, separators=(",", ":")) + "\n" for k, v in files.items()}


def write_files(files):
    """Write only the files whose content changed."""
    if not files: return []
    os.makedirs(OUT, exist_ok=True)
    changed = []
    for f in os.listdir(OUT):                       # a round nobody plays any more (all accounts deleted)
        if f.startswith("round-") and f.endswith(".json") and f not in files:
            os.remove(os.path.join(OUT, f)); changed.append(f + " (removed)")
    for name, txt in files.items():
        f = os.path.join(OUT, name)
        if not os.path.exists(f) or open(f, encoding="utf-8").read() != txt:
            with open(f + ".tmp", "w", encoding="utf-8") as fh: fh.write(txt)
            os.replace(f + ".tmp", f); changed.append(name)
    return changed


NAMES_MAX_AGE = datetime.timedelta(hours=6)


def row_pack(r):
    """One table row as a short string (Firestore has no nested arrays): uid|points|winners|exact|pole|slot bits|lead|pos"""
    return "|".join(str(x) for x in [r["uid"], r["points"], r["winners"], r["exact"], int(bool(r["pole"])),
                                      sum(1 << i for i, ok in enumerate(r["slots"]) if ok), r["lead"], r["pos"]])


def row_unpack(a):
    uid, pts, w, ex, pole, sl, lead, pos = a.split("|")
    sl = int(sl)
    return {"uid": uid, "points": int(pts), "winners": int(w), "exact": int(ex), "pole": pole == "1",
            "slots": [bool(sl >> i & 1) for i in range(5)], "lead": int(lead), "pos": int(pos)}


def score_doc(rnd, r):
    return {"uid": r["uid"], "round": rnd, "points": r["points"], "winners": r["winners"], "exact": r["exact"],
            "pole": r["pole"], "slots": r["slots"], "lead": r["lead"], "pos": r["pos"]}


_DB = None
def get_db(sa=None):
    """Firestore client: the service account in production, the emulator (no credentials) in tests."""
    global _DB
    if _DB is None:
        sa = sa if sa is not None else os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
        if sa:
            import firebase_admin
            from firebase_admin import credentials, firestore
            _DB = firestore.client(firebase_admin.initialize_app(credentials.Certificate(json.loads(sa))))
        else:
            from google.cloud import firestore as gfs
            from google.auth.credentials import AnonymousCredentials
            _DB = gfs.Client(project=os.environ.get("GCLOUD_PROJECT", "demo-trackalmanac"), credentials=AnonymousCredentials())
    return _DB


def run_firebase(D, now=None):
    """Reads are kept low for the free plan: a normal run reads the rounds, one scorer-state doc and one
    table doc per scored round. Picks are read only when a round has to be (re)scored, display names only
    every few hours (or when something was re-scored, or on a manual run)."""
    sa = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
    emu = os.environ.get("FIRESTORE_EMULATOR_HOST")
    if not sa and not emu:
        print("Predictor: FIREBASE_SERVICE_ACCOUNT is not set; skipping scoring.")
        return 0
    db = get_db(sa)
    now = now or datetime.datetime.now(UTC)
    writes = []                                   # (collection, id, doc or None), written only once everything is computed

    # 1. rounds: lock time from SCHED, status, the cars that may be picked
    allowed = G.cars(D)
    have = {d.id: d.to_dict() for d in db.collection("rounds").stream()}
    for R in D["RACES"]:
        rnd = R["r"]; lock = G.lock_at(D, rnd)
        if not lock: continue
        status = "scored" if G.official(D, rnd) else ("locked" if now >= lock else "open")
        want = {"round": rnd, "gp": R["gp"], "lockAt": lock, "status": status, "cars": sorted(allowed), "drivers": {str(k): v for k, v in allowed.items()}}
        if have.get(str(rnd)) != want:
            writes.append(("rounds", str(rnd), want)); print("rounds/%d: lock %s, %s" % (rnd, lock.isoformat(), status))

    # 2. scored rounds: re-score only when the official result changed (or the round was never scored)
    state_ref = db.collection("system").document("scorer")
    st = state_ref.get(); st = st.to_dict() if st.exists else {}
    tables, fresh = {}, {}
    for R in D["RACES"]:
        rnd = R["r"]; off = G.official(D, rnd)
        if not off or not G.lock_at(D, rnd): continue          # rounds before the game existed have no lock time
        h = G.result_hash(off, {"top5": [], "pole": None})
        t = db.collection("tables").document(str(rnd)).get(); t = t.to_dict() if t.exists else None
        tables[rnd] = t
        if t and t.get("resultHash") == h: continue
        picks = []
        for d in db.collection("picks").where("round", "==", rnd).stream():
            p = d.to_dict(); p["uid"] = p.get("uid") or d.id.split("_", 1)[1]
            ts = p.get("updatedAt"); p["updatedAt"] = ts if isinstance(ts, datetime.datetime) else None
            picks.append(p)
        fresh[rnd] = (h, picks)
        print("round %d: scoring %d picks (%s)" % (rnd, len(picks), "result changed" if t else "first time"))

    # 3. display names (pub/) and bans: refreshed every few hours, after a re-score, or on a manual run
    manual = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
    at = st.get("namesAt")
    if fresh or manual or not at or now - at > NAMES_MAX_AGE or "names" not in st:
        raw = {d.id: (d.to_dict() or {}).get("name", "") for d in db.collection("pub").stream()}
        banned = {d.id for d in db.collection("bans").stream()}
        names = {u: G.public_name(u, n, banned) for u, n in raw.items()}
        if names != st.get("names") or not at or now - at > NAMES_MAX_AGE:
            writes.append(("system", "scorer", {"names": names, "namesAt": now}))
    else:
        names = st["names"]

    # 4. tables: rows for players who still have an account (pub/ doc), ranked; diff against what is stored
    per_round, offs = {}, {}
    table_writes, score_writes = [], []
    for rnd, t in tables.items():
        off = G.official(D, rnd)
        old = {r["uid"]: r for r in map(row_unpack, (t or {}).get("rows", []))}
        if rnd in fresh:
            h, picks = fresh[rnd]
            _, rows = table_for_round(D, rnd, [p for p in picks if p["uid"] in names], names, set())
        else:
            h = t["resultHash"]
            rows = G.rank([dict(r, name=names[u]) for u, r in old.items() if u in names])
        if rows: per_round[str(rnd)], offs[str(rnd)] = rows, off      # nobody played: no table to publish
        new = {r["uid"]: r for r in rows}
        for u, r in new.items():
            if rnd in fresh or old.get(u) is None or row_pack(old[u]) != row_pack(r):
                score_writes.append(("scores", "%d_%s" % (rnd, u), score_doc(rnd, r)))
        for u in old:
            if u not in new: score_writes.append(("scores", "%d_%s" % (rnd, u), None))
        packed = [row_pack(r) for r in rows]
        if not t or t.get("resultHash") != h or t.get("rows") != packed:
            table_writes.append(("tables", str(rnd), {"round": rnd, "resultHash": h, "official": off, "rows": packed}))

    # 5. write: scores first, then the tables (a table doc marks its round as done, so an interrupted run is redone next time)
    files = publish_files(D, per_round, offs)          # also computed before anything is written
    allw = writes + score_writes + table_writes
    batch, n = db.batch(), 0
    for col, did, doc in allw:
        ref = db.collection(col).document(did)
        (batch.set(ref, doc) if doc is not None else batch.delete(ref)); n += 1
        if n % 400 == 0: batch.commit(); batch = db.batch()
    if n % 400: batch.commit()
    changed = write_files(files)
    print("Predictor: %d rounds scored (%d re-scored), %d score docs written, files changed: %s"
          % (len(per_round), len(fresh), len(score_writes), ", ".join(changed) or "none"))
    return 0


def replay(D, rnd, path):
    picks = json.load(open(path))
    lock = G.lock_at(D, rnd)
    for p in picks:
        p["updatedAt"] = lock - datetime.timedelta(seconds=p.pop("secondsBeforeLock", 3600))
    off, rows = table_for_round(D, rnd, picks, {p["uid"]: p.get("name", p["uid"]) for p in picks}, set())
    print("Official R%d: top5 %s, pole %s" % (rnd, off["top5"], off["pole"]))
    for r in rows:
        print("%2d  %-12s %2d pts  winners %d exact %d pole %s  picked %s pole %s" % (r["pos"], r["name"], r["points"], r["winners"], r["exact"], r["pole"], r["top5"], r["polePick"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", nargs=2, metavar=("ROUND", "PICKS_JSON"))
    a = ap.parse_args()
    D = load()
    if a.replay:
        replay(D, int(a.replay[0]), a.replay[1]); return 0
    try:
        return run_firebase(D)
    except Exception as e:
        print("::error::Predictor scoring failed: %s" % e)
        import traceback; traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
