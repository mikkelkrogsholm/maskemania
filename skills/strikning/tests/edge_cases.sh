#!/bin/bash
# Edge-case smoke test
set -e
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
GEN="python3 $SKILL/scripts/generate.py --format json"

check() {
  local label="$1"; shift
  echo "=== $label ==="
  $GEN "$@" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for s in d['sections']:
    print(f'  {s[\"title\"][:32]:<34} {s[\"sts_before\"]:>4} -> {s[\"sts_after\"]:>4}')
if d['warnings']:
    print('  warnings:', d['warnings'])
"
  echo
}

check "Hue baby (head=38cm, gauge 22/30)"   hue --head 38 --sts 22 --rows 30
check "Hue child (head=50cm, fingering)"     hue --head 50 --sts 28 --rows 36
check "Hue chunky adult (head=60, gauge 14/18)" hue --head 60 --sts 14 --rows 18
check "Raglan XS (bust=78cm)"                raglan --bust 78 --sts 22 --rows 30
check "Raglan 2XL (bust=124cm)"              raglan --bust 124 --sts 22 --rows 30
check "Raglan chunky (bust=94, gauge 16/22)" raglan --bust 94 --sts 16 --rows 22
check "Tørklæde 8st repeat"                  tørklæde --width 25 --length 200 --sts 22 --rows 30 --repeat-sts 8
check "Tørklæde tæppe (100 cm bredde)"       tørklæde --width 100 --length 200 --sts 14 --rows 18
