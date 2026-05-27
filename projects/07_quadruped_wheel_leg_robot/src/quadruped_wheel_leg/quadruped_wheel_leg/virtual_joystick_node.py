import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


HELP_TEXT = """
Virtual joystick for the wheel-leg quadruped

  w/s : forward / backward
  a/d : side-step left / side-step right
  q/e : turn left / turn right
  1/2/3 : walk / wheel / hybrid drive mode
  space : stop
  x : exit
"""


class VirtualJoystickNode(Node):
    """终端键盘摇杆：把 w/s/a/d 转换成 /cmd_vel。"""

    def __init__(self):
        super().__init__('quadruped_virtual_joystick_node')

        self.declare_parameter('cmd_topic', 'cmd_vel')
        self.declare_parameter('drive_mode_topic', 'quadruped_drive_mode')
        self.declare_parameter('linear_step_mps', 0.12)
        self.declare_parameter('lateral_step_mps', 0.08)
        self.declare_parameter('angular_step_radps', 0.22)
        self.declare_parameter('max_linear_speed_mps', 0.65)
        self.declare_parameter('max_lateral_speed_mps', 0.42)
        self.declare_parameter('max_angular_speed_radps', 1.35)
        self.declare_parameter('publish_rate_hz', 12.0)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.drive_mode_topic = self.get_parameter('drive_mode_topic').value
        self.linear_step = float(self.get_parameter('linear_step_mps').value)
        self.lateral_step = float(self.get_parameter('lateral_step_mps').value)
        self.angular_step = float(self.get_parameter('angular_step_radps').value)
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_lateral = float(self.get_parameter('max_lateral_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        self.drive_mode = 'hybrid'
        self.publisher = self.create_publisher(Twist, self.cmd_topic, 10)
        self.mode_publisher = self.create_publisher(
            String,
            self.drive_mode_topic,
            10,
        )

        self.stdin_is_tty = sys.stdin.isatty()
        self.original_terminal_settings = None
        if self.stdin_is_tty:
            self.original_terminal_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            print(HELP_TEXT)
        else:
            self.get_logger().warn(
                'stdin is not a TTY, so keyboard control is disabled.'
            )

        self.timer = self.create_timer(1.0 / self.publish_rate, self.update)

    def update(self):
        key = self.read_key()
        if key:
            self.handle_key(key)
        self.publish_command()

    def read_key(self):
        if not self.stdin_is_tty:
            return None

        ready, _, _ = select.select([sys.stdin], [], [], 0.0)
        if not ready:
            return None
        return sys.stdin.read(1)

    def handle_key(self, key):
        if key == 'w':
            self.linear_x = min(self.max_linear, self.linear_x + self.linear_step)
        elif key == 's':
            self.linear_x = max(-self.max_linear, self.linear_x - self.linear_step)
        elif key == 'a':
            self.linear_y = min(self.max_lateral, self.linear_y + self.lateral_step)
        elif key == 'd':
            self.linear_y = max(-self.max_lateral, self.linear_y - self.lateral_step)
        elif key == 'q':
            self.angular_z = min(self.max_angular, self.angular_z + self.angular_step)
        elif key == 'e':
            self.angular_z = max(-self.max_angular, self.angular_z - self.angular_step)
        elif key == '1':
            self.set_drive_mode('walk')
        elif key == '2':
            self.set_drive_mode('wheel')
        elif key == '3':
            self.set_drive_mode('hybrid')
        elif key == ' ':
            self.linear_x = 0.0
            self.linear_y = 0.0
            self.angular_z = 0.0
        elif key == 'x':
            self.linear_x = 0.0
            self.linear_y = 0.0
            self.angular_z = 0.0
            self.publish_command()
            self.get_logger().info('Keyboard joystick exiting.')
            rclpy.shutdown()
            return

        self.get_logger().info(
            f'mode={self.drive_mode}, '
            f'linear.x={self.linear_x:+.2f}, '
            f'linear.y={self.linear_y:+.2f}, '
            f'angular.z={self.angular_z:+.2f}'
        )

    def set_drive_mode(self, mode):
        if mode not in ('walk', 'wheel', 'hybrid'):
            return
        self.drive_mode = mode
        self.publish_mode()

    def publish_mode(self):
        message = String()
        message.data = self.drive_mode
        self.mode_publisher.publish(message)

    def publish_command(self):
        command = Twist()
        command.linear.x = self.linear_x
        command.linear.y = self.linear_y
        command.angular.z = self.angular_z
        self.publisher.publish(command)
        self.publish_mode()

    def restore_terminal(self):
        if self.original_terminal_settings is not None:
            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                self.original_terminal_settings,
            )


def main(args=None):
    rclpy.init(args=args)
    node = VirtualJoystickNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.restore_terminal()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
