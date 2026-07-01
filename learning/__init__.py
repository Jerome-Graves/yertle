"""Reinforcement-learning package for the Yertle quadruped.

Contains a Gymnasium environment (`YertleEnv`) that wraps the existing
``Simulation/yertle.URDF`` in PyBullet, plus training and evaluation scripts.
"""

from .yertle_env import YertleEnv, YertleEnvConfig

__all__ = ["YertleEnv", "YertleEnvConfig"]
