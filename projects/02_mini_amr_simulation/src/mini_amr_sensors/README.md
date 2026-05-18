# mini_amr_sensors

这个包给 Mini AMR 加一个简化的激光雷达节点。

它发布：

```text
/scan
```

消息类型：

```text
sensor_msgs/msg/LaserScan
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

## 检查

```bash
ros2 topic echo /scan --once
ros2 topic info /scan
ros2 node list
```
