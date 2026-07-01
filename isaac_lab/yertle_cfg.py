"""Isaac Lab articulation config for the Yertle quadruped.

Spawns the USD converted from ``Simulation/yertle.URDF`` and defines the leg
actuators. Modelled on Isaac Lab's small-quadruped configs (Unitree A1/Go2).
"""

from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

# The USD produced by scripts/tools/convert_urdf.py (see isaac_lab/README.md).
_USD_PATH = str(Path(__file__).resolve().parents[1] / "Simulation" / "usd" / "yertle.usd")

YERTLE_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=_USD_PATH,
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.25),
        joint_pos={
            # Standing pose (radians), carried over from the PyBullet env.
            ".*_shoulder": 0.0,
            ".*_thigh": -0.6,
            ".*_shin": 0.9,
        },
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "legs": ImplicitActuatorCfg(
            joint_names_expr=[".*_shoulder", ".*_thigh", ".*_shin"],
            effort_limit=3.0,      # N.m, hobby-servo scale (matches PyBullet env)
            velocity_limit=10.0,
            stiffness=25.0,
            damping=0.5,
        ),
    },
)
