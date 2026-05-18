# mini_amr_motion

这个包给 Mini AMR 加一个轻量运动节点。

它不依赖 Gazebo，只用 Python 发布：

- `/odom`：小车里程计
- `/tf`：`odom -> base_footprint` 坐标变换

## 运行运动节点

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 run mini_amr_motion circle_motion_node
```

## 同时显示小车模型和运动

```bash
ros2 launch mini_amr_motion moving_display.launch.py
```

只做终端测试，不打开 RViz：

```bash
ros2 launch mini_amr_motion moving_display.launch.py use_rviz:=false
```

## 用 /cmd_vel 控制小车

终端 1：

```bash
ros2 launch mini_amr_motion cmd_vel_display.launch.py
```

终端 2：

```bash
ros2 run mini_amr_motion keyboard_teleop_node
```

按键：

```text
w 前进
s 后退
a 左转
d 右转
x 停止
q 退出
```

## 检查

```bash
ros2 topic echo /odom --once
ros2 topic echo /cmd_vel
ros2 topic list
ros2 node list
```
