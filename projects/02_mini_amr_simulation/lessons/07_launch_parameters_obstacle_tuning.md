# Lesson 07: Launch Parameters And Obstacle Tuning

## 这一节学什么

这一节你学会把固定演示变成可调实验。

我们新增了三个 launch 参数：

```text
obstacle_layout
stop_distance_m
front_angle_rad
```

它们的作用是：

```text
obstacle_layout  切换 RViz 里的障碍物布局
stop_distance_m  设置多近开始禁止前进
front_angle_rad  设置正前方检测范围有多宽
```

## 为什么要用 launch 参数

如果每次想换障碍物，都去改 Python 代码，会很麻烦。

ROS 2 更常见的做法是：

```text
代码负责能力
参数负责配置
launch 负责把节点和参数一起启动
```

也就是说：

```text
world_lidar_node.py 会生成障碍物和雷达
safety_display.launch.py 决定启动时使用哪种障碍物布局
```

## 可用障碍物布局

现在支持这些布局：

```text
single_front  正前方一个障碍物，适合观察安全停车
slalom        默认绕桩练习，前方和左右侧都有障碍物
wide_gap      两个障碍物之间留通道，练习从中间穿过
left_wall     左侧连续障碍物，观察侧边雷达点
open          没有障碍物，确认小车自由运动
```

## 怎么运行不同布局

默认布局：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py
```

只放一个正前方障碍物：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=single_front
```

绕桩布局：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=slalom
```

中间留通道：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=wide_gap
```

没有障碍物：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=open
```

## 调安全距离

安全距离越大，小车越早停。

更早停车：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py stop_distance_m:=0.90
```

更晚停车：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py stop_distance_m:=0.40
```

也可以和障碍物布局一起用：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=wide_gap stop_distance_m:=0.55
```

## 调前方检测范围

`front_angle_rad` 控制 safety filter 只看多宽的正前方区域。

小一点：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py front_angle_rad:=0.25
```

这表示只看很窄的正前方，转一点方向就更容易放行。

大一点：

```bash
ros2 launch mini_amr_sensors safety_display.launch.py front_angle_rad:=0.80
```

这表示看更宽的前方区域，更保守，也更容易停车。

## 你现在要做的小实验

终端 1 运行：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch mini_amr_sensors safety_display.launch.py obstacle_layout:=wide_gap stop_distance_m:=0.55
```

终端 2 运行键盘：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run mini_amr_motion keyboard_teleop_node --ros-args -p cmd_vel_topic:=cmd_vel_raw
```

你的目标：

```text
从两个红色障碍物之间穿过去
观察靠近第三个障碍物时 safety filter 是否会拦住前进
```

## 面试表达

```text
I parameterized the ROS 2 launch file so the AMR simulation can switch obstacle layouts and tune lidar safety thresholds without changing source code.
```

中文意思：

```text
我把 ROS 2 launch 文件参数化了，因此 AMR 仿真可以不改源码就切换障碍物布局、调整激光雷达安全阈值。
```
