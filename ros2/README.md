# ROS 2 integration

A ROS 2 node that runs the learned locomotion policy on Yertle.

```
ros2/
    yertle_rl/                 ament_python package
        yertle_rl/policy_node.py   the node (thin wrapper over learning/deploy.py)
        package.xml, setup.py      package metadata
```

## What the node does

`policy_node` subscribes to a velocity command and IMU (and optionally joint
feedback), runs the trained policy at a fixed control rate, and publishes 12
joint targets:

| Direction | Topic | Type |
|-----------|-------|------|
| sub | `/cmd_vel` | `geometry_msgs/Twist` |
| sub | `/imu/data` | `sensor_msgs/Imu` |
| sub | `/joint_states` (optional) | `sensor_msgs/JointState` |
| pub | `/joint_commands` | `std_msgs/Float64MultiArray` (12 targets, rad) |

The heavy lifting (observation assembly, policy inference, joint limiting) lives
in [`learning/deploy.py`](../learning/deploy.py), which is validated by the
simulation self-check (`python -m learning.deploy --check`). The node is a thin
ROS wrapper around that same tested core.

## Status

Built and run on **ROS 2 Humble**: the package compiles with `colcon`, and the
node runs live — publishing a `/cmd_vel` and an `/imu` produces `/joint_commands`
(12 joint targets) from the policy. It was validated on Windows with no WSL, via
RoboStack (ROS 2 as conda packages), which is the quickest way to run it here.

**Closed-loop demo.** `demo_ros2_loop.py` runs the full control loop over ROS 2
topics: a PyBullet simulation node publishes `/joint_states` and `/imu/data` and
applies `/joint_commands`, while `policy_node` runs the trained policy against a
`/cmd_vel` command. With the trained PyBullet policy the robot walks
(~0.5 m of base travel in 8 s at a 0.25 m/s command):

```bash
conda run -n ros2 python ros2/demo_ros2_loop.py --policy learning/runs/ppo_walk2/policy.zip
```

**Isaac Sim bridge (validated, bidirectional).** `isaac_lab/ros2_bridge.py`
exposes the GPU simulation on ROS 2 topics through Isaac's
`isaacsim.ros2.bridge` OmniGraph extension: it publishes `/joint_states` and
`/clock` and subscribes to `/joint_command` (sensor_msgs/JointState). This was
verified end to end across two separate ROS 2 installations: the RoboStack env
receives all 12 Yertle joints on `/joint_states`, and commanding
`/joint_command` from RoboStack moves the joints in Isaac (thigh commanded to
-1.2 rad, tracked exactly). Two Windows notes, handled by the launcher: the
bridge needs `ROS_DISTRO=humble` and Isaac's bundled
`isaacsim.ros2.bridge\humble\lib` on `PATH` before startup, and the sim loop
must step with an app update (`sim.step(render=True)`) or the OmniGraph
publishers never tick.

## Build and run — Linux (Ubuntu, ROS 2 Humble/Jazzy)

```bash
# from a sourced ROS 2 workspace
mkdir -p ~/yertle_ws/src && cd ~/yertle_ws/src
ln -s /path/to/yertle/ros2/yertle_rl .
cd ~/yertle_ws
colcon build --packages-select yertle_rl
source install/setup.bash

# the node imports the repo's `learning` package; put the repo root on PYTHONPATH
PYTHONPATH=/path/to/yertle ros2 run yertle_rl policy_node \
    --ros-args -p policy_path:=/path/to/policy.zip
```

## Build and run — Windows (no WSL, via RoboStack)

```bat
:: install Miniforge, then create a ROS 2 env
conda create -y -n ros2 -c conda-forge -c robostack-staging ros-humble-ros-base colcon-common-extensions
conda run -n ros2 pip install pybullet gymnasium

:: build (keep outputs outside the repo)
cd yertle\ros2
conda run -n ros2 colcon build --base-paths . --build-base %USERPROFILE%\ros_ws\build --install-base %USERPROFILE%\ros_ws\install
```

Before building, set your maintainer email in `package.xml` and `setup.py`
(currently a placeholder). The node runs with no `policy_path` too, in which
case it outputs the standing pose (handy for a plumbing check).

## Wiring it to the robot

`/joint_commands` (target joint angles in radians) can be consumed by either:

* a `ros2_control` forward position controller in a Gazebo/RViz simulation, or
* a small relay that reuses `learning.deploy.servo_command_string` to forward
  the targets to the ESP32 firmware over UDP.

The IMU and joint feedback plumbing mirrors the sim-to-real notes in
[`learning/README.md`](../learning/README.md): base linear velocity is a
privileged term and is zero-filled on hardware.
