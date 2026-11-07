#!/usr/bin/env python3
"""Out-of-bounds rule of the senior's README (comparision_kairos d341041, 2026-11-06): a pass whose pose goes more than
1 m outside the scenario bounds is not a success. Our implementation from that description, until his updated
hits.py is available. Reads a run's table_numbers.json (analyze_sw.py) and adds per pass `oob` and the SR with the rule.
  python3 analyze_oob.py RUN_DIR SCENARIO_YAML   (dyn_expert on PYTHONPATH)"""
import glob, json, os, sys
import numpy as np
from dyn_expert.core.scenario import Scenario

MARGIN = 1.0


def main(run, scn_file):
    scn = Scenario.load(scn_file)
    lo, hi = np.array(scn.data["bounds"]["lo"], float), np.array(scn.data["bounds"]["hi"], float)
    g = np.load(glob.glob(os.path.join(run, "odom_*.npz"))[0])["gt"]; t, p = g[:, 0], g[:, 3:6]
    eps = json.load(open(glob.glob(os.path.join(run, "episodes_*.json"))[0]))["episodes"]
    tab = json.load(open(os.path.join(run, "table_numbers.json")))
    out = np.any((p < lo - MARGIN) | (p > hi + MARGIN), axis=1)
    passes, cur = [], None                      # same merging as analyze_sw.py: a timeout + its follow-on(s) = one pass
    for e in eps:
        if passes and passes[-1]["outcome"] != "reached" and passes[-1]["goal"] == e["goal"]:
            passes[-1].update(t_end=e["t_end"], outcome=e["outcome"])
        else:
            passes.append(dict(e))
    rows = tab["per_pass"]
    assert len(rows) == len(passes)
    for r, ps in zip(rows, passes):
        m = (t >= ps["t_start"]) & (t <= ps["t_end"])
        r["oob"] = bool(out[m].any())
    n = len(rows)
    sr = sum(r["outcome"] == "reached" and r["static"] + r["dynamic"] == 0 and not r["oob"] for r in rows)
    res = dict(world=tab["world"], passes=n, oob_passes=sum(r["oob"] for r in rows),
               SR_with_oob=round(100.0 * sr / n, 1) if n else None, SR_without_oob=tab["SR"], CR=tab["CR"], per_pass=rows)
    json.dump(res, open(os.path.join(run, "table_numbers_oob.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "per_pass"}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
