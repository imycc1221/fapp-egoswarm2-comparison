#!/usr/bin/env python3
"""Collect the table numbers of all FAPP senior-world runs (PLAN_SW.md) into one table, plus checks used in RESULT_SW.md:
  - the table: from each run's table_numbers.json (analyze_sw.py) and hits.txt (the senior's hits.py);
  - extra context, NOT the senior's metric: per run the fraction of pose samples inside a static obstacle (surface
    distance < 0, a point drone), the speed over reached passes only (path / time), and the largest one-step jump of the pose (a planner output fault shows up as a jump).
  python3 summarize_sw.py RUNS_DIR SCN_DIR   (dyn_expert on PYTHONPATH)"""
import glob, json, os, re, sys
import numpy as np
from dyn_expert.core.scenario import Scenario

WORLDS = ["forest_easy", "forest_medium", "forest_hard", "easy", "medium", "hard", "hard_dense"]


def main(runs, scn_dir):
    rows = []
    for w in WORLDS:
        d = os.path.join(runs, f"FAPP_dyn_sando_{w}")
        if not os.path.exists(os.path.join(d, "table_numbers.json")):
            rows.append(dict(world=w, missing=True)); continue
        r = json.load(open(os.path.join(d, "table_numbers.json")))
        h = open(os.path.join(d, "hits.txt")).read() if os.path.exists(os.path.join(d, "hits.txt")) else ""
        m = re.search(r"([\d.]+) min, (\d+) m, static (\d+), dynamic (\d+)", h)
        scn = Scenario.load(os.path.join(scn_dir, f"dyn_sando_{w}.yaml"))
        g = np.load(glob.glob(os.path.join(d, "odom_*.npz"))[0])["gt"]; t, p = g[:, 0], g[:, 3:6]
        sd = scn.static_distance(p)
        jump = float(np.max(np.linalg.norm(np.diff(p, axis=0), axis=1)))
        rows.append(dict(world=w, passes=r["passes"], reached=r["reached"], SR=r["SR"], CR=r["CR"],
                         hits_static=int(m.group(3)) if m else None, hits_dynamic=int(m.group(4)) if m else None,
                         hits_min=float(m.group(1)) if m else None, hits_m=int(m.group(2)) if m else None,
                         avg_v=round(r["avg_speed"], 2),   # distance / time, unrounded (hits.txt rounds both)
                         v_reached=round(sum(q["path"] for q in r["per_pass"] if q["outcome"] == "reached") /
                                         max(1e-9, sum(q["time"] for q in r["per_pass"] if q["outcome"] == "reached")), 2),
                         own_static=r["passes_static"], own_dynamic=r["passes_dynamic"],
                         frac_inside_static=round(float((sd < 0).mean()), 4), max_step_jump_m=round(jump, 2)))
    json.dump(rows, open(os.path.join(runs, "summary_sw.json"), "w"), indent=1)
    print("| world | passes | reached | SR % | CR % | Hits Static | Hits Dynamic | Avg. Velocity m/s | v over reached passes | inside static (point) | max pose jump m |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r.get("missing"):
            print(f"| {r['world']} | missing |"); continue
        print(f"| {r['world']} | {r['passes']} | {r['reached']} | {r['SR']} | {r['CR']} | {r['hits_static']} | "
              f"{r['hits_dynamic']} | {r['avg_v']} | {r['v_reached']} | {100 * r['frac_inside_static']:.2f} % | {r['max_step_jump_m']} |")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
