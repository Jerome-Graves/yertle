# Yertle on Isaac Lab (GPU RL)

A second, GPU-accelerated locomotion pipeline for Yertle built on **NVIDIA Isaac
Lab** (Isaac Sim 5.1 + PhysX). It trains a velocity-tracking walking policy with
thousands of parallel environments on an RTX GPU, complementing the CPU
[PyBullet pipeline](../learning/README.md).

```
isaac_lab/
    yertle_cfg.py           Articulation config (spawns the converted USD, leg actuators)
    flat_env_cfg.py         Flat-terrain velocity task (inherits Isaac Lab's locomotion env)
    rough_env_cfg.py        Rough-terrain task (procedural terrain + height scanner)
    rsl_rl_ppo_cfg.py       PPO runner configs (flat and rough)
    distill_env_cfg.py      Distillation env (student obs group without privileged terms)
    rsl_rl_distill_cfg.py   Teacher-student distillation runner config
    train.py                Train on GPU (--task flat|rough)
    play.py                 Roll out / record a trained policy (--task flat|rough)
    distill.py              Distill the trained teacher into a deployable student
    ros2_bridge.py          Expose the Isaac simulation on ROS 2 topics (bidirectional)
```

The environment inherits Isaac Lab's proven `LocomotionVelocityRoughEnvCfg` (the
task that trains ANYmal / Unitree Go2 to walk) and swaps in the Yertle robot,
remapping body names to Yertle's (`base_link`, feet = `*_shin`).

## Prerequisites

Isaac Sim needs Python 3.10/3.11 and an NVIDIA RTX GPU. Create a dedicated
Python 3.11 virtual environment (referred to as `<isaac_venv>` below) and
install per Isaac Lab's pip instructions:

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

Run from the repo root with the Isaac Sim python and the EULA accepted. Run the
scripts as plain files (not `-m`): on Windows, importing heavy libraries before
the Kit app launches is what avoids the DLL-conflict crash, and the scripts
handle that ordering themselves.

```bat
set OMNI_KIT_ACCEPT_EULA=YES
<isaac_venv>\Scripts\python.exe isaac_lab\train.py --task flat --headless --num_envs 4096 --max_iterations 1500
<isaac_venv>\Scripts\python.exe isaac_lab\train.py --task rough --headless --num_envs 4096 --max_iterations 1000
```

Logs and checkpoints: `isaac_lab/runs/<experiment>/<timestamp>/`. Watch with
`tensorboard --logdir isaac_lab/runs`.

## 3. Play / record

```bat
<isaac_venv>\Scripts\python.exe isaac_lab\play.py --task flat --checkpoint <path> --num_envs 16 --video
```

## 4. Distill to a deployable policy

The flat policy observes the base linear velocity, which the real robot cannot
measure. Distillation trains a student from a deployable observation set (no
base linear velocity, no height scan) to imitate the trained teacher:

```bat
<isaac_venv>\Scripts\python.exe isaac_lab\distill.py --headless --teacher isaac_lab\runs\yertle_flat\<run>\model_1499.pt
```

Result on this robot: student mean reward 40.4 against the teacher's 40.5, with
an imitation loss of about 1e-3.

## 5. ROS 2 bridge

`ros2_bridge.py` publishes `/joint_states` and `/clock` and subscribes to
`/joint_command`, exposing the GPU simulation to any ROS 2 stack. Validated
bidirectionally; see [ros2/README.md](../ros2/README.md) for the demo and the
Windows setup notes.

## Notes

- The default standing pose and actuator gains in `yertle_cfg.py` are starting
  points carried over from the PyBullet env; tune if the robot spawns collapsed.
- The URDF now carries firmware-derived joint limits (revolute joints) and the
  actuator enforces effort/velocity caps, so learned behavior stays within what
  the hardware can execute. An explicit DC-motor actuator model was evaluated
  and rejected as underdamped at these gains (see the comment in
  `yertle_cfg.py` and the technical report).
- A quick model sanity check after any URDF/actuator change: command the
  standing pose with zero action and confirm the base height holds steady.
