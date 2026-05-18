#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第五/六节：
# 1. 小车离障碍物远时，前进命令会被放行。
# 2. 小车靠近世界坐标里的障碍物后，前进命令会被拦截。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_safety_filter_verify"
mkdir -p "${log_dir}"
rm -f "${log_dir}"/*.log

set +u
source /opt/ros/jazzy/setup.bash
cd "${workspace_dir}"
source install/setup.bash
set -u

echo "==> Building workspace"
colcon build --symlink-install

set +u
source install/setup.bash
set -u

echo "==> Starting safety display launch without RViz"
ros2 launch mini_amr_sensors safety_display.launch.py use_rviz:=false \
  > "${log_dir}/safety_display.log" 2>&1 &
launch_pid="$!"

cleanup() {
  kill "${launch_pid}" 2>/dev/null || true
  wait "${launch_pid}" 2>/dev/null || true
  pkill -f lidar_safety_filter_node 2>/dev/null || true
  pkill -f cmd_vel_motion_node 2>/dev/null || true
  pkill -f world_lidar_node 2>/dev/null || true
  pkill -f robot_state_publisher 2>/dev/null || true
}
trap cleanup EXIT

sleep 4

echo "==> Publishing raw forward command for several seconds"
timeout 15 ros2 topic pub -r 10 /cmd_vel_raw geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.0}}" \
  > "${log_dir}/cmd_vel_raw_pub.log" 2>&1 &
publisher_pid="$!"

sleep 1

echo "==> Reading filtered /cmd_vel while obstacle is still far"
timeout 5 ros2 topic echo /cmd_vel --once \
  > "${log_dir}/cmd_vel_before_obstacle.log" 2>&1

sleep 3

echo "==> Reading filtered /cmd_vel after robot reaches obstacle"
timeout 8 ros2 topic echo /cmd_vel --once \
  > "${log_dir}/cmd_vel_near_obstacle.log" 2>&1

echo "==> Reading RViz obstacle markers"
timeout 5 ros2 topic echo /obstacles --once \
  > "${log_dir}/obstacles_once.log" 2>&1

kill "${publisher_pid}" 2>/dev/null || true
wait "${publisher_pid}" 2>/dev/null || true

grep -q 'lidar_safety_filter_node' "${log_dir}/safety_display.log"
grep -q 'world_lidar_node' "${log_dir}/safety_display.log"
grep -q 'cmd_vel_motion_node' "${log_dir}/safety_display.log"

# YAML output spans lines, so check the linear.x value in each sample.
grep -q 'linear:' "${log_dir}/cmd_vel_before_obstacle.log"
grep -q 'x: 0.3' "${log_dir}/cmd_vel_before_obstacle.log"
grep -q 'linear:' "${log_dir}/cmd_vel_near_obstacle.log"
grep -q 'x: 0.0' "${log_dir}/cmd_vel_near_obstacle.log"
grep -q 'world_obstacles' "${log_dir}/obstacles_once.log"

echo "Mini AMR safety filter check passed."
echo "Logs: ${log_dir}"
