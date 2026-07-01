"""Isaac Lab locomotion task for the Yertle quadruped.

Importing this package registers the Gym task ids. It must be importable as the
top-level ``isaac_lab`` package, i.e. the repository root should be on
``sys.path`` (the provided train.py / play.py handle this).
"""

import gymnasium as gym

gym.register(
    id="Isaac-Velocity-Flat-Yertle-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.flat_env_cfg:YertleFlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.rsl_rl_ppo_cfg:YertleFlatPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Flat-Yertle-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.flat_env_cfg:YertleFlatEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{__name__}.rsl_rl_ppo_cfg:YertleFlatPPORunnerCfg",
    },
)
