#!/usr/bin/env bash
# Builds HQ models on staging02's GPU (the box's user cannot write /home/christian, and gpu.sh
# stages at the same absolute path, so the work happens under /tmp/hqstage): copies art-src/hq and
# assets/hq there, runs build_hq.py on the card, and brings the models, maps and measure.json back.
#   art-src/hq/build.sh [build_hq args] [names...]
set -euo pipefail
R="$(cd "$(dirname "$0")/../.." && pwd)"
S=/tmp/hqstage
mkdir -p "$R/assets/hq" "$R/art-src/hq/out" "$S/art-src/hq" "$S/assets/hq"
rsync -a --delete --exclude out --exclude __pycache__ "$R/art-src/hq/" "$S/art-src/hq/"
mkdir -p "$S/art-src/hq/out"; cp -f "$R/art-src/hq/out/"*.json "$S/art-src/hq/out/" 2>/dev/null || true
rc=0
"$R/../gpu.sh" blender --stage "$S/art-src/hq" --pull "$S/assets/hq" --pull "$S/art-src/hq/out" \
    -- -b --python "$S/art-src/hq/build_hq.py" -- --out "$S/assets/hq" "$@" || rc=$?
rsync -a "$S/assets/hq/" "$R/assets/hq/" --exclude '*.import'
rsync -a "$S/art-src/hq/out/" "$R/art-src/hq/out/"
exit "$rc"
