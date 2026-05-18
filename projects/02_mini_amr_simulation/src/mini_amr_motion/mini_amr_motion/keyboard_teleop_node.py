import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP_TEXT = """
Mini AMR keyboard teleop

Controls:
  w : forward
  s : backward
  a : turn left
  d : turn right
  x : stop
  q : quit
"""


class KeyboardTeleopNode(Node):
    """读取键盘按键，并发布速度命令。"""

    def __init__(self):
        super().__init__('keyboard_teleop_node')

        self.declare_parameter('linear_speed_mps', 0.3)
        self.declare_parameter('angular_speed_radps', 0.9)
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')

        self.linear_speed = float(self.get_parameter('linear_speed_mps').value)
        self.angular_speed = float(self.get_parameter('angular_speed_radps').value)
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value

        self.publisher = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.get_logger().info(
            f'Keyboard teleop started on /{self.cmd_vel_topic}. Use w/s/a/d/x/q.'
        )

    def publish_command(self, linear_x, angular_z):
        message = Twist()
        message.linear.x = linear_x
        message.angular.z = angular_z
        self.publisher.publish(message)

    def stop(self):
        self.publish_command(0.0, 0.0)


def read_key(timeout_sec=0.1):
    """非阻塞读取一个键盘按键。"""
    ready, _, _ = select.select([sys.stdin], [], [], timeout_sec)
    if ready:
        return sys.stdin.read(1)
    return None


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleopNode()

    old_settings = termios.tcgetattr(sys.stdin)
    print(HELP_TEXT)

    try:
        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():
            key = read_key()

            if key is None:
                rclpy.spin_once(node, timeout_sec=0.0)
                continue

            if key == 'w':
                node.publish_command(node.linear_speed, 0.0)
            elif key == 's':
                node.publish_command(-node.linear_speed, 0.0)
            elif key == 'a':
                node.publish_command(0.0, node.angular_speed)
            elif key == 'd':
                node.publish_command(0.0, -node.angular_speed)
            elif key == 'x':
                node.stop()
            elif key == 'q':
                node.stop()
                break

    except KeyboardInterrupt:
        node.stop()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
