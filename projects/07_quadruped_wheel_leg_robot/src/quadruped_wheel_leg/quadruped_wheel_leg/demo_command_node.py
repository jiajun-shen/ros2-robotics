import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class DemoCommandNode(Node):
    """自动发布速度命令，让打开 RViz 后立即看到展示效果。"""

    def __init__(self):
        super().__init__('quadruped_demo_command_node')

        self.declare_parameter('cmd_topic', 'cmd_vel')
        self.declare_parameter('publish_rate_hz', 20.0)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.publisher = self.create_publisher(Twist, self.cmd_topic, 10)
        self.start_time = self.get_clock().now()
        self.last_segment_index = None

        self.segments = [
            ('forward trot', 4.5, 0.45, 0.00),
            ('left arc', 3.2, 0.34, 0.58),
            ('right arc', 3.2, 0.34, -0.58),
            ('slow reverse', 2.6, -0.26, 0.00),
            ('turn in place', 2.4, 0.00, 0.95),
            ('show stance', 1.6, 0.00, 0.00),
        ]
        self.total_duration = sum(segment[1] for segment in self.segments)

        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_command)
        self.get_logger().info(f'Auto showcase publishing /{self.cmd_topic}.')

    def publish_command(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        loop_time = math.fmod(elapsed, self.total_duration)

        accumulated = 0.0
        selected_index = 0
        selected = self.segments[0]
        for index, segment in enumerate(self.segments):
            accumulated += segment[1]
            if loop_time <= accumulated:
                selected_index = index
                selected = segment
                break

        label, _, linear_x, angular_z = selected
        if selected_index != self.last_segment_index:
            self.last_segment_index = selected_index
            self.get_logger().info(f'Demo segment: {label}')

        command = Twist()
        command.linear.x = linear_x
        command.angular.z = angular_z
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = DemoCommandNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
