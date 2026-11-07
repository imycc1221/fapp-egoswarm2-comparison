# PLAN INFL: small test, both planners with obstacle inflation 0.35 m (pre-registered 2026-11-06, before any run)

**Why.** In the senior's worlds most passes of both planners have a static contact under his 0.35 m rule. Their
original `grid_map/obstacles_inflation` is 0.1 m on a 0.1 m grid. Both planners treat the drone as a point, so they
keep only about 0.1–0.2 m from the drone centre to a static surface (`*/senior_worlds/RESULT_SW.md`). The senior
asked, on 2026-11-06, for a small test of about 6 runs with a changed safety parameter. His drone is much bigger
than these planners' default.

**Change.** Only `obstacles_inflation`, from 0.1 to 0.35 m (= the senior's contact radius).
- In both codes this is `ceil(0.35 / 0.1) = 4` cells, so 0.4 m.
- 4 cells is within the codes' limit of 4 cells, so the grid resolution stays 0.1 m.
- Nothing else changes: FAPP `sw_planner_infl035.launch`, EGO-Swarm2 `sw_ego_infl035.launch`, the same build, mission
  and scoring.
- The value in force is checked after each run:
  - FAPP: `params_grid_map.yaml`;
  - EGO-Swarm2: `params_used.yaml`.

**Runs.** 6 episodes each, in `dyn_sando_forest_medium` (static) and `dyn_sando_easy` (static + spheres), for both
planners. That is 4 runs, named `INFL035_<world>`, in each planner's `senior_worlds/runs/`.

**Report.** Per run: passes, reached, SR, CR, Hits Static / Dynamic (`hits.py`) and the per-pass minimum static
distance. These are compared with the first 6 episodes of the same world in the scored runs.
- This is an exploratory small test, not a table entry.
- 6 episodes are too few for a firm difference. Only a large change, for example SR from about 0–10 % to most
  passes, would be read as a sign.
