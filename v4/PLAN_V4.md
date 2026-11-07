# PLAN V4: FAPP and EGO-Swarm2, inflation 0.35 m, in the senior's updated worlds (pre-registered 2026-11-06, before any run)

**Why.**
- The senior updated his worlds (2026-11-06, `comparision_kairos` `d341041`) and asked to run the three dynamic ones:
  `dyn_sando_easy`, `dyn_sando_medium` and `dyn_sando_hard_dense`.
- The user chose inflation 0.35 m for both planners, after the small test (`../RESULT_INFL.md`). This matches the
  senior's NEO (inflation = drone radius 0.35 m). His SANDO uses a drone_bbox of 0.9 × 0.9 × 0.7 m.

**The worlds** (`d341041`; md5 as in his `CHECKSUMS.md5`):

| world | statics | spheres (before) | md5 |
|---|---|---|---|
| `dyn_sando_easy` | 18 | 18 (10) | `c55510b3…` |
| `dyn_sando_medium` | 26 | 28 (24) | `30f042e4…` |
| `dyn_sando_hard_dense` | 35 | 60 (60) | `867f3603…` |

- All three have bounds y ±6.5 m (were ±9).
- They live in a separate clone (`scratch/ck_new`). The first clone at `0b84ad1` stays unchanged, so the earlier runs
  can still be scored against the worlds they flew in.

**Planners.** Each is the same build and the same original settings as in its `senior_worlds/PLAN_SW.md`. The one
exception is `grid_map/obstacles_inflation`, which is 0.35 here: `sw_planner_infl035.launch` and
`sw_ego_infl035.launch`, as in PLAN_INFL.
- **FAPP `hard_dense`:** `map_size_x` 400, as in FAPP PLAN_SW amendment 1.
- **Other map sizes:** unchanged (230 / 320 × 50 × 3 m).
- **Bounds:** neither planner has a bounds input. Their map is a ring buffer around the drone, so the map size does
  not bound them, and they are not told the bounds. The senior's KAIROS raw is not bounded either; only SANDO gets
  y limits.

**Mission and scoring.**
- The mission is unchanged: 24 episodes, pads A / B, the same limits.
- **Hits:** the senior's `hits.py` as we have it (`comparison_scripts_20261104`), static / dynamic contacts at 0.35 m.
- **SR / CR:** `analyze_sw.py`.
- **New referee rule (his README `d341041`):** a pass whose pose goes more than 1 m outside the bounds is not a
  success. His updated `hits.py`, which prints this as a second line, is not in his repo. Until it is available,
  `analyze_oob.py` implements the rule from his description. SR is then reported both with the rule (the table
  value) and without it.

**Runs** (names `V4I035_<world>` in each planner's `senior_worlds/runs/`), in this order:
1. EGO-Swarm2 easy, medium, hard_dense;
2. FAPP easy, medium, hard_dense.

No smoke run: the build, launch files and harness are the ones already used.

## Amendment 1 (2026-11-06, after 5 episodes of the first run, before any scored run of this design)
- **What we found.** The senior's new `hits.py` (`senior_code/comparison_scripts_20261106/hits.py`, sha256
  `d6a70ecf…`) counts an out-of-bounds excursion when the pose is more than 1 m outside the bounds.
  - In the earlier runs, scored against the new bounds, 23 / 24 EGO-Swarm2 episodes and 20–23 / 24 FAPP episodes go
    past a pad by more than 3 m (x up to 118–125).
  - None of them go sideways: at most one episode has |y| > 7.5.
  - The cause is our mission. It sends the next goal as soon as the drone is within 0.6 m of the pad, while it still
    flies at 1–3 m/s, and both planners run 12–20 m on before turning.
- **Decision (the user, 2026-11-06):** a pass ends only when the drone is within 0.6 m of the pad **and** slower than
  0.1 m/s; only then is the next goal sent. The 0.1 m/s is SANDO's success rule.
  - It is implemented as `mission.py _stop_speed:=0.1`. The speed is taken over the last ≥ 0.2 s of poses.
  - The default is 0, which keeps the earlier behaviour.
  - The time limit per pass is unchanged.
- **The first run is stopped and kept:** `egoswarm2/senior_worlds/runs/V4I035_dyn_sando_easy`, 5 episodes, all
  reached, with the old mission.
- **Runs:** `V4S035_<world>` (`v4/run_v4s.sh`), in the same order. Scoring uses the senior's new `hits.py` (both
  lines) plus `analyze_sw.py` / `analyze_oob.py`.
- **Smoke run first (not a result):** 2 episodes of `dyn_sando_easy` per planner, to check that the drone stops at
  the pad and stays inside the bounds.

## Amendment 2 (2026-11-06, while the dynamic V4S runs fly, before any forest run)
- The user: all worlds are rerun with inflation 0.35, not only the dynamic ones.
- The three static forests `dyn_sando_forest_easy` / `_medium` / `_hard` are unchanged in `d341041` (md5 equal to
  `0b84ad1`: `5b1fe921…`, `1ed00f52…`, `03cf804a…`).
- They are run exactly as the V4S dynamic runs: inflation 0.35, stop at the pad, the new `hits.py` and
  `analyze_oob.py`, 24 episodes, both planners.
  - Names: `V4S035_<forest>` (`v4/run_v4s_forest.sh`).
  - They start after the dynamic batch, so the two never share the CPU.
- FAPP map sizes as in its PLAN_SW: 230 m, and 320 m for `forest_hard`.

## Amendment 3 (2026-11-07 12:50): the first forest runs are invalid (the Mac slept); rerun
- **What happened:** the Mac ran on battery with the lid closed and went to sleep repeatedly. pmset shows clamshell /
  maintenance sleep; `caffeinate -i` does not prevent that.
- **Invalid runs:** `egoswarm2/senior_worlds/runs/V4S035_dyn_sando_forest_easy` (complete) and `…_forest_medium`
  (stopped at episode 15).
  - Their recorded wall clock has 9 and 18 gaps of up to 5491 s and 2949 s.
  - After the first gap the simulation broke: lost planner heartbeats, and every episode timed out.
- **Kept, not scored:** both runs stay in `runs/`.
- **Checked:** every other run of this work has no wall-clock gap over 2 s (scan of all `odom_*.npz`), including the
  dynamic V4S runs.
- **Rerun:** the three forests for both planners as `V4S035R_<forest>` (`v4/run_v4s_forest_r.sh`), identical
  settings. The Mac must stay on mains power with the lid open, and each run is checked for wall-clock gaps
  afterwards.
