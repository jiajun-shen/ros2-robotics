# Project 03: Warehouse Navigation

## Status

Started.

## Goal

Make the simulated mobile robot build a map and navigate through a warehouse-like environment.

## Planned ROS 2 Skills

- SLAM
- Map saving and loading
- Nav2 navigation stack
- Localization
- Global and local planning
- Costmaps
- Waypoint navigation
- `rosbag2` experiment recording

## Planned Deliverables

- A warehouse simulation map
- SLAM demo and saved map
- Nav2 bringup launch file
- Goal navigation demo
- Recorded rosbag and README explanation

## Current Package

```text
src/warehouse_navigation
```

## Lesson 01: Simple Goal Navigation

This first step creates a minimal goal-following controller before introducing Nav2.

Data flow:

```text
simple_goal_follower_node -- /cmd_vel_raw --> lidar_safety_filter_node -- /cmd_vel --> cmd_vel_motion_node
          ^
          |
        /odom
```

Run:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py
```

Change the goal:

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py goal_x_m:=2.8 goal_y_m:=0.4
```

Verify:

```bash
projects/03_warehouse_navigation/scripts/verify_warehouse_navigation_start.sh
```

Lesson:

- [01_simple_goal_navigation.md](lessons/01_simple_goal_navigation.md)

## Resume Bullet

```text
Integrated Nav2 and SLAM for autonomous warehouse navigation with map building, localization, costmaps, and waypoint execution.
```

## Why It Matters

Autonomous navigation is one of the most common requirements in mobile robotics roles.
