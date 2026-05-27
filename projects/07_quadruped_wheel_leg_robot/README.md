# Project 07: Wheel-Leg Quadruped Robot in ROS 2

这是一个面向作品集展示的 ROS 2 轮腿式四足机器人项目。

项目目标：

- 在 RViz 中展示一个轮腿式四足机器狗模型。
- 使用 URDF 描述机身、四条腿、髋关节、膝关节和轮足。
- 发布 `/joint_states` 让四条腿执行 trot 风格步态动画。
- 订阅 `/cmd_vel`，让机器人可以前进、后退和转向。
- 发布 `/odom`、`odom -> base_footprint` TF、运动轨迹和状态可视化。
- 支持自动演示，也支持键盘虚拟摇杆控制。

## Portfolio Positioning

English summary for resume/GitHub:

> A ROS 2 RViz simulation of a wheel-legged quadruped robot, including URDF modeling, trot gait animation, cmd_vel teleoperation, odometry, TF, path visualization, and a showcase launch file.

这个项目不是完整物理仿真。它优先展示机器人建模、ROS topic、TF、里程计、关节状态和步态控制的工程结构。后续可以继续升级到 Gazebo / ros2_control / Nav2。

## Package

```text
projects/07_quadruped_wheel_leg_robot/
├── README.md
├── lessons/
├── scripts/
└── src/
    └── quadruped_wheel_leg/
        ├── launch/
        ├── quadruped_wheel_leg/
        ├── rviz/
        └── urdf/
```

ROS 2 package:

```text
quadruped_wheel_leg
```

## Build

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select quadruped_wheel_leg
source install/setup.bash
```

## Run Auto Showcase

这个命令会打开 RViz，并自动发布 `/cmd_vel`，所以你一启动就能看到机器狗移动和行走。

```bash
ros2 launch quadruped_wheel_leg wheel_leg_demo.launch.py
```

如果 WSL/RViz 窗口偶尔空白，可以先关掉 RViz 再重新运行。launch 已经默认使用更稳定的软件渲染参数。

## Run With Manual Keyboard Control

终端 1：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch quadruped_wheel_leg wheel_leg_demo.launch.py auto_demo:=false
```

终端 2：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run quadruped_wheel_leg virtual_joystick_node
```

按键：

```text
w / s：前进 / 后退
a / d：左转 / 右转
space：停止
x：退出键盘控制
```

也可以使用 ROS 2 常见键盘遥控包：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Important Topics

```text
/cmd_vel              输入速度命令
/joint_states         四足关节动画
/odom                 机器人里程计
/tf                   odom -> base_footprint
/quadruped_path       RViz 运动轨迹
/quadruped_status     RViz 状态和地面 marker
```

## Verify

```bash
projects/07_quadruped_wheel_leg_robot/scripts/verify_quadruped_demo.sh
```
