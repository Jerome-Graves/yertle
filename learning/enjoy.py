"""Watch (or record) a trained Yertle policy.

Examples
--------
Render in the PyBullet GUI::

    python -m learning.enjoy --policy learning/runs/ppo_yertle/policy.zip

Run headless and just print the achieved velocity (useful over SSH)::

    python -m learning.enjoy --policy <path> --no-render --episodes 5
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from .yertle_env import YertleEnv, YertleEnvConfig


def main():
    parser = argparse.ArgumentParser(description="Roll out a trained Yertle policy.")
    parser.add_argument("--policy", type=str, required=True, help="Path to a saved PPO .zip")
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--no-randomize", action="store_true")
    args = parser.parse_args()

    if not Path(args.policy).exists():
        raise FileNotFoundError(f"Policy not found: {args.policy}")

    from stable_baselines3 import PPO

    render_mode = None if args.no_render else "human"
    env = YertleEnv(YertleEnvConfig(randomize=not args.no_randomize), render_mode=render_mode)
    model = PPO.load(args.policy, device="cpu")

    control_dt = env.cfg.sim_timestep * env.cfg.control_decimation
    for ep in range(args.episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0.0
        vx_samples = []
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            vx_samples.append(obs[0])  # base forward velocity (body frame)
            done = terminated or truncated
            if render_mode == "human":
                time.sleep(control_dt)
        cmd = info["command"]
        print(
            f"episode {ep + 1}: reward={total_reward:7.1f}  "
            f"cmd_vx={cmd[0]:.2f}  mean_vx={np.mean(vx_samples):.2f} m/s"
        )
    env.close()


if __name__ == "__main__":
    main()
