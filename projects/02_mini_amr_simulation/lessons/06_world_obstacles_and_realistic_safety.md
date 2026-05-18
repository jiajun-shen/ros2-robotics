# Lesson 06: World Obstacles And Realistic Safety

## 为什么你刚才按 `w` 完全不前进

你观察得很对。

上一版 `fake_lidar_node` 的逻辑是：

```text
不管小车在哪里，雷达正前方永远有一个近距离障碍物。
```

所以安全过滤器看到的永远是：

```text
前方太近 -> 不允许继续前进
```

这不是 bug，但它只是“解释 LaserScan 和 safety filter 概念”的简化演示，还不像一个真正能绕障碍物的小车。

## 这一节升级成什么

现在新增了：

```text
world_lidar_node
```

它做三件事：

```text
订阅 /odom，知道小车当前在哪里
在 odom 世界坐标里放几个固定圆形障碍物
根据小车位置和朝向，实时生成 /scan
```

同时它还发布：

```text
/obstacles
```

RViz 会把这些障碍物显示成红色圆柱。

## 新的数据流

```text
cmd_vel_motion_node -- /odom --------------------+
                                                 |
                                                 v
                                      world_lidar_node -- /scan --> RViz
                                                 |
                                                 +---- /obstacles --> RViz

keyboard_teleop_node -- /cmd_vel_raw --> lidar_safety_filter_node -- /cmd_vel --> cmd_vel_motion_node
                                           ^
                                           |
                                         /scan
```

## 关键理解

`/cmd_vel_raw` 是你键盘想让小车做的事：

```text
我想前进
我想后退
我想左转
```

`/cmd_vel` 是安全过滤器允许小车实际做的事：

```text
前方安全 -> 允许前进
前方太近 -> 禁止前进，但保留转向
```

`/scan` 是雷达看到的环境。

`/odom` 是小车在世界里的位置。

## 运行

终端 1：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

终端 2：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

终端 3：

```bash
ros2 topic echo /cmd_vel_raw
```

终端 4：

```bash
ros2 topic echo /cmd_vel
```

## 你要怎么操作

1. 在终端 2 按 `w`。
2. 小车一开始应该可以前进。
3. 靠近红色障碍物时，小车会停下。
4. 继续看终端 3 和终端 4：

```text
/cmd_vel_raw 还是 linear.x: 0.3
/cmd_vel 变成 linear.x: 0.0
```

这说明键盘命令发出来了，但是安全过滤器拦住了危险前进。

5. 按 `a` 或 `d` 让小车转向。
6. 当雷达正前方不再对着障碍物，再按 `w`。
7. 小车应该可以绕开障碍物继续走。

## RViz 里应该看什么

你应该看到：

```text
小车模型
TF 坐标轴
雷达点云 /scan
红色圆柱障碍物 /obstacles
```

红色圆柱不是“真实物理墙”，它是 `visualization_msgs/msg/MarkerArray`，作用是让你看见代码里设定的障碍物在哪里。

真正的物理碰撞、轮子打滑、机器人撞墙弹不开，这些要到后面的 Gazebo 或 Isaac Sim 才会学。

## 这节代码在哪里

```text
src/mini_amr_sensors/mini_amr_sensors/world_lidar_node.py
src/mini_amr_sensors/mini_amr_sensors/lidar_safety_filter_node.py
src/mini_amr_sensors/launch/safety_display.launch.py
src/mini_amr_description/rviz/mini_amr_obstacles.rviz
```

## 面试表达

```text
Built a lightweight ROS 2 AMR safety simulation with odometry-aware lidar ray casting, RViz obstacle markers, and a LaserScan-based velocity safety filter.
```
