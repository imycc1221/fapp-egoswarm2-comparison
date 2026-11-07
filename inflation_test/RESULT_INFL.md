# RESULT INFL: obstacle inflation 0.35 m, small test (2026-11-06)

**Plan:** [PLAN_INFL.md](PLAN_INFL.md), pre-registered in commit `d7cbfd0`. This is an exploratory test of 6 episodes,
not a table entry.

**Change:** only `grid_map/obstacles_inflation`, from 0.1 m to 0.35 m (4 cells of 0.1 m). The value was checked in
`params_grid_map.yaml` (FAPP) and `params_used.yaml` (EGO-Swarm2) after each run. For comparison, the first 6
episodes of the scored runs used the original 0.1 m.

| planner | world | inflation | passes | reached | SR | CR | Hits Static | Hits Dynamic | per-pass min static distance |
|---|---|---|---|---|---|---|---|---|---|
| EGO-Swarm2 | forest_medium | 0.1 m | 6 | 6 | 1/6 | 5/6 | 7 | 0 | 0.19–0.51 m |
| EGO-Swarm2 | forest_medium | **0.35 m** | 6 | 6 | **6/6** | 0/6 | **0** | 0 | 0.52–0.70 m |
| EGO-Swarm2 | easy | 0.1 m | 6 | 6 | 1/6 | 5/6 | 8 | 0 | 0.17–0.41 m |
| EGO-Swarm2 | easy | **0.35 m** | 6 | 6 | **6/6** | 0/6 | **0** | 0 | 0.49–0.70 m |
| FAPP | forest_medium | 0.1 m | 6 | 6 | 1/6 | 5/6 | 11 | 0 | 0.18–0.36 m |
| FAPP | forest_medium | **0.35 m** | 6 | 6 | 4/6 | 2/6 | 2 | 0 | −0.92 to 0.55 m |
| FAPP | easy | 0.1 m | 6 | 6 | 0/6 | 6/6 | 19 | 2 | 0.12–0.26 m |
| FAPP | easy | **0.35 m** | 3 | 2 | 0/3 | 3/3 | 3 | 0 | −0.13 to 0.27 m |

Notes on reading the table:
- Hits come from the senior's `hits.py` (run's `hits.txt`).
- The 0.1 m rows are the per-pass numbers of the first 6 episodes of the scored runs (`table_numbers.json`).
- A negative minimum distance means the drone centre went inside an obstacle.

## What it shows (6 episodes, exploratory)
- **EGO-Swarm2:** with the inflation set to the senior's contact radius, all 12 passes are contact-free and reach
  the goal at the same speed (1.42–1.43 m/s). Its static contacts at 0.1 m came from the small default clearance:
  the planner treats the drone as a point and keeps only 0.1–0.2 m.
- **FAPP:** the static contacts became fewer, but those that remain are real collisions: in 2 forest passes and
  2 box passes the drone centre went inside an obstacle (down to −0.92 m). FAPP's avoidance is a soft cost, and at
  3.3 m/s it sometimes cuts through.
- **FAPP still stops for good:** in `easy` pass 3 it ran to x −19 after turning at pad A, then stopped 2.8 m short of
  pad B in a permanent `EMERGENCY_STOP`. This is the same failure as in the scored runs, and it is not related to
  the inflation.
- **Sample size:** 6 episodes per cell are few. EGO-Swarm2's change (12/12 vs 2/12 contact-free) is large; FAPP's is
  mixed.

## Files
- `fapp/senior_worlds/runs/INFL035_dyn_sando_{forest_medium,easy}/` and
  `egoswarm2/senior_worlds/runs/INFL035_dyn_sando_{forest_medium,easy}/`: npz, episodes, `table_numbers.json`,
  `hits.txt`, logs, parameter dumps.
- Launch variants: `fapp/senior_worlds/sw_planner_infl035.launch`, `egoswarm2/senior_worlds/sw_ego_infl035.launch`.
- Runner: `run_infl.sh`.
