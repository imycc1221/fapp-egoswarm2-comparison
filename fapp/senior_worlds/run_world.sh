#!/bin/bash
# Host: one world in a fresh fapp:sando container. Usage: run_world.sh WORLD PASSES [RUN_NAME]; writes runs/RUN_NAME/.
set -eu
H=$(cd "$(dirname "$0")" && pwd); W=$1; N=$2; R=${3:-$W}
SCN=${SCN_DIR:?set SCN_DIR to .../sando_worlds/worlds/scenarios}
DX=${DYN_EXPERT:?set DYN_EXPERT to .../dyn_obstacle_nav/dyn_expert}
O=$H/runs/$R; [ -e "$O" ] && { echo "ABORT: $O exists"; exit 1; }; mkdir -p "$O"
case $W in *hard*) MX=320.0;; *) MX=230.0;; esac; MY=50.0
MX=${MX_OVERRIDE:-$MX}   # amendment 1 (map-400 rerun of the 150 m worlds)
MAXT=$(python3 -c "print(int($N*420+120))")
docker run --rm -v "$O":/out -v "$H":/sw:ro -v "$SCN":/scn:ro -v "$DX":/dyn_expert:ro \
  fapp:sando bash /sw/run_in_container.sh "$W" "$N" "$MX" "$MY" "$MAXT"
