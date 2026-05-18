#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第三节：/cmd_vel 控制链路能工作。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_cmd_vel_verify"
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

echo "==> Starting cmd_vel display launch without RViz"
ros2 launch mini_amr_motion cmd_vel_display.launch.py use_rviz:=false \
  > "${log_dir}/cmd_vel_display.log" 2>&1 &
launch_pid="$!"

cleanup() {
  kill "${launch_pid}" 2>/dev/null || true
  wait "${launch_pid}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 3

echo "==> Publishing /cmd_vel"
timeout 3 ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.4}}" \
  > "${log_dir}/cmd_vel_pub.log" 2>&1 || true

echo "==> Reading /odom"
timeout 5 ros2 topic echo /odom --once > "${log_dir}/odom_once.log" 2>&1

grep -q 'cmd_vel_motion_node' "${log_dir}/cmd_vel_display.log"
grep -q 'robot_state_publisher' "${log_dir}/cmd_vel_display.log"
grep -q 'child_frame_id: base_footprint' "${log_dir}/odom_once.log"
grep -q 'frame_id: odom' "${log_dir}/odom_once.log"

echo "Mini AMR cmd_vel control check passed."
echo "Logs: ${log_dir}"
