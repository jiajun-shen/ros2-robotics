# Project 02: Mini AMR Simulation

## Status

In progress.

Current package:

```text
src/mini_amr_description
src/mini_amr_motion
```

## Goal

Build a simulated differential-drive autonomous mobile robot, similar to a small warehouse or delivery robot.

## Planned ROS 2 Skills

- URDF and xacro robot modeling
- RViz visualization
- Gazebo simulation
- Differential-drive kinematics
- `ros2_control`
- Keyboard teleoperation
- Sensor topics for lidar and camera

## Planned Deliverables

- A mobile robot model with wheels, chassis, and sensors
- A Gazebo world for simulation
- A launch file that starts the robot in simulation
- RViz configuration for visualizing the robot and sensor data
- README screenshots and run commands

## Current Folder Layout

```text
02_mini_amr_simulation/
├── README.md
├── lessons/
│   └── 01_urdf_robot_model_rviz.md
│   └── 02_odometry_and_tf_motion.md
├── scripts/
│   └── verify_description.sh
│   └── verify_motion.sh
└── src/
    └── mini_amr_description/
    └── mini_amr_motion/
```

## Lesson 01: Robot Model In RViz

This first step creates a visible AMR model using URDF, `robot_state_publisher`, TF, and RViz.

Build:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

Run with RViz:

```bash
ros2 launch mini_amr_description display.launch.py
```

Run without RViz for terminal-only testing:

```bash
ros2 launch mini_amr_description display.launch.py use_rviz:=false
```

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_description.sh
```

Lesson:

- [01_urdf_robot_model_rviz.md](lessons/01_urdf_robot_model_rviz.md)

Code:

- [mini_amr_description](src/mini_amr_description)

## Lesson 02: Odometry And TF Motion

This step adds a Python node that publishes `/odom` and the `odom -> base_footprint` TF transform, so the robot can move in RViz.

Run with RViz:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_motion moving_display.launch.py
```

Run without RViz for terminal-only testing:

```bash
ros2 launch mini_amr_motion moving_display.launch.py use_rviz:=false
```

Inspect odometry:

```bash
ros2 topic echo /odom --once
```

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_motion.sh
```

Lesson:

- [02_odometry_and_tf_motion.md](lessons/02_odometry_and_tf_motion.md)

Code:

- [mini_amr_motion](src/mini_amr_motion)

## Resume Bullet

```text
Developed a simulated differential-drive AMR in ROS 2 with URDF/xacro, Gazebo, ros2_control, RViz, and sensor topic visualization.
```

## Why It Matters

This project turns ROS 2 basics into a real robot system. It is the bridge between simple nodes and autonomous navigation.
