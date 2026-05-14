# Project 1: ROS 2 Core Basics

## 目标

这个项目用最小代码理解 ROS 2 的核心通信模型：

- 一个节点发布消息。
- 另一个节点订阅消息。
- 使用 ROS 2 命令检查 node、topic 和消息流。

## 核心概念

### Node

node 是 ROS 2 程序运行时的基本单元。一个机器人系统通常不是一个巨大程序，而是很多 node 协同工作。

例如：

- 相机 node 负责发布图像。
- 激光雷达 node 负责发布点云或扫描数据。
- 导航 node 负责规划路径。
- 控制 node 负责给电机发送速度命令。

### Topic

topic 是节点之间传递消息的频道。

在本项目里：

```text
goal_publisher  -- career_goal topic -->  goal_subscriber
```

### Publisher

publisher 负责向 topic 发送消息。

### Subscriber

subscriber 负责从 topic 接收消息。每次收到消息，callback 函数会被调用。

## 本项目的命令

构建：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

运行发布者：

```bash
ros2 run ros2_job_ready_basics goal_publisher
```

运行订阅者：

```bash
ros2 run ros2_job_ready_basics goal_subscriber
```

检查 topic：

```bash
ros2 topic list
ros2 topic echo /career_goal
ros2 topic info /career_goal
```

继续学习：

```text
projects/01_ros2_core_basics/lessons/02_parameters_services_actions_launch.md
```

## 面试表达

我用 ROS 2 Jazzy 和 Python `rclpy` 实现了一个基础通信包，包含 publisher 和 subscriber 节点，并使用 ROS 2 CLI 检查节点图、topic 和消息流。
