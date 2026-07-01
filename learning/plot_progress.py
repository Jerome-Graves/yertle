"""Plot a training reward curve from a stable-baselines3 log.

Parses the console log written by ``train.py`` (the ``ep_rew_mean`` /
``total_timesteps`` rollout tables) and saves a reward-vs-steps PNG. Works on a
finished or an in-progress run, and needs nothing beyond the log file.

    python -m learning.plot_progress --log learning/runs/train_ppo_walk2.log \
        --output learning/media/reward_curve.png
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402

_ROW = re.compile(r"^\|\s*([a-zA-Z_/]+)\s*\|\s*(-?[\d.eE+]+)\s*\|")


def parse_log(log_path: str):
    """Return (timesteps, ep_rew_mean) point lists parsed from the log."""
    steps, rewards = [], []
    pending_reward = None
    for line in Path(log_path).read_text(errors="ignore").splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        try:
            fval = float(val)
        except ValueError:
            continue
        if key == "ep_rew_mean":
            pending_reward = fval
        elif key == "total_timesteps" and pending_reward is not None:
            steps.append(int(fval))
            rewards.append(pending_reward)
    return steps, rewards


def main():
    parser = argparse.ArgumentParser(description="Plot the PPO reward curve from a training log.")
    parser.add_argument("--log", type=str, default="learning/runs/train_ppo_walk2.log")
    parser.add_argument("--output", type=str, default="learning/media/reward_curve.png")
    parser.add_argument("--title", type=str, default="Yertle PPO locomotion: episode reward")
    args = parser.parse_args()

    steps, rewards = parse_log(args.log)
    if not steps:
        raise SystemExit(f"No rollout data found in {args.log} (has training logged a rollout yet?)")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.5))
    plt.plot(steps, rewards, linewidth=1.8)
    plt.xlabel("environment steps")
    plt.ylabel("mean episode reward")
    plt.title(args.title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out, dpi=120)
    print(f"parsed {len(steps)} points (last: {steps[-1]:,} steps, reward {rewards[-1]:.1f})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
