#!/usr/bin/env bash
# Cycles frames of the shipped GLBs on staging02: art-src/hq/render.sh <out dir> <px> <samples> <setup>...
# (setups as in render_hq.py: "m4_carbine+red_dot+laser"). Stages assets/hq and art-src/hq under
# /tmp/hqstage (see build.sh) and copies the frames into <out dir>.
set -euo pipefail
R="$(cd "$(dirname "$0")/../.." && pwd)"
S=/tmp/hqstage
OUT="$1"; PX="$2"; SM="$3"; shift 3
mkdir -p "$S/art-src/hq/out" "$S/assets/hq" "$S/frames" "$OUT"
rsync -a --delete --exclude out --exclude __pycache__ "$R/art-src/hq/" "$S/art-src/hq/"
cp -f "$R/art-src/hq/out/"*.json "$S/art-src/hq/out/"
rsync -a --delete --include '*.glb' --exclude '*' "$R/assets/hq/" "$S/assets/hq/"
rm -f "$S/frames/"*.png
"$R/../gpu.sh" blender --stage "$S/art-src/hq" --stage "$S/assets/hq" --pull "$S/frames" \
    -- -b --python "$S/art-src/hq/render_hq.py" -- "$S/assets/hq" "$S/frames" "$PX" "$SM" "$@"
for f in "$S/frames/"*.png; do python3 -I -c "
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB'); im.save(sys.argv[2], quality=88)" "$f" "$OUT/$(basename "${f%.png}").jpg"; done
