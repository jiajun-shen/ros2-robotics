# ros2_job_ready_basics

这是 `ros2_ws` 工作空间里的第一个 ROS 2 Python 包。

它演示 ROS 2 最核心的通信模式：

- `goal_publisher`：向 `career_goal` topic 发布文本消息。
- `goal_subscriber`：订阅 `career_goal` topic，并打印收到的消息。
- `robot_status_publisher`：演示 parameter 如何控制节点配置。
- `mission_service_server` / `mission_service_client`：演示 service 请求-响应通信。
- `fibonacci_action_server` / `fibonacci_action_client`：演示 action 的 goal、feedback、result。
- `core_basics.launch.py`：一次启动多个节点。

## 你会学到什么

- node：ROS 2 程序运行时的基本单元。
- topic：节点之间传递消息的频道。
- publisher：向 topic 发送消息的节点组件。
- subscriber：从 topic 接收消息的节点组件。
- message：节点之间传递的数据结构。

## 构建

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## 运行

打开终端 1：

```bash
ros2 run ros2_job_ready_basics goal_publisher
```

打开终端 2：

```bash
ros2 run ros2_job_ready_basics goal_subscriber
```

## 常用检查命令

```bash
ros2 node list
ros2 topic list
ros2 topic echo /career_goal
```

## Parameter 示例

```bash
ros2 run ros2_job_ready_basics robot_status_publisher --ros-args \
  -p robot_name:=shenbot \
  -p current_task:=warehouse_demo \
  -p battery_level_percent:=80
```

查看和修改参数：

```bash
ros2 param list
ros2 param get /robot_status_publisher current_task
ros2 param set /robot_status_publisher current_task navigation_practice
```

## Service 示例

终端 1：

```bash
ros2 run ros2_job_ready_basics mission_service_server
```

终端 2：

```bash
ros2 run ros2_job_ready_basics mission_service_client start
ros2 run ros2_job_ready_basics mission_service_client stop
```

## Action 示例

终端 1：

```bash
ros2 run ros2_job_ready_basics fibonacci_action_server
```

终端 2：

```bash
ros2 run ros2_job_ready_basics fibonacci_action_client 8
```

## Launch 示例

```bash
ros2 launch ros2_job_ready_basics core_basics.launch.py
```

## 简历表达参考

```text
Built a ROS 2 Jazzy Python package using rclpy to demonstrate topics, parameters, services, actions, launch files, and CLI-based system inspection.
```
