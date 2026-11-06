# PLAN R2: reproduce SANDO's Table VI EGO-Swarm2 rows with SANDO's published pipeline (pre-registered 2026-11-06, before any R2 run)

Same approach as the FAPP reproduction (`../fapp/PLAN_R2.md`, `../fapp/RESULT_R2.md`: reproduced).

**Senior's rule:** hyperparameters and fixes outside the main algorithm are acceptable.

## Target: SANDO (Kondo et al., arXiv 2604.07599), Table VI, EGO-Swarm2 rows, 10 trials per case
| case | success | T_opt per replan | T_trav | L_path |
|---|---|---|---|---|
| easy | 100 % | 5.7 ms | 25.4 s | 107.5 m |
| medium | 100 % | 8.5 ms | 26.2 s | 108.3 m |
| hard | 80 % | 18.7 ms | 29.6 s | 114.2 m |

The SANDO paper says EGO-Swarm2 was fed the ground-truth positions and future predictions of the dynamic obstacles.
Its pipeline broadcasts each obstacle's future trajectory as a `MINCOTraj`, EGO-Swarm2's own swarm mechanism.

## Code
- github.com/kotakondo/EGO-Planner-v2, branch `dynus_benchmark`, `6917c9f`, as published. It changes EGO-Planner-v2:
  - the L∞ feasibility option;
  - timing logs;
  - point-cloud self-filtering.
- Its scripts are used unchanged: `docker/run_ego_benchmark.py`, `docker/dynamic_forest.py`,
  `docker/single_drone_waypoints_dynamic.launch` and the analysis `docker/analyze_ego_benchmark.py`.

## How (as their `docker/Makefile` `run-dynamic-benchmark` target, defaults)
- **Build:** their `docker/Dockerfile` (FROM `ros:noetic`).
  - If the build runs out of the Docker VM's memory, the only change allowed is fewer parallel jobs (as for FAPP).
- **Cases:** easy / medium / hard = 50 / 100 / 200 obstacles, dynamic ratio 0.65.
  - `--num-trials 10 --seed-start 0 --timeout 100`;
  - `--weight-time 10 --max-vel 5.0 --planning-horizon 7.5`;
  - L∞ on (`USE_LINF_FEAS` 1, the Makefile default).
- **Not as theirs:**
  - no `--gpus` / X11 (the Mac has no NVIDIA GPU; EGO's CUDA rendering is off in the code), headless, arm64;
  - started with `docker run` directly, with the same command inside the container;
  - their host paths (`/home/kkondo/...`, the LaTeX table) are not mounted, because they are not needed to run.
- **Metrics:** their own:
  - success = goal reached (0.5 m, speed < 0.1 m/s) without a collision;
  - a collision = the drone (a point) inside an obstacle's box;
  - T_trav and L_path averaged over the successful trials.
- **"Reproduced" (fixed now), per case:**
  1. the paper's success rate is inside the Wilson 95 % interval of our 10 trials;
  2. T_trav and L_path are within ±15 % of the paper's.

  T_opt is reported only, because the machine differs.

## When
After the FAPP senior-world batch has finished, so that the two do not share the CPU.

## Amendment 1 (2026-11-06, after reading their Dockerfile; before any R2 build or run)
- **Their Dockerfile clones the fork's DEFAULT branch.** It runs `git clone https://github.com/kotakondo/EGO-Planner-v2.git`,
  which is `main`, last commit `58bc7bf` (2026-01-09, "change start_tol to 0.05"), and compiles that planner.
- **Their Makefile mounts the rest from the branch it is run from (`dynus_benchmark`, `6917c9f`):**
  - the benchmark scripts (`docker/` → `.../EGO-Planner-v2/docker`);
  - the launch includes (`swarm-playground/main_ws/src/planner/plan_manage/launch/include`).
- **So the paper's pipeline is:** the `main` planner + the `dynus_benchmark` scripts and launch parameters. The two
  branches differ in `poly_traj_optimizer` (the L∞ code) and in `run_in_sim.xml`.
- **This is reproduced as is:**
  - the image is built from `dynus_benchmark`'s `docker/Dockerfile`;
  - the `main` commit inside the image is recorded and must be `58bc7bf`;
  - the two directories are mounted as the Makefile does.
- The image also builds Livox-SDK2, `acl-gazebo` (`ego_swarm_noetic`), `snapstack_msgs`, `livox_ros_driver2` and the
  Mid360 plugin. They are all public; checked 2026-11-06.

## Amendment 2 (2026-11-06, before any R2 build or run): build the planner from `dynus_benchmark` `6917c9f`
- **Why:**
  - SANDO Section IX-B (Table VI) says: "All methods use L∞ dynamic constraints set to v_max = 5.0 m/s,
    a_max = 20.0 m/s², and j_max = 100.0 m/s³".
  - The L∞ option (`optimization/use_linf_feas`, `poly_traj_optimizer.cpp`) exists only on `dynus_benchmark`. `main`
    (`58bc7bf`, what the Dockerfile clones) has no L∞ code (`git grep linf origin/main` is empty). The mounted
    launch file would set `use_linf_feas`, but a `main` build would ignore it and run L2.
  - So the paper's Table VI EGO-Swarm2 rows must come from a `dynus_benchmark` build (the author's image was built
    from his own checkout).
- **Change:**
  - In a copy of their Dockerfile, the clone line becomes
    `git clone -b dynus_benchmark ... && git checkout 6917c9f`.
  - `catkin_make` / `make` use `-j3`, as for FAPP, because unbounded `-j` ran out of the 8 GB Docker VM; this does
    not change the binaries.
  - Nothing else changes. Amendment 1's `main` remark is superseded.
- **Run (as `make run-dynamic-benchmark`):**
  - for easy / medium / hard with `NUM_OBSTACLES` 50 / 100 / 200:
    `--num-trials 10 --timeout 100 --dynamic-ratio 0.65 --seed-start 0 --weight-time 10 --max-vel 5.0
    --planning-horizon 7.5 --case-name <case>`, no `--rviz`;
  - the `docker/` and `launch/include` directories of `6917c9f` mounted as their Makefile does.
- **Analysis:** their `analyze_ego_benchmark.py --data-dir <dir>`, with the LaTeX-table writing pointed at a scratch
  path.
- **If the arm64 build fails** in a package the dynamic benchmark does not use (Livox / Mid360 / Gazebo plugins), it
  may be dropped. That will be reported, and no planner source is touched.

## Amendment 3 (2026-11-06 04:55, after the image build, before any run)
- In the built image, `import pandas` fails: their Dockerfile's `pip install pandas` gave pandas 2.0.3, which needs
  numpy >= 1.20.3, but the image has the system numpy 1.17.4.
- Only their analysis script needs pandas. The planner, the obstacle node and the benchmark runner do not.
- So in the analysis container only, `pip3 install pandas==1.1.5` is run first (checked: it imports with numpy
  1.17.4). This takes the place of their Makefile's `pip install -q pandas`. Nothing in the flight runs changes.
- Image check: commit `6917c9f`; `use_linf_feas` is in `poly_traj_optimizer.cpp`; `ego_planner_node` and
  `traj_server` are built.
