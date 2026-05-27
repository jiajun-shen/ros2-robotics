# Project 07 Notes

这个项目已经按作品集 demo 方式完成。以后如果要继续深入，可以按下面顺序拆开学习：

1. `urdf/wheel_leg_quadruped.urdf`：银白色四足轮腿机器人建模，包含质量、惯性、四色腿、深灰履轮足和髋部侧摆关节。
2. `wheel_leg_motion_node.py`：`/cmd_vel`、`/quadruped_drive_mode`、`/odom`、TF 和 `/joint_states` 的核心控制逻辑，支持 walk、wheel、hybrid 三种运动模式。
3. `demo_command_node.py`：自动演示速度命令。
4. `on_screen_joystick_node.py`：圆盘方向键控制窗口，拖动摇杆发布 `/cmd_vel`。
5. `virtual_joystick_node.py`：终端键盘摇杆控制。
6. `wheel_leg_demo.launch.py`：把模型、控制、自动演示和 RViz 组合成一个完整 demo。
7. `wheel_leg_joystick.launch.py`：把模型、控制、RViz 和圆盘方向键组合成手动控制 demo。

简历表达重点：

```text
Built a ROS 2 wheel-legged quadruped RViz simulation with inertial URDF robot
modeling, spring-like gait animation, wheeled rolling mode, hybrid wheel-leg
locomotion, side-step locomotion, cmd_vel teleoperation, odometry, TF
broadcasting, and path/status visualization.
```
