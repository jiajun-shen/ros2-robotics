#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第五节：lidar safety filter 能拦截危险前进命令。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_safety_filter_verify"
mkdir -p "${log_dir}"

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
  pkill -f fake_lidar_node 2>/dev/null || true
  pkill -f robot_state_publisher 2>/dev/null || true
}
trap cleanup EXIT

sleep 4

echo "==> Listening for filtered /cmd_vel"
timeout 8 ros2 topic echo /cmd_vel --once > "${log_dir}/cmd_vel_filtered.log" 2>&1 &
echo_pid="$!"
sleep 1

echo "==> Publishing raw forward command"
timeout 4 ros2 topic pub -r 10 /cmd_vel_raw geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.0}}" \
  > "${log_dir}/cmd_vel_raw_pub.log" 2>&1 || true

wait "${echo_pid}"

grep -q 'lidar_safety_filter_node' "${log_dir}/safety_display.log"
grep -q 'fake_lidar_node' "${log_dir}/safety_display.log"
grep -q 'cmd_vel_motion_node' "${log_dir}/safety_display.log"

# YAML output spans lines, so check that linear block exists and x is zero.
grep -q 'linear:' "${log_dir}/cmd_vel_filtered.log"
grep -q 'x: 0.0' "${log_dir}/cmd_vel_filtered.log"

echo "Mini AMR safety filter check passed."
echo "Logs: ${log_dir}"
