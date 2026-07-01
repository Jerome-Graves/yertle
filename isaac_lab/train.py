r"""Train the Yertle flat locomotion policy in Isaac Lab with rsl_rl (GPU).

Run from the repo root with the Isaac Sim python:

    set OMNI_KIT_ACCEPT_EULA=YES
    <isaac_venv>\Scripts\python.exe -m isaac_lab.train --headless --num_envs 4096 --max_iterations 500

Logs and checkpoints go to ``isaac_lab/runs/yertle_flat/<timestamp>``.
"""

import argparse
import os
import sys
from datetime import datetime, timezone

# IMPORTANT (Windows): import torch and rsl_rl (which pulls tensordict) BEFORE
# launching Isaac Sim. Kit and torch both bundle math/OpenMP runtimes; loading
# torch's first avoids a hard DLL-conflict crash when rsl_rl imports later.
import torch  # noqa: F401,E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Train Yertle locomotion in Isaac Lab (rsl_rl).")
parser.add_argument("--num_envs", type=int, default=4096)
parser.add_argument("--max_iterations", type=int, default=500)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch Isaac Sim first; everything below needs the running app.
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402

from isaaclab.utils.io import dump_yaml  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402

# Make the repo root importable so `import isaac_lab` works, then register tasks.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac_lab  # noqa: F401,E402  (registers the gym task)
from isaac_lab.flat_env_cfg import YertleFlatEnvCfg  # noqa: E402
from isaac_lab.rsl_rl_ppo_cfg import YertleFlatPPORunnerCfg  # noqa: E402

TASK = "Isaac-Velocity-Flat-Yertle-v0"


def main():
    env_cfg = YertleFlatEnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed

    agent_cfg = YertleFlatPPORunnerCfg()
    agent_cfg.max_iterations = args_cli.max_iterations
    agent_cfg.seed = args_cli.seed

    log_dir = os.path.join(
        os.path.dirname(__file__), "runs", agent_cfg.experiment_name,
        datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S"),
    )
    os.makedirs(log_dir, exist_ok=True)

    env = gym.make(TASK, cfg=env_cfg, render_mode=None)
    env = RslRlVecEnvWrapper(env, clip_actions=getattr(agent_cfg, "clip_actions", None))

    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    print(f"TRAIN_START task={TASK} num_envs={args_cli.num_envs} iters={args_cli.max_iterations}", flush=True)
    print(f"TRAIN_LOGDIR {log_dir}", flush=True)
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    print("TRAIN_DONE", flush=True)

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
