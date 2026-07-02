r"""Roll out / record a trained Yertle Isaac Lab policy.

    set OMNI_KIT_ACCEPT_EULA=YES
    <isaac_venv>\Scripts\python.exe isaac_lab\play.py --checkpoint <path.pt> --num_envs 32 --video
"""

import argparse
import os
import sys

# Windows DLL-order fix: import torch/rsl_rl before launching Isaac Sim. Also
# pre-import h5py so its bundled HDF5 DLL loads before Isaac Sim's rendering kit
# pulls in a conflicting one (video path imports isaaclab.utils.datasets -> h5py).
import h5py  # noqa: F401
import torch  # noqa: F401
from rsl_rl.runners import OnPolicyRunner

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Play a trained Yertle policy in Isaac Lab.")
parser.add_argument("--task", type=str, default="flat", choices=["flat", "rough"])
parser.add_argument("--checkpoint", type=str, required=True, help="Path to a saved model_*.pt")
parser.add_argument("--num_envs", type=int, default=32)
parser.add_argument("--steps", type=int, default=600)
parser.add_argument("--video", action="store_true")
parser.add_argument("--video_length", type=int, default=400)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
if args_cli.video:
    args_cli.enable_cameras = True

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac_lab  # noqa: F401,E402  (registers tasks)
from isaac_lab.flat_env_cfg import YertleFlatEnvCfg_PLAY  # noqa: E402
from isaac_lab.rough_env_cfg import YertleRoughEnvCfg_PLAY  # noqa: E402
from isaac_lab.rsl_rl_ppo_cfg import YertleFlatPPORunnerCfg, YertleRoughPPORunnerCfg  # noqa: E402

_TASKS = {
    "flat": ("Isaac-Velocity-Flat-Yertle-Play-v0", YertleFlatEnvCfg_PLAY, YertleFlatPPORunnerCfg),
    "rough": ("Isaac-Velocity-Rough-Yertle-Play-v0", YertleRoughEnvCfg_PLAY, YertleRoughPPORunnerCfg),
}


def main():
    TASK, EnvCfg, RunnerCfg = _TASKS[args_cli.task]
    env_cfg = EnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    agent_cfg = RunnerCfg()

    env = gym.make(TASK, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if args_cli.video:
        video_folder = os.path.join(os.path.dirname(os.path.abspath(args_cli.checkpoint)), "videos_play")
        env = gym.wrappers.RecordVideo(
            env,
            video_folder=video_folder,
            step_trigger=lambda step: step == 0,
            video_length=args_cli.video_length,
            disable_logger=True,
        )
        print(f"PLAY_VIDEO_DIR {video_folder}", flush=True)

    env = RslRlVecEnvWrapper(env, clip_actions=getattr(agent_cfg, "clip_actions", None))

    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(args_cli.checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    obs = env.get_observations()
    if isinstance(obs, tuple):
        obs = obs[0]

    print("PLAY_START", flush=True)
    with torch.inference_mode():
        for _ in range(args_cli.steps):
            actions = policy(obs)
            obs, _, _, _ = env.step(actions)
            if isinstance(obs, tuple):
                obs = obs[0]
    print("PLAY_DONE", flush=True)

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
