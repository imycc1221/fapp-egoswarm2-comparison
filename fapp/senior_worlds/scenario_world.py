#!/usr/bin/env python3
"""The senior's world for FAPP's own simulator (PLAN_SW.md): stands in for FAPP's random map generator
(map_generator/random_forest_sensing.cpp) and publishes the same topics with a scenario of the senior's test:
  /map_generator/static_obs_cloud  the scenario's boxes and cylinders, surface points at RES (the generator's 0.2 m),
                                   what FAPP's simulated sensor (pcl_render_node) renders for the planner's map
  /map_generator/global_cloud      the same static points (the generator's cloudMap; moving objects not included)
  /map_generator/obj_cloud         every sphere's surface points at its scenario position pos(t), at 50 Hz (the
                                   generator's loop rate), what FAPP's perception (mot_mapping) clusters and tracks
World time t = ROS time - the node's start; it is written to the parameter /senior_world/t0 for the recorder, so the
recorded poses and the scenario's motions share one clock (as the senior's hits.py assumes).
  rosrun ... scenario_world.py _scenario:=/scn/dyn_sando_easy.yaml   (dyn_expert on PYTHONPATH)"""
import numpy as np
import rospy
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from dyn_expert.core.scenario import Scenario

RES = 0.2       # FAPP's generator resolution (simulator_example.launch map/resolution)
RATE = 50.0     # FAPP's generator loop rate (pub_rate)


def box_points(c, half, yaw, res=RES):
    """surface points of an oriented box (centre c, half sizes, yaw about z)"""
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
    R = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return P @ R.T + np.asarray(c)


def cylinder_points(cx, cy, r, h, res=RES):
    """surface points of a vertical cylinder standing on the ground (wall and top)"""
    n = max(8, int(np.ceil(2 * np.pi * r / res)))
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    z = np.arange(0.0, h + 1e-9, res)
    A, Z = np.meshgrid(a, z, indexing="ij")
    wall = np.c_[cx + r * np.cos(A.ravel()), cy + r * np.sin(A.ravel()), Z.ravel()]
    rr = np.arange(0.0, r, res)
    top = [np.c_[cx + q * np.cos(a), cy + q * np.sin(a), np.full(n, h)] for q in rr]
    return np.vstack([wall] + top)


def sphere_template(r, res=RES):
    n = max(6, int(np.ceil(np.pi * r / res)))
    th = np.linspace(0, np.pi, n); out = []
    for t in th:
        m = max(1, int(np.ceil(2 * np.pi * r * np.sin(t) / res)))
        ph = np.linspace(0, 2 * np.pi, m, endpoint=False)
        out.append(np.c_[r * np.sin(t) * np.cos(ph), r * np.sin(t) * np.sin(ph), np.full(m, r * np.cos(t))])
    return np.vstack(out)


def cloud(points, stamp):
    h = Header(stamp=stamp, frame_id="world")
    return point_cloud2.create_cloud_xyz32(h, points.astype(np.float32).tolist())


def main():
    rospy.init_node("senior_world")
    scn = Scenario.load(rospy.get_param("~scenario"))
    static = [box_points(c, half, yaw) for c, half, yaw in scn.boxes] + [cylinder_points(*row) for row in scn.cyl]
    static = np.vstack(static) if static else np.zeros((0, 3))
    tmpl = [sphere_template(ob.radius) for ob in scn.dynamic]
    pub_static = rospy.Publisher("/map_generator/static_obs_cloud", PointCloud2, queue_size=1, latch=True)
    pub_global = rospy.Publisher("/map_generator/global_cloud", PointCloud2, queue_size=1, latch=True)
    pub_obj = rospy.Publisher("/map_generator/obj_cloud", PointCloud2, queue_size=1)
    rospy.sleep(0.5)
    t0 = rospy.get_time()
    rospy.set_param("/senior_world/t0", t0)
    rospy.set_param("/senior_world/name", scn.name)
    rospy.loginfo(f"senior_world {scn.name}: {len(static)} static points ({len(scn.boxes)} boxes, {len(scn.cyl)} "
                  f"cylinders), {len(scn.dynamic)} spheres, t0 {t0:.3f}")
    msg_static = cloud(static, rospy.Time.now())
    pub_static.publish(msg_static); pub_global.publish(msg_static)
    rate = rospy.Rate(RATE); k = 0
    while not rospy.is_shutdown():
        now = rospy.Time.now(); t = now.to_sec() - t0
        if scn.dynamic:
            P = np.vstack([np.asarray(ob.pos(t)).reshape(3) + T for ob, T in zip(scn.dynamic, tmpl)])
        else:
            P = np.zeros((0, 3))
        pub_obj.publish(cloud(P, now))
        k += 1
        if k % int(RATE) == 0:                         # the generator republishes its static clouds in its loop
            msg_static.header.stamp = now; pub_static.publish(msg_static); pub_global.publish(msg_static)
        rate.sleep()


if __name__ == "__main__":
    main()
