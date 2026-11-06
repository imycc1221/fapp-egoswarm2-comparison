# PLAN SW: EGO-Swarm2 with its original settings in the senior's worlds (pre-registered 2026-11-06, before any run)

This is the same task as FAPP's (`../../fapp/senior_worlds/PLAN_SW.md`, `RESULT_SW.md`): run the method with its
original settings, in its own simulator, with the senior's world, and give the numbers of his table. The reproduction
step is done: SANDO Table VI was reproduced (`../RESULT_R2.md`).

## Build and settings
- **Build:** the one that reproduced Table VI, `ego_swarm_v2:r2` = kotakondo/EGO-Planner-v2 `dynus_benchmark`
  `6917c9f`. This is the original EGO-Planner-v2 (`9d85475` is its ancestor) plus SANDO's L∞ option, timing logs and
  grid-map changes. The senior allows these changes.
- **Settings: EGO-Planner-v2's original values**, from ZJU-FAST-Lab `9d85475` main_ws `run_in_sim.xml`,
  `advanced_param.xml` and `simulator.xml`. The fork had changed these, so they are set back in `sw_ego.launch`:

  | parameter | original value | the fork's value |
  |---|---|---|
  | `max_vel` | 1.5 m/s | 2.0 m/s |
  | `max_acc` | 6 m/s² | 5 m/s² |
  | `max_jer` | 20 m/s³ | 30 m/s³ |
  | constraint norm | L2 (`use_linf_feas` false) | L∞ |
  | `weight_time` | 10 | 1000 |
  | `obstacles_inflation` | 0.1 m | 0.199 m |
  | `local_update_range` | 5.5 × 5.5 × 2.0 m | 10 × 10 × 10 m |
  | `local_map_margin` | 10 | 100 |
  | `virtual_ceil` | 3.0 m | 5.0 m |
  | `virtual_ground` | −0.1 m | 1.0 m |
  | `ground_height` | −0.01 m | 1.0 m |
  | `max_ray_length` | 4.5 m | 10 m |

  Unchanged because the fork kept the original: `planning_horizon` 7.5, `fading_time` 1000, clearances
  (`obstacle_clearance` 0.1, soft 0.5, `swarm_clearance` 0.15) and `traj_server` `time_forward` 1.0.
- **The paper's settings:** the EGO-Swarm2 paper (Sci. Robot. 2022) is paywalled and has not been read yet. If it
  states other values, this is rerun with them as a separate, labelled run.
- **Simulator (the original one):**
  - `poscmd_2_odom`, ideal tracking;
  - the original simulated sensor `pcl_render_node` (CPU version: static points within 5 m, 30 Hz, vertical cut at
    30°). The fork had commented it out; its output is fed to the fork's grid-map input `/SQ01s/camera/cloud`.
- **Moving obstacles:** as EGO-Swarm2 receives them, ground-truth future trajectories broadcast as `MINCOTraj`. This is
  its swarm mechanism, used by its own moving-obstacle demo and by SANDO.
  - They are built exactly as SANDO's `dynamic_forest.py` builds them: 8 pieces over 7.5 s, exact position, velocity
    and acceleration at both ends, 50 Hz.
  - Only spheres within `planning_horizon × max_vel × 3` of the drone are sent.
  - `des_clearance` is the sphere's radius.
  - The source is the scenario's `pos(t)`, with velocity and acceleration by central differences of 1 ms.
- **Changed because of the world:**
  - `ego_world.py` replaces the random map generator and the moving obstacles. It publishes
    `/map_generator/global_cloud`: the boxes and cylinders as surface points at 0.1 m (the original generator's
    resolution), latched and republished at 1 Hz.
  - Map 230 × 50 × 3 m (320 × 50 × 3 m for the 150 m courses).
  - Start (0, 0, 2.0).

## Mission, recording and table numbers: identical to FAPP's PLAN_SW
- **Mission:**
  - pads A (0, 0) and B (105 or 150, 0); the first goal is B, then alternating;
  - a goal is a `GoalSet` on `/goal_with_id`;
  - reached when within 0.6 m of (pad, z 2.0): EGO-Swarm2 does not force a height, so the senior's route height is
    used;
  - time limit per pass 4 × distance / 1.5 + 10 s, the goal kept after a timeout;
  - 24 episodes per world.
- **Recording:** `/drone_0_visual_slam/odom` in the senior's `record.py` format.
- **Scoring:**
  - Hits from the senior's `hits.py`, unchanged;
  - SR / CR per pass with his rules (`../../fapp/senior_worlds/analyze_sw.py`);
  - Avg. Velocity = total distance / total time; the speed over reached passes only is also given.
- **Table columns:**
  - Obstacle prediction: none of its own; it receives ground-truth future trajectories (as in SANDO);
  - Sensor: EGO-Swarm2's simulated point-cloud sensor, 5 m (its paper uses a depth camera);
  - Optimizer: MINCO with L-BFGS, soft constraints.

## Worlds, in this order
`dyn_sando_forest_easy`, `forest_medium`, `forest_hard`, `easy`, `medium`, `hard`, `hard_dense`, from the senior's
`comparision_kairos` `0b84ad1`.

## Smoke run first (not a result)
`dyn_sando_forest_easy` and `dyn_sando_easy`, 2 episodes each, to check that EGO-Swarm2 flies, senses, receives the
sphere trajectories and is recorded, and that the parameters in force are the original ones (`params_used.yaml`).
After it, only harness fixes are allowed, never EGO-Swarm2's settings.

## Caveats to report
- **Advantages over the senior's system:**
  - ideal tracking;
  - the sensor sees through obstacles within 5 m;
  - ground-truth sphere futures (EGO-Swarm2 has no predictor of its own).
- **Clearance:** the senior's 0.35 m contact radius against EGO-Swarm2's own 0.1 m inflation and clearance.
- **Sample:** one run per world.

## Amendment 1 (after smoke 1, before any scored run): harness fix
- **What smoke 1 showed** (`runs/SMOKE_forest_easy`, 2/2 reached, 1.42 m/s):
  - `launch.log` repeats `TF Error: "world" passed to lookupTransform ... does not exist`, plus 51
    `Lost heartbeat`.
  - The original sensor stamps its cloud with frame `map`. The fork's grid map transforms every cloud to `world` and
    drops it if that fails, after waiting 0.1 s. So the planner never saw a static obstacle, and the waits stalled
    it.
  - Smoke 1 is invalid for that reason; it is kept.
- **Fix:** an identity static transform `world` → `map` in `sw_ego.launch`. In EGO-Planner-v2's own simulator `map`
  is the world frame. EGO-Swarm2's settings are not changed.
- The world and mission nodes now run with `python3 -u`, so their logs are written.
