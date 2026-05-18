# mini_amr_sensors

这个包给 Mini AMR 加简化的激光雷达和安全过滤节点。

它可以发布：

```text
/scan
/obstacles
```

常见消息类型：

```text
sensor_msgs/msg/LaserScan
visualization_msgs/msg/MarkerArray
```

## 只运行 fake lidar

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 run mini_amr_sensors fake_lidar_node
```

## 和小车模型、运动节点、RViz 一起运行

```bash
ros2 launch mini_amr_sensors sensor_display.launch.py
```

## 加上安全过滤器

终端 1：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

终端 2：

```bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

安全过滤器会读取 `/scan`，把 `/cmd_vel_raw` 过滤成 `/cmd_vel`。

`safety_display.launch.py` 使用 `world_lidar_node`，所以 RViz 中会看到红色圆柱障碍物。
小车离障碍物远时可以前进；靠近障碍物后，继续按 `w` 会被安全过滤器拦住。

## 检查

```bash
ros2 topic echo /scan --once
ros2 topic echo /cmd_vel_raw
ros2 topic echo /cmd_vel
ros2 topic echo /obstacles --once
ros2 topic info /scan
ros2 node list
```
