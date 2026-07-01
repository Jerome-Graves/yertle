"""Flat-terrain velocity-tracking env for Yertle, on Isaac Lab.

Inherits Isaac Lab's proven locomotion-velocity task (the one that trains
ANYmal/Go2 to walk) and swaps in the Yertle robot, remapping body names to
Yertle's (base_link, feet = ``*_shin``) and tuning for a small robot.
"""

import math

from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

from .yertle_cfg import YERTLE_CFG

_BASE = "base_link"
_FEET = ".*_shin"


@configclass
class YertleFlatEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # --- robot ---
        self.scene.robot = YERTLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # --- flat terrain (no rough terrain, no height scanner) ---
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.curriculum.terrain_levels = None

        # --- command ranges: Yertle has ~20 cm legs, so slower than a Go2 ---
        self.commands.base_velocity.ranges.lin_vel_x = (-0.3, 0.5)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.2, 0.2)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
        self.commands.base_velocity.ranges.heading = (-math.pi, math.pi)

        # --- action ---
        self.actions.joint_pos.scale = 0.25

        # --- events (body-name remap to Yertle) ---
        self.events.add_base_mass.params["asset_cfg"].body_names = _BASE
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.3, 0.3)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = _BASE
        self.events.base_com = None
        self.events.push_robot = None
        self.events.reset_robot_joints.params["position_range"] = (0.8, 1.2)
        self.events.reset_base.params = {
            "pose_range": {"x": (-0.3, 0.3), "y": (-0.3, 0.3), "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0),
                "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0),
            },
        }

        # --- rewards (body-name remap + small-robot tuning) ---
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = _FEET
        self.rewards.feet_air_time.weight = 0.25
        self.rewards.undesired_contacts = None
        self.rewards.flat_orientation_l2.weight = -2.5
        self.rewards.dof_torques_l2.weight = -0.0002
        self.rewards.track_lin_vel_xy_exp.weight = 1.5
        self.rewards.track_ang_vel_z_exp.weight = 0.75
        self.rewards.dof_acc_l2.weight = -2.5e-7

        # --- terminations ---
        self.terminations.base_contact.params["sensor_cfg"].body_names = _BASE


@configclass
class YertleFlatEnvCfg_PLAY(YertleFlatEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
