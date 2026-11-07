# Why FAPP stops for good (diagnosis, 2026-11-07)

**What "stuck" means:** in FAPP's FSM (`ego_replan_fsm.cpp`), the safety check (`checkCollisionCallback`) finds the
current trajectory in collision. If a replan from the local trajectory fails within 0.8 s, it switches to
`EMERGENCY_STOP`: a 2 s hover trajectory at the current pose. The only way out is
`enable_fail_safe_ && odom_vel_.norm() < 0.1`, which goes to `GEN_NEW_TRAJ`. A stuck run never gets back to
`EXEC_TRAJ`.

## Type B, confirmed: the drone ends inside the inflated map, and every replan fails
- **Logs:** after the last stop, `GEN_NEW_TRAJ` repeats with `Success=no`. The optimizer reports "The drone is in
  obstacle. It means a crash in real-world." (`poly_traj_optimizer.cpp`): no control point from the start is free.
  A* also fails, with "time limit exceeded".
- **Frozen poses, distance to the static surface:**

  | run | distance at the frozen pose |
  |---|---|
  | V4S035 medium | 0.08 m (inflation 0.35, so inside the 0.4 m inflated cells) |
  | V4S035R forest_hard | −0.92 m |
  | FAPP forest_hard (0.1 inflation) | −0.49 m |

  In the forest runs the drone is inside a cylinder at z ≈ 4.0.
- **Why it never ends:** FAPP has no recovery when its own position is occupied. With ideal tracking
  (`poscmd_2_odom`) nothing moves the drone out.

## Type A, not reproduced: the FSM stays in `EMERGENCY_STOP` with nothing near
- **Logs:** in V4S035 easy, V4S035 hard_dense and FAPP_MAP400 hard, the final `EXEC_TRAJ → EMERGENCY_STOP` is
  followed by about 1 s of repeated "Emergency stop!" (96–101 times), or a single one, and then for 600–5600 s only
  "state: EMERGENCY_STOP". There is no `GEN_NEW_TRAJ`.
- **What that means:** the exit condition never held. `enable_fail_safe_` is only cleared by "Depth Lost", which
  never appears, so the odom speed must have stayed ≥ 0.1. `poscmd_2_odom` publishes the last command's velocity as
  the odom twist.
- **Frozen poses:** 1.25–3.9 m from static surfaces, and 1.5–12.8 m from sphere surfaces, so nothing was near.
- **Diagnostic runs** (`runs/DIAG_estop_hard_dense`, 14 episodes; `runs/DIAG_estop_medium`, 5 episodes; same
  settings as V4S035, with odom twist and `pos_cmd` recorded in `diag.bag`):
  - all 19 episodes reached;
  - 9 emergency stops, and every one recovered (6 exits to `GEN_NEW_TRAJ`; the others were bursts);
  - the odom speed went to 0.000 within 1 s each time.
  - The permanent case did not reproduce, so it depends on timing.
- **Not confirmed:** the cause of type A. The likely mechanism is that the odom velocity stays at a last nonzero
  command, so the exit check never passes, but this was not observed.

## For the comparison
- Both types are FAPP's own behaviour in its own simulator with ideal tracking.
- Type B comes from flying into or very close to obstacles, which its soft avoidance at about 3 m/s allows.
- The stops are not deterministic. A rerun of the same world can stop at a different pass, or not at all.
