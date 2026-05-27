#!/usr/bin/env bash
set -euo pipefail

# 只清理 Project 07 demo 相关进程，用来修复误开两套 launch 后的 RViz 抖动。
pkill -f '[w]heel_leg_demo.launch.py' || true
pkill -f '[w]heel_leg_joystick.launch.py' || true
pkill -f '[w]heel_leg_motion_node' || true
pkill -f '[d]emo_command_node' || true
pkill -f '[o]n_screen_joystick_node' || true
pkill -f '[v]irtual_joystick_node' || true
pkill -f '[q]uadruped_robot_state_publisher' || true
pkill -f '[r]viz2.*wheel_leg_quadruped.rviz' || true

echo "Stopped Project 07 quadruped demo processes."
