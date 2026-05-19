#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 03 第二节：航点导航 demo 能启动、发布路线 marker 和 /goal_pose。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/warehouse_waypoint_patrol_verify"
mkdir -p "${log_dir}"
rm -f "${log_dir}"/*.log

set +u
source /opt/ros/jazzy/setup.bash
cd "${workspace_dir}"
source install/setup.bash
set -u

stop_existing_demo_nodes() {
  pkill -f waypoint_patrol_node 2>/dev/null || true
  pkill -f warehouse_map_node 2>/dev/null || true
  pkill -f clicked_point_goal_node 2>/dev/null || true
  pkill -f send_goal_node 2>/dev/null || true
  pkill -f simple_goal_follower_node 2>/dev/null || true
  pkill -f warehouse_scene_node 2>/dev/null || true
  pkill -f lidar_safety_filter_node 2>/dev/null || true
  pkill -f cmd_vel_motion_node 2>/dev/null || true
  pkill -f world_lidar_node 2>/dev/null || true
  pkill -f robot_state_publisher 2>/dev/null || true
}

wait_for_topic() {
  local topic_name="$1"
  local timeout_sec="$2"
  local start_sec
  start_sec="$(date +%s)"

  while true; do
    if ros2 topic list | grep -qx "${topic_name}"; then
      return 0
    fi

    if [ "$(( $(date +%s) - start_sec ))" -ge "${timeout_sec}" ]; then
      echo "Timed out waiting for topic ${topic_name}" >&2
      return 1
    fi

    sleep 0.5
  done
}

echo "==> Building workspace"
colcon build --symlink-install

set +u
source install/setup.bash
set -u

echo "==> Stopping any previous demo nodes"
stop_existing_demo_nodes
sleep 1

echo "==> Starting waypoint patrol launch without RViz"
ros2 launch warehouse_navigation warehouse_waypoint_demo.launch.py \
  use_rviz:=false \
  route_name:=short_demo \
  > "${log_dir}/warehouse_waypoint_demo.log" 2>&1 &
launch_pid="$!"

cleanup() {
  kill "${launch_pid}" 2>/dev/null || true
  wait "${launch_pid}" 2>/dev/null || true
  stop_existing_demo_nodes
}
trap cleanup EXIT

sleep 5

wait_for_topic /map 10
wait_for_topic /waypoint_route 10

echo "==> Reading waypoint route markers"
timeout 5 ros2 topic echo /waypoint_route --once \
  > "${log_dir}/waypoint_route_once.log" 2>&1

echo "==> Reading warehouse occupancy map"
timeout 10 ros2 topic echo /map --once \
  > "${log_dir}/map_once.log" 2>&1

echo "==> Reading current goal"
timeout 5 ros2 topic echo /goal_pose --once \
  > "${log_dir}/goal_pose_once.log" 2>&1

echo "==> Reading filtered command"
timeout 5 ros2 topic echo /cmd_vel --once \
  > "${log_dir}/cmd_vel_once.log" 2>&1

grep -q 'waypoint_patrol_node' "${log_dir}/warehouse_waypoint_demo.log"
grep -q 'warehouse_map_node' "${log_dir}/warehouse_waypoint_demo.log"
grep -q 'route=short_demo' "${log_dir}/warehouse_waypoint_demo.log"
grep -q 'simple_goal_follower_node' "${log_dir}/warehouse_waypoint_demo.log"
grep -q 'waypoint_route' "${log_dir}/waypoint_route_once.log"
grep -q 'WP1' "${log_dir}/waypoint_route_once.log"
grep -q 'WP2' "${log_dir}/waypoint_route_once.log"
grep -q 'resolution: 0.05' "${log_dir}/map_once.log"
grep -q 'width: 84' "${log_dir}/map_once.log"
grep -q 'height: 68' "${log_dir}/map_once.log"
grep -q 'data:' "${log_dir}/map_once.log"
grep -q 'pose:' "${log_dir}/goal_pose_once.log"
grep -q 'linear:' "${log_dir}/cmd_vel_once.log"

echo "Warehouse waypoint patrol check passed."
echo "Logs: ${log_dir}"
