# Lesson 05: Lidar Safety Filter

## 这一节学什么

上一节我们已经有：

```text
fake_lidar_node -- /scan --> RViz
keyboard_teleop_node -- /cmd_vel --> cmd_vel_motion_node
```

这一节我们在键盘和运动节点之间加一个安全过滤器：

```text
keyboard_teleop_node
        |
        v
    /cmd_vel_raw
        |
        v
lidar_safety_filter_node  <--- /scan
        |
        v
     /cmd_vel
        |
        v
cmd_vel_motion_node
        |
        v
   /odom + TF
```

## 为什么要有 safety filter

真实机器人里，控制命令通常不能直接进底盘。

因为：

- 人可能误操作
- 导航算法可能给出危险速度
- 前方可能突然出现障碍物

所以常见架构是：

```text
原始速度命令 -> 安全过滤器 -> 安全速度命令 -> 底盘
```

## 当前安全规则

`lidar_safety_filter_node` 做一件简单但真实的事：

```text
如果前方最近障碍物距离 < stop_distance_m，
并且当前命令还想继续前进，
那就把 linear.x 改成 0。
```

它保留转向速度：

```text
angular.z 不被清零
```

原因是：前方有障碍时，机器人不能继续前进，但应该还能原地转弯寻找安全方向。

## 运行

第一个 Ubuntu 窗口：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

第二个 Ubuntu 窗口启动键盘，但这次发布到 `/cmd_vel_raw`：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

第三个 Ubuntu 窗口观察过滤前命令：

```bash
ros2 topic echo /cmd_vel_raw
```

第四个 Ubuntu 窗口观察过滤后命令：

```bash
ros2 topic echo /cmd_vel
```

## 你应该看到什么

按 `w`：

```text
/cmd_vel_raw:
  linear.x: 0.3

/cmd_vel:
  linear.x: 0.0
```

因为 fake lidar 的前方障碍距离约是 1.1 m，而 safety filter 默认阈值是 1.3 m。

按 `a` 或 `d`：

```text
/cmd_vel_raw:
  angular.z: ...

/cmd_vel:
  angular.z: ...
```

转向命令会被放行。

## 这一节你要真正理解

```text
/cmd_vel_raw 是未过滤速度命令
/cmd_vel 是安全过滤后的速度命令
safety filter 订阅 /scan 和 /cmd_vel_raw
safety filter 发布 /cmd_vel
motion node 只听 /cmd_vel
```

## 面试表达

```text
Implemented a ROS 2 lidar-based safety filter that consumes LaserScan and raw velocity commands, blocks unsafe forward motion, and publishes filtered cmd_vel for AMR motion control.
```
