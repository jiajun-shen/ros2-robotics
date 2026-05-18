import math

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


def clamp(value, min_value, max_value):
    """把数值限制在指定范围内。"""
    return max(min_value, min(value, max_value))


def normalize_angle(angle):
    """把角度限制到 -pi 到 pi，方便计算转向误差。"""
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_quaternion(orientation):
    """把四元数方向转换成平面导航里常用的 yaw 角。"""
    siny_cosp = 2.0 * (
        orientation.w * orientation.z + orientation.x * orientation.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        orientation.y * orientation.y + orientation.z * orientation.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class SimpleGoalFollowerNode(Node):
    """一个最小版导航控制器：根据 /odom 朝目标点发布 /cmd_vel_raw。"""

    def __init__(self):
        super().__init__('simple_goal_follower_node')

        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('goal_topic', 'goal_pose')
        self.declare_parameter('cmd_topic', 'cmd_vel_raw')
        self.declare_parameter('control_rate_hz', 20.0)

        # 默认目标点在 odom 坐标系里，单位是米和弧度。
        self.declare_parameter('goal_x_m', 2.0)
        self.declare_parameter('goal_y_m', 0.6)
        self.declare_parameter('goal_yaw_rad', 0.0)

        # 控制器参数。先用保守速度，方便初学者观察 RViz。
        self.declare_parameter('goal_tolerance_m', 0.10)
        self.declare_parameter('yaw_tolerance_rad', 0.18)
        self.declare_parameter('heading_tolerance_rad', 0.25)
        self.declare_parameter('max_linear_speed_mps', 0.35)
        self.declare_parameter('max_angular_speed_radps', 0.9)
        self.declare_parameter('linear_gain', 0.7)
        self.declare_parameter('angular_gain', 1.6)

        self.odom_topic = self.get_parameter('odom_topic').value
        self.goal_topic = self.get_parameter('goal_topic').value
        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.control_rate = float(self.get_parameter('control_rate_hz').value)

        self.goal_x = float(self.get_parameter('goal_x_m').value)
        self.goal_y = float(self.get_parameter('goal_y_m').value)
        self.goal_yaw = float(self.get_parameter('goal_yaw_rad').value)

        self.goal_tolerance = float(self.get_parameter('goal_tolerance_m').value)
        self.yaw_tolerance = float(self.get_parameter('yaw_tolerance_rad').value)
        self.heading_tolerance = float(
            self.get_parameter('heading_tolerance_rad').value
        )
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)
        self.linear_gain = float(self.get_parameter('linear_gain').value)
        self.angular_gain = float(self.get_parameter('angular_gain').value)

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.have_odom = False
        self.goal_reached = False

        self.odom_subscriber = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            10,
        )
        self.goal_subscriber = self.create_subscription(
            PoseStamped,
            self.goal_topic,
            self.goal_callback,
            10,
        )
        self.cmd_publisher = self.create_publisher(Twist, self.cmd_topic, 10)
        self.timer = self.create_timer(1.0 / self.control_rate, self.control_loop)

        self.get_logger().info(
            'Simple goal follower started: '
            f'goal=({self.goal_x:.2f}, {self.goal_y:.2f}), '
            f'publishing /{self.cmd_topic}'
        )

    def odom_callback(self, odom):
        """保存机器人当前位置。/odom 是导航控制器最重要的反馈。"""
        self.robot_x = odom.pose.pose.position.x
        self.robot_y = odom.pose.pose.position.y
        self.robot_yaw = yaw_from_quaternion(odom.pose.pose.orientation)
        self.have_odom = True

    def goal_callback(self, goal):
        """以后你可以通过 /goal_pose topic 临时发送新目标点。"""
        self.goal_x = goal.pose.position.x
        self.goal_y = goal.pose.position.y
        self.goal_yaw = yaw_from_quaternion(goal.pose.orientation)
        self.goal_reached = False
        self.get_logger().info(
            f'Received new goal: ({self.goal_x:.2f}, {self.goal_y:.2f})'
        )

    def control_loop(self):
        """核心导航逻辑：看当前位置和目标点的误差，算出速度命令。"""
        command = Twist()

        if not self.have_odom:
            self.cmd_publisher.publish(command)
            return

        error_x = self.goal_x - self.robot_x
        error_y = self.goal_y - self.robot_y
        distance_to_goal = math.hypot(error_x, error_y)

        if distance_to_goal > self.goal_tolerance:
            self.drive_toward_goal(command, error_x, error_y, distance_to_goal)
        else:
            self.rotate_to_goal_yaw(command)

        self.cmd_publisher.publish(command)

    def drive_toward_goal(self, command, error_x, error_y, distance_to_goal):
        """还没到目标点时，先转向目标，再向前走。"""
        angle_to_goal = math.atan2(error_y, error_x)
        heading_error = normalize_angle(angle_to_goal - self.robot_yaw)

        angular_speed = self.angular_gain * heading_error
        command.angular.z = clamp(
            angular_speed,
            -self.max_angular,
            self.max_angular,
        )

        # 如果车头偏得比较多，先原地转正；这样小车不会斜着乱冲。
        if abs(heading_error) > self.heading_tolerance:
            command.linear.x = 0.0
            return

        linear_speed = self.linear_gain * distance_to_goal
        command.linear.x = clamp(linear_speed, 0.0, self.max_linear)

    def rotate_to_goal_yaw(self, command):
        """已经到目标点附近后，再把车头方向转到目标 yaw。"""
        yaw_error = normalize_angle(self.goal_yaw - self.robot_yaw)

        if abs(yaw_error) > self.yaw_tolerance:
            command.angular.z = clamp(
                self.angular_gain * yaw_error,
                -self.max_angular,
                self.max_angular,
            )
            return

        command.linear.x = 0.0
        command.angular.z = 0.0

        if not self.goal_reached:
            self.goal_reached = True
            self.get_logger().info(
                f'Goal reached near ({self.robot_x:.2f}, {self.robot_y:.2f})'
            )


def main(args=None):
    rclpy.init(args=args)
    node = SimpleGoalFollowerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
