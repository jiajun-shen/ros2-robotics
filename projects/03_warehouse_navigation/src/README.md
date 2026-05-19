# Code

这里放 Project 03 的 ROS 2 代码。

当前包：

- `warehouse_navigation`：最小仓库导航 demo。
  - `simple_goal_follower_node`：单目标点导航控制器。
  - `waypoint_patrol_node`：顺序航点任务层。
  - `warehouse_map_node`：OccupancyGrid 仓库地图发布器。
  - `warehouse_scene_node`：RViz 仓库场景 marker。

计划后续包：

- `warehouse_nav_bringup`：Nav2 和 SLAM 启动文件。
- `warehouse_maps`：地图和导航配置。
- `warehouse_waypoints`：航点任务节点。
