# Lesson 00: How The mini_amr_description Package Is Built

## 先搞清楚一句话

`mini_amr_description` 这个包本身不负责让机器人运动。

它负责：

```text
描述机器人长什么样、有哪些零件、零件之间怎么连接。
```

让机器人运动的是后面的包：

```text
mini_amr_motion
```

所以 Project 02 现在分成两层：

```text
mini_amr_description  ->  让机器人在 RViz 里“看得见”
mini_amr_motion       ->  发布 /odom 和 TF，让机器人“动起来”
```

## 当前文件夹结构

```text
mini_amr_description/
├── package.xml
├── setup.py
├── setup.cfg
├── README.md
├── resource/
│   └── mini_amr_description
├── mini_amr_description/
│   └── __init__.py
├── urdf/
│   └── mini_amr.urdf
├── launch/
│   └── display.launch.py
└── rviz/
    └── mini_amr.rviz
```

## 每个文件夹是什么意思

### `package.xml`

这是 ROS 2 包的身份说明书。

它告诉 ROS 2：

- 这个包叫什么
- 版本是多少
- 作者是谁
- 许可证是什么
- 运行时依赖哪些 ROS 2 包

在本项目里，重要依赖是：

```xml
<exec_depend>robot_state_publisher</exec_depend>
<exec_depend>rviz2</exec_depend>
<exec_depend>launch</exec_depend>
<exec_depend>launch_ros</exec_depend>
```

意思是：

- 需要 `robot_state_publisher` 发布机器人 TF
- 需要 `rviz2` 可视化机器人
- 需要 `launch` 和 `launch_ros` 启动节点

### `setup.py`

这是 Python/ament 包的安装规则。

重点是 `data_files`：

```python
(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
(os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
(os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
```

意思是：

- 把 `launch/` 里的 launch 文件安装到 ROS 2 能找到的位置
- 把 `urdf/` 里的机器人模型安装到 ROS 2 能找到的位置
- 把 `rviz/` 里的 RViz 配置安装到 ROS 2 能找到的位置

如果不写这些，`ros2 launch mini_amr_description display.launch.py` 可能找不到 URDF 或 RViz 配置。

### `setup.cfg`

这是 Python 安装脚本路径配置。

这个包目前没有 Python 可执行节点，但 ament_python 包通常会有这个文件。

### `resource/mini_amr_description`

这是 ROS 2 的包索引标记文件。

它通常是空文件，但不能随便删。

ROS 2 会通过 ament index 找包。这个文件帮助 ROS 2 知道：

```text
这里有一个包叫 mini_amr_description
```

### `mini_amr_description/__init__.py`

这是 Python 包标记文件。

它告诉 Python：

```text
mini_amr_description/ 这个目录可以被当成 Python package
```

目前这个文件是空的，正常。

### `urdf/mini_amr.urdf`

这是这个包最重要的文件。

URDF 是机器人结构说明书。

它描述：

- `link`：机器人零件
- `joint`：零件之间的连接
- `visual`：零件看起来的形状
- `collision`：仿真碰撞形状
- `inertial`：质量和惯量

当前机器人结构：

```text
base_footprint
└── base_link
    ├── left_wheel_link
    ├── right_wheel_link
    ├── front_caster_link
    ├── lidar_link
    └── camera_link
```

### `launch/display.launch.py`

这是启动文件。

它一次启动两个东西：

```text
robot_state_publisher
rviz2
```

核心逻辑是：

1. 找到 `mini_amr.urdf`
2. 读取 URDF 内容
3. 把 URDF 内容作为 `robot_description` 参数传给 `robot_state_publisher`
4. 打开 RViz，并加载 `mini_amr.rviz`

### `rviz/mini_amr.rviz`

这是 RViz 的显示配置。

它告诉 RViz：

- Fixed Frame 用 `base_footprint`
- 显示 Grid
- 显示 RobotModel
- 显示 TF
- 从 `/robot_description` 读取机器人模型

这个文件通常可以手写，也可以在 RViz 里调好后保存出来。

## 后缀是什么意思

```text
.xml        XML 文件。ROS 2 的 package.xml 用它描述包信息。
.py         Python 文件。launch 文件和 Python 节点都用它。
.cfg        配置文件。setup.cfg 是 Python 安装配置。
.urdf       机器人模型文件，本质也是 XML。
.rviz       RViz 配置文件，本质是 YAML 风格文本。
.md         Markdown 文档，用来写 README 和中文教案。
```

## 如果从 0 创建，人类应该怎么做

假设你已经有：

```text
~/ros2_ws
```

### 1. 进入 Project 02 的代码目录

```bash
cd ~/ros2_ws/projects/02_mini_amr_simulation/src
```

### 2. 创建 ROS 2 包

```bash
ros2 pkg create mini_amr_description \
  --build-type ament_python \
  --dependencies robot_state_publisher rviz2 launch launch_ros
```

这一步会生成：

```text
mini_amr_description/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
└── mini_amr_description/
```

### 3. 创建三个资源文件夹

```bash
cd mini_amr_description
mkdir -p urdf launch rviz
```

### 4. 写 URDF

创建：

```text
urdf/mini_amr.urdf
```

最小版本可以先只有一个底盘：

```xml
<?xml version="1.0"?>
<robot name="mini_amr">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.55 0.38 0.18"/>
      </geometry>
    </visual>
  </link>
</robot>
```

确认能显示以后，再逐步加轮子、雷达、相机。

### 5. 修改 `setup.py`

让 ROS 2 安装 URDF、launch、RViz 文件：

```python
from glob import glob
import os

(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
(os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
(os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
```

### 6. 写 launch 文件

创建：

```text
launch/display.launch.py
```

这个文件负责：

- 找到 URDF
- 启动 `robot_state_publisher`
- 可选启动 RViz

### 7. 写 RViz 配置

创建：

```text
rviz/mini_amr.rviz
```

最重要的是让 RViz 显示：

- Grid
- RobotModel
- TF

### 8. 接入工作空间根目录 `src`

因为我们把真实代码放在项目文件夹里，所以根目录 `src` 放一个链接：

```bash
cd ~/ros2_ws/src
ln -s ../projects/02_mini_amr_simulation/src/mini_amr_description mini_amr_description
```

这样你仍然可以在工作空间根目录运行：

```bash
cd ~/ros2_ws
colcon build
```

### 9. 构建

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### 10. 运行

```bash
ros2 launch mini_amr_description display.launch.py
```

如果能在 RViz 里看到机器人，说明 description 包成功。

## 那怎么让它动起来

`mini_amr_description` 只描述机器人，不负责运动。

要让它动起来，你需要再做一个运动相关包，比如当前项目里的：

```text
mini_amr_motion
```

运动包做的事情是：

```text
发布 odom -> base_footprint 的 TF
发布 /odom
```

当 RViz 收到这个 TF 后，就知道机器人在 `odom` 坐标系里移动，于是画面里的机器人也会跟着动。

后面进入 Gazebo 后，运动会更真实：

```text
Gazebo 物理引擎 + 差速轮控制器 + /cmd_vel
```

但从学习顺序上，先理解：

```text
description 描述机器人
motion 发布位置变化
RViz 根据 TF 显示运动
```

这个顺序最稳。
