"""Sim-to-real deployment bridge for a trained Yertle policy.

This module runs a trained locomotion policy at the control rate and turns its
output into joint-angle commands for the robot. The important pieces are
framework-agnostic and unit-tested in simulation, so the same core drives both
the PyBullet closed-loop check here and the ROS 2 node in ``ros2/``.

Pipeline
--------
    sensors  ->  ObservationBuilder  ->  policy  ->  joint targets (rad)
                                                  ->  servo command string  ->  robot

Observation layout matches ``YertleEnv`` exactly (48-dim):
    [ base_lin_vel(3), base_ang_vel(3), projected_gravity(3),
      command(3), (q - stance)(12), 0.1*dq(12), prev_action(12) ]

The real robot cannot measure everything the simulator can (base linear
velocity, and joint velocity feedback from open-loop servos). Those terms are
estimated or zero-filled in :class:`UdpRobotInterface`; see the notes there and
in ``learning/README.md``. This is the honest sim-to-real gap and the reason a
deployment-ready policy is usually retrained without the privileged terms.

Usage
-----
Validate the whole bridge in simulation (no hardware, no robot policy needed)::

    python -m learning.deploy --check

Drive the PyBullet robot with a trained policy::

    python -m learning.deploy --policy learning/runs/ppo_yertle/policy.zip --sim

Drive the real robot over WiFi (needs the ESP32 running its firmware)::

    python -m learning.deploy --policy <path> --udp --robot-ip 10.0.0.88
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from .yertle_env import DEFAULT_STANCE, JOINT_NAMES, YertleEnvConfig

OBS_DIM = 48
N_JOINTS = len(JOINT_NAMES)


# --------------------------------------------------------------------- sensors
@dataclass
class RobotSensors:
    """Everything the observation needs, in SI units / radians.

    Fields the physical robot cannot supply should be left at their defaults
    (zeros); the observation builder will pass them through unchanged.
    """

    base_lin_vel: np.ndarray = field(default_factory=lambda: np.zeros(3, np.float32))   # body frame, m/s
    base_ang_vel: np.ndarray = field(default_factory=lambda: np.zeros(3, np.float32))   # body frame, rad/s
    projected_gravity: np.ndarray = field(default_factory=lambda: np.array([0, 0, -1], np.float32))
    joint_pos: np.ndarray = field(default_factory=lambda: DEFAULT_STANCE.copy())        # rad
    joint_vel: np.ndarray = field(default_factory=lambda: np.zeros(N_JOINTS, np.float32))  # rad/s


def projected_gravity_from_rpy(roll: float, pitch: float) -> np.ndarray:
    """Gravity direction in the base frame from roll/pitch (radians).

    Matches ``rot.T @ [0, 0, -1]`` used in the environment, so an IMU that
    reports orientation is enough to reconstruct this observation term.
    """
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    return np.array([sp, -sr * cp, -cr * cp], dtype=np.float32)


class ObservationBuilder:
    """Assembles the 48-dim policy observation. Mirrors ``YertleEnv._get_obs``."""

    def __init__(self, stance: np.ndarray | None = None):
        self.stance = DEFAULT_STANCE if stance is None else np.asarray(stance, np.float32)

    def build(self, sensors: RobotSensors, command: np.ndarray, prev_action: np.ndarray) -> np.ndarray:
        obs = np.concatenate([
            np.asarray(sensors.base_lin_vel, np.float32),
            np.asarray(sensors.base_ang_vel, np.float32),
            np.asarray(sensors.projected_gravity, np.float32),
            np.asarray(command, np.float32),
            (np.asarray(sensors.joint_pos, np.float32) - self.stance),
            0.1 * np.asarray(sensors.joint_vel, np.float32),
            np.asarray(prev_action, np.float32),
        ]).astype(np.float32)
        assert obs.shape == (OBS_DIM,), f"observation is {obs.shape}, expected ({OBS_DIM},)"
        return obs


# ---------------------------------------------------------------------- policy
class Policy(Protocol):
    """Anything with a stable-baselines3-style predict() works here."""

    def predict(self, obs, deterministic: bool = ...): ...


class ZeroPolicy:
    """Stub policy that always outputs the standing pose. Used for the
    self-check and as a safe default when no checkpoint is provided."""

    def predict(self, obs, deterministic: bool = True):
        return np.zeros(N_JOINTS, dtype=np.float32), None


class PolicyController:
    """Stateful controller: sensors + command -> joint targets (radians)."""

    def __init__(self, policy: Policy, action_scale: float, joint_lower, joint_upper,
                 stance: np.ndarray | None = None):
        self.policy = policy
        self.action_scale = action_scale
        self.joint_lower = np.asarray(joint_lower, np.float32)
        self.joint_upper = np.asarray(joint_upper, np.float32)
        self.stance = DEFAULT_STANCE if stance is None else np.asarray(stance, np.float32)
        self.obs_builder = ObservationBuilder(self.stance)
        self.prev_action = np.zeros(N_JOINTS, dtype=np.float32)

    def reset(self):
        self.prev_action = np.zeros(N_JOINTS, dtype=np.float32)

    def act(self, sensors: RobotSensors, command: np.ndarray) -> np.ndarray:
        obs = self.obs_builder.build(sensors, command, self.prev_action)
        action, _ = self.policy.predict(obs, deterministic=True)
        action = np.clip(np.asarray(action, np.float32), -1.0, 1.0)
        self.prev_action = action
        targets = self.stance + action * self.action_scale
        return np.clip(targets, self.joint_lower, self.joint_upper).astype(np.float32)

    @classmethod
    def from_checkpoint(cls, policy_path: str | None, cfg: YertleEnvConfig, joint_lower, joint_upper):
        if policy_path is None:
            policy = ZeroPolicy()
        else:
            from stable_baselines3 import PPO
            policy = PPO.load(policy_path, device="cpu")
        return cls(policy, cfg.action_scale, joint_lower, joint_upper)


# ------------------------------------------------------------- command encoding
@dataclass
class JointMapping:
    """Maps policy joint targets (URDF radians) to firmware servo angles (deg).

    The firmware ``a`` command expects 12 angles in servo-logical degrees, in
    the order lf/rf/lb/rb x (theta1, theta2, theta3), which is the same order as
    ``JOINT_NAMES``. Per-joint ``sign`` and ``offset_deg`` let you calibrate the
    axis convention against the real servos. Physical zero trimming already
    lives in ``servoOffsets`` in ``yertle_lib.h``; this only aligns direction.
    Defaults are identity: verify each joint direction on the bench before use.
    """

    sign: np.ndarray = field(default_factory=lambda: np.ones(N_JOINTS, np.float32))
    offset_deg: np.ndarray = field(default_factory=lambda: np.zeros(N_JOINTS, np.float32))

    def to_servo_degrees(self, targets_rad: np.ndarray) -> np.ndarray:
        return self.sign * np.degrees(np.asarray(targets_rad, np.float32)) + self.offset_deg


def servo_command_string(targets_rad: np.ndarray, mapping: JointMapping | None = None) -> str:
    """Encode joint targets into a firmware ``a`` command line."""
    mapping = mapping or JointMapping()
    degs = mapping.to_servo_degrees(targets_rad)
    return "a " + " ".join(f"{d:.2f}" for d in degs) + "\n"


# ------------------------------------------------------------- robot interfaces
class RobotInterface(Protocol):
    def read(self) -> RobotSensors: ...
    def apply(self, targets_rad: np.ndarray) -> None: ...
    def close(self) -> None: ...


class SimRobotInterface:
    """Closes the loop in PyBullet, reusing YertleEnv's physics setup.

    This lets us validate the controller + observation builder against the same
    dynamics the policy trained on, with no hardware.
    """

    def __init__(self, render: bool = False):
        from .yertle_env import YertleEnv
        self.env = YertleEnv(YertleEnvConfig(randomize=False), render_mode="human" if render else None)
        self.env.reset()
        self._pb = __import__("pybullet")

    def read(self) -> RobotSensors:
        _, lin_body, ang_body, gravity_body = self.env._base_state()
        q, dq = self.env._joint_state()
        return RobotSensors(
            base_lin_vel=lin_body.astype(np.float32),
            base_ang_vel=ang_body.astype(np.float32),
            projected_gravity=gravity_body.astype(np.float32),
            joint_pos=q, joint_vel=dq,
        )

    def apply(self, targets_rad: np.ndarray) -> None:
        p = self._pb
        for idx, joint in enumerate(self.env._joint_indices):
            p.setJointMotorControl2(
                self.env._robot, joint, p.POSITION_CONTROL,
                targetPosition=float(targets_rad[idx]),
                force=self.env.cfg.max_torque, positionGain=self.env.cfg.position_gain,
            )
        for _ in range(self.env.cfg.control_decimation):
            p.stepSimulation()

    def close(self) -> None:
        self.env.close()


class UdpRobotInterface:
    """Talks to the ESP32 firmware over UDP.

    Sends ``a`` joint commands to the robot and reads its telemetry. The current
    firmware streams orientation (``r`` = yaw/pitch/roll) but not linear
    velocity or joint feedback, so:

      * projected_gravity is reconstructed from roll/pitch,
      * base_ang_vel is finite-differenced from orientation,
      * base_lin_vel is zero-filled (privileged term; drop-and-retrain for a
        production policy),
      * joint_pos/joint_vel fall back to the last commanded targets.

    This interface is provided for on-robot use; it is not exercised by the
    simulation self-check.
    """

    def __init__(self, robot_ip: str, robot_port: int = 24321, listen_ip: str = "0.0.0.0",
                 listen_port: int = 1234, mapping: JointMapping | None = None):
        import socket
        self.mapping = mapping or JointMapping()
        self.addr = (robot_ip, robot_port)
        self._tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rx.bind((listen_ip, listen_port))
        self._rx.setblocking(False)
        self._last_targets = DEFAULT_STANCE.copy()
        self._prev_rpy = np.zeros(3, np.float32)
        self._last_t = time.time()

    def read(self) -> RobotSensors:
        import socket  # noqa: F401  (kept for clarity of dependency)
        roll = pitch = 0.0
        try:
            while True:
                data, _ = self._rx.recvfrom(1024)
                parts = data.decode(errors="ignore").split()
                if parts and parts[0] == "r" and len(parts) >= 4:
                    # firmware sends r yaw pitch roll (degrees)
                    pitch = math.radians(float(parts[2]))
                    roll = math.radians(float(parts[3]))
        except (BlockingIOError, ValueError):
            pass
        now = time.time()
        dt = max(now - self._last_t, 1e-3)
        rpy = np.array([0.0, pitch, roll], np.float32)
        ang_vel = (rpy - self._prev_rpy) / dt
        self._prev_rpy, self._last_t = rpy, now
        return RobotSensors(
            base_lin_vel=np.zeros(3, np.float32),
            base_ang_vel=ang_vel,
            projected_gravity=projected_gravity_from_rpy(roll, pitch),
            joint_pos=self._last_targets.copy(),
            joint_vel=np.zeros(N_JOINTS, np.float32),
        )

    def apply(self, targets_rad: np.ndarray) -> None:
        self._last_targets = np.asarray(targets_rad, np.float32)
        msg = servo_command_string(targets_rad, self.mapping)
        self._tx.sendto(msg.encode(), self.addr)

    def close(self) -> None:
        self._tx.close()
        self._rx.close()


# --------------------------------------------------------------------- runners
def _joint_limits(cfg: YertleEnvConfig):
    """Recreate the env's per-joint limits without spinning up a simulator."""
    from .yertle_env import SEGMENT_LIMITS, LEG_PREFIXES, JOINT_SEGMENTS
    lower = np.array([SEGMENT_LIMITS[s][0] for _ in LEG_PREFIXES for s in JOINT_SEGMENTS], np.float32)
    upper = np.array([SEGMENT_LIMITS[s][1] for _ in LEG_PREFIXES for s in JOINT_SEGMENTS], np.float32)
    return lower, upper


def run(interface: RobotInterface, controller: PolicyController, command, seconds: float,
        control_hz: float, realtime: bool = False):
    controller.reset()
    command = np.asarray(command, np.float32)
    dt = 1.0 / control_hz
    n_steps = int(seconds * control_hz)
    for _ in range(n_steps):
        sensors = interface.read()
        targets = controller.act(sensors, command)
        interface.apply(targets)
        if realtime:
            time.sleep(dt)


def self_check():
    """Run the bridge closed-loop in sim with a stub policy. No hardware, no
    trained model. Verifies observation shape, command encoding and that the
    robot stays upright while standing."""
    cfg = YertleEnvConfig(randomize=False)
    lower, upper = _joint_limits(cfg)

    # 1. Observation builder produces the right shape.
    builder = ObservationBuilder()
    obs = builder.build(RobotSensors(), np.zeros(3), np.zeros(N_JOINTS))
    assert obs.shape == (OBS_DIM,)

    # 2. Command string round-trips through the firmware's parser logic.
    targets = DEFAULT_STANCE.copy()
    cmd = servo_command_string(targets)
    parts = cmd.split()
    assert parts[0] == "a" and len(parts) == 1 + N_JOINTS
    decoded = np.array([float(x) for x in parts[1:]], np.float32)
    assert np.allclose(decoded, np.degrees(targets), atol=0.01)

    # 3. Closed-loop in PyBullet with the standing stub policy stays upright.
    controller = PolicyController(ZeroPolicy(), cfg.action_scale, lower, upper)
    sim = SimRobotInterface(render=False)
    controller.reset()
    heights = []
    for _ in range(180):  # 3 s at 60 Hz
        sensors = sim.read()
        targets = controller.act(sensors, np.array([0.2, 0.0, 0.0], np.float32))
        sim.apply(targets)
        heights.append(sensors.projected_gravity[2])
    tilt = math.degrees(math.acos(min(max(-float(np.mean(heights[-30:])), -1.0), 1.0)))
    sim.close()
    assert tilt < 20.0, f"robot not upright in closed loop (tilt {tilt:.1f} deg)"
    print(f"self-check OK: obs_dim={OBS_DIM}, command round-trip OK, "
          f"closed-loop stance tilt={tilt:.1f} deg")


def main():
    parser = argparse.ArgumentParser(description="Deploy a Yertle policy (sim or real robot).")
    parser.add_argument("--policy", type=str, default=None, help="Path to a trained PPO .zip")
    parser.add_argument("--check", action="store_true", help="Run the sim self-check and exit.")
    parser.add_argument("--sim", action="store_true", help="Drive the PyBullet robot (GUI).")
    parser.add_argument("--udp", action="store_true", help="Drive the real robot over UDP.")
    parser.add_argument("--robot-ip", type=str, default="10.0.0.88")
    parser.add_argument("--vx", type=float, default=0.2, help="Commanded forward velocity (m/s).")
    parser.add_argument("--seconds", type=float, default=15.0)
    args = parser.parse_args()

    if args.check:
        self_check()
        return

    cfg = YertleEnvConfig(randomize=False)
    lower, upper = _joint_limits(cfg)
    controller = PolicyController.from_checkpoint(args.policy, cfg, lower, upper)
    control_hz = 1.0 / (cfg.sim_timestep * cfg.control_decimation)
    command = np.array([args.vx, 0.0, 0.0], np.float32)

    if args.udp:
        interface: RobotInterface = UdpRobotInterface(args.robot_ip)
        realtime = True
    else:
        interface = SimRobotInterface(render=args.sim)
        realtime = args.sim

    try:
        run(interface, controller, command, args.seconds, control_hz, realtime=realtime)
    finally:
        interface.close()
    print("done")


if __name__ == "__main__":
    main()
