"""Gymnasium environment for learned locomotion on the Yertle quadruped.

The environment loads the existing ``Simulation/yertle.URDF`` in PyBullet and
exposes a standard Gymnasium API so it can be trained with any off-the-shelf RL
library (stable-baselines3, CleanRL, RLlib, etc.).

Design notes
------------
* **Physics sanitation.** The shipped URDF was authored for visualisation, so
  its inertia tensors are not physically valid (e.g. equal diagonal and
  off-diagonal terms, or all-zero on the base). Left as-is the simulation
  diverges. On load we override every link's inertia with a stable isotropic
  estimate derived from its mass, and set foot friction. This is the modelling
  step that turns a display model into a trainable one.
* **Position control.** Actions are joint-angle *residuals* around a fixed
  standing pose, tracked by PyBullet's position controller. This mirrors the
  real robot, which is commanded with joint angles over WiFi/serial, and keeps
  the sim-to-real gap small.
* **Domain randomisation.** Base mass, foot friction, observation noise and
  random pushes are randomised per episode so a trained policy is more likely
  to survive transfer to the physical robot.

The observation intentionally includes a couple of privileged terms (base
linear velocity) that are cheap in simulation. For deployment these are either
estimated on-board or dropped; see ``learning/README.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError as exc:  # pragma: no cover - clearer error for new users
    raise ImportError(
        "gymnasium is required. Install the RL extras: "
        "pip install -r learning/requirements-rl.txt"
    ) from exc

import pybullet as p
import pybullet_data

# Repository layout: this file lives at <repo>/learning/yertle_env.py
REPO_ROOT = Path(__file__).resolve().parents[1]
URDF_PATH = REPO_ROOT / "Simulation" / "yertle.URDF"

# The 12 actuated joints, in a fixed policy order (leg, then segment).
LEG_PREFIXES = ("lf", "rf", "lb", "rb")
JOINT_SEGMENTS = ("shoulder", "thigh", "shin")
JOINT_NAMES = tuple(f"{leg}_{seg}" for leg in LEG_PREFIXES for seg in JOINT_SEGMENTS)

# Per-joint soft limits (radians), derived from the firmware servo limits in
# ``Software/ESP32/firmware/yertle_lib.h``. Order matches JOINT_SEGMENTS.
_DEG = np.pi / 180.0
SEGMENT_LIMITS = {
    "shoulder": (-45.0 * _DEG, 45.0 * _DEG),
    "thigh": (-90.0 * _DEG, 20.0 * _DEG),
    "shin": (13.0 * _DEG, 90.0 * _DEG),
}

# A neutral standing pose in URDF joint space (radians). Chosen so the feet sit
# below the body. Tunable; see scripts/tune_stance if the robot does not rest
# flat on your PyBullet version.
DEFAULT_STANCE = np.array(
    [0.0, -0.6, 0.9] * 4,  # [shoulder, thigh, shin] repeated for each leg
    dtype=np.float32,
)


@dataclass
class YertleEnvConfig:
    """Tunable parameters for :class:`YertleEnv`."""

    # Simulation / control timing
    sim_timestep: float = 1.0 / 240.0
    control_decimation: int = 4          # -> 60 Hz control
    episode_seconds: float = 12.0

    # Action
    action_scale: float = 0.4            # rad; residual added to DEFAULT_STANCE
    max_torque: float = 1.5              # N.m per servo (hobby servo scale)
    position_gain: float = 0.4

    # Command range (target base velocity): vx (m/s), vy (m/s), yaw (rad/s)
    command_x_range: tuple[float, float] = (0.0, 0.35)
    command_y_range: tuple[float, float] = (-0.1, 0.1)
    command_yaw_range: tuple[float, float] = (-0.5, 0.5)

    # Termination
    min_base_height: float = 0.08        # m
    max_tilt: float = 0.7                # rad from upright (~40 deg)

    # Reward weights
    w_lin_vel: float = 1.5
    w_yaw_vel: float = 0.5
    w_alive: float = 0.5
    w_energy: float = 2e-3
    w_action_rate: float = 0.01
    w_orientation: float = 0.5
    w_height: float = 0.5

    # Domain randomisation
    randomize: bool = True
    base_mass_range: tuple[float, float] = (0.85, 1.15)   # scale factor
    foot_friction_range: tuple[float, float] = (0.6, 1.2)
    obs_noise: float = 0.02
    push_interval_steps: int = 150       # 0 disables random pushes
    push_velocity: float = 0.25          # m/s impulse magnitude

    target_height: float = 0.18          # nominal standing height (m)
    seed: int | None = None


class YertleEnv(gym.Env):
    """PyBullet locomotion environment for the Yertle quadruped."""

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, config: YertleEnvConfig | None = None, render_mode: str | None = None):
        super().__init__()
        self.cfg = config or YertleEnvConfig()
        self.render_mode = render_mode

        if not URDF_PATH.exists():
            raise FileNotFoundError(f"Could not find robot model: {URDF_PATH}")

        self._connect()
        self._max_steps = int(self.cfg.episode_seconds / (self.cfg.sim_timestep * self.cfg.control_decimation))

        n_joints = len(JOINT_NAMES)
        self._joint_lower = np.array(
            [SEGMENT_LIMITS[seg][0] for _ in LEG_PREFIXES for seg in JOINT_SEGMENTS], dtype=np.float32
        )
        self._joint_upper = np.array(
            [SEGMENT_LIMITS[seg][1] for _ in LEG_PREFIXES for seg in JOINT_SEGMENTS], dtype=np.float32
        )

        # Action: residual per joint in [-1, 1], scaled by action_scale.
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(n_joints,), dtype=np.float32)

        # Observation: see module docstring. 48-dim.
        obs_dim = 3 + 3 + 3 + 3 + n_joints + n_joints + n_joints
        high = np.full(obs_dim, np.inf, dtype=np.float32)
        self.observation_space = spaces.Box(low=-high, high=high, dtype=np.float32)

        self._robot = None
        self._joint_indices: list[int] = []
        self._prev_action = np.zeros(n_joints, dtype=np.float32)
        self._command = np.zeros(3, dtype=np.float32)
        self._step_count = 0
        self._np_random = np.random.default_rng(self.cfg.seed)

    # ------------------------------------------------------------------ setup
    def _connect(self):
        if self.render_mode == "human":
            self._client = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        else:
            self._client = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    def _hard_reset_world(self):
        p.resetSimulation()
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(self.cfg.sim_timestep)
        self._plane = p.loadURDF("plane.urdf")

        friction = self._sample(self.cfg.foot_friction_range) if self.cfg.randomize else 0.9
        p.changeDynamics(self._plane, -1, lateralFriction=friction)

        # PyBullet resolves relative mesh paths against the URDF directory.
        self._robot = p.loadURDF(
            str(URDF_PATH),
            basePosition=[0, 0, self.cfg.target_height + 0.02],
            baseOrientation=p.getQuaternionFromEuler([0, 0, 0]),
            useFixedBase=False,
        )
        self._map_joints()
        self._sanitize_physics(friction)

    def _map_joints(self):
        name_to_index = {}
        for j in range(p.getNumJoints(self._robot)):
            info = p.getJointInfo(self._robot, j)
            name_to_index[info[1].decode("utf-8")] = j
        missing = [n for n in JOINT_NAMES if n not in name_to_index]
        if missing:
            raise RuntimeError(f"URDF is missing expected joints: {missing}")
        self._joint_indices = [name_to_index[n] for n in JOINT_NAMES]

    def _sanitize_physics(self, foot_friction: float):
        """Replace invalid URDF inertia with stable estimates; set friction.

        The shipped URDF has non-physical inertia tensors. We override each
        link with an isotropic diagonal inertia derived from its mass, which is
        numerically stable and good enough for locomotion learning.
        """
        base_mass_scale = self._sample(self.cfg.base_mass_range) if self.cfg.randomize else 1.0

        # Base link (index -1)
        base_mass = p.getDynamicsInfo(self._robot, -1)[0] * base_mass_scale
        p.changeDynamics(
            self._robot, -1,
            mass=max(base_mass, 0.1),
            localInertiaDiagonal=self._isotropic_inertia(base_mass, gyration=0.06),
        )

        for j in range(p.getNumJoints(self._robot)):
            mass = p.getDynamicsInfo(self._robot, j)[0]
            p.changeDynamics(
                self._robot, j,
                localInertiaDiagonal=self._isotropic_inertia(mass, gyration=0.02),
            )

        # Feet are the shin links; give them ground friction.
        for j in self._joint_indices:
            name = p.getJointInfo(self._robot, j)[1].decode("utf-8")
            if name.endswith("shin"):
                p.changeDynamics(self._robot, j, lateralFriction=foot_friction)

        # Disable PyBullet's default velocity motors so our position
        # controller has full authority.
        for j in self._joint_indices:
            p.setJointMotorControl2(self._robot, j, p.VELOCITY_CONTROL, force=0.0)

    @staticmethod
    def _isotropic_inertia(mass: float, gyration: float) -> list[float]:
        i = max(mass, 0.01) * gyration * gyration
        return [i, i, i]

    def _sample(self, rng_range: tuple[float, float]) -> float:
        return float(self._np_random.uniform(rng_range[0], rng_range[1]))

    # ------------------------------------------------------------------ gym API
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        if seed is not None:
            self._np_random = np.random.default_rng(seed)
        self._hard_reset_world()

        # Set the robot to the standing pose.
        for idx, joint in enumerate(self._joint_indices):
            p.resetJointState(self._robot, joint, float(DEFAULT_STANCE[idx]))
        self._hold_stance()

        # Sample a velocity command for this episode.
        self._command = np.array(
            [
                self._sample(self.cfg.command_x_range),
                self._sample(self.cfg.command_y_range),
                self._sample(self.cfg.command_yaw_range),
            ],
            dtype=np.float32,
        )
        self._prev_action = np.zeros(len(JOINT_NAMES), dtype=np.float32)
        self._step_count = 0
        return self._get_obs(), {}

    def _hold_stance(self):
        for idx, joint in enumerate(self._joint_indices):
            p.setJointMotorControl2(
                self._robot, joint, p.POSITION_CONTROL,
                targetPosition=float(DEFAULT_STANCE[idx]),
                force=self.cfg.max_torque, positionGain=self.cfg.position_gain,
            )

    def step(self, action: np.ndarray):
        action = np.clip(np.asarray(action, dtype=np.float32), -1.0, 1.0)
        targets = DEFAULT_STANCE + action * self.cfg.action_scale
        targets = np.clip(targets, self._joint_lower, self._joint_upper)

        for idx, joint in enumerate(self._joint_indices):
            p.setJointMotorControl2(
                self._robot, joint, p.POSITION_CONTROL,
                targetPosition=float(targets[idx]),
                force=self.cfg.max_torque, positionGain=self.cfg.position_gain,
            )

        self._maybe_push()
        for _ in range(self.cfg.control_decimation):
            p.stepSimulation()

        obs = self._get_obs()
        reward, terminated = self._reward_and_done(action)
        self._prev_action = action
        self._step_count += 1
        truncated = self._step_count >= self._max_steps
        return obs, reward, terminated, truncated, {"command": self._command.copy()}

    def _maybe_push(self):
        interval = self.cfg.push_interval_steps
        if not self.cfg.randomize or interval <= 0 or self._step_count == 0:
            return
        if self._step_count % interval == 0:
            v = self.cfg.push_velocity
            lin_vel, ang_vel = p.getBaseVelocity(self._robot)
            kick = self._np_random.uniform(-v, v, size=2)
            p.resetBaseVelocity(
                self._robot,
                linearVelocity=[lin_vel[0] + kick[0], lin_vel[1] + kick[1], lin_vel[2]],
                angularVelocity=ang_vel,
            )

    # ------------------------------------------------------------ observation
    def _base_state(self):
        pos, orn = p.getBasePositionAndOrientation(self._robot)
        lin_vel, ang_vel = p.getBaseVelocity(self._robot)
        rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)
        # Base velocities expressed in the base frame.
        lin_body = rot.T @ np.array(lin_vel)
        ang_body = rot.T @ np.array(ang_vel)
        gravity_body = rot.T @ np.array([0, 0, -1.0])  # projected gravity (IMU-like)
        return np.array(pos), lin_body, ang_body, gravity_body

    def _joint_state(self):
        states = p.getJointStates(self._robot, self._joint_indices)
        q = np.array([s[0] for s in states], dtype=np.float32)
        dq = np.array([s[1] for s in states], dtype=np.float32)
        return q, dq

    def _get_obs(self):
        _, lin_body, ang_body, gravity_body = self._base_state()
        q, dq = self._joint_state()
        obs = np.concatenate([
            lin_body.astype(np.float32),
            ang_body.astype(np.float32),
            gravity_body.astype(np.float32),
            self._command,
            (q - DEFAULT_STANCE).astype(np.float32),
            (dq * 0.1).astype(np.float32),
            self._prev_action,
        ]).astype(np.float32)

        if self.cfg.randomize and self.cfg.obs_noise > 0:
            obs = obs + self._np_random.normal(0, self.cfg.obs_noise, size=obs.shape).astype(np.float32)
        return obs

    # ----------------------------------------------------------------- reward
    def _reward_and_done(self, action: np.ndarray):
        pos, lin_body, ang_body, gravity_body = self._base_state()
        q, dq = self._joint_state()
        cfg = self.cfg

        # Velocity tracking (exp kernel).
        lin_err = np.sum((self._command[:2] - lin_body[:2]) ** 2)
        yaw_err = (self._command[2] - ang_body[2]) ** 2
        r_lin = cfg.w_lin_vel * np.exp(-lin_err / 0.25)
        r_yaw = cfg.w_yaw_vel * np.exp(-yaw_err / 0.25)

        # Penalties.
        r_energy = -cfg.w_energy * float(np.sum(np.abs(dq * action)))
        r_action_rate = -cfg.w_action_rate * float(np.sum((action - self._prev_action) ** 2))
        # gravity_body[2] is -1 when perfectly upright.
        r_orient = -cfg.w_orientation * float(gravity_body[0] ** 2 + gravity_body[1] ** 2)
        r_height = -cfg.w_height * float((pos[2] - cfg.target_height) ** 2)
        r_alive = cfg.w_alive

        reward = r_lin + r_yaw + r_alive + r_energy + r_action_rate + r_orient + r_height

        tilt = np.arccos(np.clip(-gravity_body[2], -1.0, 1.0))
        fell = (pos[2] < cfg.min_base_height) or (tilt > cfg.max_tilt)
        if fell:
            reward -= 5.0
        return float(reward), bool(fell)

    # ----------------------------------------------------------------- render
    def render(self):
        if self.render_mode == "rgb_array":
            width, height = 640, 480
            view = p.computeViewMatrixFromYawPitchRoll(
                cameraTargetPosition=p.getBasePositionAndOrientation(self._robot)[0],
                distance=0.6, yaw=50, pitch=-30, roll=0, upAxisIndex=2,
            )
            proj = p.computeProjectionMatrixFOV(60, width / height, 0.1, 100)
            _, _, rgb, _, _ = p.getCameraImage(width, height, view, proj)
            return np.reshape(rgb, (height, width, 4))[:, :, :3]
        return None

    def close(self):
        if getattr(self, "_client", None) is not None and p.isConnected(self._client):
            p.disconnect(self._client)
            self._client = None
