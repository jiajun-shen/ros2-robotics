#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 03 第一节：最小仓库导航 demo 能启动，并发布导航速度和 RViz marker。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/warehouse_navigation_start_verify"
mkdir -p "${log_dir}"
rm -f "${log_dir}"/*.log

set +u
source /opt/ros/jazzy/setup.bash
cd "${workspace_dir}"
source install/setup.bash
set -u

stop_existing_demo_nodes() {
  pkill -f send_goal_node 2>/dev/null || true
  pkill -f simple_goal_follower_node 2>/dev/null || true
  pkill -f warehouse_scene_node 2>/dev/null || true
  pkill -f lidar_safety_filter_node 2>/dev/null || true
  pkill -f cmd_vel_motion_node 2>/dev/null || true
  pkill -f world_lidar_node 2>/dev/null || true
  pkill -f robot_state_publisher 2>/dev/null || true
}

echo "==> Building workspace"
colcon build --symlink-install

set +u
source install/setup.bash
set -u

echo "==> Stopping any previous demo nodes"
stop_existing_demo_nodes
sleep 1

echo "==> Starting warehouse navigation launch without RViz"
ros2 launch warehouse_navigation warehouse_nav_demo.launch.py \
  use_rviz:=false \
  obstacle_layout:=open \
  goal_x_m:=1.4 \
  goal_y_m:=0.5 \
  > "${log_dir}/warehouse_nav_demo.log" 2>&1 &
launch_pid="$!"

cleanup() {
  kill "${launch_pid}" 2>/dev/null || true
  wait "${launch_pid}" 2>/dev/null || true
  stop_existing_demo_nodes
}
trap cleanup EXIT

sleep 5

echo "==> Sending a new goal without launching a second robot system"
ros2 run warehouse_navigation send_goal_node --ros-args \
  -p goal_x_m:=2.4 \
  -p goal_y_m:=0.2 \
  > "${log_dir}/send_goal_node.log" 2>&1

sleep 1

echo "==> Reading navigation command"
timeout 5 ros2 topic echo /cmd_vel_raw --once \
  > "${log_dir}/cmd_vel_raw_once.log" 2>&1

echo "==> Reading warehouse scene markers"
timeout 5 ros2 topic echo /warehouse_scene --once \
  > "${log_dir}/warehouse_scene_once.log" 2>&1

echo "==> Reading odometry"
timeout 5 ros2 topic echo /odom --once \
  > "${log_dir}/odom_once.log" 2>&1

grep -q 'simple_goal_follower_node' "${log_dir}/warehouse_nav_demo.log"
grep -q 'warehouse_scene_node' "${log_dir}/warehouse_nav_demo.log"
grep -q 'cmd_vel_motion_node' "${log_dir}/warehouse_nav_demo.log"
grep -q 'Goal sent' "${log_dir}/send_goal_node.log"
grep -q 'linear:' "${log_dir}/cmd_vel_raw_once.log"
grep -Eq 'x: 0\.[0-9]|z: 0\.[0-9]|z: -0\.[0-9]' \
  "${log_dir}/cmd_vel_raw_once.log"
grep -q 'warehouse_goal' "${log_dir}/warehouse_scene_once.log"
grep -q 'warehouse_shelves' "${log_dir}/warehouse_scene_once.log"
grep -q 'x: 2.4' "${log_dir}/warehouse_scene_once.log"
grep -q 'y: 0.2' "${log_dir}/warehouse_scene_once.log"
grep -q 'pose:' "${log_dir}/odom_once.log"

echo "Warehouse navigation start check passed."
echo "Logs: ${log_dir}"
