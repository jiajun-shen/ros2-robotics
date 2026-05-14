#!/usr/bin/env bash
set -Eeuo pipefail

# 一键验证第一个 ROS 2 项目的核心功能。
# 这个脚本会短暂启动节点，检查它们是否真的能发布、接收、请求和返回。

workspace_dir="${HOME}/ros2_ws"
log_dir="/tmp/ros2_job_ready_basics_verify"
mkdir -p "${log_dir}"

source_ros() {
  # ROS 2 的 setup 脚本内部会使用一些可能未定义的变量。
  # 所以 source 时临时关闭 nounset，source 完再打开。
  set +u
  source /opt/ros/jazzy/setup.bash
  cd "${workspace_dir}"
  source install/setup.bash
  set -u
}

cleanup() {
  for pid in "${background_pids[@]:-}"; do
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  done
}

background_pids=()
trap cleanup EXIT

source_ros

echo "==> Building workspace"
colcon build --symlink-install
source_ros

echo "==> Verifying parameter node"
timeout 4 ros2 run ros2_job_ready_basics robot_status_publisher --ros-args \
  -p robot_name:=shenbot \
  -p current_task:=warehouse_demo \
  -p battery_level_percent:=80 \
  > "${log_dir}/parameter.log" 2>&1 || true
grep -q 'Published status:' "${log_dir}/parameter.log"

echo "==> Verifying service server/client"
ros2 run ros2_job_ready_basics mission_service_server \
  > "${log_dir}/service_server.log" 2>&1 &
background_pids+=("$!")
sleep 2
ros2 run ros2_job_ready_basics mission_service_client start \
  > "${log_dir}/service_client_start.log" 2>&1
ros2 run ros2_job_ready_basics mission_service_client stop \
  > "${log_dir}/service_client_stop.log" 2>&1
grep -q 'Mission started.' "${log_dir}/service_server.log"
grep -q 'Mission stopped.' "${log_dir}/service_server.log"

echo "==> Verifying action server/client"
ros2 run ros2_job_ready_basics fibonacci_action_server \
  > "${log_dir}/action_server.log" 2>&1 &
background_pids+=("$!")
sleep 2
ros2 run ros2_job_ready_basics fibonacci_action_client 6 \
  > "${log_dir}/action_client.log" 2>&1
grep -q 'Goal was accepted.' "${log_dir}/action_client.log"
grep -q 'Result:' "${log_dir}/action_client.log"

echo "==> Verifying launch file"
timeout 4 ros2 launch ros2_job_ready_basics core_basics.launch.py \
  > "${log_dir}/launch.log" 2>&1 || true
grep -q 'goal_publisher' "${log_dir}/launch.log"
grep -q 'goal_subscriber' "${log_dir}/launch.log"
grep -q 'robot_status_publisher' "${log_dir}/launch.log"

echo "All ROS 2 core basics checks passed."
echo "Logs: ${log_dir}"
