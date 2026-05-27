# Project 07: Wheel-Leg Quadruped Robot in ROS 2

这是一个面向作品集展示的 ROS 2 轮腿式四足机器人项目。

项目目标：

- 在 RViz 中展示一个轮腿式四足机器狗模型。
- 使用 URDF 描述银白色机身、四色金属腿、髋部侧摆关节、髋关节、膝关节和深灰履轮足。
- 在 URDF 中加入质量和惯性参数，为后续 Gazebo / ros2_control 物理仿真打基础。
- 发布 `/joint_states` 让四条腿执行前后步态、左右侧步、履轮滚动和原地转向步态。
- 订阅 `/cmd_vel`，让机器人可以前进、后退、左平移、右平移和原地转向。
- 订阅 `/quadruped_drive_mode`，支持 `walk`、`wheel`、`hybrid` 三种运动模式。
- 发布 `/odom`、`odom -> base_footprint` TF、运动轨迹和状态可视化。
- 支持自动演示，也支持键盘虚拟摇杆控制。

## Portfolio Positioning

English summary for resume/GitHub:

> A ROS 2 RViz simulation of a wheel-legged quadruped robot, including inertial URDF modeling, spring-like gait animation, wheeled rolling mode, hybrid wheel-leg locomotion, side-step locomotion, cmd_vel teleoperation, odometry, TF, path visualization, and a showcase launch file.

这个项目不是完整物理仿真。RViz 只负责可视化，不会真实求解重力、摩擦和接触力。本项目已经把质量/惯性写进 URDF，并用关节步态模拟贴地支撑、弹簧感和左右侧步；后续可以继续升级到 Gazebo / ros2_control / Nav2。

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

## Manual Control Rule

先注意一个规则：

```text
一次只运行一套 quadruped launch。
如果你已经开了自动 demo，先在那个终端按 Ctrl+C，再打开手动控制。
```

如果已经误开两套，RViz 里出现抖动、红色箭头乱飘、绿色轨迹乱颤，先清理：

```bash
cd ~/ros2_ws
projects/07_quadruped_wheel_leg_robot/scripts/stop_quadruped_demo.sh
```

## Run With Circular On-Screen Joystick

推荐使用这个方式。它会一次性启动机器人、RViz 和一个圆盘方向键控制窗口。

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch quadruped_wheel_leg wheel_leg_joystick.launch.py
```

圆盘控制方式：

```text
Walk Steps：主要用腿走路
Wheel Drive：主要用履轮/轮足滚动
Hybrid：腿部步态 + 轮足滚动一起工作
往上拖：前进
往下拖：后退
往左拖：向左平移侧步
往右拖：向右平移侧步
Turn Left 按钮：原地左转
Turn Right 按钮：原地右转
松开鼠标：停止
```

键盘也可以控制圆盘窗口：

```text
W / S：前进 / 后退
A / D：左平移 / 右平移
Q / E：原地左转 / 原地右转
1 / 2 / 3：Walk / Wheel / Hybrid 模式
Space：停止
```

## Run With Terminal Keyboard Control

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
a / d：左平移 / 右平移
q / e：原地左转 / 原地右转
1 / 2 / 3：walk / wheel / hybrid 模式
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
  linear.x            前进/后退
  linear.y            左右平移侧步
  angular.z           原地转向
/quadruped_drive_mode 运动模式：walk / wheel / hybrid
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
