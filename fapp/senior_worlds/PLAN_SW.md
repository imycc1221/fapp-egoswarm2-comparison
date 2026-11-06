# PLAN SW: FAPP with its original settings in the senior's worlds (pre-registered 2026-11-06, before any run)

**What the user asked (2026-11-06):**
- The FAPP reproduction is done (`../RESULT_R2.md`).
- Now run FAPP **with its paper / original settings** in the senior's static and dynamic worlds.
- Give the numbers of his table: CR, SR, Hits Static, Hits Dynamic, Avg. Velocity, Obstacle prediction, Sensor,
  Optimizer.
- ROS 1 is fine. The user's Mac first; the senior reruns on his desktop.

## How (as SANDO ran FAPP: FAPP's own simulator, the world replaced)
- **FAPP:** the build that reproduced SANDO's Table VI, `fapp:sando` (kotakondo/FAPP `d5e02a1`: the original plus the
  tracker fix, which the senior accepts), ROS Noetic in Docker on the Mac.
- **FAPP's original settings, unchanged:**
  - `run_in_test.xml` / `adv_test.xml` defaults: v / a / j = 3.5 / 10 / 20, L2 limits, `weight_time` 10;
  - its simulator `simulator.xml`: `poscmd_2_odom` (ideal tracking) and `pcl_render_node` (8 m point-cloud sensor);
  - its perception `mot_mapping` with `sim_mapping.launch` parameters;
  - its own constant-velocity obstacle prediction;
  - yaw as FAPP's `traj_server` (0);
  - goal height as FAPP forces (z 1.5);
  - start (0, 0, 1.5) as in `sim_test.launch`.
- **Changed, because of the world:**
  - FAPP's random map generator is replaced by `scenario_world.py`. It publishes the same topics with the senior's
    world:
    - `/map_generator/static_obs_cloud` and `/map_generator/global_cloud`: the scenario's boxes and cylinders as
      surface points at 0.2 m, the generator's resolution;
    - `/map_generator/obj_cloud` at 50 Hz: every sphere's surface points at its scenario position `pos(t)`;
      hidden spheres are parked underground by the scenario itself.
    - The world time is `t = ROS time − node start`.
  - `map_size_x` / `map_size_y` are set so that the world fits: 230 × 50 m for the 105 m courses, 320 × 50 m for the
    150 m ones. `sim_test.launch` has 200 × 200 m, which does not contain pad B at x = 105, and 200 m in y does not fit
    in 8 GB. `map_size_z` stays 3 m.
- **Mission (the senior's protocol):**
  - pads A (0, 0) and B (105 or 150, 0); the first goal is B, then alternating;
  - a goal is sent as `GoalSet` on `/goal_with_id` (what FAPP's RViz tool sends);
  - reached when within 0.6 m of (pad, z 1.5);
  - time limit per pass 4 × distance / 1.5 + 10 s (290 / 410 s). After a timeout the same goal is kept with a new
    limit;
  - 24 passes per world.
- **Recording:** the drone pose `/drone_0_visual_slam/odom` in the senior's `record.py` format (`gt`: t, t, wall, x,
  y, z, yaw; t = world time), and the passes in `episodes.json`.

## Worlds (the senior's repo `comparision_kairos` `0b84ad1`, `sando_worlds/worlds/scenarios`), in this order
1. `dyn_sando_forest_easy`, `dyn_sando_forest_medium`, `dyn_sando_forest_hard` (static only);
2. `dyn_sando_easy`, `dyn_sando_medium`, `dyn_sando_hard`, `dyn_sando_hard_dense` (static + dynamic).

## Smoke run first (not a result)
`dyn_sando_forest_easy` and `dyn_sando_easy`, 2 passes each, to check that FAPP flies, perceives and is recorded.
Fixes to our harness are allowed after it; FAPP's settings are not changed.

## The table's numbers (the senior's definitions, `../../../ego_compare/SETTINGS_FROM_SENIOR.md` C2–C4)
- **Hits Static / Dynamic:** the senior's `hits.py`, unchanged (via `score_hits.sh`, his `dyn_expert` and these
  scenario files), on the recorded `gt`. A contact is centre to surface < 0.35 m; contacts < 0.5 s apart are one;
  all statics form one group, each sphere its own.
- **CR / SR per pass:**
  - CR = % of passes with ≥ 1 contact; SR = % of passes reached with 0 contacts;
  - the same contact rule, counted inside each pass's time window;
  - a timeout and its follow-on to the same pad form one failed pass.
- **Avg. Velocity:** total distance / total time, from the `hits.py` line (as the NEO 0.67).
- **Obstacle prediction:** FAPP's own (adaptive Kalman filter, constant velocity).
- **Sensor:** FAPP's simulated point-cloud sensor (stands in for its Livox MID-360).
- **Optimizer:** MINCO + L-BFGS (FAPP, from GCOPTER).

## Caveats to report with the numbers
- FAPP's own simulator is not the senior's Gazebo + PX4:
  - its tracking is ideal;
  - its sensor sees the static map without occlusion within 8 m;
  - its perception gets the spheres' points directly, as in FAPP's own simulation.
- The senior's 0.35 m contact radius is his drone's. FAPP's own avoidance distance is 1.4 m to obstacle centres.
- One run per world on the Mac; the senior reruns on his desktop.

## Amendment 1 (2026-11-06, after the scored runs, before this rerun): map-400 rerun of `hard` and `hard_dense`
- **Why:** in both 150 m worlds FAPP stopped for good right after reaching pad B (x 150). Pad B is 10 m from the edge
  of FAPP's internal map (`map_size_x` 320, so x up to 160), and the drone ran to x 171. Whether our map-size choice
  caused this was not tested (`RESULT_SW.md`).
- **Rerun:** `dyn_sando_hard` and `dyn_sando_hard_dense` with `map_size_x` 400 (x up to 200), as `FAPP_MAP400_<world>`.
  - Everything else is unchanged: the world, `map_size_y` 50, `map_size_z` 3, the 24 episodes, the scoring.
  - `map_size_x` is FAPP's map-extent parameter; the senior's world is not changed.
- **Fixed now:** the map-400 runs become the table entries for these two worlds, whatever their outcome, because 400 m
  leaves the same kind of margin past pad B that the 105 m worlds have past their edge (no 10 m squeeze).
- **Reading the outcome:**
  - If FAPP again stops for good right after pad B, the failure is FAPP's own and does not depend on the map margin.
  - If it does not, the first runs were affected by our map size.
- **Kept:** the first runs stay in `runs/` and are reported next to the reruns.
