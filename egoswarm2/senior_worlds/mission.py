#!/usr/bin/env python3
"""The senior's mission for EGO-Swarm2 in its own simulator (PLAN_SW.md), plus the recorder (copy of
../../fapp/senior_worlds/mission.py; only the goal height differs: EGO-Swarm2 does not force one, so the senior's
route height _goal_z:=2.0 is used).
  - pads A = route.a, B = route.b; the first goal is B, then alternating; a goal is FAPP's GoalSet on /goal_with_id
    (EGO-Swarm2's own GoalSet input, remapped from /goal in its advanced_param.xml);
  - reached: the drone within GOAL_TOL of (pad, goal_z); time limit per pass = TF * |goal - start| / V_NOM + 10 s; after
    a timeout the same goal is kept with a new limit (the senior's keep_goal_after_failure);
  - stops after N_PASSES passes (episodes), then writes everything and exits.
Recorder: every pose of /drone_0_visual_slam/odom (EGO-Swarm2's simulated drone) as the senior's record.py rows
(t, t, wall, x, y, z, yaw) with t = the world time of scenario_world.py (ROS time - /senior_world/t0), into
/out/odom_<NAME>.npz under key gt (and ekf / kairos empty), saved every 30 s and at the end; passes in episodes.json.
  args: _name:=NAME _passes:=24"""
import json, math, time
import numpy as np
import rospy
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import GoalSet

GOAL_TOL, TF, V_NOM = 0.6, 4.0, 1.5


def main():
    rospy.init_node("senior_mission")
    name = rospy.get_param("~name"); n_pass = int(rospy.get_param("~passes", 24))
    GOAL_Z = float(rospy.get_param("~goal_z", 2.0))
    while not rospy.has_param("/senior_world/t0") and not rospy.is_shutdown():
        rospy.sleep(0.1)
    t0 = rospy.get_param("/senior_world/t0")
    from dyn_expert.core.scenario import Scenario
    scn = Scenario.load(rospy.get_param("~scenario"))
    A = np.array(scn.data["route"]["a"], float); B = np.array(scn.data["route"]["b"], float)
    rows, st = [], {"p": None}

    def on_odom(m):
        p, q = m.pose.pose.position, m.pose.pose.orientation
        t = m.header.stamp.to_sec() - t0
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        rows.append((t, t, time.time(), p.x, p.y, p.z, yaw)); st["p"] = np.array([p.x, p.y, p.z]); st["t"] = t

    rospy.Subscriber("/drone_0_visual_slam/odom", Odometry, on_odom, queue_size=100)
    pub = rospy.Publisher("/goal_with_id", GoalSet, queue_size=1, latch=True)
    out = f"/out/odom_{name}.npz"
    save = lambda: np.savez(out, gt=np.array(rows, float).reshape(-1, 7), ekf=np.zeros((0, 7)), kairos=np.zeros((0, 7)))
    while st["p"] is None and not rospy.is_shutdown():
        rospy.sleep(0.1)
    rospy.sleep(5.0)                                   # let the planner and the sensor start
    eps, goal_is_b, last_save = [], True, time.time()
    while len(eps) < n_pass and not rospy.is_shutdown():
        g = B if goal_is_b else A
        start, t_start = st["p"].copy(), st["t"]
        limit = TF * float(np.linalg.norm(np.r_[g, GOAL_Z] - start)) / V_NOM + 10.0
        msg = GoalSet(); msg.drone_id = 0; msg.goal = [float(g[0]), float(g[1]), GOAL_Z]; pub.publish(msg)
        rospy.loginfo(f"pass {len(eps) + 1}: goal {g.tolist()} limit {limit:.0f} s")
        outcome = None
        while not rospy.is_shutdown():
            if np.linalg.norm(st["p"] - np.r_[g, GOAL_Z]) < GOAL_TOL:
                outcome = "reached"; break
            if st["t"] - t_start > limit:
                outcome = "timeout"; break
            if time.time() - last_save > 30:
                save(); last_save = time.time()
            rospy.sleep(0.02)
        eps.append(dict(episode=len(eps) + 1, goal=g.tolist(), start=start.tolist(), t_start=t_start, t_end=st["t"],
                        outcome=outcome, limit=limit))
        rospy.loginfo(f"pass {len(eps)}: {outcome} in {st['t'] - t_start:.1f} s")
        json.dump(dict(name=name, scenario=scn.name, t0=t0, episodes=eps), open(f"/out/episodes_{name}.json", "w"), indent=1)
        if outcome == "reached":
            goal_is_b = not goal_is_b
    save()
    rospy.loginfo(f"MISSION DONE {name}: {sum(e['outcome'] == 'reached' for e in eps)}/{len(eps)} reached")


if __name__ == "__main__":
    main()
