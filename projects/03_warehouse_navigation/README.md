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

Change the startup goal:

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py goal_x_m:=2.8 goal_y_m:=0.4
```

Send a new goal while the launch is already running:

```bash
ros2 run warehouse_navigation send_goal_node --ros-args -p goal_x_m:=2.8 -p goal_y_m:=0.4
```

Do not start a second `warehouse_nav_demo.launch.py` while the first one is still running. That creates duplicate publishers on `/odom`, `/cmd_vel_raw`, and `/warehouse_scene`.

Click a goal in RViz:

```text
Select 2D Goal Pose in RViz, then click-drag on the odom grid.
```

`2D Goal Pose` publishes `/goal_pose` directly. The older `Publish Point` tool is still available as a teaching helper; it publishes `/clicked_point`, and `clicked_point_goal_node` converts it to `/goal_pose`.

Verify:

```bash
projects/03_warehouse_navigation/scripts/verify_warehouse_navigation_start.sh
```

Lesson:

- [01_simple_goal_navigation.md](lessons/01_simple_goal_navigation.md)

## Lesson 02: Waypoint Patrol

This step adds a task layer that sends multiple goals in sequence.

Data flow:

```text
waypoint_patrol_node -- /goal_pose --> simple_goal_follower_node -- /cmd_vel_raw --> safety filter
        |
        +-- /waypoint_route --> RViz
```

Run:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py
```

Run a short route:

```bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py route_name:=short_demo
```

Verify:

```bash
projects/03_warehouse_navigation/scripts/verify_waypoint_patrol.sh
```

Lesson:

- [02_waypoint_patrol.md](lessons/02_waypoint_patrol.md)

## Resume Bullet

```text
Integrated Nav2 and SLAM for autonomous warehouse navigation with map building, localization, costmaps, and waypoint execution.
```

## Why It Matters

Autonomous navigation is one of the most common requirements in mobile robotics roles.
