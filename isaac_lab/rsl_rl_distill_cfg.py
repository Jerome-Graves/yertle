"""rsl_rl teacher-student distillation config for Yertle (flat terrain).

The teacher is the trained flat PPO policy (privileged observations, including
base linear velocity). The student sees the deployable ``student`` observation
group only. The teacher hidden dims mirror the flat PPO runner so its checkpoint
loads directly.
"""

from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import (
    RslRlDistillationAlgorithmCfg,
    RslRlDistillationRunnerCfg,
    RslRlDistillationStudentTeacherCfg,
)


@configclass
class YertleFlatDistillationRunnerCfg(RslRlDistillationRunnerCfg):
    num_steps_per_env = 120
    max_iterations = 300
    save_interval = 50
    experiment_name = "yertle_flat_distill"
    obs_groups = {"student": ["student"], "teacher": ["policy"]}
    policy = RslRlDistillationStudentTeacherCfg(
        init_noise_std=0.1,
        student_obs_normalization=False,
        teacher_obs_normalization=False,
        student_hidden_dims=[128, 128, 128],
        teacher_hidden_dims=[128, 128, 128],   # must match the flat PPO actor
        activation="elu",
    )
    algorithm = RslRlDistillationAlgorithmCfg(
        num_learning_epochs=2,
        learning_rate=1.0e-3,
        gradient_length=15,
    )
