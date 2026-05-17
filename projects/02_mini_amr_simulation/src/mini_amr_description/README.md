# mini_amr_description

这是 Project 02 的第一个 ROS 2 包：小型 AMR 机器人的 URDF + RViz 可视化。

## 运行

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_description display.launch.py
```

如果只想测试 `robot_state_publisher`，不打开 RViz：

```bash
ros2 launch mini_amr_description display.launch.py use_rviz:=false
```

## 你会看到什么

- `base_footprint`：机器人地面坐标系
- `base_link`：机器人主体坐标系
- `left_wheel_link` / `right_wheel_link`：左右轮
- `front_caster_link`：前万向轮
- `lidar_link`：雷达
- `camera_link`：相机

## 检查命令

```bash
ros2 topic list
ros2 topic echo /robot_description --once
ros2 run tf2_tools view_frames
```
