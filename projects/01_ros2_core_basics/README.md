# Project 01: ROS 2 Core Basics

## Status

In progress. The buildable ROS 2 package is:

```text
src/ros2_job_ready_basics
```

The workspace-level path below is a link to this same package, so `colcon build` still works normally:

```text
../../src/ros2_job_ready_basics
```

## Goal

Build a clean beginner ROS 2 package that demonstrates the core communication patterns used in robotics software.

## What This Project Covers

- Node
- Topic
- Publisher
- Subscriber
- Parameter
- Service server/client
- Action server/client
- Launch file
- ROS 2 CLI inspection commands

## Folder Layout

```text
01_ros2_core_basics/
├── README.md
├── lessons/
│   ├── 01_ros2_core_basics.md
│   └── 02_parameters_services_actions_launch.md
├── scripts/
│   └── verify_core_basics.sh
└── src/
    └── ros2_job_ready_basics/
```

## Build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Verify

```bash
cd ~/ros2_ws
projects/01_ros2_core_basics/scripts/verify_core_basics.sh
```

## Lessons

- [01_ros2_core_basics.md](lessons/01_ros2_core_basics.md)
- [02_parameters_services_actions_launch.md](lessons/02_parameters_services_actions_launch.md)

## Code

- [ros2_job_ready_basics](src/ros2_job_ready_basics)

## Resume Bullet

```text
Built a ROS 2 Jazzy Python package using rclpy to demonstrate topics, parameters, services, actions, launch files, and CLI-based system inspection.
```

## Why It Matters

This project is the foundation for all later robotics projects. Nav2, MoveIt 2, perception pipelines, and embodied AI task execution all rely on these same ROS 2 communication ideas.
