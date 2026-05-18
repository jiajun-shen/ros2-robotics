# Lesson 01: Simple Goal Navigation

## 这一节学什么

Project 03 从“仓库导航”开始。

但我们先不直接上 Nav2，因为 Nav2 会一下子出现很多新词：

```text
map
localization
costmap
planner
controller
behavior tree
```

所以第一节先做一个最小导航控制器：

```text
给小车一个目标点
读取 /odom 知道小车当前位置
计算目标点和当前位置的误差
发布 /cmd_vel_raw 让小车自己开过去
```

## 当前系统结构

```text
simple_goal_follower_node
        ^
        |
      /odom
        |
cmd_vel_motion_node

simple_goal_follower_node -- /cmd_vel_raw --> lidar_safety_filter_node -- /cmd_vel --> cmd_vel_motion_node
```

注意这里仍然保留了 Project 02 的 safety filter。

也就是说：

```text
Project 03 的导航节点只发布“我想怎么走”
Project 02 的安全节点负责确认“这样走是否安全”
```

这个分层非常像真实机器人软件系统。

## 新增节点

### simple_goal_follower_node

这个节点负责导航控制。

它订阅：

```text
/odom
/goal_pose
```

它发布：

```text
/cmd_vel_raw
```

第一节默认不用你手动发 `/goal_pose`，launch 会通过参数给它一个目标点：

```text
goal_x_m
goal_y_m
goal_yaw_rad
```

### warehouse_scene_node

这个节点负责在 RViz 里画辅助场景。

它发布：

```text
/warehouse_scene
```

里面有：

```text
蓝色仓库货架
绿色目标点
绿色参考路径线
```

这些 marker 是视觉辅助，不是物理碰撞体。

## 运行

终端 1：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py
```

你应该看到：

```text
小车
蓝色货架
绿色目标点
绿色参考线
雷达点
```

小车会自动朝绿色目标点移动。

## 改目标点

例如，把目标点改到更远一点：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py goal_x_m:=2.8 goal_y_m:=0.4
```

换到另一侧：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py goal_x_m:=1.8 goal_y_m:=-0.8
```

## 加回 Project 02 的障碍物

默认这一节用：

```text
obstacle_layout:=open
```

这样先让你看懂“去目标点”。

如果你想让安全过滤器参与，可以这样运行：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py obstacle_layout:=single_front
```

这时导航节点还会想往目标走，但 safety filter 可能会阻止危险前进。

这说明：

```text
导航控制器不是路径规划器
它只会朝目标点走
遇到障碍物时，还需要 planner 或 waypoint logic
```

这就是后面接 Nav2 的原因。

## 这一节你要真正理解

```text
/odom 是当前位置反馈
goal_x_m / goal_y_m 是目标点
simple_goal_follower_node 根据误差算速度
/cmd_vel_raw 是导航节点发出的原始速度
/cmd_vel 是 safety filter 放行后的速度
```

## 面试表达

```text
Implemented a minimal ROS 2 goal-following controller that uses odometry feedback to drive a mobile robot toward a warehouse navigation goal while keeping velocity commands behind a safety filter.
```
