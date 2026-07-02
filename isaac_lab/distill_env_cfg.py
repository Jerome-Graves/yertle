"""Teacher-student distillation env for Yertle (flat terrain).

Adds a ``student`` observation group that omits the privileged base linear
velocity (measurable in simulation, not on the real robot). The ``policy``
group keeps the full observation and feeds the trained teacher; the student is
trained to imitate the teacher from deployable observations only.
"""

from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import ObservationsCfg

from .flat_env_cfg import YertleFlatEnvCfg


@configclass
class YertleStudentObsCfg(ObservationsCfg.PolicyCfg):
    """Deployable observation set: the policy group minus privileged terms."""

    def __post_init__(self):
        super().__post_init__()
        self.base_lin_vel = None    # privileged: not measurable on hardware
        self.height_scan = None     # no terrain scanner on the robot


@configclass
class YertleDistillObservationsCfg(ObservationsCfg):
    student: YertleStudentObsCfg = YertleStudentObsCfg()


@configclass
class YertleFlatDistillEnvCfg(YertleFlatEnvCfg):
    observations: YertleDistillObservationsCfg = YertleDistillObservationsCfg()

    def __post_init__(self):
        super().__post_init__()
        # flat env removes the height scanner from the policy group; the student
        # group already has it removed in its own __post_init__.
