# Lesson 02: Waypoint Patrol

## 这一节学什么

上一节你已经会了：

```text
给一个目标点 /goal_pose
小车根据 /odom 朝目标点运动
```

这一节升级成：

```text
给一串目标点
小车按顺序一个一个走过去
```

这就叫航点导航，英文常见说法是：

```text
waypoint navigation
waypoint patrol
multi-goal navigation
```

仓储机器人很常见这种任务：

```text
从起点出发
经过货架 A
到货架 B
去拣货点
回到等待区
```

## 新增节点

新增节点是：

```text
waypoint_patrol_node
```

它订阅：

```text
/odom
```

它发布：

```text
/goal_pose
/waypoint_route
```

其中：

```text
/goal_pose       当前要去的航点
/waypoint_route  RViz 里显示路线、航点和 WP1/WP2 标签
```

## 系统结构

现在 Project 03 有三层：

```text
任务层：
waypoint_patrol_node  -- /goal_pose -->

控制层：
simple_goal_follower_node -- /cmd_vel_raw -->

安全层：
lidar_safety_filter_node -- /cmd_vel -->

运动层：
cmd_vel_motion_node -- /odom + TF --> RViz
```

换成人话就是：

```text
waypoint_patrol_node 决定“下一站去哪”
simple_goal_follower_node 决定“现在怎么开过去”
lidar_safety_filter_node 决定“这个速度安不安全”
cmd_vel_motion_node 让小车在 RViz 里真的动起来
```

这就是机器人软件里很重要的分层思想。

## 运行航点导航

先把旧 launch 都按 `Ctrl+C` 停掉。

然后运行：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py
```

你应该在 RViz 里看到：

```text
蓝色货架
绿色当前目标点
蓝色航点路线
WP1 / WP2 / WP3 等航点标签
小车按顺序移动
```

## 换一条短路线

如果你想先看简单版本：

```bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py route_name:=short_demo
```

## 如果 RViz 任务栏有进程但窗口是空白

这是 WSL2 + RViz 偶尔会出现的图形渲染问题，不是 ROS 节点写错。

更稳的启动方式是分开开：

终端 1，只启动机器人系统：

```bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py use_rviz:=false route_name:=short_demo
```

终端 2，用安全渲染模式打开 RViz：

```bash
projects/03_warehouse_navigation/scripts/open_warehouse_rviz_safe.sh
```

这个脚本会使用软件渲染，速度可能慢一点，但窗口更不容易空白。

默认路线是：

```bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py route_name:=aisle_inspection
```

## 循环巡航

让小车一直重复这条路线：

```bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py loop_route:=true
```

停止时按：

```text
Ctrl+C
```

## 你要观察什么

打开一个新终端看当前目标点：

```bash
ros2 topic echo /goal_pose
```

你会看到 `/goal_pose` 随着航点切换而变化。

看航点路线：

```bash
ros2 topic echo /waypoint_route --once
```

看小车位置：

```bash
ros2 topic echo /odom
```

## 为什么这还不是 Nav2

现在的 waypoint patrol 是“按固定航点顺序走”。

它还不会自己从地图上规划路线。

如果两个航点之间有障碍物，它不会自动绕开。

所以它能做：

```text
按人工设计好的路线巡航
分解复杂路线
展示任务层 -> 控制层 -> 安全层的结构
```

它还不能做：

```text
给任意终点后自动找最优路径
自动根据 costmap 绕障碍
动态重规划
```

这些就是后面 Nav2 要学的内容。

## 面试表达

```text
Implemented a ROS 2 waypoint patrol layer that publishes sequential PoseStamped goals, visualizes the route in RViz, and reuses the lower-level goal follower and lidar safety filter for mobile robot navigation.
```
