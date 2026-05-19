#!/usr/bin/env bash
set -Eeuo pipefail

# 安全打开 Project 03 的 RViz。
# 这个脚本专门处理 WSL2/WSLg 下 RViz 有进程但窗口空白的问题。

workspace_dir="${HOME}/ros2_ws"

set +u
source /opt/ros/jazzy/setup.bash
cd "${workspace_dir}"
source install/setup.bash
set -u

# 只关闭进程名正好叫 rviz2 的旧窗口，避免误杀正在执行本脚本的 shell。
pkill -x rviz2 2>/dev/null || true
sleep 1

if [ -z "${DISPLAY:-}" ]; then
  export DISPLAY=:0
fi

export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1

rviz_config="${workspace_dir}/install/warehouse_navigation/share/warehouse_navigation/rviz/warehouse_navigation.rviz"

echo "Opening RViz in WSL safe-rendering mode..."
echo "Config: ${rviz_config}"
exec rviz2 -d "${rviz_config}"
