"""ROS 2 node that runs a trained Yertle locomotion policy.

This is a thin wrapper around the tested controller core in
``learning/deploy.py``: the node handles ROS plumbing (subscriptions, a control
timer, publishing joint targets) and delegates the actual observation building
and policy inference to :class:`~learning.deploy.PolicyController`, which is
exercised by the simulation self-check. Keeping the substance in the shared core
means the logic is validated even though ROS 2 itself is not run in CI here.

Topics
------
Subscribes
    /cmd_vel      geometry_msgs/Twist       desired body velocity (x, y, yaw)
    /imu/data     sensor_msgs/Imu           orientation + angular velocity
    /joint_states sensor_msgs/JointState    (optional) joint feedback
Publishes
    /joint_commands  std_msgs/Float64MultiArray   12 joint targets (radians)

Run
---
    ros2 run yertle_rl policy_node --ros-args -p policy_path:=/abs/path/policy.zip
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Make the repository's `learning` package importable when this node runs from
# an installed ROS 2 workspace.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from learning.deploy import PolicyController, RobotSensors, N_JOINTS, _joint_limits  # noqa: E402
from learning.yertle_env import YertleEnvConfig, DEFAULT_STANCE  # noqa: E402

import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from std_msgs.msg import Float64MultiArray  # noqa: E402
from sensor_msgs.msg import Imu, JointState  # noqa: E402
from geometry_msgs.msg import Twist  # noqa: E402


def _projected_gravity_from_quaternion(x: float, y: float, z: float, w: float) -> np.ndarray:
    """Gravity direction in the base frame: R^T @ [0, 0, -1]."""
    # Rotation matrix (body -> world) from a unit quaternion.
    r = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w),     2 * (x * z + y * w)],
        [2 * (x * y + z * w),     1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w),     2 * (y * z + x * w),     1 - 2 * (x * x + y * y)],
    ], dtype=np.float32)
    return r.T @ np.array([0, 0, -1], dtype=np.float32)


class PolicyNode(Node):
    def __init__(self):
        super().__init__("yertle_policy")

        self.declare_parameter("policy_path", "")
        self.declare_parameter("control_hz", 60.0)

        policy_path = self.get_parameter("policy_path").get_parameter_value().string_value or None
        self.control_hz = self.get_parameter("control_hz").get_parameter_value().double_value

        cfg = YertleEnvConfig(randomize=False)
        lower, upper = _joint_limits(cfg)
        self.controller = PolicyController.from_checkpoint(policy_path, cfg, lower, upper)
        self.controller.reset()

        self._command = np.zeros(3, dtype=np.float32)
        self._sensors = RobotSensors()
        self._joint_names = None

        self.create_subscription(Twist, "cmd_vel", self._on_cmd_vel, 10)
        self.create_subscription(Imu, "imu/data", self._on_imu, 10)
        self.create_subscription(JointState, "joint_states", self._on_joint_states, 10)
        self._pub = self.create_publisher(Float64MultiArray, "joint_commands", 10)

        self.create_timer(1.0 / self.control_hz, self._on_control_tick)
        self.get_logger().info(
            f"yertle_policy up: policy={'(standing stub)' if not policy_path else policy_path}, "
            f"control_hz={self.control_hz}"
        )

    # --------------------------------------------------------------- callbacks
    def _on_cmd_vel(self, msg: Twist):
        self._command = np.array([msg.linear.x, msg.linear.y, msg.angular.z], dtype=np.float32)

    def _on_imu(self, msg: Imu):
        q = msg.orientation
        self._sensors.projected_gravity = _projected_gravity_from_quaternion(q.x, q.y, q.z, q.w)
        w = msg.angular_velocity
        self._sensors.base_ang_vel = np.array([w.x, w.y, w.z], dtype=np.float32)

    def _on_joint_states(self, msg: JointState):
        if len(msg.position) >= N_JOINTS:
            self._sensors.joint_pos = np.array(msg.position[:N_JOINTS], dtype=np.float32)
        if len(msg.velocity) >= N_JOINTS:
            self._sensors.joint_vel = np.array(msg.velocity[:N_JOINTS], dtype=np.float32)

    def _on_control_tick(self):
        targets = self.controller.act(self._sensors, self._command)
        out = Float64MultiArray()
        out.data = [float(v) for v in targets]
        self._pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = PolicyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
