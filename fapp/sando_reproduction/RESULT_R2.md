# RESULT R2: a credible reproduction of published FAPP results (2026-11-05)

**Plan:** `PLAN_R2.md`, pre-registered in `80ea053` before any R2 run.

## Answer
- **We reproduced the FAPP rows of SANDO's Table VI** with SANDO's own published FAPP pipeline (the SANDO author's
  fork and benchmark scripts), on the user's Mac.
  - The success rates match: easy 80 % vs 80 %, medium 90 % vs 80 %, hard 60 % vs 50 %. Each paper value is inside our
    95 % interval.
  - Travel time and path length are within 15 % of the paper's in easy and hard. Medium's travel time is 21 % longer
    (26.3 s vs 21.7 s).
  - By the pre-registered criterion, **easy and hard are reproduced; medium is reproduced in success and path, not in
    travel time.**
- **The FAPP paper's own Env 1** still cannot be run with its rings. The fork's tracker fix does not stop the
  perception crash (R2b).

## R2a: SANDO's Table VI, FAPP rows (ground-truth obstacle states, as the SANDO paper states)
- **Code:** kotakondo/FAPP `d5e02a1`, unchanged, built from its own `docker/Dockerfile`.
  - The one difference is `catkin_make -j3` instead of all cores: the default build ran out of the Docker VM's 8 GB
    memory. This is a build setting, not the code.
- **Command:** as their Makefile `run-benchmark`, without `--gpus` (no NVIDIA on the Mac), headless:
  `run_fapp_benchmark.py --num-trials 10 --seed-start 0 --case <case> --ground-truth-states`.
- **Analysis:** their `analyze_fapp_benchmark.py`, which re-checks collisions from the rosbags (output `analysis.log`,
  `benchmark_fapp_postprocessed.csv`, `benchmark_summary.csv`). It gives the same counts as the online check.
  - Success = goal reached (0.5 m, speed < 0.1 m/s) and no collision (the drone as a point inside an obstacle's box).
  - Travel time and path length are averaged over the successful trials, as in their analysis.

| case | success (ours, 10 trials) | 95 % Wilson | paper | T_trav ours / paper | L_path ours / paper | T_opt per replan ours / paper | reproduced? |
|---|---|---|---|---|---|---|---|
| easy (50 obstacles) | **8/10 = 80 %** | 49–94 % | 80 % | 24.74 / 22.8 s (+8 %) | 106.98 / 106.3 m | 1.0 / 0.6 ms | **yes** |
| medium (100) | **9/10 = 90 %** | 60–98 % | 80 % | 26.32 / 21.7 s (**+21 %**) | 109.07 / 106.7 m | 1.1 / 0.7 ms | success and path yes, travel time no |
| hard (200) | **6/10 = 60 %** | 31–83 % | 50 % | 27.78 / 27.9 s | 110.16 / 111.3 m | 1.3 / 0.6 ms | **yes** |

- Every trial reached the goal (30/30); all failures are collisions.
- T_opt is only reported: the machine differs (arm64 Mac in Docker vs their workstation).
- **Not run:** the planned secondary runs with FAPP's own perception (ground truth off). Each case writes about 3 GB of
  rosbags, the Mac has about 6 GB free, and deleting evidence is not allowed. They can be run on a machine with
  more disk.
- The rosbags (about 9.5 GB) stay out of git, in `runs_r2a/<case>_gt/<case>_benchmark_*/bags/`.

## R2b: the original FAPP + only the tracker fix, in the FAPP paper's Env 1 (with rings)
- **Build:** `docker/Dockerfile.tracker` = `fapp:orig` (`dbd8173`) + `patches/tracker_fix.patch`. The patch is only
  `mot_mapping/src/mapping_manger.cpp`, the fork's tracker change.
- **Step 1 diagnosis** (Env 1 with 100 rings, 45 s; `runs/diag/tracker_env1all_rep`, `_rep2`): the perception still
  died with exit −11 in both valid runs, and `/states` was never published. One more run (`_DOCKER_FAIL`) was killed
  before the simulation started, because the SANDO image was being built at the same time; it is kept.
- **Conclusion:** the tracker fix does not stop the crash, so F2c was not run (as pre-registered). The ring crash comes
  from something else in the released perception.

## What this means
- **Our setup reproduces a published third-party FAPP result.** This is SANDO's benchmark, with FAPP given
  ground-truth obstacle states, run with the authors' published fork. It supports that the harness, the machine and
  the way we run FAPP are sound.
- **The FAPP paper's own Table III (94 % in Env 1) is still not reproduced:**
  - its scenario is not released;
  - the released code crashes with the stated rings, with or without the tracker fix;
  - without rings and with our 0.2 m rule it was 55 % (R1).

  Two of the differences R1 found matter here. SANDO's collision rule treats the drone as a point, much looser than
  our 0.2 m. And SANDO gives FAPP ground-truth obstacle states instead of its own perception.
- **For the senior's comparison:** the senior allows tracker fixes and hyperparameters. So the SANDO fork, as used
  here, is an acceptable FAPP build: it differs from the original only in the tracker fix, the optional L∞ limit and
  timing logs.
