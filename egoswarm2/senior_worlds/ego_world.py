#!/usr/bin/env python3
"""The senior's world for EGO-Swarm2 in its own simulator (PLAN_SW.md), standing in for EGO-Swarm2's random map
generator and for its moving obstacles, with the same topics:
  /map_generator/global_cloud   the scenario's boxes and cylinders as surface points at RES (the original generator's
                                0.1 m in moving_obstacles_avoidance.launch), latched and republished at 1 Hz (its
                                pub_rate); EGO-Swarm2's own simulated sensor (pcl_render_node) cuts its 5 m view from it
  /broadcast_traj_to_planner    every sphere near the drone as a MINCOTraj (EGO-Swarm2's swarm trajectory message,
                                how its moving obstacles reach the planner), built from the scenario's motion pos(t)
                                exactly as SANDO's dynamic_forest.py builds them (8 pieces over PRED_T s, exact p/v/a
                                at both ends, inner positions), des_clearance = the sphere radius (SANDO: half the size)
World time t = ROS time - the node's start, written to /senior_world/t0 for the recorder (as for FAPP).
  rosrun ... ego_world.py _scenario:=/scn/dyn_sando_easy.yaml   (dyn_expert on PYTHONPATH)"""
import numpy as np
import rospy
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
from traj_utils.msg import MINCOTraj
from dyn_expert.core.scenario import Scenario

RES = 0.1            # original map generator resolution
RATE = 50.0          # SANDO dynamic_forest.py publish rate for the trajectories
PRED_T = 7.5         # prediction horizon of each MINCOTraj (SANDO: the planning_horizon value)
N_PIECES = 8
DYN_ID_OFFSET = 100  # SANDO: drone ids of the obstacles
H_FD = 1e-3          # finite-difference step for v, a of pos(t)


def box_points(c, half, yaw, res=RES):
    pts = []
    for ax in range(3):
        o = [a for a in range(3) if a != ax]
        u = np.arange(-half[o[0]], half[o[0]] + 1e-9, res); v = np.arange(-half[o[1]], half[o[1]] + 1e-9, res)
        U, V = np.meshgrid(u, v, indexing="ij")
        for s in (-1.0, 1.0):
            P = np.zeros((U.size, 3)); P[:, ax] = s * half[ax]; P[:, o[0]] = U.ravel(); P[:, o[1]] = V.ravel()
            pts.append(P)
    P = np.vstack(pts)
    cz, sz = np.cos(yaw), np.sin(yaw)
    return P @ np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]).T + np.asarray(c)


def cylinder_points(cx, cy, r, h, res=RES):
    n = max(8, int(np.ceil(2 * np.pi * r / res)))
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    A, Z = np.meshgrid(a, np.arange(0.0, h + 1e-9, res), indexing="ij")
    wall = np.c_[cx + r * np.cos(A.ravel()), cy + r * np.sin(A.ravel()), Z.ravel()]
    top = [np.c_[cx + q * np.cos(a), cy + q * np.sin(a), np.full(n, h)] for q in np.arange(0.0, r, res)]
    return np.vstack([wall] + top)


def pva(ob, t):
    p = lambda s: np.asarray(ob.pos(s), float).reshape(3)
    p0, pp, pm = p(t), p(t + H_FD), p(t - H_FD)
    return p0, (pp - pm) / (2 * H_FD), (pp - 2 * p0 + pm) / (H_FD * H_FD)


def minco(ob, i, t, stamp):
    dt = PRED_T / N_PIECES
    p0, v0, a0 = pva(ob, t); pN, vN, aN = pva(ob, t + PRED_T)
    inner = [np.asarray(ob.pos(t + k * dt), float).reshape(3) for k in range(1, N_PIECES)]
    m = MINCOTraj()
    m.drone_id = DYN_ID_OFFSET + i; m.traj_id = 0; m.start_time = stamp; m.order = 5
    m.des_clearance = float(ob.radius)
    m.start_p, m.start_v, m.start_a = p0.tolist(), v0.tolist(), a0.tolist()
    m.end_p, m.end_v, m.end_a = pN.tolist(), vN.tolist(), aN.tolist()
    m.inner_x = [float(q[0]) for q in inner]; m.inner_y = [float(q[1]) for q in inner]; m.inner_z = [float(q[2]) for q in inner]
    m.duration = [float(dt)] * N_PIECES
    return m


def main():
    rospy.init_node("senior_world")
    scn = Scenario.load(rospy.get_param("~scenario"))
    static = [box_points(c, half, yaw) for c, half, yaw in scn.boxes] + [cylinder_points(*row) for row in scn.cyl]
    static = np.vstack(static) if static else np.zeros((0, 3))
    pub_global = rospy.Publisher("/map_generator/global_cloud", PointCloud2, queue_size=1, latch=True)
    pub_traj = rospy.Publisher("/broadcast_traj_to_planner", MINCOTraj, queue_size=100)
    drone = {"p": None}
    rospy.Subscriber("/drone_0_visual_slam/odom", Odometry,
                     lambda m: drone.update(p=np.array([m.pose.pose.position.x, m.pose.pose.position.y,
                                                        m.pose.pose.position.z])), queue_size=1)
    # SANDO's filter: only obstacles within planning_horizon * max_vel * 3 of the drone get a trajectory
    horizon_radius = (rospy.get_param("/drone_0_ego_planner_node/manager/planning_horizon", 7.5)
                      * rospy.get_param("/drone_0_ego_planner_node/manager/max_vel", 1.5) * 3.0)
    rospy.sleep(0.5)
    t0 = rospy.get_time()
    rospy.set_param("/senior_world/t0", t0); rospy.set_param("/senior_world/name", scn.name)
    rospy.loginfo(f"senior_world {scn.name}: {len(static)} static points ({len(scn.boxes)} boxes, {len(scn.cyl)} "
                  f"cylinders), {len(scn.dynamic)} spheres, horizon_radius {horizon_radius:.1f} m, t0 {t0:.3f}")
    msg_static = point_cloud2.create_cloud_xyz32(Header(stamp=rospy.Time.now(), frame_id="world"),
                                                 static.astype(np.float32).tolist())
    pub_global.publish(msg_static)
    rate = rospy.Rate(RATE); k = 0
    while not rospy.is_shutdown():
        now = rospy.Time.now(); t = now.to_sec() - t0
        for i, ob in enumerate(scn.dynamic):
            p = np.asarray(ob.pos(t), float).reshape(3)
            if drone["p"] is not None and np.linalg.norm(p - drone["p"]) > horizon_radius:
                continue
            pub_traj.publish(minco(ob, i, t, now))
        k += 1
        if k % int(RATE) == 0:
            msg_static.header.stamp = now; pub_global.publish(msg_static)
        rate.sleep()


if __name__ == "__main__":
    main()
