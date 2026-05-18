#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第四节：fake lidar 能发布 /scan。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_fake_lidar_verify"
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

echo "==> Starting fake lidar"
ros2 run mini_amr_sensors fake_lidar_node \
  > "${log_dir}/fake_lidar_node.log" 2>&1 &
node_pid="$!"

cleanup() {
  kill "${node_pid}" 2>/dev/null || true
  wait "${node_pid}" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2

echo "==> Reading /scan"
timeout 5 ros2 topic echo /scan --once > "${log_dir}/scan_once.log" 2>&1

grep -q 'Fake lidar publishing' "${log_dir}/fake_lidar_node.log"
grep -q 'frame_id: lidar_link' "${log_dir}/scan_once.log"
grep -q 'ranges:' "${log_dir}/scan_once.log"

echo "Mini AMR fake lidar check passed."
echo "Logs: ${log_dir}"
