#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第二节：运动节点能发布 /odom，并和 robot model 一起启动。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_motion_verify"
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

echo "==> Verifying circle motion node"
timeout 5 ros2 run mini_amr_motion circle_motion_node \
  > "${log_dir}/circle_motion_node.log" 2>&1 || true
grep -q 'Circle motion started' "${log_dir}/circle_motion_node.log"

echo "==> Verifying /odom output"
ros2 run mini_amr_motion circle_motion_node \
  > "${log_dir}/circle_motion_node_for_odom.log" 2>&1 &
node_pid="$!"
cleanup() {
  kill "${node_pid}" 2>/dev/null || true
  wait "${node_pid}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2
timeout 5 ros2 topic echo /odom --once > "${log_dir}/odom_once.log" 2>&1
grep -q 'child_frame_id: base_footprint' "${log_dir}/odom_once.log"
grep -q 'frame_id: odom' "${log_dir}/odom_once.log"

echo "Mini AMR motion check passed."
echo "Logs: ${log_dir}"
