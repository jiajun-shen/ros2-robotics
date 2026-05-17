# Code

这里放 Project 02 的 ROS 2 代码。

当前包：

- `mini_amr_description`：URDF 小车模型、robot_state_publisher launch、RViz 配置。
- `mini_amr_motion`：发布 `/odom` 和 `odom -> base_footprint` TF，让小车在 RViz 里运动。

计划中的后续包可能包括：

- `mini_amr_bringup`：启动仿真、RViz、控制器。
- `mini_amr_control`：移动机器人控制相关节点。
