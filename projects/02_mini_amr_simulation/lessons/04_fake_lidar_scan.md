# Lesson 04: Fake Lidar And LaserScan

## 这一节学什么

真实 AMR 通常会有激光雷达，用来感知周围障碍物。

这一节我们先不接真实雷达，也不进 Gazebo，而是写一个轻量 fake lidar 节点：

```text
fake_lidar_node
```

它发布：

```text
/scan
```

消息类型是：

```text
sensor_msgs/msg/LaserScan
```

## 系统链路

```text
fake_lidar_node  -- /scan -->  RViz LaserScan display

keyboard_teleop_node  -- /cmd_vel -->  cmd_vel_motion_node
cmd_vel_motion_node   -- /odom + TF --> RViz
```

所以这一节你会同时看到：

- 小车模型
- 小车运动
- 雷达扫描点

## LaserScan 是什么

`LaserScan` 可以理解成一圈距离数据。

核心字段：

```text
header.frame_id  雷达坐标系，这里是 lidar_link
angle_min        扫描起始角度
angle_max        扫描结束角度
angle_increment  每两个激光束之间的角度间隔
range_min        最小有效距离
range_max        最大有效距离
ranges           每个方向测到的距离数组
```

本项目里的 fake lidar 会模拟：

- 前方一堵较近的墙
- 左右两侧稍远的障碍
- 其他方向更远的自由空间

## 运行

第一个 Ubuntu 窗口：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors sensor_display.launch.py
```

第二个 Ubuntu 窗口，如果你想继续用键盘控制：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run mini_amr_motion keyboard_teleop_node
```

## 检查 /scan

第三个 Ubuntu 窗口：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic echo /scan --once
```

你应该看到：

```text
header:
  frame_id: lidar_link
angle_min: -3.14159...
angle_max: 3.14159...
ranges:
- ...
- ...
```

## 这一节你要真正理解

```text
lidar_link 是雷达坐标系
/scan 是雷达测距 topic
LaserScan.ranges 是一圈距离数组
RViz 根据 lidar_link 的 TF 和 /scan 数据把雷达点画出来
```

## 为什么它重要

后面的 SLAM 和 Nav2 都会需要雷达数据：

```text
/scan -> SLAM 建图
/scan -> costmap 障碍物层
/scan -> 避障
```

所以虽然这个 fake lidar 很简单，但它让你先理解雷达 topic 的数据结构。

## 面试表达

```text
Added a ROS 2 fake lidar sensor node publishing sensor_msgs/LaserScan for RViz visualization and future SLAM/Nav2 integration practice.
```
