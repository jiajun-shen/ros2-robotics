# Lesson 03: cmd_vel And Keyboard Control

## 这一节学什么

前面我们已经做了两件事：

```text
mini_amr_description：描述小车模型
circle_motion_node：让小车按固定速度绕圈
```

这一节我们让小车更像真实移动机器人：

```text
keyboard_teleop_node  -- /cmd_vel -->  cmd_vel_motion_node  -- /odom + TF --> RViz
```

也就是：

- 键盘节点发布速度命令
- 运动节点订阅速度命令
- 运动节点更新小车位置
- RViz 根据 TF 显示小车运动

## /cmd_vel 是什么

`/cmd_vel` 是移动机器人里非常常见的话题。

消息类型是：

```text
geometry_msgs/msg/Twist
```

最常用的两个字段：

```text
linear.x   前进/后退速度，单位 m/s
angular.z  左转/右转角速度，单位 rad/s
```

## 当前新增代码

```text
projects/02_mini_amr_simulation/src/mini_amr_motion/mini_amr_motion/cmd_vel_motion_node.py
projects/02_mini_amr_simulation/src/mini_amr_motion/mini_amr_motion/keyboard_teleop_node.py
```

## 运行

第一个 Ubuntu 窗口启动模型、运动节点和 RViz：

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mini_amr_motion cmd_vel_display.launch.py
```

第二个 Ubuntu 窗口启动键盘控制：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run mini_amr_motion keyboard_teleop_node
```

按键：

```text
w : 前进
s : 后退
a : 左转
d : 右转
x : 停止
q : 退出
```

## 第二个窗口以外的检查命令

再开第三个 Ubuntu 窗口，可以观察 `/cmd_vel`：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic echo /cmd_vel
```

按键盘控制时，你会看到类似：

```text
linear:
  x: 0.3
angular:
  z: 0.0
```

查看 `/odom`：

```bash
ros2 topic echo /odom --once
```

查看节点：

```bash
ros2 node list
```

你应该看到：

```text
/cmd_vel_motion_node
/keyboard_teleop_node
/robot_state_publisher
```

## 这一节你要真正理解

```text
/cmd_vel 是控制命令
/odom 是机器人估计出来的位置和速度
TF 是坐标系关系
键盘节点不直接移动机器人，只发布速度命令
运动节点收到速度命令后，才更新 odom 和 TF
```

## 为什么真实机器人也这么设计

真实机器人通常也是这种结构：

```text
遥控器/导航算法/自动驾驶算法
        |
        v
     /cmd_vel
        |
        v
底盘控制器/仿真控制器
        |
        v
     /odom + TF
```

这样做的好处是：

- 控制来源可以替换：键盘、Nav2、自动驾驶算法都可以发 `/cmd_vel`
- 底盘执行逻辑可以独立：真实底盘或仿真底盘都可以订阅 `/cmd_vel`
- 系统更模块化，更像真实机器人软件架构

## 面试表达

```text
Implemented a ROS 2 cmd_vel-based AMR motion pipeline with keyboard teleoperation, odometry publishing, and TF broadcasting for RViz visualization.
```
