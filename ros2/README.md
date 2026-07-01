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
