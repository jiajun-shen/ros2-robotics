# Lesson 02: Odometry And TF Motion

## 这一节学什么

上一节你已经在 RViz 里看到了小车模型。

这一节我们让小车“动起来”。

这次还不进 Gazebo，也不做真实物理仿真。我们先写一个轻量 Python 节点：

```text
circle_motion_node
```

它会假装小车正在以固定线速度和角速度运动，然后发布：

- `/odom`：小车的位置和速度估计
- `/tf`：`odom -> base_footprint` 坐标变换

## 为什么要学 odom 和 TF

移动机器人里最常见的坐标关系是：

```text
odom -> base_footprint -> base_link -> lidar_link / camera_link / wheel_link
```

你可以这样理解：

- `odom`：一个局部世界坐标系，小车从哪里出发就从哪里算。
- `base_footprint`：小车在地面上的中心。
- `base_link`：小车身体中心。
- `lidar_link`：雷达位置。
- `camera_link`：相机位置。

机器人导航、建图、传感器融合都离不开 TF。

## 当前新增代码

```text
projects/02_mini_amr_simulation/src/mini_amr_motion/mini_amr_motion/circle_motion_node.py
```

这个节点做三件事：

1. 根据速度更新 `x, y, yaw`
2. 发布 `/odom`
3. 发布 `odom -> base_footprint` 的 TF

## 运行

打开 Ubuntu 终端：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_motion moving_display.launch.py
```

你应该会看到 RViz 里小车沿着圆形轨迹运动。

如果你只想终端测试：

```bash
ros2 launch mini_amr_motion moving_display.launch.py use_rviz:=false
```

## 第二个窗口检查

再打开一个 Ubuntu 终端：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 node list
```

你应该看到：

```text
/circle_motion_node
/robot_state_publisher
```

查看 odom：

```bash
ros2 topic echo /odom --once
```

你会看到里面有：

```text
pose:
  pose:
    position:
      x: ...
      y: ...
twist:
  twist:
    linear:
      x: 0.25
    angular:
      z: 0.45
```

## 参数实验

你可以调慢一点：

```bash
ros2 launch mini_amr_motion moving_display.launch.py use_rviz:=false
```

后面我们会把速度改成从 `/cmd_vel` 接收，这样就能用键盘控制。

## 这一节你要真正理解

```text
/odom 是机器人估计出来的位置和速度
TF 是坐标系之间的关系
odom -> base_footprint 表示机器人在 odom 坐标系中的位置
RViz 根据 TF 把机器人画到正确位置
```

## 面试表达

```text
Implemented a lightweight ROS 2 odometry and TF broadcaster node for a mini AMR, publishing /odom and odom->base_footprint transforms for RViz motion visualization.
```
