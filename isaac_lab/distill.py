r"""Distill the trained (privileged) Yertle teacher into a deployable student.

The teacher is a flat PPO checkpoint (full observations, including privileged
base linear velocity). The student learns to imitate it from the deployable
``student`` observation group only (no base linear velocity, no height scan).

    set OMNI_KIT_ACCEPT_EULA=YES
    <isaac_venv>\Scripts\python.exe isaac_lab\distill.py --headless ^
        --teacher isaac_lab\runs\yertle_flat\<run>\model_1499.pt
"""

import argparse
import os
import sys
from datetime import datetime, timezone

# Windows DLL-order fix: import torch/rsl_rl before launching Isaac Sim.
import torch  # noqa: F401
from rsl_rl.runners import DistillationRunner  # noqa: E402

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Teacher-student distillation for Yertle.")
parser.add_argument("--teacher", type=str, required=True, help="Path to the trained flat PPO model_*.pt")
parser.add_argument("--num_envs", type=int, default=4096)
parser.add_argument("--max_iterations", type=int, default=300)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402

from isaaclab.utils.io import dump_yaml  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac_lab  # noqa: F401,E402  (registers tasks)
from isaac_lab.distill_env_cfg import YertleFlatDistillEnvCfg  # noqa: E402
from isaac_lab.rsl_rl_distill_cfg import YertleFlatDistillationRunnerCfg  # noqa: E402

TASK = "Isaac-Velocity-Flat-Yertle-Distill-v0"


def main():
    env_cfg = YertleFlatDistillEnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed

    agent_cfg = YertleFlatDistillationRunnerCfg()
    agent_cfg.max_iterations = args_cli.max_iterations
    agent_cfg.seed = args_cli.seed

    log_dir = os.path.join(
        os.path.dirname(__file__), "runs", agent_cfg.experiment_name,
        datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S"),
    )
    os.makedirs(log_dir, exist_ok=True)

    env = gym.make(TASK, cfg=env_cfg, render_mode=None)
    env = RslRlVecEnvWrapper(env, clip_actions=getattr(agent_cfg, "clip_actions", None))

    runner = DistillationRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    # Load the trained PPO policy as the (frozen) teacher.
    runner.load(args_cli.teacher, load_optimizer=False)
    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    print(f"DISTILL_START teacher={args_cli.teacher} num_envs={args_cli.num_envs}", flush=True)
    print(f"DISTILL_LOGDIR {log_dir}", flush=True)
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    print("DISTILL_DONE", flush=True)

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
