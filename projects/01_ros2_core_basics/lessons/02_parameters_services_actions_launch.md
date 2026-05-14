# Project 1 Extension: Parameters, Services, Actions, Launch

## 你已经会了

你已经会运行：

```text
publisher -> topic -> subscriber
```

这是 ROS 2 最常见的数据流。

接下来补齐第一个项目的另外四个基础能力：

- parameter：给节点传配置。
- service：请求一次，回复一次。
- action：发送一个长期任务，中途有 feedback，最后有 result。
- launch：一次启动多个节点。

## 1. Parameter

parameter 可以理解成“节点配置”。

运行机器人状态发布器：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run ros2_job_ready_basics robot_status_publisher
```

带参数运行：

```bash
ros2 run ros2_job_ready_basics robot_status_publisher --ros-args \
  -p robot_name:=shenbot \
  -p current_task:=warehouse_demo \
  -p battery_level_percent:=80
```

查看参数：

```bash
ros2 param list
ros2 param get /robot_status_publisher robot_name
```

修改参数：

```bash
ros2 param set /robot_status_publisher current_task navigation_practice
ros2 param set /robot_status_publisher battery_level_percent 72
```

## 2. Service

service 适合“我问你一次，你回答我一次”的场景。

终端 1 启动 server：

```bash
ros2 run ros2_job_ready_basics mission_service_server
```

终端 2 启动任务：

```bash
ros2 run ros2_job_ready_basics mission_service_client start
```

终端 2 停止任务：

```bash
ros2 run ros2_job_ready_basics mission_service_client stop
```

也可以直接用 ROS 2 命令调用：

```bash
ros2 service call /set_mission_active std_srvs/srv/SetBool "{data: true}"
```

## 3. Action

action 适合“任务会持续一段时间”的场景。

机器人里常见的 action：

- 导航到某个目标点。
- 机械臂执行一段抓取动作。
- 执行多步任务，中途持续反馈进度。

终端 1 启动 action server：

```bash
ros2 run ros2_job_ready_basics fibonacci_action_server
```

终端 2 发送 action goal：

```bash
ros2 run ros2_job_ready_basics fibonacci_action_client 8
```

你会看到：

- Goal was accepted.
- Feedback: 中途反馈。
- Result: 最终结果。

## 4. Launch

launch 的作用是“一次启动多个节点”。

运行：

```bash
ros2 launch ros2_job_ready_basics core_basics.launch.py
```

这个 launch 文件会同时启动：

- `goal_publisher`
- `goal_subscriber`
- `robot_status_publisher`

## 第一项目完整知识地图

```text
topic:
  goal_publisher -> /career_goal -> goal_subscriber

parameter:
  robot_status_publisher uses robot_name/current_task/battery_level_percent

service:
  mission_service_client -> /set_mission_active -> mission_service_server

action:
  fibonacci_action_client -> /calculate_fibonacci -> fibonacci_action_server

launch:
  core_basics.launch.py starts multiple nodes together
```

## 简历表达参考

```text
Built a ROS 2 Jazzy Python core-basics package covering topics, parameters, services, actions, and launch files with documented CLI workflows and reproducible examples.
```
