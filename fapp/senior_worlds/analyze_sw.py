#!/usr/bin/env python3
"""The table's numbers for one FAPP run in a senior's world (PLAN_SW.md), with the senior's definitions:
  - a contact: drone centre to an obstacle's surface < 0.35 m; samples < 0.5 s apart are one contact; all statics are
    one group, each sphere its own (hits.py's rule, here counted inside each pass);
  - a pass = one episode; a timeout and its follow-on episode(s) to the same pad form ONE failed pass;
  - SR = % of passes reached with 0 contacts; CR = % of passes with >= 1 contact.
Hits Static / Dynamic and Avg. Velocity for the table come from the senior's hits.py (run separately on the same npz);
this script also prints its own whole-run totals as a cross-check.
  python3 analyze_sw.py RUN_DIR SCENARIO_YAML   (dyn_expert on PYTHONPATH)"""
import glob, json, os, sys
import numpy as np
from dyn_expert.core.scenario import Scenario

R_CONTACT, MERGE = 0.35, 0.5


def events(t, bad):
    x = t[bad]
    return (1 + int(np.sum(np.diff(x) > MERGE))) if len(x) else 0


def contacts(scn, t, p):
    st = events(t, scn.static_distance(p) < R_CONTACT) if len(t) else 0
    dy = 0
    for ob in scn.dynamic:
        q = np.asarray(ob.pos(t)).reshape(len(t), 3)
        dy += events(t, np.linalg.norm(p - q, axis=1) - ob.radius < R_CONTACT) if len(t) else 0
    return st, dy


def main(run, scn_file):
    scn = Scenario.load(scn_file)
    g = np.load(glob.glob(os.path.join(run, "odom_*.npz"))[0])["gt"]; t, p = g[:, 0], g[:, 3:6]
    eps = json.load(open(glob.glob(os.path.join(run, "episodes_*.json"))[0]))["episodes"]
    passes = []
    for e in eps:                                      # merge a timeout with its follow-on(s) to the same pad
        if passes and passes[-1]["outcome"] != "reached" and passes[-1]["goal"] == e["goal"]:
            passes[-1].update(t_end=e["t_end"], outcome=e["outcome"], merged=True)
        else:
            passes.append(dict(e, merged=False))
    rows = []
    for k, ps in enumerate(passes):
        m = (t >= ps["t_start"]) & (t <= ps["t_end"])
        st, dy = contacts(scn, t[m], p[m])
        path = float(np.sum(np.linalg.norm(np.diff(p[m], axis=0), axis=1))) if m.sum() > 1 else 0.0
        rows.append(dict(pass_=k + 1, outcome=ps["outcome"], merged=ps["merged"], time=round(ps["t_end"] - ps["t_start"], 2),
                         path=round(path, 1), static=st, dynamic=dy))
    n = len(rows)
    sr = sum(r["outcome"] == "reached" and r["static"] + r["dynamic"] == 0 for r in rows)
    cr = sum(r["static"] + r["dynamic"] > 0 for r in rows)
    st_all, dy_all = contacts(scn, t, p)
    dist = float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))
    res = dict(world=scn.name, episodes=len(eps), passes=n, reached=sum(r["outcome"] == "reached" for r in rows),
               SR=round(100.0 * sr / n, 1) if n else None, CR=round(100.0 * cr / n, 1) if n else None,
               passes_static=sum(r["static"] for r in rows), passes_dynamic=sum(r["dynamic"] for r in rows),
               whole_run_static=st_all, whole_run_dynamic=dy_all, distance_m=round(dist, 1),
               time_min=round((t[-1] - t[0]) / 60, 2), avg_speed=round(dist / (t[-1] - t[0]), 3), per_pass=rows)
    json.dump(res, open(os.path.join(run, "table_numbers.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "per_pass"}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
