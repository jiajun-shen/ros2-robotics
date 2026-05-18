# Project 02: Mini AMR Simulation

## Status

In progress.

Current package:

```text
src/mini_amr_description
src/mini_amr_motion
src/mini_amr_sensors
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
    └── mini_amr_sensors/
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

- [00_how_mini_amr_description_is_built.md](lessons/00_how_mini_amr_description_is_built.md)
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

## Lesson 03: cmd_vel And Keyboard Control

This step upgrades the motion demo from fixed circular motion to command-velocity control.

Data flow:

```text
keyboard_teleop_node  -- /cmd_vel -->  cmd_vel_motion_node  -- /odom + TF --> RViz
```

Run model, motion node, and RViz:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_motion cmd_vel_display.launch.py
```

Run keyboard control in another terminal:

```bash
ros2 run mini_amr_motion keyboard_teleop_node
```

Keys:

```text
w forward
s backward
a turn left
d turn right
x stop
q quit
```

Lesson:

- [03_cmd_vel_keyboard_control.md](lessons/03_cmd_vel_keyboard_control.md)

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_cmd_vel_control.sh
```

## Lesson 04: Fake Lidar And LaserScan

This step adds a fake 2D lidar sensor topic.

Data flow:

```text
fake_lidar_node -- /scan --> RViz LaserScan display
```

Run model, motion, fake lidar, and RViz:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors sensor_display.launch.py
```

Inspect scan data:

```bash
ros2 topic echo /scan --once
```

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_fake_lidar.sh
```

Lesson:

- [04_fake_lidar_scan.md](lessons/04_fake_lidar_scan.md)

Code:

- [mini_amr_sensors](src/mini_amr_sensors)

## Lesson 05: Lidar Safety Filter

This step adds a simple safety layer between teleoperation and robot motion.

Data flow:

```text
keyboard_teleop_node -- /cmd_vel_raw --> lidar_safety_filter_node -- /cmd_vel --> cmd_vel_motion_node
                                      ^
                                      |
                                    /scan
```

Run model, motion, world-obstacle lidar, safety filter, and RViz:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

Run keyboard control in another terminal:

```bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

Inspect raw and filtered commands:

```bash
ros2 topic echo /cmd_vel_raw
ros2 topic echo /cmd_vel
```

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_safety_filter.sh
```

Lesson:

- [05_lidar_safety_filter.md](lessons/05_lidar_safety_filter.md)
- [06_world_obstacles_and_realistic_safety.md](lessons/06_world_obstacles_and_realistic_safety.md)
- [07_launch_parameters_obstacle_tuning.md](lessons/07_launch_parameters_obstacle_tuning.md)

## Lesson 06: World Obstacles And Realistic Safety

This step upgrades the safety demo from a fixed fake front obstacle to odometry-aware lidar ray casting.

New behavior:

```text
world_lidar_node subscribes /odom
world_lidar_node publishes /scan and /obstacles
RViz shows red cylinder obstacles
lidar_safety_filter_node blocks forward motion only when the obstacle is actually close ahead
```

Run:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

Keyboard:

```bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

Verify:

```bash
projects/02_mini_amr_simulation/scripts/verify_safety_filter.sh
```

Launch with a different obstacle layout:

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=wide_gap
```

Tune the safety threshold:

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=slalom stop_distance_m:=0.80
```

Code:

- [lidar_safety_filter_node.py](src/mini_amr_sensors/mini_amr_sensors/lidar_safety_filter_node.py)

## Resume Bullet

```text
Developed a simulated differential-drive AMR in ROS 2 with URDF/xacro, Gazebo, ros2_control, RViz, and sensor topic visualization.
```

## Why It Matters

This project turns ROS 2 basics into a real robot system. It is the bridge between simple nodes and autonomous navigation.
