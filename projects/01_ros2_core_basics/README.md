# Project 01: ROS 2 Core Basics

## Status

In progress. The buildable ROS 2 package is:

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

## Build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Verify

```bash
cd ~/ros2_ws
./scripts/verify_core_basics.sh
```

## Resume Bullet

```text
Built a ROS 2 Jazzy Python package using rclpy to demonstrate topics, parameters, services, actions, launch files, and CLI-based system inspection.
```

## Why It Matters

This project is the foundation for all later robotics projects. Nav2, MoveIt 2, perception pipelines, and embodied AI task execution all rely on these same ROS 2 communication ideas.
