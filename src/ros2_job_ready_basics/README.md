# ros2_job_ready_basics

这是 `ros2_ws` 工作空间里的第一个 ROS 2 Python 包。

它演示 ROS 2 最核心的通信模式：

- `goal_publisher`：向 `career_goal` topic 发布文本消息。
- `goal_subscriber`：订阅 `career_goal` topic，并打印收到的消息。

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

## 简历表达参考

```text
Built a ROS 2 Python package using rclpy to demonstrate publisher/subscriber communication, topic inspection, and workspace build workflows.
```
