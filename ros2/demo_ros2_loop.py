"""Closed-loop ROS 2 demo: a policy drives a simulated Yertle over ROS topics.

A PyBullet simulation node publishes ``/joint_states`` and ``/imu/data`` and
applies ``/joint_commands``. The trained-policy node (``yertle_rl.policy_node``)
consumes those, tracks a ``/cmd_vel`` command, and publishes joint commands. The
whole control loop therefore runs over real ROS 2 topics.

Run in the RoboStack ROS 2 env (needs stable-baselines3 to load the policy):

    conda run -n ros2 python ros2/demo_ros2_loop.py --policy learning/runs/ppo_walk2/policy.zip

With no --policy it uses the standing stub (still exercises the full loop).
"""

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))                       # learning.*
sys.path.insert(0, str(REPO / "ros2" / "yertle_rl"))  # yertle_rl.*

import rclpy  # noqa: E402
from rclpy.executors import SingleThreadedExecutor  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from std_msgs.msg import Float64MultiArray  # noqa: E402
from sensor_msgs.msg import Imu, JointState  # noqa: E402
from geometry_msgs.msg import Twist  # noqa: E402

import pybullet as p  # noqa: E402
from yertle_rl.policy_node import PolicyNode  # noqa: E402
from learning.deploy import SimRobotInterface  # noqa: E402
from learning.yertle_env import JOINT_NAMES, DEFAULT_STANCE  # noqa: E402


class SimNode(Node):
    """PyBullet Yertle exposed over ROS 2 topics."""

    def __init__(self):
        super().__init__("yertle_sim")
        self.iface = SimRobotInterface(render=False)
        self.env = self.iface.env
        self._targets = DEFAULT_STANCE.copy()
        self.create_subscription(Float64MultiArray, "joint_commands", self._on_cmd, 10)
        self.js_pub = self.create_publisher(JointState, "joint_states", 10)
        self.imu_pub = self.create_publisher(Imu, "imu/data", 10)
        self.start_xy = np.array(p.getBasePositionAndOrientation(self.env._robot)[0][:2])
        self.create_timer(1.0 / 60.0, self._tick)

    def _on_cmd(self, msg):
        if len(msg.data) >= 12:
            self._targets = np.array(msg.data[:12], np.float32)

    def _tick(self):
        self.iface.apply(self._targets)  # apply targets + step the sim

        q, dq = self.env._joint_state()
        js = JointState()
        js.name = list(JOINT_NAMES)
        js.position = [float(x) for x in q]
        js.velocity = [float(x) for x in dq]
        self.js_pub.publish(js)

        _, orn = p.getBasePositionAndOrientation(self.env._robot)
        _, ang = p.getBaseVelocity(self.env._robot)
        im = Imu()
        im.orientation.x, im.orientation.y, im.orientation.z, im.orientation.w = [float(v) for v in orn]
        im.angular_velocity.x, im.angular_velocity.y, im.angular_velocity.z = [float(v) for v in ang]
        self.imu_pub.publish(im)

    def base_travel(self):
        xy = np.array(p.getBasePositionAndOrientation(self.env._robot)[0][:2])
        return float(np.linalg.norm(xy - self.start_xy))


class CmdNode(Node):
    def __init__(self, vx):
        super().__init__("yertle_cmd")
        self.vx = vx
        self.pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_timer(0.1, self._tick)

    def _tick(self):
        t = Twist()
        t.linear.x = self.vx
        self.pub.publish(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", type=str, default=None)
    ap.add_argument("--vx", type=float, default=0.25)
    ap.add_argument("--seconds", type=float, default=8.0)
    args = ap.parse_args()

    rclpy.init()
    overrides = []
    if args.policy:
        overrides.append(Parameter("policy_path", Parameter.Type.STRING, args.policy))
    policy = PolicyNode(parameter_overrides=overrides)
    sim = SimNode()
    cmd = CmdNode(args.vx)

    exe = SingleThreadedExecutor()
    for n in (policy, sim, cmd):
        exe.add_node(n)

    print("DEMO_START policy=%s vx=%.2f" % (args.policy or "(stub)", args.vx), flush=True)
    deadline = time.time() + args.seconds
    while time.time() < deadline:
        exe.spin_once(timeout_sec=0.05)

    travel = sim.base_travel()
    print("DEMO_BASE_TRAVEL_M %.3f" % travel, flush=True)
    print("DEMO_OK" if travel > 0.05 else "DEMO_LOOP_RAN_BUT_LITTLE_MOTION", flush=True)

    for n in (policy, sim, cmd):
        n.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
