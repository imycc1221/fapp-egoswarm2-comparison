#!/bin/bash
# Host: one world in a fresh ego_swarm_v2:r2 container. Usage: run_world.sh WORLD PASSES [RUN_NAME]; writes runs/RUN_NAME/.
set -eu
H=$(cd "$(dirname "$0")" && pwd); W=$1; N=$2; R=${3:-$W}
SCN=${SCN_DIR:?set SCN_DIR to .../sando_worlds/worlds/scenarios}
DX=${DYN_EXPERT:?set DYN_EXPERT to .../dyn_obstacle_nav/dyn_expert}
O=$H/runs/$R; [ -e "$O" ] && { echo "ABORT: $O exists"; exit 1; }; mkdir -p "$O"
case $W in *hard*) MX=320.0;; *) MX=230.0;; esac; MY=50.0
MAXT=$(python3 -c "print(int($N*450+120))")
docker run --rm ${LAUNCH_FILE:+-e LAUNCH_FILE=$LAUNCH_FILE} ${STOP_SPEED:+-e STOP_SPEED=$STOP_SPEED} -v "$O":/out -v "$H":/sw:ro -v "$SCN":/scn:ro -v "$DX":/dyn_expert:ro \
  ego_swarm_v2:r2 bash /sw/run_in_container.sh "$W" "$N" "$MX" "$MY" "$MAXT"
