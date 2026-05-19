# Lesson 03: OccupancyGrid Warehouse Map

## 这一节学什么

前两节我们已经有：

```text
目标点导航
RViz 点击目标点
航点巡航
```

现在开始进入真正导航系统的核心概念：

```text
地图 /map
```

ROS 2 里常见的 2D 导航地图类型是：

```text
nav_msgs/msg/OccupancyGrid
```

它不是普通图片，而是一张带坐标、分辨率和占据信息的栅格地图。

## OccupancyGrid 是什么

你可以把它理解成：

```text
一张二维表格
每个格子代表现实世界的一小块区域
每个格子里存一个数字
```

常见数字含义：

```text
0    空地，可以通过
100  障碍物，占用
-1   未知区域
```

这一节新增的节点是：

```text
warehouse_map_node
```

它发布：

```text
/map
```

消息类型：

```text
nav_msgs/msg/OccupancyGrid
```

## 新的数据流

```text
warehouse_map_node -- /map --> RViz Map display

waypoint_patrol_node -- /goal_pose --> simple_goal_follower_node
simple_goal_follower_node -- /cmd_vel_raw --> safety filter
```

现在 `/map` 只是显示和教学用。

后面学 Nav2 时，planner 和 costmap 才会真正用地图来规划路径。

## 运行

先把旧 launch 都按 `Ctrl+C` 停掉。

终端 1：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py use_rviz:=false route_name:=short_demo
```

终端 2：

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
projects/03_warehouse_navigation/scripts/open_warehouse_rviz_safe.sh
```

你应该在 RViz 里看到：

```text
灰色/黑白地图层
蓝色货架 marker
航点路线
小车模型
```

## 看地图 topic

新开一个终端：

```bash
ros2 topic echo /map --once
```

重点看：

```text
resolution: 0.05
width: 84
height: 68
data:
```

意思是：

```text
每个格子是 0.05 米
地图宽 84 个格子
地图高 68 个格子
data 是每个格子的占用值
```

## 为什么地图 frame 还是 odom

现在我们还没有 SLAM 和定位系统，所以为了降低难度，地图先发布在：

```text
odom
```

后面学真正 Nav2/SLAM 时，会出现：

```text
map
odom
base_footprint
```

那时候 `map -> odom -> base_footprint` 是定位和导航里非常重要的一条 TF 链。

现在先把 OccupancyGrid 消息本身学懂。

## 当前限制

这一节的 `/map` 是我们手写出来的教学地图。

它不是 SLAM 自动建图。

所以它能帮助你理解：

```text
地图 topic 长什么样
RViz 怎么显示地图
障碍物在栅格地图里怎么表达
Nav2 为什么需要 map
```

它暂时不能做到：

```text
用雷达自动建图
自动保存 map.yaml 和 map.pgm
让 planner 真正沿地图绕路
```

这些就是接下来要学的 SLAM 和 Nav2。

## 面试表达

```text
Implemented a ROS 2 OccupancyGrid warehouse map publisher and visualized the map in RViz as preparation for SLAM, localization, and Nav2 path planning.
```
