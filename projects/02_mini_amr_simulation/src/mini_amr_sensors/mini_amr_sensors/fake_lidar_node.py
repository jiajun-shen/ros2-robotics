import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class FakeLidarNode(Node):
    """发布一个简化版 2D 激光雷达 /scan。

    这个节点不是物理仿真。它的目标是帮你理解 LaserScan 消息、
    lidar_link 坐标系，以及 RViz 里雷达数据是怎么显示的。
    """

    def __init__(self):
        super().__init__('fake_lidar_node')

        self.declare_parameter('scan_topic', 'scan')
        self.declare_parameter('frame_id', 'lidar_link')
        self.declare_parameter('scan_rate_hz', 10.0)
        self.declare_parameter('range_min_m', 0.12)
        self.declare_parameter('range_max_m', 3.5)
        self.declare_parameter('num_readings', 181)

        self.scan_topic = self.get_parameter('scan_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.scan_rate_hz = float(self.get_parameter('scan_rate_hz').value)
        self.range_min = float(self.get_parameter('range_min_m').value)
        self.range_max = float(self.get_parameter('range_max_m').value)
        self.num_readings = int(self.get_parameter('num_readings').value)

        self.angle_min = -math.pi
        self.angle_max = math.pi
        self.angle_increment = (self.angle_max - self.angle_min) / (self.num_readings - 1)

        self.publisher = self.create_publisher(LaserScan, self.scan_topic, 10)
        self.timer = self.create_timer(1.0 / self.scan_rate_hz, self.publish_scan)
        self.phase = 0.0

        self.get_logger().info(
            f'Fake lidar publishing /{self.scan_topic} in frame {self.frame_id}'
        )

    def publish_scan(self):
        message = LaserScan()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = self.frame_id

        message.angle_min = self.angle_min
        message.angle_max = self.angle_max
        message.angle_increment = self.angle_increment
        message.time_increment = 0.0
        message.scan_time = 1.0 / self.scan_rate_hz
        message.range_min = self.range_min
        message.range_max = self.range_max

        # 构造一个容易在 RViz 里看见的假环境：
        # 前方有一堵较近的墙，左右两侧有稍远的障碍。
        ranges = []
        for index in range(self.num_readings):
            angle = self.angle_min + index * self.angle_increment

            if abs(angle) < 0.35:
                distance = 1.1
            elif abs(abs(angle) - math.pi / 2.0) < 0.25:
                distance = 1.7
            else:
                distance = 2.8

            # 加一点很小的波动，让数据看起来不是完全死板的常数。
            distance += 0.05 * math.sin(4.0 * angle + self.phase)
            distance = max(self.range_min, min(distance, self.range_max))
            ranges.append(distance)

        self.phase += 0.08
        message.ranges = ranges
        message.intensities = [1.0] * self.num_readings

        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = FakeLidarNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
