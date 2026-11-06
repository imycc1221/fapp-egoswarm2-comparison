# RESULT R2: SANDO's Table VI EGO-Swarm2 rows reproduced (2026-11-06)

**Plan:** [PLAN_R2.md](PLAN_R2.md), pre-registered in commit `7c47ce1`; amendments 1–3 were made before any run (commits
`506e876`, `8b8fb48`, `b489e65`).
- **Code:** kotakondo/EGO-Planner-v2 `dynus_benchmark` `6917c9f`, the branch that has the L∞ option SANDO says Table VI
  uses.
- **Pipeline:** their Dockerfile (branch pin and `-j3` only) and their `run_ego_benchmark.py`, run with the Makefile's
  `run-dynamic-benchmark` defaults, headless, 10 trials per case, seeds 0–9.
- **Analysis:** their `analyze_ego_benchmark.py`.
- **Machine:** the user's Mac, Docker arm64.

| case | | success | T_opt per replan | T_trav | L_path | S_jerk | ρ_vel |
|---|---|---|---|---|---|---|---|
| easy (50 obstacles) | ours | 100 % (10/10), Wilson 95 % 72–100 % | 0.5 ms | 24.3 s | 106.3 m | 144.2 | 11.4 % |
| | SANDO | 100 % | 5.7 ms | 25.4 s | 107.5 m | 130.4 | 11.8 % |
| | ours vs SANDO | inside | report only | −4.4 % | −1.2 % | | |
| medium (100) | ours | 100 % (10/10), Wilson 72–100 % | 0.8 ms | 24.6 s | 106.7 m | 169.8 | 10.0 % |
| | SANDO | 100 % | 8.5 ms | 26.2 s | 108.3 m | 145.3 | 10.4 % |
| | ours vs SANDO | inside | report only | −6.1 % | −1.5 % | | |
| hard (200) | ours | 70 % (7/10), Wilson 40–89 % | 1.9 ms | 26.1 s | 109.2 m | 252.9 | 6.7 % |
| | SANDO | 80 % | 18.7 ms | 29.6 s | 114.2 m | 221.2 | 5.1 % |
| | ours vs SANDO | inside | report only | −11.8 % | −4.3 % | | |

**Verdict, by the criterion fixed before the runs: REPRODUCED in all three cases.**
- SANDO's success rate is inside our Wilson 95 % interval.
- T_trav and L_path are within ±15 % of SANDO's.

**What the verdict covers:**
- It means the pre-registered criterion passed. It does not show statistical equivalence or that every column of the
  table was reproduced: S_jerk and ρ_vel are shown but were not part of the criterion.
- As in SANDO, T_trav, L_path, S_jerk and ρ_vel are averaged over the successful trials only: 10, 10 and 7.
- Amendment 2's "the author built from his own checkout" is an inference, not confirmed. The branch was chosen to match
  the L∞ constraints that the paper states for Table VI.

**Notes:**
- **Hard-case failures.** In hard, all 10 trials reached the goal. 3 of them had a collision, with 47 collision events
  in total, under their rule: the drone as a point inside an obstacle's box. That gives 70 % success. None timed out.
- **Optimisation time.** T_opt is about 10 times smaller than SANDO's in every case. The machines differ, and the
  timing comes from the planner's own CSV (`comp_times_trial_*.csv`). It is reported only, as pre-registered.
- **Smoke run.** One easy trial with seed 0 (`runs_r2_smoke/`), made before the scored runs and not part of the table:
  reached in 24.0 s over 106.1 m.
- **Checks.**
  - Inside the image the commit is `6917c9f` (`runs_r2/meta.txt`).
  - The mounted fork checkout was clean (0 changed files).
  - The runner printed `Use L-inf feas: True` for every case.
  - The image build's `pip` installed pandas 2.0.3, which does not import with the image's numpy 1.17.4. So only the
    analysis step used pandas 1.1.5 (amendment 3).

## Files
- **Logs:** `runs_r2/run_<case>.log` and `analyze_<case>.log`.
- **Per case:** `runs_r2/<case>_benchmark_<ts>/` holds:
  - `benchmark_ego_swarm_v2_*.csv` / `.json` (per trial);
  - `benchmark_summary.csv`;
  - `benchmark_ego_swarm_v2_postprocessed.csv`;
  - `comp_times_trial_*.csv`.
- **Out of git:** the 30 trial bags, 2.8 GB, plus the smoke bag. Their sha256 are in
  `runs_r2/SHA256SUMS_bags_out_of_git.txt`.
- **Image:** `ego_swarm_v2:r2`, built from `docker_r2/` (see `Dockerfile.diff`). Build log: `runs_r2/build.log`.
- **Rerun:** `bash docker_r2/run_r2.sh <their docker/ dir with the edited Dockerfile> <fork checkout at 6917c9f> <out dir>`.

## Next
Run EGO-Swarm2 in the senior's worlds with its original settings, the same way FAPP was run
(`../fapp/senior_worlds/`). Its speed and other settings follow the EGO-Swarm2 paper, which the user is getting.
