import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GoalPublisher(Node):
    """每秒发布一条文本消息的 ROS 2 节点。"""

    def __init__(self):
        # 每一个 ROS 2 Python 节点都必须有一个节点名。
        # 之后可以用 `ros2 node list` 看到这个名字。
        super().__init__('goal_publisher')

        # publisher 的作用：向某个 topic 发布消息。
        # 这里的 topic 名叫 career_goal，消息类型是 std_msgs/String。
        # 最后的 10 是队列长度，表示网络或处理变慢时最多缓存 10 条消息。
        self.publisher = self.create_publisher(String, 'career_goal', 10)

        # timer 的作用：让某个函数按固定频率执行。
        # 这里每 1 秒调用一次 publish_goal()。
        self.timer = self.create_timer(1.0, self.publish_goal)
        self.count = 0

    def publish_goal(self):
        # String 是 ROS 2 里的标准消息类型，里面最重要的字段是 data。
        message = String()
        message.data = f'Learning ROS 2 for embodied intelligence robotics #{self.count}'

        # 真正把消息发布到 career_goal topic。
        self.publisher.publish(message)
        self.get_logger().info(f'Published: "{message.data}"')
        self.count += 1


def main(args=None):
    # 初始化 rclpy。任何 ROS 2 Python 程序开始时都要先做这一步。
    rclpy.init(args=args)

    node = GoalPublisher()

    try:
        # spin 会让节点持续运行，这样 timer 才能一直触发。
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 程序退出前释放节点资源，并关闭 rclpy。
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
