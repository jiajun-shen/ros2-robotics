# Lesson 01: Simple Goal Navigation

## 这一节学什么

Project 03 从“仓库导航”开始。

但我们先不直接上 Nav2，因为 Nav2 会一下子出现很多新词：

```text
map
localization
costmap
planner
controller
behavior tree
```

所以第一节先做一个最小导航控制器：

```text
给小车一个目标点
读取 /odom 知道小车当前位置
计算目标点和当前位置的误差
发布 /cmd_vel_raw 让小车自己开过去
```

## 当前系统结构

```text
simple_goal_follower_node
        ^
        |
      /odom
        |
cmd_vel_motion_node

simple_goal_follower_node -- /cmd_vel_raw --> lidar_safety_filter_node -- /cmd_vel --> cmd_vel_motion_node
```

注意这里仍然保留了 Project 02 的 safety filter。

也就是说：

```text
Project 03 的导航节点只发布“我想怎么走”
Project 02 的安全节点负责确认“这样走是否安全”
```

这个分层非常像真实机器人软件系统。

## 新增节点

### simple_goal_follower_node

这个节点负责导航控制。

它订阅：

```text
/odom
/goal_pose
```

它发布：

```text
/cmd_vel_raw
```

第一节默认不用你手动发 `/goal_pose`，launch 会通过参数给它一个目标点：

```text
goal_x_m
goal_y_m
goal_yaw_rad
```

### warehouse_scene_node

这个节点负责在 RViz 里画辅助场景。

它发布：

```text
/warehouse_scene
```

里面有：

```text
蓝色仓库货架
绿色目标点
绿色参考路径线
```

这些 marker 是视觉辅助，不是物理碰撞体。

## 运行

终端 1：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py
```

你应该看到：

```text
小车
蓝色货架
绿色目标点
绿色参考线
雷达点
```

小车会自动朝绿色目标点移动。

## 改目标点

第一条 launch 命令只开一次。

如果你想改目标点，不要再运行第二次 launch。

正确做法是在第二个终端发送一个新的 `/goal_pose`：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run warehouse_navigation send_goal_node --ros-args -p goal_x_m:=2.8 -p goal_y_m:=0.4
```

换到另一侧：

```bash
ros2 run warehouse_navigation send_goal_node --ros-args -p goal_x_m:=1.8 -p goal_y_m:=-0.8
```

这时你会看到 RViz 里的绿色目标点移动到新坐标，小车也会朝新目标点开。

## 用 RViz 鼠标点击发送目标点

现在有两种 RViz 鼠标方式。

推荐方式是 `2D Goal Pose`：

```text
RViz 2D Goal Pose 工具 -> /goal_pose -> simple_goal_follower_node
```

运行第一条 launch 后，在 RViz 顶部工具栏选择 `2D Goal Pose`。

操作方式：

```text
在地面网格上按住鼠标左键
拖出一个箭头方向
松开鼠标
```

你应该看到：

```text
绿色目标点移动到你选择的位置
小车先转向，再朝目标点移动
```

这个方式更像以后 Nav2 里真正使用的 RViz 目标点交互。

另一个辅助方式是 `Publish Point`：

```text
RViz Publish Point 工具 -> /clicked_point -> clicked_point_goal_node -> /goal_pose
```

这里发生的事是：

```text
RViz 点击平面，发布 geometry_msgs/msg/PointStamped
clicked_point_goal_node 收到 /clicked_point
clicked_point_goal_node 把点转换成 geometry_msgs/msg/PoseStamped
simple_goal_follower_node 收到 /goal_pose
小车朝新目标点移动
```

`Publish Point` 更像点一个 3D 点，有时点击范围和手感会比较奇怪。
所以导航练习优先用 `2D Goal Pose`。

代码位置：

```text
src/warehouse_navigation/warehouse_navigation/clicked_point_goal_node.py
```

注意：这个入门版本只处理 `odom` 坐标系里的点击点，所以 RViz 的 `Fixed Frame` 要保持 `odom`。

## 为什么不能开第二个 launch

你如果这样做：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py goal_x_m:=2.8 goal_y_m:=0.4
```

但第一个 launch 还没关掉，就会出现两套系统同时运行：

```text
两个 simple_goal_follower_node 同时发布 /cmd_vel_raw
两个 cmd_vel_motion_node 同时发布 /odom
两个 warehouse_scene_node 同时发布 /warehouse_scene
```

所以 RViz 里的绿色目标点会在两个坐标之间来回闪，小车也会被两套控制命令干扰。

正确规则：

```text
启动机器人系统：用 launch，只开一次
改变导航目标：用 send_goal_node
鼠标点击目标：优先用 RViz 的 2D Goal Pose 工具
```

如果你已经看到绿色目标点来回闪，说明旧 launch 还没关干净。
先在所有正在运行 launch 的终端按 `Ctrl+C`，再重新启动一次：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py
```

## 加回 Project 02 的障碍物

默认这一节用：

```text
obstacle_layout:=open
```

这样先让你看懂“去目标点”。

如果你想让安全过滤器参与，可以这样运行：

```bash
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py obstacle_layout:=single_front
```

这时导航节点还会想往目标走，但 safety filter 可能会阻止危险前进。

这说明：

```text
导航控制器不是路径规划器
它只会朝目标点走
遇到障碍物时，还需要 planner 或 waypoint logic
```

这就是后面接 Nav2 的原因。

## 这一节你要真正理解

```text
/odom 是当前位置反馈
goal_x_m / goal_y_m 是启动时默认目标点
/goal_pose 是运行中更新目标点
/clicked_point 是 RViz 鼠标点击出来的点
2D Goal Pose 会直接发布 /goal_pose
simple_goal_follower_node 根据误差算速度
/cmd_vel_raw 是导航节点发出的原始速度
/cmd_vel 是 safety filter 放行后的速度
```

## 面试表达

```text
Implemented a minimal ROS 2 goal-following controller that uses odometry feedback to drive a mobile robot toward a warehouse navigation goal while keeping velocity commands behind a safety filter.
```
## 现在这个导航还不能做什么

现在的小车会朝目标点直线行驶。

如果你点的是货架/障碍物后面的点，它不会自己绕路，因为我们还没有真正的路径规划器。

它能做到：

```text
点击开阔地面上的目标点
小车先转向，再开过去
运行中重新点一个新目标点
小车重新调整方向
```

它暂时不能做到：

```text
自动规划绕开货架的曲线路径
自动从障碍物中找通道
自动生成全局路径和局部避障轨迹
```

这些就是后面 Nav2 的 planner、controller、costmap 要解决的问题。
