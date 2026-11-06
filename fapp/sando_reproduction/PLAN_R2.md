# PLAN R2: a credible reproduction of FAPP results (pre-registered 2026-11-05, before any R2 run)

## Why
R1 could not reproduce the FAPP paper's Env 1:
- its scenario is not released;
- with its stated rings the released perception crashes;
- without them, success was 55 %.

The user asked for a reproduction that is credible.

The senior's rule (2026-11-05, 9:47–9:48), which applies to these runs:
- changes may be the hyperparameters we use (e.g. v_max);
- fixing something inside the original code for specific testing is acceptable, if it is the tracker and not the main
  algorithm.

## R2a: reproduce the FAPP rows of SANDO's Table VI with SANDO's own published pipeline
- **Target**, SANDO (Kondo et al., arXiv 2604.07599), Table VI, dynamic benchmark, 10 trials per case:

  | case | success | T_trav | L_path | T_opt per replan |
  |---|---|---|---|---|
  | easy | 80 % | 22.8 s | 106.3 m | 0.6 ms |
  | medium | 80 % | 21.7 s | 106.7 m | 0.7 ms |
  | hard | 50 % | 27.9 s | 111.3 m | 0.6 ms |

  - The paper's text says FAPP was fed ground-truth obstacle positions and velocities.
- **Code:** github.com/kotakondo/FAPP (the SANDO author's fork, `main` `d5e02a1`), as published. Against the
  original it changes:
  - the tracker (a bug fix in `mot_mapping`);
  - an optional per-axis (L∞) feasibility limit, a hyperparameter;
  - timing logs.

  Its benchmark scripts are used unchanged:
  - `scripts/run_fapp_benchmark.py`, `docker/scripts/dynamic_forest.py`, `docker/launch/*`;
  - the analysis `scripts/analyze_fapp_benchmark.py`.
- **How, as their `docker/Makefile` `run-benchmark` target:**
  - built from their `docker/Dockerfile`;
  - cases easy / medium / hard (their script: 50 / 100 / 200 obstacles, 65 % dynamic);
  - `--num-trials 10 --seed-start 0`, `--ground-truth-states` (because the paper's text says so; the Makefile
    default is off);
  - headless.
- **Not as theirs:**
  - the container runs without `--gpus all` (no NVIDIA GPU on the Mac; CUDA rendering is off in the code), arm64;
  - it is started with `docker run` directly instead of `make`. The same command inside the container.
- **Metrics:** their own:
  - success = goal reached (within 0.5 m, speed < 0.1 m/s) without a collision;
  - a collision = the drone (a point; their `drone_half_extents` is 0) inside an obstacle's box.
- **"Reproduced" (fixed now), per case:**
  1. the paper's success rate is inside the Wilson 95 % interval of our 10 trials;
  2. our mean travel time and path length are within ±15 % of the paper's.

  T_opt is reported only, because the machine differs.
- **Secondary (exploratory):** the same with `--ground-truth-states` off (FAPP's own perception), 10 trials per case,
  if time allows.

## R2b: the original FAPP with only the tracker fix, in the FAPP paper's Env 1
- **Code:** the original `dbd8173` plus **only** the fork's change to `src/mot_mapping/src/mapping_manger.cpp`
  (tracker age once per frame; trackers created in a frame are not matched again in the same frame). It is the
  tracker, not the planner (the senior's rule), and is applied as a patch file `patches/tracker_fix.patch`.
- **Step 1 (diagnosis):** the R1 `env1all` diagnosis (Env 1 with 100 rings, 45 s). Does the perception survive?
- **Step 2, only if it survives — F2c:** F2 of R1 rerun with the patched build, with the same settings as R1 amendments
  1–2:
  - the same 20 goals, 120 s, per-goal limit 115 s;
  - the same referee and task window, the same 0.2 m contact rule and the same validity rule.
  - Reported as in R1, plus the success under SANDO's point-collision definition (contact distance < 0 m ⇒ we use
    < 0.05 m as the nearest equivalent with point clouds), as a secondary number.
- If it does not survive, R2b stops there and this is reported.

All runs are kept. Nothing in FAPP's planner is changed in R2a or R2b.
