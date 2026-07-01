# Yertle on Isaac Lab (GPU RL)

A second, GPU-accelerated locomotion pipeline for Yertle built on **NVIDIA Isaac
Lab** (Isaac Sim 5.1 + PhysX). It trains a velocity-tracking walking policy with
thousands of parallel environments on an RTX GPU, complementing the CPU
[PyBullet pipeline](../learning/README.md).

```
isaac_lab/
    yertle_cfg.py         Articulation config (spawns the converted USD, leg actuators)
    flat_env_cfg.py       Flat-terrain velocity task (inherits Isaac Lab's locomotion env)
    rsl_rl_ppo_cfg.py     PPO runner config (rsl_rl)
    train.py              Train on GPU
    play.py               Roll out / record a trained policy
```

The environment inherits Isaac Lab's proven `LocomotionVelocityRoughEnvCfg` (the
task that trains ANYmal / Unitree Go2 to walk) and swaps in the Yertle robot,
remapping body names to Yertle's (`base_link`, feet = `*_shin`).

## Prerequisites

Isaac Sim needs Python 3.10/3.11 and an NVIDIA GPU. This project uses a
dedicated env at `C:\Users\Jerome\isaac\.venv` (Python 3.11). Install per Isaac
Lab's pip instructions:

```bash
pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
pip install "isaaclab[isaacsim,all]==2.3.2.post1" --extra-index-url https://pypi.nvidia.com
```

## 1. Convert the robot model (URDF -> USD)

```bash
python IsaacLab/scripts/tools/convert_urdf.py \
    Simulation/yertle.URDF Simulation/usd/yertle.usd --merge-joints --headless
```

This is already done; the USD lives in `Simulation/usd/`.

## 2. Train (GPU)

Run from the repo root with the Isaac Sim python and the EULA accepted:

```bat
set OMNI_KIT_ACCEPT_EULA=YES
C:\Users\Jerome\isaac\.venv\Scripts\python.exe -m isaac_lab.train --headless --num_envs 4096 --max_iterations 500
```

Logs and checkpoints: `isaac_lab/runs/yertle_flat/<timestamp>/`. Watch with
`tensorboard --logdir isaac_lab/runs`.

## 3. Play / record

```bat
C:\Users\Jerome\isaac\.venv\Scripts\python.exe -m isaac_lab.play --checkpoint <path> --num_envs 32 --video
```

## Notes

- The default standing pose and actuator gains in `yertle_cfg.py` are starting
  points carried over from the PyBullet env; tune if the robot spawns collapsed.
- The Yertle joints have no hard limits in the URDF (they were `continuous`), so
  motion is bounded by the action scale. Add joint limits for a closer
  sim-to-real match.
