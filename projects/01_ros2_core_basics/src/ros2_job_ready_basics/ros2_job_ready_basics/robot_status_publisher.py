import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotStatusPublisher(Node):
    """用参数控制发布内容的机器人状态发布节点。"""

    def __init__(self):
        super().__init__('robot_status_publisher')

        # parameter 是节点的可配置参数。
        # 这里先给每个参数一个默认值，运行时可以通过命令行覆盖。
        self.declare_parameter('robot_name', 'shenbot')
        self.declare_parameter('current_task', 'learning_ros2_core')
        self.declare_parameter('battery_level_percent', 95)
        self.declare_parameter('publish_period_sec', 1.0)

        # 发布 String 类型消息到 /robot_status topic。
        self.publisher = self.create_publisher(String, 'robot_status', 10)

        # 读取参数决定发布频率。
        publish_period = self.get_parameter('publish_period_sec').value
        self.timer = self.create_timer(float(publish_period), self.publish_status)

    def publish_status(self):
        # 每次发布前都重新读取参数。
        # 这样你可以用 `ros2 param set` 改 current_task 或 battery_level_percent。
        robot_name = self.get_parameter('robot_name').value
        current_task = self.get_parameter('current_task').value
        battery_level = self.get_parameter('battery_level_percent').value

        message = String()
        message.data = (
            f'robot={robot_name}; '
            f'task={current_task}; '
            f'battery={battery_level}%'
        )

        self.publisher.publish(message)
        self.get_logger().info(f'Published status: "{message.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = RobotStatusPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
