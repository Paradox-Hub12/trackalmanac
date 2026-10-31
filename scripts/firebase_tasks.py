#!/usr/bin/env python3
"""Firebase jobs for the Predictor, run by .github/workflows/firebase.yml with the service account
in the FIREBASE_SERVICE_ACCOUNT secret (never stored in the repo).

  python3 scripts/firebase_tasks.py deploy-rules   publish firebase/firestore.rules to Cloud Firestore
  python3 scripts/firebase_tasks.py web-config     fill in src/game.json from the project's web app, if it is empty
                                                   (the web config is public; it is what the browser uses)
  python3 scripts/firebase_tasks.py auth-helper    copy Firebase's sign-in helper pages to /__/auth/ on this site
                                                   (needs no secret)

Why auth-helper: Google sign-in normally finishes on <project>.firebaseapp.com, and browsers that block
third-party storage (Safari, Firefox, Brave, Chrome with third-party cookies off, in-app browsers) leave the
pop-up hanging. Serving the helper pages from trackalmanac.com itself and setting authDomain to
trackalmanac.com keeps sign-in on one site. Firebase's guide: "Self-host the helper code"
(https://firebase.google.com/docs/auth/web/redirect-best-practices). GitHub Pages can't serve a file without
an extension as a web page, so handler, iframe and links are saved as .html: /__/auth/handler is served from
handler.html. Re-run now and then (Run workflow) so the copies stay in step with Firebase.
"""
import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/firebase"]


def session():
    import google.auth.transport.requests
    from google.oauth2 import service_account
    info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return google.auth.transport.requests.AuthorizedSession(creds), info["project_id"]


def deploy_rules():
    s, pid = session()
    src = open(os.path.join(ROOT, "firebase", "firestore.rules"), encoding="utf-8").read()
    base = "https://firebaserules.googleapis.com/v1/projects/%s" % pid
    r = s.post(base + "/rulesets", json={"source": {"files": [{"name": "firestore.rules", "content": src}]}})
    if r.status_code != 200:
        sys.exit("::error::Firestore rules were not accepted (%s): %s" % (r.status_code, r.text[:2000]))
    ruleset = r.json()["name"]
    rel = "projects/%s/releases/cloud.firestore" % pid
    r = s.patch("https://firebaserules.googleapis.com/v1/" + rel, json={"release": {"name": rel, "rulesetName": ruleset}})
    if r.status_code == 404:
        r = s.post(base + "/releases", json={"name": rel, "rulesetName": ruleset})
    if r.status_code != 200:
        sys.exit("::error::Could not publish the Firestore rules (%s): %s" % (r.status_code, r.text[:2000]))
    print("Firestore rules published: %s" % ruleset)


def web_config():
    """Never fails the run: if the service account may not read the web app, it says so and stops."""
    p = os.path.join(ROOT, "src", "game.json")
    cfg = json.load(open(p, encoding="utf-8"))
    if cfg["firebase"].get("apiKey"):
        print("src/game.json already has the web config."); return
    s, pid = session()
    r = s.get("https://firebase.googleapis.com/v1beta1/projects/%s/webApps" % pid)
    apps = r.json().get("apps", []) if r.status_code == 200 else []
    if not apps:
        print("::warning::Couldn't read the web app config with the service account (%s). Paste the firebaseConfig into src/game.json instead." % r.status_code)
        return
    r = s.get("https://firebase.googleapis.com/v1beta1/%s/config" % apps[0]["name"])
    if r.status_code != 200:
        print("::warning::Couldn't read the web app config (%s). Paste the firebaseConfig into src/game.json instead." % r.status_code)
        return
    c = r.json()
    cfg["firebase"] = {k: c.get(k, "") for k in ("apiKey", "authDomain", "projectId", "storageBucket", "messagingSenderId", "appId")}   # no measurementId: Firebase Analytics stays off
    open(p, "w", encoding="utf-8").write(json.dumps(cfg, indent=1) + "\n")
    print("src/game.json filled in from web app %s" % apps[0].get("displayName", apps[0]["name"]))


HELPER = {"handler": "handler.html", "handler.js": "handler.js", "experiments.js": "experiments.js",
          "iframe": "iframe.html", "iframe.js": "iframe.js", "links": "links.html", "links.js": "links.js"}


def auth_helper():
    pid = json.load(open(os.path.join(ROOT, "src", "game.json"), encoding="utf-8"))["firebase"]["projectId"]
    base = "https://%s.firebaseapp.com" % pid
    get = lambda path: urllib.request.urlopen(urllib.request.Request(base + path, headers={"User-Agent": "trackalmanac-build"}), timeout=30).read()
    files = {"__/auth/" + out: get("/__/auth/" + src) for src, out in HELPER.items()}
    files["__/firebase/init.json"] = get("/__/firebase/init.json")
    json.loads(files["__/firebase/init.json"])                     # must be valid JSON
    for k in ("handler", "iframe"):
        if b"<html" not in files["__/auth/%s.html" % k].lower(): sys.exit("::error::%s from Firebase is not a web page" % k)
    for rel, data in files.items():
        p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    print("Sign-in helper pages saved: " + ", ".join(sorted(files)))


if __name__ == "__main__":
    {"deploy-rules": deploy_rules, "web-config": web_config, "auth-helper": auth_helper}[sys.argv[1]]()
