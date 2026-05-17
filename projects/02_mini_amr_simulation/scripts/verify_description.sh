#!/usr/bin/env bash
set -Eeuo pipefail

# 验证 Project 02 第一节：URDF 模型能被 robot_state_publisher 正常加载。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/mini_amr_description_verify"
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

echo "==> Verifying mini AMR robot description"
timeout 5 ros2 launch mini_amr_description display.launch.py use_rviz:=false \
  > "${log_dir}/display_no_rviz.log" 2>&1 || true

grep -q 'robot_state_publisher' "${log_dir}/display_no_rviz.log"
grep -q 'Robot initialized' "${log_dir}/display_no_rviz.log"

urdf_file="${workspace_dir}/projects/02_mini_amr_simulation/src/mini_amr_description/urdf/mini_amr.urdf"
grep -q 'link name="base_link"' "${urdf_file}"
grep -q 'link name="lidar_link"' "${urdf_file}"
grep -q 'link name="camera_link"' "${urdf_file}"

echo "Mini AMR description check passed."
echo "Logs: ${log_dir}"
