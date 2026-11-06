#!/bin/bash
# Inside ego_swarm_v2:r2: EGO-Swarm2's own simulator with the senior's world (PLAN_SW.md). Args: SCENARIO PASSES MAPX MAPY MAXSEC
set -u
W=$1; N=$2; MX=$3; MY=$4; MAXT=$5
EGO=/home/kota/ego_swarm_v2_ws/src/EGO-Planner-v2
source $EGO/swarm-playground/main_ws/devel/setup.bash
export PYTHONPATH=/dyn_expert:${PYTHONPATH:-}
mkdir -p /home/kota/data   # the planner writes its timing CSV there (ego_replan_fsm.cpp)
cd /out; echo "world $W passes $N map $MX x $MY started $(date -u +%FT%TZ)" > meta.txt
(cd $EGO && git log -1 --format='ego %H') >> meta.txt
roscore > roscore.log 2>&1 & sleep 3
stdbuf -oL roslaunch /sw/sw_ego.launch map_size_x:=$MX map_size_y:=$MY > launch.log 2>&1 &
sleep 4
python3 -u /sw/ego_world.py _scenario:=/scn/$W.yaml > world.log 2>&1 &
sleep 3
python3 -u /sw/mission.py _name:=$W _passes:=$N _scenario:=/scn/$W.yaml _goal_z:=2.0 > mission.log 2>&1 &
MP=$!
for i in $(seq 1 $MAXT); do sleep 1; kill -0 $MP 2>/dev/null || break; done
kill -0 $MP 2>/dev/null && { echo "MAX TIME reached" >> meta.txt; kill -INT $MP; sleep 3; }
rosparam get /drone_0_ego_planner_node > params_used.yaml 2>&1
pkill -INT -f roslaunch; sleep 4; pkill -INT -f ros; sleep 2
cp /home/kota/data/results_num_*.csv /out/ 2>/dev/null
grep -c "process has died" launch.log >> meta.txt
echo "end $(date -u +%FT%TZ)" >> meta.txt
