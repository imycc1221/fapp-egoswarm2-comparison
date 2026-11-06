#!/bin/bash
# Inside fapp:sando: FAPP's own simulator with the senior's world (PLAN_SW.md). Args: SCENARIO_NAME PASSES MAPX MAPY MAXSEC
set -u
W=$1; N=$2; MX=$3; MY=$4; MAXT=$5
source /opt/ros/noetic/setup.bash; source /root/fapp_ws/devel/setup.bash
export PYTHONPATH=/dyn_expert:${PYTHONPATH:-}
cd /out; echo "world $W passes $N map $MX x $MY started $(date -u +%FT%TZ)" > meta.txt
cat /root/fapp_ws/src/FAPP/.git/HEAD 2>/dev/null >> meta.txt; (cd /root/fapp_ws/src/FAPP && git log -1 --format='fapp %H' 2>/dev/null) >> meta.txt
roscore > roscore.log 2>&1 & sleep 3
python3 /sw/scenario_world.py _scenario:=/scn/$W.yaml > world.log 2>&1 &
sleep 2
stdbuf -oL roslaunch /sw/sw_planner.launch map_size_x:=$MX map_size_y:=$MY > launch.log 2>&1 &
sleep 2
stdbuf -oL roslaunch mot_mapping sim_mapping.launch > mapping.log 2>&1 &
sleep 3
python3 /sw/mission.py _name:=$W _passes:=$N _scenario:=/scn/$W.yaml > mission.log 2>&1 &
MP=$!
for i in $(seq 1 $MAXT); do sleep 1; kill -0 $MP 2>/dev/null || break; done
kill -0 $MP 2>/dev/null && { echo "MAX TIME reached" >> meta.txt; kill -INT $MP; sleep 3; }
pkill -INT -f roslaunch; sleep 4; pkill -INT -f ros; sleep 2
grep -c "process has died" launch.log mapping.log >> meta.txt
echo "end $(date -u +%FT%TZ)" >> meta.txt
