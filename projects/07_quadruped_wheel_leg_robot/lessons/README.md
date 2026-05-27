# Project 07 Notes

这个项目已经按作品集 demo 方式完成。以后如果要继续深入，可以按下面顺序拆开学习：

1. `urdf/wheel_leg_quadruped.urdf`：四足轮腿机器人建模。
2. `wheel_leg_motion_node.py`：`/cmd_vel`、`/odom`、TF 和 `/joint_states` 的核心控制逻辑。
3. `demo_command_node.py`：自动演示速度命令。
4. `on_screen_joystick_node.py`：圆盘方向键控制窗口，拖动摇杆发布 `/cmd_vel`。
5. `virtual_joystick_node.py`：终端键盘摇杆控制。
6. `wheel_leg_demo.launch.py`：把模型、控制、自动演示和 RViz 组合成一个完整 demo。
7. `wheel_leg_joystick.launch.py`：把模型、控制、RViz 和圆盘方向键组合成手动控制 demo。

简历表达重点：

```text
Built a ROS 2 wheel-legged quadruped RViz simulation with URDF robot modeling,
trot gait joint animation, cmd_vel teleoperation, odometry, TF broadcasting,
and path/status visualization.
```
