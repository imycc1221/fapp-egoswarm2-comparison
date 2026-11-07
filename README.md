# FAPP and EGO-Swarm2 in the dyn_sando worlds

**What this is.** Two published planners, FAPP (Lu et al., T-RO 2024) and EGO-Swarm2 (Zhou et al., Sci. Robot.
2022), were run with their original code in the `dyn_sando` worlds of
[Michael-BJ/comparision_kairos](https://github.com/Michael-BJ/comparision_kairos). All scoring uses that project's `hits.py`
and its pass rules, so both planners can be placed in that project's comparison table.

**What each planner ran in.** Each planner runs in its own simulator: ROS Noetic, ideal tracking, and its own
simulated point-cloud sensor. They do not run in Gazebo + PX4. The `dyn_sando` world replaces their random map generator.

**How the code was checked first.** Before the dyn_sando worlds, each setup was checked against a published result: SANDO
(Kondo et al., arXiv 2604.07599), Table VI. Both reproduced it:
- FAPP: easy 80 % / 80 %, medium 90 % / 80 %, hard 60 % / 50 % (ours / paper).
- EGO-Swarm2: easy 100 % / 100 %, medium 100 % / 100 %, hard 70 % / 80 %.

Details are in `*/sando_reproduction/RESULT_R2.md`.

## Main results: inflation 0.35 m, the updated worlds (`d341041`)

**Setup.**
- Each method keeps its original settings, except obstacle inflation 0.35 m: the project's drone size (its contact radius), as used for its NEO baseline.
- Scored with the project's new `hits.py`, which includes the out-of-bounds line.
- The drone stops at each pad (< 0.1 m/s) before it gets the next goal. Without this, both planners overshot the pad
  by 12–20 m and went out of bounds.
- 24 episodes per world.

Details are in `v4/RESULT_V4.md`; the runs are named `V4S035_*` and `V4S035R_*` (forests).

| World | Method | Passes | Reached | SR | CR | Hits Static | Hits Dynamic | Out of bounds | Avg. Velocity |
|---|---|---|---|---|---|---|---|---|---|
| forest_easy | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 |
| | FAPP | 24 | 24 | 79.2 % | 20.8 % | 5 | 0 | 0 | 2.97 |
| forest_medium | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 |
| | FAPP | 24 | 24 | 62.5 % | 37.5 % | 9 | 0 | 1 | 3.20 |
| forest_hard | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 |
| | FAPP | 5 | 4 | 40.0 % | 60.0 % | 3 | 0 | 0 | 0.25 |
| easy (18 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 |
| | FAPP | 20 | 19 | 40.0 % | 60.0 % | 15 | 0 | 0 | 1.04 |
| medium (28 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 |
| | FAPP | 3 | 2 | 66.7 % | 33.3 % | 1 | 2 | 0 | 0.32 |
| hard_dense (60 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 |
| | FAPP | 13 | 12 | 38.5 % | 61.5 % | 5 | 6 | 0 | 1.59 |

**What the main results show.**
- **EGO-Swarm2:** all 144 passes were reached with no contact.
- **FAPP gets stuck for good** in an emergency stop, so 4 worlds have fewer than 24 passes. The low Avg. Velocity
  there includes the time it sat stopped; while flying it averages about 3 m/s.
  - We found two causes (`fapp/senior_worlds/DIAG_STUCK.md`). First, it can end inside an obstacle, or within the
    inflation, and then it can never plan again.
  - Second, sometimes it stays in the emergency stop with nothing near. This one is random and did not reproduce in
    19 diagnostic episodes.

## Small test that led to 0.35 m (`inflation_test/RESULT_INFL.md`)
With 6 passes in forest_medium and easy, raising the inflation from 0.1 to 0.35 m made EGO-Swarm2 contact-free in
12/12 passes (2/12 before). FAPP had fewer contacts, but the remaining ones were real crashes.

## Round 1: original settings (inflation 0.1 m), first worlds (`0b84ad1`)

This round used the project's earlier `hits.py`, with no out-of-bounds line. Hits come from that `hits.py`. SR and CR are per pass. Avg. Velocity is total distance / total time.

| World | Method | Passes | Reached | SR | CR | Hits Static | Hits Dynamic | Avg. Velocity |
|---|---|---|---|---|---|---|---|---|
| forest_easy | EGO-Swarm2 | 24 | 24 | 25.0 % | 75.0 % | 21 | 0 | 1.43 |
| | FAPP | 24 | 24 | 33.3 % | 66.7 % | 20 | 0 | 3.26 |
| forest_medium | EGO-Swarm2 | 24 | 24 | 8.3 % | 91.7 % | 34 | 0 | 1.43 |
| | FAPP | 24 | 24 | 4.2 % | 95.8 % | 50 | 0 | 3.27 |
| forest_hard | EGO-Swarm2 | 24 | 24 | 0.0 % | 100.0 % | 73 | 0 | 1.43 |
| | FAPP | 23 | 22 | 0.0 % | 100.0 % | 162 | 0 | 2.54 |
| easy | EGO-Swarm2 | 24 | 24 | 8.3 % | 91.7 % | 32 | 0 | 1.43 |
| | FAPP | 21 | 20 | 0.0 % | 100.0 % | 63 | 6 | 2.13 |
| medium | EGO-Swarm2 | 24 | 24 | 0.0 % | 100.0 % | 51 | 0 | 1.43 |
| | FAPP | 24 | 24 | 0.0 % | 100.0 % | 71 | 9 | 3.23 |
| hard | EGO-Swarm2 | 24 | 24 | 0.0 % | 100.0 % | 78 | 0 | 1.43 |
| | FAPP | 8 | 7 | 0.0 % | 100.0 % | 25 | 3 | 0.23 |
| hard_dense | EGO-Swarm2 | 24 | 24 | 0.0 % | 100.0 % | 71 | 0 | 1.43 |
| | FAPP | 3 | 2 | 0.0 % | 66.7 % | 6 | 0 | 0.05 |

Avg. Velocity is in m/s. The forest worlds have no moving spheres, so Hits Dynamic is 0 there for both.

| | EGO-Swarm2 | FAPP |
|---|---|---|
| Obstacle prediction | None of its own. It was given each sphere's true future path (7.5 s ahead), as SANDO did. | Its own: Kalman filter, constant velocity, from its own sensor |
| Sensor | Own simulated point cloud, static obstacles within 5 m | Own simulated point cloud, 8 m |
| Optimizer | MINCO + L-BFGS, soft constraints | MINCO + L-BFGS, soft constraints |
| Settings (original) | v_max 1.5 m/s, a_max 6, L2, inflation 0.1 m | v_max 3.5 m/s, a_max 10, L2, inflation 0.1 m |

## Please read with the round-1 numbers
1. **CR is high for both.** Both keep only about 0.1–0.3 m from static obstacles by their original settings, inside
   the 0.35 m contact radius of `hits.py`.
   - EGO-Swarm2 never entered an obstacle: its closest approach was 0.11 m.
   - FAPP sometimes did, and once got stuck inside a cylinder.
2. **The moving spheres are not a like-for-like comparison.** EGO-Swarm2 knew where each sphere would go; FAPP had to
   detect and predict them itself.
3. **Speed.** FAPP flies at 3.3 m/s, EGO-Swarm2 at 1.4 m/s.
4. **FAPP fails for good in some passes.** It switches to an emergency stop and never recovers, usually right after
   turning around at a pad.
   - This happened in forest_hard, easy, hard and hard_dense. The pass counts in those worlds are below 24.
   - In hard and hard_dense this happens within a few passes. We reran both with a larger internal map
     (`map_size_x` 400 instead of 320; the world unchanged) and it still happened, so it is FAPP's own behaviour.
   - Both runs are reported in `fapp/senior_worlds/RESULT_SW.md`.
   - The low Avg. Velocity in those worlds includes the time it sat stopped.
5. **EGO-Swarm2 settings.** These are the defaults of the official repository (ZJU-FAST-Lab EGO-Planner-v2), because
   the paper could not be accessed.
6. **One run per world** on a Mac (Apple M4, Docker, arm64). A rerun on another machine may differ.

## Check the numbers with hits.py
Each run folder has `odom_<world>.npz` in the project's `record.py` format (key `gt`). For example:

```bash
mkdir -p ~/kairos_test/20261102_compare
cp egoswarm2/senior_worlds/runs/V4S035_dyn_sando_easy/odom_dyn_sando_easy.npz ~/kairos_test/20261102_compare/
python3 hits.py dyn_sando_easy dyn_sando_easy      # with the d341041 scenarios
# expected: dyn_sando_easy: 29.5 min, 2534 m, static 0, dynamic 0
#           dyn_sando_easy: out of bounds 0
```

This needs the scenario yaml in `~/Dynamic_obstacle/src/dyn_obstacle_nav/dyn_gz_worlds/scenarios/`. Each run's
`hits.txt` shows our output, and the pass-by-pass numbers are in `table_numbers.json`.

## Rerun (Docker, x86 or arm64)
Each planner is rerun in three steps: build the image, run one world, score it.

**Step 1: build the images (once).**

FAPP uses the SANDO author's fork, `kotakondo/FAPP` `d5e02a1`. It is the original code plus a tracker fix.

```bash
git clone https://github.com/kotakondo/FAPP.git && (cd FAPP && git checkout d5e02a1)
docker build -t fapp:sando -f fapp/docker/Dockerfile .      # run where ./FAPP is
```

EGO-Swarm2 uses `kotakondo/EGO-Planner-v2`, branch `dynus_benchmark`, `6917c9f`. The Dockerfile clones it itself.
`Dockerfile.diff` shows the only changes to the author's Dockerfile: the branch pin and `-j3`, which is only for an 8 GB
machine. The Dockerfile also copies a few files from the author's `docker/` folder, so build it inside that folder:

```bash
git clone -b dynus_benchmark https://github.com/kotakondo/EGO-Planner-v2.git ego_src
cp egoswarm2/docker/Dockerfile ego_src/docker/
docker build -t ego_swarm_v2:r2 ego_src/docker
```

**Step 2: run one world, 24 passes.** This takes about 40–100 min in real time.

```bash
export DYN_EXPERT=~/Dynamic_obstacle/src/dyn_obstacle_nav/dyn_expert
export SCN_DIR=~/comparision_kairos/sando_worlds/worlds/scenarios
# main results (inflation 0.35, stop at the pad):
STOP_SPEED=0.1 LAUNCH_FILE=/sw/sw_planner_infl035.launch bash fapp/senior_worlds/run_world.sh dyn_sando_easy 24 MY_FAPP_easy
STOP_SPEED=0.1 LAUNCH_FILE=/sw/sw_ego_infl035.launch bash egoswarm2/senior_worlds/run_world.sh dyn_sando_easy 24 MY_EGO_easy
# FAPP in hard_dense as in our table: add MX_OVERRIDE=400.0
# round 1 (original settings): leave out STOP_SPEED and LAUNCH_FILE
```

The output goes to `*/senior_worlds/runs/<name>/`, as `odom_<world>.npz` plus logs.

**Step 3: score it.** Score with `hits.py` as shown above, then get the per-pass SR / CR and the out-of-bounds passes:

```bash
PYTHONPATH=$DYN_EXPERT python3 fapp/senior_worlds/analyze_sw.py fapp/senior_worlds/runs/MY_FAPP_easy $SCN_DIR/dyn_sando_easy.yaml
PYTHONPATH=$DYN_EXPERT python3 v4/analyze_oob.py fapp/senior_worlds/runs/MY_FAPP_easy $SCN_DIR/dyn_sando_easy.yaml
```

## What is in this folder
- **`fapp/` and `egoswarm2/`:**
  - `senior_worlds/` holds:
    - the plan (`PLAN_SW.md`), the results (`RESULT_SW.md`) and the code;
    - `runs/`: per world, the npz, the per-pass numbers, `hits.txt` and logs;
  - `sando_reproduction/` holds the reproduction of SANDO Table VI;
  - `docker/` holds the image recipe.
- **`v4/`:** the plan and results of the main runs.
- **`inflation_test/`:** the 6-pass test.
- **`SHA256SUMS_kit.txt`:** checksums of every file.

## Credits and licenses
- **FAPP:** [arclab-hku/FAPP](https://github.com/arclab-hku/FAPP), MIT. The SANDO author's fork used here is
  [kotakondo/FAPP](https://github.com/kotakondo/FAPP).
- **EGO-Planner-v2 / EGO-Swarm2:** [ZJU-FAST-Lab/EGO-Planner-v2](https://github.com/ZJU-FAST-Lab/EGO-Planner-v2),
  GPL-3.0. The SANDO author's fork used here is [kotakondo/EGO-Planner-v2](https://github.com/kotakondo/EGO-Planner-v2).
- **SANDO:** [mit-acl/sando](https://github.com/mit-acl/sando), arXiv 2604.07599.
- **The worlds, `hits.py` and `record.py`:** [Michael-BJ/comparision_kairos](https://github.com/Michael-BJ/comparision_kairos)
  and its `dyn_expert` package. They are not included here.
- **This repository:** GPL-3.0 (`LICENSE`), because parts are derived from EGO-Planner-v2. The upstream licenses are
  in `third_party_licenses/`.
