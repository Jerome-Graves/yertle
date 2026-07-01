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

## Build and run

This package needs a ROS 2 environment (tested target: Humble / Jazzy on Ubuntu).
It is not built in this repository's CI because that runs on Windows without ROS.

```bash
# from a sourced ROS 2 workspace
mkdir -p ~/yertle_ws/src && cd ~/yertle_ws/src
ln -s /path/to/yertle/ros2/yertle_rl .
cd ~/yertle_ws
colcon build --packages-select yertle_rl
source install/setup.bash

ros2 run yertle_rl policy_node --ros-args -p policy_path:=/path/to/policy.zip
```

Before building, set your maintainer email in `package.xml` and `setup.py`
(currently a placeholder).

## Wiring it to the robot

`/joint_commands` (target joint angles in radians) can be consumed by either:

* a `ros2_control` forward position controller in a Gazebo/RViz simulation, or
* a small relay that reuses `learning.deploy.servo_command_string` to forward
  the targets to the ESP32 firmware over UDP.

The IMU and joint feedback plumbing mirrors the sim-to-real notes in
[`learning/README.md`](../learning/README.md): base linear velocity is a
privileged term and is zero-filled on hardware.
