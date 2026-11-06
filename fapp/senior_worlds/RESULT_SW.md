# RESULT SW: FAPP with its original settings in the senior's 7 worlds (2026-11-06)

Plan: [PLAN_SW.md](PLAN_SW.md), pre-registered in commit `afbec88` before any scored run. One run per world on the
user's Mac (Docker, ROS Noetic, arm64). The world, the mission and the scoring are the senior's; FAPP and its settings
are the original ones (`fapp:sando` = kotakondo/FAPP `d5e02a1`, the original code plus the tracker fix).

## The senior's table, FAPP row(s)

| world | passes | reached | SR | CR | Hits Static | Hits Dynamic | Avg. Velocity (total distance / total time, as his hits.py) | speed over reached passes only |
|---|---|---|---|---|---|---|---|---|
| dyn_sando_forest_easy | 24 | 24 | 33.3 % | 66.7 % | 20 | 0 | 3.26 m/s | 3.27 m/s |
| dyn_sando_forest_medium | 24 | 24 | 4.2 % | 95.8 % | 50 | 0 | 3.27 m/s | 3.29 m/s |
| dyn_sando_forest_hard | 23 | 22 | 0.0 % | 100.0 % | 162 | 0 | 2.54 m/s | 3.23 m/s |
| dyn_sando_easy | 21 | 20 | 0.0 % | 100.0 % | 63 | 6 | 2.13 m/s | 3.27 m/s |
| dyn_sando_medium | 24 | 24 | 0.0 % | 100.0 % | 71 | 9 | 3.23 m/s | 3.24 m/s |
| dyn_sando_hard (map-400 rerun, the table entry) | 8 | 7 | 0.0 % | 100.0 % | 25 | 3 | 0.23 m/s | 3.30 m/s |
| dyn_sando_hard_dense (map-400 rerun, the table entry) | 3 | 2 | 0.0 % | 66.7 % | 6 | 0 | 0.05 m/s | 3.30 m/s |
| static worlds pooled (forest_*) | 71 | 70 | 12.7 % | 87.3 % | 232 | 0 | | |
| dynamic worlds pooled (easy, medium, both reruns) | 56 | 53 | 0.0 % | 98.2 % | 165 | 18 | | |

**The first runs of the 150 m worlds** (internal map 320 m), kept and shown as amendment 1 of the plan fixed before
the rerun:

| world | passes | reached | SR | CR | Hits Static | Hits Dynamic | Avg. Velocity | speed over reached passes |
|---|---|---|---|---|---|---|---|---|
| dyn_sando_hard | 2 | 1 | 0.0 % | 50.0 % | 5 | 0 | 0.13 m/s | 3.26 m/s |
| dyn_sando_hard_dense | 8 | 7 | 0.0 % | 87.5 % | 20 | 16 | 0.25 m/s | 3.28 m/s |

**Map-400 rerun** (`runs/FAPP_MAP400_*`, plan amendment 1): only FAPP's internal map extent (`map_size_x`) was
raised from 320 to 400 m; the world and the scoring did not change.
- FAPP still stopped for good in both worlds.
  - In `hard` it happened in pass 8, right after reaching pad B; the drone ran to x 176.7, inside the larger map.
  - In `hard_dense` it happened in pass 3, right after reaching pad A (x 0, 200 m from the map edge); the drone ran
    to x −27 and ended below the ground at (0.4, −6.4, −1.3).
- So the failure is FAPP's own and does not come from the map margin.
- The larger map only changed when it happened. In both worlds and both runs, FAPP flies 3.3 m/s and fails within a
  few passes, so the pass counts stay small.

The other columns:
- **Obstacle prediction:** FAPP's own. An adaptive Kalman filter on clustered points, constant velocity, a short look-ahead
  (0.12 s), and a fixed avoidance distance of about 1.4 m.
- **Sensor:** FAPP's own simulated point-cloud sensor (`pcl_render_node`, 8 m range). It stands in for the Livox MID-360
  LiDAR of the paper. The moving spheres reach FAPP's perception (`mot_mapping`) as points, as in FAPP's own
  simulation.
- **Optimizer:** MINCO trajectories with L-BFGS (from GCOPTER), soft constraints.

## How the numbers were computed
- **Contacts:** a contact is drone centre to obstacle surface < 0.35 m; samples less than 0.5 s apart count as one.
- **Hits Static / Dynamic:** the senior's `hits.py` (`c3d925b45ee3`), unchanged, on the recorded poses (`hits.txt` in
  each run folder).
- **SR / CR:** per pass (`analyze_sw.py`, the same contact rule inside each pass).
- **Passes:** a timeout and the episodes that follow it to the same pad form one failed pass. That is why some worlds
  have fewer than 24 passes.
- **Avg. Velocity:** as the senior computes it (total distance / total recorded time), from the unrounded distance
  and time; `hits.txt` prints both rounded. It includes the time FAPP sat still after a failure, and in `easy` one
  140 m pose jump, so the last column gives the speed over reached passes only. Those passes can still contain
  contacts.
- **Episodes and passes:** each world ran 24 episodes. A pass is not an independent trial: in `hard`, 23 of the 24
  episodes are one failed pass. A low CR there (50 %) does not mean safer flight; it rests on 2 passes.
- **Pooled rows:** sum the passes of the worlds.
- **Cross-check:** our per-pass contact totals equal `hits.py`'s whole-run totals in every world (`own_*` vs `hits_*` in `summary_sw.json`).

## What happened in the failed passes
In each of the 4 worlds with a failure, FAPP's FSM entered `EMERGENCY_STOP` (`launch.log`) and never returned to
`EXEC_TRAJ` after that. It either stayed in `EMERGENCY_STOP` or switched between it and `GEN_NEW_TRAJ` without
executing a new trajectory. From then on the drone holds its pose and every later episode times out. These are
failures of FAPP in this integration. Their root cause was not located, and an influence of our harness is not
excluded: the map size (230 or 320 × 50 × 3 m), pad B 10 m from the map edge, and the new goal sent at once on
arrival.

| world | failing pass | what the pose shows |
|---|---|---|
| forest_hard | 23 | stuck inside a cylinder at (93.2, 0.9) |
| easy | 21 | one 10 ms step jumps the pose from (33.7, 0, 1.5) to (-107, -19, -6), then holds at (39.8, 0, 1.5) |
| hard (first run) | 2 | right after reaching B (150, 0) it climbs to z 17.9 and runs to x 171, outside the 320 m map (x up to 160) |
| hard_dense (first run) | 8 | right after reaching B it runs to x 171.5, then holds at (113, 9.2, -0.6) |
| hard (map-400) | 8 | right after reaching B it runs to x 176.7 (inside the map), then holds at (126.5, 0, 1.4) |
| hard_dense (map-400) | 3 | right after reaching A it runs to x −27, then holds at (0.4, −6.4, −1.3), below the ground |

In the 150 m worlds, every failure starts right after FAPP reached a pad and got the opposite goal while still
flying at about 3 m/s. The map-400 rerun shows the map margin is not the cause. Why this happens in the 150 m worlds
and rarely in the 105 m ones was not found. The 150 m worlds have more spheres (39 and 60), but this is not tested.

Note: a `boost::lock_error` line appears at the end of every world's `launch.log`, including the worlds without
failures. It comes from shutdown, not from a crash during the flight.

## Caveats to send with the numbers
- **FAPP's simulator is not the senior's Gazebo + PX4.** Tracking is ideal (the pose follows FAPP's command). The sensor
  sees the static map within 8 m. Perception gets the spheres' points directly.
- **The 0.35 m contact radius is the senior's drone size; FAPP's own settings keep much less clearance from static
  obstacles.** FAPP uses `obstacles_inflation` 0.1 m and `obstacle_clearance` 0.1 m (soft 0.5 m) in `adv_test.xml`.
  So many passes have a contact under his rule although the drone did not enter an obstacle. As extra context (not
  his metric), the share of pose samples inside a static obstacle for a point drone is:

  | world | share inside a static obstacle |
  |---|---|
  | forest_easy | 0.29 % |
  | forest_medium | 0.07 % |
  | forest_hard | 21.78 %, almost all of it the stuck period |
  | easy | 0.24 % |
  | medium, hard, hard_dense (first runs and map-400 reruns) | 0 % |
- **Goal height.** FAPP flies at z = 1.5 m, its forced goal height; the senior's route says z 2.0 ± 1.0.
- **Speed.** FAPP flies at its original v_max 3.5 m/s, about 3.3 m/s on average, much faster than the senior's 1.5 m/s
  nominal.
- **Sample size.** One run per world (two for the 150 m worlds). `hard` (8 passes) and `hard_dense` (3 passes) rest
  on very few passes. The senior's rerun on his desktop may differ.

## Files
- **Each run:** `runs/FAPP_dyn_sando_<world>/` holds:
  - `odom_*.npz` (the senior's `record.py` format, key `gt`);
  - `episodes_*.json`, `table_numbers.json` (per pass), `hits.txt`;
  - `mission.log`, `world.log`, `launch.log`, `meta.txt`.
- **Summaries:** `runs/summary_sw.md` and `runs/summary_sw.json` (`summarize_sw.py`).
- **Out of git (sha256 in `runs/SHA256SUMS_logs_out_of_git.txt`):** every `mapping.log`, and `hard_dense`'s
  `launch.log` (55 MB).
- **Hashes:** the npz sha256 are in `runs/SHA256SUMS_odom.txt`.
- **Versions:**
  - the senior's worlds: `comparision_kairos` `0b84ad1`;
  - `dyn_expert` from `senior_code/Dynamic_obstacle_20261103`;
  - FAPP `d5e02a1`.
- **Rerun:** `bash run_all.sh` (it uses `run_world.sh WORLD 24` for each world).
