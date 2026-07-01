"""Fast sanity check for YertleEnv: no RL libraries required.

Loads the environment, runs a short random-action rollout and asserts the
observations, rewards and reset all behave. Handy as a first check after
cloning and as a CI smoke test.

    python -m learning.smoke_test
"""

from __future__ import annotations

import numpy as np

from .yertle_env import YertleEnv, YertleEnvConfig


def run(steps: int = 300) -> None:
    env = YertleEnv(YertleEnvConfig(randomize=True, seed=0))
    obs, info = env.reset(seed=0)

    assert env.observation_space.contains(obs), "reset obs outside observation_space"
    assert obs.shape == env.observation_space.shape

    ep_return = 0.0
    resets = 0
    for _ in range(steps):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        assert np.all(np.isfinite(obs)), "non-finite observation"
        assert np.isfinite(reward), "non-finite reward"
        ep_return += reward
        if terminated or truncated:
            obs, info = env.reset()
            resets += 1
    env.close()

    print(f"OK: {steps} steps ran, {resets} episode boundaries, "
          f"obs_dim={obs.shape[0]}, act_dim={env.action_space.shape[0]}, "
          f"return_so_far={ep_return:.1f}")


if __name__ == "__main__":
    run()
