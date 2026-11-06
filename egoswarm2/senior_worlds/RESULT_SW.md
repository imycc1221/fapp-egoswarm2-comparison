# RESULT SW: EGO-Swarm2 with its original settings in the senior's 7 worlds (2026-11-06)

**Plan:** [PLAN_SW.md](PLAN_SW.md), pre-registered in commit `adec498`. Amendment 1 is the harness fix found in smoke
1, made before any scored run. One run per world on the user's Mac (Docker, ROS Noetic, arm64).
- **Build:** `ego_swarm_v2:r2` (`6917c9f`), the build that reproduced SANDO Table VI (`../RESULT_R2.md`).
- **Settings:** the configuration parameters of upstream EGO-Planner-v2 (`9d85475`) restored on SANDO's fork
  `6917c9f`. These are v 1.5 m/s, a 6 m/s², j 20 m/s³, L2, inflation 0.1 m, local map 5.5 × 5.5 × 2 m, planning
  horizon 7.5.
  - The planner parameters are checked in each run's `params_used.yaml`.
  - The sensor and `traj_server` parameters are as written in `sw_ego.launch` and the fork's `run_in_sim.xml`.
  - Restoring the parameters does not restore the original implementation: the fork's code changes stay, notably its
    grid-map changes.
  - No other numeric parameter of the upstream launch files differs.
- **Sensor:** the original simulated sensor, static points within 5 m.
- **Spheres:** given as ground-truth future trajectories, the way SANDO fed EGO-Swarm2.

## The senior's table, EGO-Swarm2 row(s)

| world | passes | reached | SR | CR | Hits Static | Hits Dynamic | Avg. Velocity |
|---|---|---|---|---|---|---|---|
| dyn_sando_forest_easy | 24 | 24 | 25.0 % | 75.0 % | 21 | 0 | 1.43 m/s |
| dyn_sando_forest_medium | 24 | 24 | 8.3 % | 91.7 % | 34 | 0 | 1.43 m/s |
| dyn_sando_forest_hard | 24 | 24 | 0.0 % | 100.0 % | 73 | 0 | 1.43 m/s |
| dyn_sando_easy | 24 | 24 | 8.3 % | 91.7 % | 32 | 0 | 1.43 m/s |
| dyn_sando_medium | 24 | 24 | 0.0 % | 100.0 % | 51 | 0 | 1.43 m/s |
| dyn_sando_hard | 24 | 24 | 0.0 % | 100.0 % | 78 | 0 | 1.43 m/s |
| dyn_sando_hard_dense | 24 | 24 | 0.0 % | 100.0 % | 71 | 0 | 1.43 m/s |
| static worlds pooled (forest_*) | 72 | 72 | 11.1 % | 88.9 % | 128 | 0 | |
| dynamic worlds pooled | 96 | 96 | 2.1 % | 97.9 % | 232 | 0 | |

The other columns:
- **Obstacle prediction:** none of its own. EGO-Swarm2 receives each sphere's ground-truth future trajectory (7.5 s,
  as a MINCO polynomial through its swarm channel), as in SANDO's benchmark.
- **Sensor:** EGO-Swarm2's own simulated point-cloud sensor (static obstacles within 5 m, no occlusion). Its paper
  uses a depth camera.
- **Optimizer:** MINCO trajectories with L-BFGS, soft constraints.

## How the numbers were computed (identical to FAPP's, `../../fapp/senior_worlds/RESULT_SW.md`)
- **Hits Static / Dynamic:** the senior's `hits.py`, unchanged (`hits.txt` in each run).
- **SR / CR:** per pass, with his contact rule: centre to surface < 0.35 m, contacts within 0.5 s merged
  (`analyze_sw.py`).
- **Cross-check:** our per-pass contact totals equal `hits.py`'s whole-run totals in every world (`summary_sw.json`).
- **Avg. Velocity:** total distance / total time. No pass timed out, so it is almost the same as the speed over
  reached passes only: 1.43 against 1.43–1.44 m/s (`summary_sw.md`).
- **Mission failures:** none.
  - Every episode reached its pad, so passes = episodes = 24, with no timeouts.
  - No `TF Error`, `Lost heartbeat`, dropped trajectory or dead process in any `launch.log`.
  - In `easy`, the safety check triggered `EMERGENCY_STOP` twice (`launch.log` lines 3528 and 3651), and each time
    the planner went straight back to `GEN_NEW_TRAJ`.
  - As with FAPP, each `launch.log` ends with a `boost::lock_error` line at shutdown.
  - The contacts counted above are not failures in this sense.

## Extra context (not the senior's metric)

| world | min surface distance, static | min surface distance, spheres | spheres that came within 1 m |
|---|---|---|---|
| forest_easy | 0.15 m | | |
| forest_medium | 0.19 m | | |
| forest_hard | 0.16 m | | |
| easy | 0.16 m | 0.41 m | 9 / 10 |
| medium | 0.12 m | 0.39 m | 22 / 24 |
| hard | 0.11 m | 0.40 m | 31 / 39 |
| hard_dense | 0.15 m | 0.39 m | 49 / 60 |

- **Static obstacles:** the pose was never inside one.
- **Why CR is high (likely main reason):** EGO-Swarm2's own clearance is 0.1 m (`obstacles_inflation`,
  `obstacle_clearance`), below the senior's 0.35 m contact radius.
- **Spheres:** most came within 1 m but none closer than 0.39 m, so Hits Dynamic is 0. That the ground-truth input
  caused the zero was not tested: there is no run without it.
- **Height:** EGO-Swarm2 sometimes left the 3 m virtual ceiling (z up to 3.5 m), because its constraints are soft.

## Caveats to send with the numbers
- **Not a like-for-like comparison with FAPP on dynamic obstacles.**
  - EGO-Swarm2 is given every sphere within 33.75 m together with its true future over the next 7.5 s, refreshed at
    50 Hz. This is a MINCO fit through samples of the true motion, so it bypasses perception and prediction.
  - FAPP had to detect and predict the spheres itself.
  - EGO-Swarm2's Hits Dynamic = 0 should be read with that advantage in mind.
- **Simulator.** Like FAPP's, its simulator is not the senior's Gazebo + PX4: ideal tracking, and a sensor without
  occlusion within 5 m.
- **Speed.** EGO-Swarm2's original v_max is 1.5 m/s, close to the senior's 1.5 m/s nominal. FAPP's is 3.5 m/s.
- **Settings source.** The settings are the code's defaults. The EGO-Swarm2 paper (Sci. Robot. 2022) has not been read;
  if it gives other values, a separate run is needed.
- **Sample.** One run per world.

## Files
- **Each run:** `runs/EGO_dyn_sando_<world>/` holds:
  - `odom_*.npz` (the senior's `record.py` format);
  - `episodes_*.json`, `table_numbers.json`, `hits.txt`;
  - `launch.log`, `mission.log`, `world.log`, `meta.txt`;
  - `params_used.yaml`;
  - `results_num_0.csv` (the planner's timing).
- **Summaries:** `runs/summary_sw.md` and `runs/summary_sw.json`.
- **Hashes:** the npz sha256 are in `runs/SHA256SUMS_odom.txt`.
- **Smoke runs:** `runs/SMOKE_forest_easy` (invalid, see amendment 1), `runs/SMOKE2_forest_easy`, `runs/SMOKE_easy`.
- **Versions:**
  - EGO `6917c9f`;
  - the senior's worlds: `comparision_kairos` `0b84ad1`;
  - `dyn_expert` from `senior_code/Dynamic_obstacle_20261103`.
- **Rerun:** `bash run_all.sh`.
