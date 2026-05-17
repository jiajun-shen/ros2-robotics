# ROS 2 Robotics Portfolio

这是我的 ROS 2 机器人项目作品集，目标是系统学习 ROS 2，并逐步构建面向机器人、具身智能、移动机器人和机械臂岗位的项目经验。

## Environment

- OS: Ubuntu 24.04 on WSL2
- ROS 2: Jazzy
- Language: Python first, C++ later
- Build tool: colcon

## Project Roadmap

每个项目都放在 `projects/` 下面。每个项目文件夹里都会有：

- `README.md`：项目目标、运行方式、简历表达。
- `lessons/`：中文教案和复习笔记。
- `src/`：这个项目对应的 ROS 2 代码。

为了让 `colcon build` 继续保持 ROS 2 标准习惯，根目录的 `src/` 会保留指向项目代码的入口。

1. [`projects/01_ros2_core_basics`](projects/01_ros2_core_basics)  
   ROS 2 核心基础：node、topic、publisher、subscriber、service、action、parameter、launch。

2. [`projects/02_mini_amr_simulation`](projects/02_mini_amr_simulation)  
   差速移动机器人仿真：URDF/xacro、RViz、Gazebo、ros2_control、传感器 topic。

3. [`projects/03_warehouse_navigation`](projects/03_warehouse_navigation)  
   仓储机器人自主导航：SLAM、Nav2、地图、定位、路径规划、避障。

4. [`projects/04_perception_to_action`](projects/04_perception_to_action)  
   感知驱动行为：相机 topic、OpenCV、目标检测、检测结果转机器人动作。

5. [`projects/05_manipulation_pick_and_place`](projects/05_manipulation_pick_and_place)  
   机械臂抓取放置：MoveIt 2、运动规划、planning scene、夹爪控制。

6. [`projects/06_embodied_ai_task_executor`](projects/06_embodied_ai_task_executor)  
   具身智能任务执行：自然语言目标解析，调用导航、感知、操作模块完成任务。

## Repository Structure

```text
ros2_ws/
├── projects/
│   ├── 01_ros2_core_basics/
│   │   ├── lessons/   # 中文教案
│   │   ├── scripts/   # 项目验证脚本
│   │   └── src/       # 本项目 ROS 2 代码
│   ├── 02_mini_amr_simulation/
│   ├── 03_warehouse_navigation/
│   ├── 04_perception_to_action/
│   ├── 05_manipulation_pick_and_place/
│   └── 06_embodied_ai_task_executor/
└── src/                # colcon build 入口，链接到各项目的 ROS 包
```

## Current Project

The first package is:

```bash
projects/01_ros2_core_basics/src/ros2_job_ready_basics
```

For normal ROS 2 commands, you can still use the workspace-level package path:

```bash
src/ros2_job_ready_basics
```

This path is a link to the project folder code.

It covers:

- topic publisher/subscriber
- runtime parameters
- service server/client
- action server/client
- launch files

Build:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

Run publisher:

```bash
ros2 run ros2_job_ready_basics goal_publisher
```

Run subscriber in another terminal:

```bash
ros2 run ros2_job_ready_basics goal_subscriber
```

Inspect ROS graph:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /career_goal
```

Run parameter example:

```bash
ros2 run ros2_job_ready_basics robot_status_publisher --ros-args \
  -p robot_name:=shenbot \
  -p current_task:=warehouse_demo \
  -p battery_level_percent:=80
```

Run service example:

```bash
ros2 run ros2_job_ready_basics mission_service_server
ros2 run ros2_job_ready_basics mission_service_client start
```

Run action example:

```bash
ros2 run ros2_job_ready_basics fibonacci_action_server
ros2 run ros2_job_ready_basics fibonacci_action_client 8
```

Run launch example:

```bash
ros2 launch ros2_job_ready_basics core_basics.launch.py
```

Verify Project 01:

```bash
projects/01_ros2_core_basics/scripts/verify_core_basics.sh
```

## Current Project 02

The first package for the mini AMR project is:

```bash
projects/02_mini_amr_simulation/src/mini_amr_description
```

Run the robot model in RViz:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_description display.launch.py
```

Terminal-only verification:

```bash
projects/02_mini_amr_simulation/scripts/verify_description.sh
```

## Learning Goal

Build practical ROS 2 projects that can be discussed in robotics software engineering interviews.
