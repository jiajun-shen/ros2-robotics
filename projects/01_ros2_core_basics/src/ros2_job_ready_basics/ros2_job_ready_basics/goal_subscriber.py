import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GoalSubscriber(Node):
    """订阅 career_goal topic，并打印收到的每一条消息。"""

    def __init__(self):
        # 创建一个名为 goal_subscriber 的 ROS 2 节点。
        super().__init__('goal_subscriber')

        # subscriber 的作用：从某个 topic 接收消息。
        # 这里订阅 career_goal，消息类型必须和 publisher 保持一致。
        # 每收到一条新消息，ROS 2 就会自动调用 goal_callback()。
        self.subscription = self.create_subscription(
            String,
            'career_goal',
            self.goal_callback,
            10,
        )

    def goal_callback(self, message):
        # callback 是“收到消息后的处理函数”。
        # 这里先只打印消息，之后可以改成控制机器人、记录数据、触发任务等。
        self.get_logger().info(f'Received: "{message.data}"')


def main(args=None):
    # 初始化 ROS 2 Python 客户端库。
    rclpy.init(args=args)

    node = GoalSubscriber()

    try:
        # 保持节点运行，等待 topic 上的新消息。
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 程序退出前清理资源。
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
