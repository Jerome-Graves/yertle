"""Rough-terrain velocity-tracking env for Yertle, on Isaac Lab.

Keeps Isaac Lab's terrain generator and height-scanner (unlike the flat env),
so the policy learns to walk over bumps and slopes. Terrain is scaled down for a
small (~20 cm leg) robot.
"""

from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

from .yertle_cfg import YERTLE_CFG

_BASE = "base_link"
_FEET = ".*_shin"


@configclass
class YertleRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # --- robot + height scanner attach point ---
        self.scene.robot = YERTLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/base_link"

        # --- scale the terrain down for a small robot ---
        tg = self.scene.terrain.terrain_generator
        if tg is not None:
            if "boxes" in tg.sub_terrains:
                tg.sub_terrains["boxes"].grid_height_range = (0.025, 0.1)
            if "random_rough" in tg.sub_terrains:
                tg.sub_terrains["random_rough"].noise_range = (0.01, 0.06)
                tg.sub_terrains["random_rough"].noise_step = 0.01

        # --- command ranges for a small robot ---
        self.commands.base_velocity.ranges.lin_vel_x = (-0.3, 0.5)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.2, 0.2)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)

        # --- action ---
        self.actions.joint_pos.scale = 0.25

        # --- events (body-name remap) ---
        self.events.add_base_mass.params["asset_cfg"].body_names = _BASE
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.3, 0.3)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = _BASE
        self.events.base_com = None
        self.events.push_robot = None
        self.events.reset_robot_joints.params["position_range"] = (0.8, 1.2)

        # --- rewards ---
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = _FEET
        self.rewards.feet_air_time.weight = 0.25
        self.rewards.undesired_contacts = None
        self.rewards.dof_torques_l2.weight = -0.0002
        self.rewards.track_lin_vel_xy_exp.weight = 1.5
        self.rewards.track_ang_vel_z_exp.weight = 0.75
        self.rewards.dof_acc_l2.weight = -2.5e-7

        # --- terminations ---
        self.terminations.base_contact.params["sensor_cfg"].body_names = _BASE


@configclass
class YertleRoughEnvCfg_PLAY(YertleRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False
