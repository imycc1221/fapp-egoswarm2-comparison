# RESULT V4: FAPP and EGO-Swarm2, inflation 0.35 m, the senior's d341041 worlds (2026-11-07)

**Plan:** [PLAN_V4.md](PLAN_V4.md) with amendments 1–3, all made before the runs they govern.
- **Settings:** each planner's original settings, except `obstacles_inflation` 0.35 m (= the senior's contact
  radius, as his NEO). The value was checked in each run's parameter dump.
- **Mission:** a pass ends at the pad only when the drone is also slower than 0.1 m/s; then the next goal is sent.
- **Scoring:** the senior's new `hits.py` (sha256 `d6a70ecf…`, contacts plus out-of-bounds), with SR / CR per pass.
- **Validity:** every run has a recorded wall-clock gap below 0.2 s, so the Mac did not sleep. The two forest runs
  made while it slept are invalid and kept (amendment 3).

## Table

| world | planner | passes | reached | SR | CR | Hits Static | Hits Dynamic | out of bounds | Avg. Velocity | speed over reached passes |
|---|---|---|---|---|---|---|---|---|---|---|
| forest_easy | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 | 1.45 |
| | FAPP | 24 | 24 | 79.2 % | 20.8 % | 5 | 0 | 0 | 2.97 | 2.99 |
| forest_medium | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 | 1.45 |
| | FAPP | 24 | 24 | 62.5 % | 37.5 % | 9 | 0 | 1 | 3.20 | 3.22 |
| forest_hard | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 | 1.43 |
| | FAPP | 5 | 4 | 40.0 % | 60.0 % | 3 | 0 | 0 | 0.25 | 2.95 |
| easy (18 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 | 1.44 |
| | FAPP | 20 | 19 | 40.0 % | 60.0 % | 15 | 0 | 0 | 1.04 | 3.12 |
| medium (28 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.44 | 1.44 |
| | FAPP | 3 | 2 | 66.7 % | 33.3 % | 1 | 2 | 0 | 0.32 | 3.18 |
| hard_dense (60 spheres) | EGO-Swarm2 | 24 | 24 | 100 % | 0 % | 0 | 0 | 0 | 1.43 | 1.44 |
| | FAPP | 13 | 12 | 38.5 % | 61.5 % | 5 | 6 | 0 | 1.59 | 3.14 |

Avg. Velocity is total distance / total time in m/s. It includes the time a planner sat stopped after a failure.
The forest worlds have no spheres.

## Reading
- **EGO-Swarm2:** 144 / 144 passes reached, with no contact and no excursion.
  - With the drone size in its inflation and a stop at each pad, it flies all six worlds cleanly at 1.43–1.44 m/s.
  - Its spheres are given as true future trajectories (as in SANDO), so its zero dynamic hits are not comparable
    with methods that perceive and predict.
- **FAPP** stops for good in four of the six worlds (permanent `EMERGENCY_STOP`, as before), so those worlds have
  only 3–20 passes.
  - In the passes it flies, it often goes inside static obstacles. Its avoidance is a soft cost at about 3 m/s.
  - It perceives and predicts the spheres itself.
- **Out of bounds:** with the stop at the pad, there is one excursion in 288 episodes (FAPP, `forest_medium`, in a
  pass that already had a contact).

## Files
- **Runs:** `egoswarm2/senior_worlds/runs/V4S035*_<world>/` and `fapp/senior_worlds/runs/V4S035*_<world>/`.
  - For the forests, the valid runs are the `V4S035R_` ones.
  - Each run folder holds the npz, the episodes, `table_numbers.json`, `table_numbers_oob.json`, `hits.txt`
    (two lines), the logs and the parameter dump.
- **Runners:** `v4/run_v4s.sh` (dynamic) and `v4/run_v4s_forest_r.sh` (forest).
