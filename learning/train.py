"""Train a locomotion policy for Yertle with PPO (stable-baselines3).

Examples
--------
Quick smoke test (a few thousand steps, CPU, seconds)::

    python -m learning.train --timesteps 5000 --n-envs 2

A real training run::

    python -m learning.train --timesteps 3_000_000 --n-envs 8

Checkpoints and TensorBoard logs are written to ``learning/runs/``. Watch a
trained policy with ``python -m learning.enjoy``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .yertle_env import YertleEnv, YertleEnvConfig

RUNS_DIR = Path(__file__).resolve().parent / "runs"


def make_env(seed: int, randomize: bool):
    def _init():
        env = YertleEnv(YertleEnvConfig(randomize=randomize, seed=seed))
        return env

    return _init


def main():
    parser = argparse.ArgumentParser(description="Train a Yertle locomotion policy with PPO.")
    parser.add_argument("--timesteps", type=int, default=2_000_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--run-name", type=str, default="ppo_yertle")
    parser.add_argument("--no-randomize", action="store_true", help="Disable domain randomisation.")
    args = parser.parse_args()

    # Imported here so the env module stays importable without the RL extras.
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecMonitor
    from stable_baselines3.common.callbacks import CheckpointCallback

    randomize = not args.no_randomize
    env_fns = [make_env(args.seed + i, randomize) for i in range(args.n_envs)]
    vec_cls = DummyVecEnv if args.n_envs == 1 else SubprocVecEnv
    venv = VecMonitor(vec_cls(env_fns))

    run_dir = RUNS_DIR / args.run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # TensorBoard logging is optional; only enable it if the package is present.
    try:
        import tensorboard  # noqa: F401
        tb_log = str(RUNS_DIR)
    except ImportError:
        tb_log = None
        print("tensorboard not installed; continuing without TB logs.")

    model = PPO(
        "MlpPolicy",
        venv,
        seed=args.seed,
        n_steps=2048,
        batch_size=4096 if args.n_envs >= 4 else 512,
        gae_lambda=0.95,
        gamma=0.99,
        n_epochs=5,
        ent_coef=0.0,
        learning_rate=3e-4,
        clip_range=0.2,
        policy_kwargs=dict(net_arch=[256, 256]),
        tensorboard_log=tb_log,
        verbose=1,
    )

    checkpoint = CheckpointCallback(
        save_freq=max(50_000 // args.n_envs, 1),
        save_path=str(run_dir),
        name_prefix="ckpt",
    )

    model.learn(total_timesteps=args.timesteps, callback=checkpoint, tb_log_name=args.run_name)
    final_path = run_dir / "policy.zip"
    model.save(str(final_path))
    venv.close()
    print(f"Saved final policy to {final_path}")


if __name__ == "__main__":
    main()
