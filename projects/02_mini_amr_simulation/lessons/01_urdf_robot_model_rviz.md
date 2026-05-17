# Lesson 01: URDF Robot Model And RViz

## 这一节学什么

Project 02 的目标是做一个小型 AMR 仿真机器人。

这一节先不让机器人动，只做第一件事：

```text
把机器人“描述出来”，并在 RViz 里看见它。
```

机器人软件里，这一步非常重要。因为导航、仿真、传感器、控制都需要知道：

- 机器人主体在哪里？
- 轮子在哪里？
- 雷达在哪里？
- 相机在哪里？
- 各个坐标系之间是什么关系？

## URDF 是什么

URDF 可以理解成机器人的“结构说明书”。

它描述：

- link：机器人零件，比如底盘、轮子、雷达、相机。
- joint：零件之间怎么连接。
- visual：这个零件看起来是什么形状。
- collision：仿真里碰撞体是什么形状。
- inertial：仿真里质量和惯量。

当前模型文件：

```text
projects/02_mini_amr_simulation/src/mini_amr_description/urdf/mini_amr.urdf
```

## 当前机器人结构

```text
base_footprint
└── base_link
    ├── left_wheel_link
    ├── right_wheel_link
    ├── front_caster_link
    ├── lidar_link
    └── camera_link
```

## robot_state_publisher 是什么

`robot_state_publisher` 会读取 URDF，然后把机器人各个 link 的坐标关系发布到 `/tf`。

你可以这样理解：

```text
URDF 文件告诉 ROS 2 机器人长什么样
robot_state_publisher 告诉 ROS 2 每个零件坐标系在哪里
RViz 把这些信息画出来
```

## 运行

打开桌面：

```text
ROS2 1 Ubuntu Terminal
```

输入：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_description display.launch.py
```

你应该会看到 RViz 打开，并显示一个小型蓝色机器人：

- 蓝色长方体底盘
- 两个黑色轮子
- 前面一个黑色万向轮
- 上方绿色雷达
- 前方黑色相机

## 如果 RViz 打不开

先运行不带 RViz 的测试：

```bash
ros2 launch mini_amr_description display.launch.py use_rviz:=false
```

如果这个能运行，说明 ROS 2 模型发布是正常的，只是图形界面需要再处理。

## 检查命令

查看 topic：

```bash
ros2 topic list
```

查看机器人描述：

```bash
ros2 topic echo /robot_description --once
```

查看当前节点：

```bash
ros2 node list
```

你应该能看到：

```text
/robot_state_publisher
```

## 这一节你要真正理解

```text
URDF 描述机器人结构
link 是零件
joint 是零件之间的连接
robot_state_publisher 发布机器人坐标树
RViz 用来可视化机器人模型
```

## 面试表达

```text
Created a ROS 2 robot description package for a mini AMR using URDF, robot_state_publisher, TF, and RViz visualization.
```
