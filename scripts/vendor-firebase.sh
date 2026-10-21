#!/bin/sh
# Rebuilds src/vendor/firebase-game.js, the small Firebase bundle used only by the /game/ pages.
# Needs Node. Run from the repository root: sh scripts/vendor-firebase.sh
set -e
V=13.0.0
T=$(mktemp -d)
cp src/vendor/firebase-game.entry.js "$T/entry.js"
cd "$T" && npm init -y >/dev/null && npm i -q firebase@$V esbuild@0.24.0 >/dev/null
npx esbuild entry.js --bundle --format=esm --minify --target=es2020 --legal-comments=none --outfile=out.js
cd - >/dev/null
{ printf '/*! Firebase JS SDK %s (app, auth, firestore/lite), Apache License 2.0, https://github.com/firebase/firebase-js-sdk. Built with scripts/vendor-firebase.sh */\n' "$V"; cat "$T/out.js"; } > src/vendor/firebase-game.js
rm -rf "$T"
echo "src/vendor/firebase-game.js rebuilt with firebase@$V"
