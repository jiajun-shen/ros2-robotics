#!/usr/bin/env bash
set -eo pipefail

cd "${HOME}/ros2_ws"
source /opt/ros/jazzy/setup.bash

colcon build --symlink-install --packages-select quadruped_wheel_leg
source install/setup.bash
set -u

log_file="/tmp/quadruped_wheel_leg_demo.log"
joint_file="/tmp/quadruped_joint_states.txt"
odom_file="/tmp/quadruped_odom.txt"
path_file="/tmp/quadruped_path.txt"

ros2 launch quadruped_wheel_leg wheel_leg_demo.launch.py use_rviz:=false auto_demo:=true \
  > "${log_file}" 2>&1 &
launch_pid=$!

cleanup() {
  kill "${launch_pid}" >/dev/null 2>&1 || true
  wait "${launch_pid}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 4

timeout 8 ros2 topic echo /joint_states --once > "${joint_file}"
timeout 8 ros2 topic echo /odom --once > "${odom_file}"
timeout 8 ros2 topic echo /quadruped_path --once > "${path_file}"

grep -q "front_left_hip_joint" "${joint_file}"
grep -q "rear_right_wheel_joint" "${joint_file}"
grep -q "child_frame_id: base_footprint" "${odom_file}"
grep -q "poses:" "${path_file}"

echo "Quadruped wheel-leg demo verification passed."
