from setuptools import setup

package_name = "yertle_rl"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Jerome Graves",
    maintainer_email="you@example.com",
    description="ROS 2 node that runs a learned locomotion policy for the Yertle quadruped.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "policy_node = yertle_rl.policy_node:main",
        ],
    },
)
