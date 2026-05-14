# ROS 2 Robotics Portfolio

这是我的 ROS 2 机器人项目作品集，目标是系统学习 ROS 2，并逐步构建面向机器人、具身智能、移动机器人和机械臂岗位的项目经验。

## Environment

- OS: Ubuntu 24.04 on WSL2
- ROS 2: Jazzy
- Language: Python first, C++ later
- Build tool: colcon

## Project Roadmap

1. `ros2_job_ready_basics`  
   ROS 2 核心基础：node、topic、publisher、subscriber、service、action、parameter、launch。

2. Mini AMR Simulation  
   差速移动机器人仿真：URDF/xacro、RViz、Gazebo、ros2_control、传感器 topic。

3. Warehouse Navigation  
   仓储机器人自主导航：SLAM、Nav2、地图、定位、路径规划、避障。

4. Perception To Action  
   感知驱动行为：相机 topic、OpenCV、目标检测、检测结果转机器人动作。

5. Manipulation Pick And Place  
   机械臂抓取放置：MoveIt 2、运动规划、planning scene、夹爪控制。

6. Embodied AI Task Executor  
   具身智能任务执行：自然语言目标解析，调用导航、感知、操作模块完成任务。

## Current Project

The first package is:

```bash
src/ros2_job_ready_basics
```

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

## Learning Goal

Build practical ROS 2 projects that can be discussed in robotics software engineering interviews.
