"""Track Almanac Predictor: scoring rules, kept free of Firebase so they can be tested offline.

Each Grand Prix a player picks the top five finishers in order and the pole sitter.
Exact matches only: P1 5, P2 3, P3 2, P4 1, P5 1, pole 3 (15 for a perfect weekend).
"""
import datetime, hashlib, json, unicodedata

SEASON = 2026
SLOT_POINTS = [5, 3, 2, 1, 1]
POLE_POINTS = 3
MAX_POINTS = sum(SLOT_POINTS) + POLE_POINTS


def lock_at(D, rnd):
    """Start of Qualifying for the round (UTC datetime), or None if the schedule has no qualifying."""
    s = (D.get("SCHED") or {}).get(str(rnd))
    if not s: return None
    for name, start, _dur in s[1]:
        if name == "Qualifying":
            return datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
    return None


def official(D, rnd):
    """The result the game scores against: top five of the race classification and P1 of qualifying
    (before grid penalties). None until the race has a classification."""
    S = (D.get("SEASON") or {}).get(str(rnd)) or {}
    race = S.get("race") or []
    top = {}
    for row in race:
        if str(row[0]).isdigit() and 1 <= int(row[0]) <= 5:
            top[int(row[0])] = int(row[1])
    if len(top) < 5: return None
    pole = next((int(r[1]) for r in (S.get("quali") or []) if str(r[0]) == "1"), None)
    return {"top5": [top[i] for i in range(1, 6)], "pole": pole}


def cars(D, rnd=None):
    """Car numbers a player may pick, with full names: the 22 regular drivers (BIO) first, by number,
    then anyone who has stood in this season (from the classifications), by number."""
    key = lambda n: "".join(c for c in unicodedata.normalize("NFD", str(n)) if not unicodedata.combining(c)).lower()
    full = {key(d[0].split()[-1]): d[0] for d in (D.get("DRIVERS") or [])}
    reg, extra = {}, {}
    for b in (D.get("BIO") or {}).values():
        if b.get("num") is not None: reg[int(b["num"])] = full.get(key(b.get("last", ""))) or b.get("name") or b.get("last")
    for r, S in sorted((D.get("SEASON") or {}).items(), key=lambda kv: int(kv[0])):
        for row in (S.get("race") or []) + (S.get("quali") or []):
            try: n = int(row[1])
            except (TypeError, ValueError): continue
            if n not in reg: extra.setdefault(n, full.get(key(str(row[2]).split()[-1])) or row[2])
    return dict(sorted(reg.items()) + sorted(extra.items()))


def standins(D):
    """Car numbers in cars() that are not regular drivers."""
    reg = {int(b["num"]) for b in (D.get("BIO") or {}).values() if b.get("num") is not None}
    return [n for n in cars(D) if n not in reg]


def valid_pick(pick, allowed):
    t = pick.get("top5")
    return (isinstance(t, list) and len(t) == 5 and len(set(t)) == 5 and all(isinstance(x, int) and x in allowed for x in t)
            and isinstance(pick.get("pole"), int) and pick["pole"] in allowed)


def score(pick, off):
    """Points for one pick against the official result."""
    slots = [bool(pick["top5"][i] == off["top5"][i]) for i in range(5)]
    pole = off["pole"] is not None and pick["pole"] == off["pole"]
    pts = sum(p for p, ok in zip(SLOT_POINTS, slots) if ok) + (POLE_POINTS if pole else 0)
    return {"points": pts, "slots": slots, "pole": pole, "winner": slots[0], "exact": sum(slots)}


def result_hash(off, pick):
    return hashlib.sha1(json.dumps([off, pick["top5"], pick["pole"]], sort_keys=True).encode()).hexdigest()[:16]


def rank(rows, key_time="lead"):
    """Sort a table and give positions. rows: dicts with points, winners, exact and `lead`
    (seconds the final pick was submitted before the lock; more = earlier). Ties on every
    criterion share a position."""
    def k(r): return (-r["points"], -r["winners"], -r["exact"], -(r.get(key_time) or 0))
    rows = sorted(rows, key=lambda r: (k(r), r.get("name") or ""))
    pos, prev = 0, None
    for i, r in enumerate(rows):
        if k(r) != prev: pos, prev = i + 1, k(r)
        r["pos"] = pos
    return rows


# ---------------------------------------------------------------- display names
BLOCK = ["fuck", "shit", "cunt", "bitch", "nigg", "fag", "rape", "nazi", "hitler", "whore", "slut", "porn", "dick", "pussy",
         "wank", "twat", "retard", "kys", "admin", "moderator", "official", "trackalmanac"]


def name_ok(name):
    """Same checks as the sign-up form: 3-20 letters, numbers, spaces, . _ -; no emails, links or blocked words."""
    import re
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9 _.\-]{3,20}", name): return False
    low = re.sub(r"[^a-z0-9]", "", name.lower())
    if re.search(r"(www|https?|\.com|\.net|\.org|\.io)", name.lower()): return False
    return not any(w in low for w in BLOCK)


def public_name(uid, name, banned):
    if uid in banned or not name_ok(name): return "Player " + uid[:4].upper()
    return name
