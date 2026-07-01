# Learned locomotion for Yertle

Reinforcement-learning pipeline that replaces the hand-tuned sinusoidal gait
with a **policy trained in simulation** and intended for **sim-to-real**
transfer onto the physical robot.

The environment reuses the existing `Simulation/yertle.URDF`, so the learned
controller drives the same 12-DOF machine the rest of the repository builds.

```
learning/
    yertle_env.py         Gymnasium environment (PyBullet backend)
    train.py              PPO training (stable-baselines3)
    enjoy.py              Roll out / render a trained policy
    deploy.py             Sim-to-real bridge (see also ../ros2)
    record_video.py       Save an mp4/gif of a trained policy
    plot_progress.py      Reward curve PNG from a training log
    smoke_test.py         Fast env check, no RL deps required
    requirements-rl.txt   RL dependencies (gymnasium, sb3, torch, ...)
```

## Install

```bash
pip install -r requirements.txt -r learning/requirements-rl.txt
```

`smoke_test.py` only needs `pybullet`, `gymnasium` and `numpy` (already in the
base `requirements.txt`), so you can check the environment before pulling in
Torch.

## Quick start

```bash
# 1. Sanity-check the environment (random actions, a few seconds)
python -m learning.smoke_test

# 2. Short training smoke run
python -m learning.train --timesteps 20000 --n-envs 2

# 3. A real run (minutes-to-hours depending on hardware)
python -m learning.train --timesteps 3000000 --n-envs 8

# 4. Watch the result
python -m learning.enjoy --policy learning/runs/ppo_yertle/policy.zip

# 5. Produce demo artifacts
python -m learning.record_video --policy learning/runs/ppo_yertle/policy.zip --seconds 8
python -m learning.plot_progress --log learning/runs/train_ppo_yertle.log
```

TensorBoard: `tensorboard --logdir learning/runs`.

## Environment design

**Action** (12): joint-angle residuals around a fixed standing pose, tracked by
a position controller. This matches how the real robot is commanded (joint
angles over WiFi/serial), which keeps the sim-to-real gap small.

**Observation** (48): base linear velocity, base angular velocity, projected
gravity (an IMU-style "which way is down" signal), the velocity command, and
joint positions / velocities / previous action.

**Reward**: track a commanded body velocity (forward, lateral, yaw) while
staying upright and at height, with penalties on energy, action rate,
orientation and falling.

**Physics sanitation.** The shipped URDF was authored for visualisation and its
inertia tensors are not physically valid, so the raw model diverges when
simulated freely. On load the environment overrides each link's inertia with a
stable estimate from its mass and sets foot friction. Turning a display model
into a trainable dynamics model is part of the work here.

**Domain randomisation** (per episode): base mass, foot friction, observation
noise and random pushes. This is the main lever for surviving transfer to
hardware.

## Sim-to-real plan

The policy is a small MLP, so deployment is light:

1. Export the trained weights (the residual-around-stance action design makes
   the mapping to servo angles direct).
2. Run inference at the control rate on the Raspberry Pi (or a laptop) using
   the IMU + commanded joint state to build the observation.
3. Stream the resulting joint targets to the ESP32 over the existing UDP path
   (`f`/`a` command strings in `Software/ESP32/firmware`).

The two privileged observation terms (base linear velocity) are either
estimated on-board or dropped and retrained; both are standard practice.

## Status

The environment, training and evaluation scripts are complete and validated
(the env steps, resets and trains). Producing a polished trotting policy needs
a full training run (order of a few million steps); the standing pose and
reward weights in `yertle_env.py` are sensible starting points and are the
first things to tune for your servos.
