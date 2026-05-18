import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarSafetyFilterNode(Node):
    """根据 /scan 过滤速度命令，阻止机器人继续向近障碍物前进。"""

    def __init__(self):
        super().__init__('lidar_safety_filter_node')

        # 输入速度命令。键盘节点会发布到这里。
        self.declare_parameter('input_cmd_topic', 'cmd_vel_raw')

        # 输出速度命令。运动节点订阅这里。
        self.declare_parameter('output_cmd_topic', 'cmd_vel')

        # 雷达 topic。
        self.declare_parameter('scan_topic', 'scan')

        # 前方扇区角度范围。0.7 rad 大约是正前方 +/- 40 度。
        self.declare_parameter('front_angle_rad', 0.7)

        # 小于这个距离就认为前方太近，需要阻止继续前进。
        self.declare_parameter('stop_distance_m', 1.3)

        self.input_cmd_topic = self.get_parameter('input_cmd_topic').value
        self.output_cmd_topic = self.get_parameter('output_cmd_topic').value
        self.scan_topic = self.get_parameter('scan_topic').value
        self.front_angle = float(self.get_parameter('front_angle_rad').value)
        self.stop_distance = float(self.get_parameter('stop_distance_m').value)

        self.closest_front_distance = math.inf

        self.cmd_subscriber = self.create_subscription(
            Twist,
            self.input_cmd_topic,
            self.cmd_callback,
            10,
        )
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self.scan_callback,
            10,
        )
        self.cmd_publisher = self.create_publisher(Twist, self.output_cmd_topic, 10)

        self.get_logger().info(
            'Safety filter started: '
            f'/{self.input_cmd_topic} -> /{self.output_cmd_topic}, '
            f'stop_distance={self.stop_distance} m'
        )

    def scan_callback(self, scan):
        """从 LaserScan 中找出正前方扇区的最近障碍物距离。"""
        closest_distance = math.inf

        for index, distance in enumerate(scan.ranges):
            if not math.isfinite(distance):
                continue
            if distance < scan.range_min or distance > scan.range_max:
                continue

            angle = scan.angle_min + index * scan.angle_increment
            if abs(angle) <= self.front_angle:
                closest_distance = min(closest_distance, distance)

        self.closest_front_distance = closest_distance

    def cmd_callback(self, raw_cmd):
        """收到原始速度命令后，决定是否放行。"""
        safe_cmd = Twist()
        safe_cmd.linear.x = raw_cmd.linear.x
        safe_cmd.linear.y = raw_cmd.linear.y
        safe_cmd.linear.z = raw_cmd.linear.z
        safe_cmd.angular.x = raw_cmd.angular.x
        safe_cmd.angular.y = raw_cmd.angular.y
        safe_cmd.angular.z = raw_cmd.angular.z

        obstacle_too_close = self.closest_front_distance < self.stop_distance
        moving_forward = raw_cmd.linear.x > 0.0

        if obstacle_too_close and moving_forward:
            # 只拦截“继续向前冲”的速度，保留转向能力。
            # 这样机器人还能原地转弯，寻找安全方向。
            safe_cmd.linear.x = 0.0
            self.get_logger().warn(
                'Forward command blocked: '
                f'front obstacle at {self.closest_front_distance:.2f} m'
            )

        self.cmd_publisher.publish(safe_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = LidarSafetyFilterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
