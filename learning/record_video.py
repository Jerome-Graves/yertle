"""Record a video of a trained Yertle policy walking.

Rolls out a checkpoint in the environment, captures rendered frames and writes
them to an mp4 (or gif). This produces the demo artifact for the README / a
portfolio.

    python -m learning.record_video --policy learning/runs/ppo_walk2/policy.zip \
        --output learning/media/yertle_walk.mp4 --seconds 8

Falls back to .gif automatically if ffmpeg is unavailable.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .yertle_env import YertleEnv, YertleEnvConfig


def record(policy_path: str, output: str, seconds: float, vx: float, fps: int,
           randomize: bool, deterministic: bool) -> str:
    import imageio
    from stable_baselines3 import PPO

    if not Path(policy_path).exists():
        raise FileNotFoundError(f"Policy not found: {policy_path}")

    env = YertleEnv(YertleEnvConfig(randomize=randomize), render_mode="rgb_array")
    model = PPO.load(policy_path, device="cpu")

    # Hold a fixed forward command so the clip shows steady walking.
    env._command = np.array([vx, 0.0, 0.0], dtype=np.float32)
    obs, _ = env.reset()
    env._command = np.array([vx, 0.0, 0.0], dtype=np.float32)

    n_steps = int(seconds / (env.cfg.sim_timestep * env.cfg.control_decimation))
    frames = []
    for _ in range(n_steps):
        action, _ = model.predict(obs, deterministic=deterministic)
        obs, _, terminated, truncated, _ = env.step(action)
        env._command = np.array([vx, 0.0, 0.0], dtype=np.float32)  # keep command fixed
        frames.append(env.render())
        if terminated or truncated:
            obs, _ = env.reset()
            env._command = np.array([vx, 0.0, 0.0], dtype=np.float32)
    env.close()

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        imageio.mimsave(str(out), frames, fps=fps)
    except Exception as exc:  # ffmpeg missing or codec issue -> gif fallback
        gif = out.with_suffix(".gif")
        print(f"mp4 write failed ({exc}); falling back to {gif}")
        imageio.mimsave(str(gif), frames, fps=fps)
        out = gif
    print(f"wrote {len(frames)} frames to {out}")
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="Record a video of a trained Yertle policy.")
    parser.add_argument("--policy", type=str, required=True)
    parser.add_argument("--output", type=str, default="learning/media/yertle_walk.mp4")
    parser.add_argument("--seconds", type=float, default=8.0)
    parser.add_argument("--vx", type=float, default=0.25, help="Fixed forward command (m/s).")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--no-randomize", action="store_true")
    parser.add_argument("--stochastic", action="store_true", help="Sample actions instead of the mean.")
    args = parser.parse_args()

    record(args.policy, args.output, args.seconds, args.vx, args.fps,
           randomize=not args.no_randomize, deterministic=not args.stochastic)


if __name__ == "__main__":
    main()
