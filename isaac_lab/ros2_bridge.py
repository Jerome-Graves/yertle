r"""Isaac Sim <-> ROS 2 bridge for Yertle (OmniGraph, isaacsim.ros2.bridge).

Isaac Sim simulates the Yertle articulation and, through an OmniGraph action
graph, publishes ``/joint_states`` and ``/clock`` and subscribes to a joint
command on ``/joint_command`` (sensor_msgs/JointState) which is applied to the
robot by an articulation controller. This exposes the GPU simulation on real
ROS 2 topics, so the RoboStack ROS 2 environment (or any ROS 2 stack) can drive
and observe it.

Run in the Isaac Sim python env (Isaac's ROS 2 bridge uses its own bundled
ROS 2 Humble libraries):

    set OMNI_KIT_ACCEPT_EULA=YES
    C:\Users\Jerome\isaac\.venv\Scripts\python.exe isaac_lab\ros2_bridge.py --headless

Then, from the RoboStack ROS 2 env, confirm the topics cross the bridge:

    conda run -n ros2 ros2 topic echo /joint_states --once

Notes
-----
* Isaac's ``ROS2SubscribeJointState`` node expects ``sensor_msgs/JointState``.
  The ``yertle_rl.policy_node`` publishes ``std_msgs/Float64MultiArray``; to close
  the loop through this bridge, publish the policy output as a JointState on
  ``/joint_command`` (a few-line relay) or extend policy_node to do so.
* Both sides must use the same ``ROS_DOMAIN_ID`` and a compatible RMW (Humble
  defaults to FastDDS on both) for the topics to interoperate over localhost.
"""

import argparse
import os
from pathlib import Path

os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "YES")

from isaacsim.simulation_app import SimulationApp  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
args, _ = parser.parse_known_args()

app = SimulationApp({"headless": args.headless})

# Enable the ROS 2 bridge extension before using its OmniGraph nodes.
from isaacsim.core.utils.extensions import enable_extension  # noqa: E402
enable_extension("isaacsim.ros2.bridge")
app.update()

import omni.graph.core as og  # noqa: E402
from isaacsim.core.api import SimulationContext  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402

USD = str(Path(__file__).resolve().parents[1] / "simulation" / "usd" / "yertle.usd")
ROBOT_PRIM = "/World/Yertle"

add_reference_to_stage(usd_path=USD, prim_path=ROBOT_PRIM)

sim = SimulationContext(stage_units_in_meters=1.0)

# Build the ROS 2 action graph.
og.Controller.edit(
    {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnTick", "omni.graph.action.OnPlaybackTick"),
            ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
            ("SubscribeJointState", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
            ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
        ],
        og.Controller.Keys.CONNECT: [
            ("OnTick.outputs:tick", "PublishClock.inputs:execIn"),
            ("OnTick.outputs:tick", "PublishJointState.inputs:execIn"),
            ("OnTick.outputs:tick", "SubscribeJointState.inputs:execIn"),
            ("OnTick.outputs:tick", "ArticulationController.inputs:execIn"),
            ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
            ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
            ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
            ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
        ],
        og.Controller.Keys.SET_VALUES: [
            ("PublishJointState.inputs:targetPrim", ROBOT_PRIM + "/base_link"),
            ("PublishJointState.inputs:topicName", "joint_states"),
            ("SubscribeJointState.inputs:topicName", "joint_command"),
            ("ArticulationController.inputs:targetPrim", ROBOT_PRIM + "/base_link"),
            ("PublishClock.inputs:topicName", "clock"),
        ],
    },
)

sim.reset()
print("ROS2_BRIDGE_UP publishing /joint_states and /clock, subscribing /joint_command", flush=True)

try:
    # render=True even when headless: the app update is what ticks the
    # OmniGraph action graph (and therefore the ROS 2 publishers).
    while app.is_running():
        sim.step(render=True)
except KeyboardInterrupt:
    pass
finally:
    sim.stop()
    app.close()
