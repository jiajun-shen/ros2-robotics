import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换成四元数。

    ROS 2 里的姿态通常用 quaternion 表示。
    对移动小车来说，我们暂时只关心绕 z 轴旋转的 yaw。
    """
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


class CircleMotionNode(Node):
    """发布一个简化的 AMR 圆周运动 odom 和 TF。"""

    def __init__(self):
        super().__init__('circle_motion_node')

        # 这些参数决定小车怎么动。
        # linear_speed_mps：线速度，单位 m/s。
        # angular_speed_radps：角速度，单位 rad/s。
        # update_rate_hz：每秒更新多少次。
        self.declare_parameter('linear_speed_mps', 0.25)
        self.declare_parameter('angular_speed_radps', 0.45)
        self.declare_parameter('update_rate_hz', 30.0)

        self.linear_speed = float(self.get_parameter('linear_speed_mps').value)
        self.angular_speed = float(self.get_parameter('angular_speed_radps').value)
        self.update_rate = float(self.get_parameter('update_rate_hz').value)

        # 小车在 odom 坐标系下的位置和朝向。
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.last_time = self.get_clock().now()

        # /odom 是移动机器人非常常见的话题，表示里程计估计。
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)

        # TF broadcaster 用来发布 odom -> base_footprint 的坐标变换。
        self.tf_broadcaster = TransformBroadcaster(self)

        timer_period = 1.0 / self.update_rate
        self.timer = self.create_timer(timer_period, self.update_motion)

        self.get_logger().info(
            'Circle motion started: '
            f'linear={self.linear_speed} m/s, '
            f'angular={self.angular_speed} rad/s'
        )

    def update_motion(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # 简化平面运动模型：
        # 小车沿当前朝向前进，同时以固定角速度转弯。
        self.x += self.linear_speed * math.cos(self.yaw) * dt
        self.y += self.linear_speed * math.sin(self.yaw) * dt
        self.yaw += self.angular_speed * dt

        # 避免 yaw 无限变大，保持在 -pi 到 pi 附近，方便阅读。
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

        quaternion = quaternion_from_yaw(self.yaw)

        self.publish_tf(now, quaternion)
        self.publish_odom(now, quaternion)

    def publish_tf(self, now, quaternion):
        transform = TransformStamped()
        transform.header.stamp = now.to_msg()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'

        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0

        transform.transform.rotation.x = quaternion['x']
        transform.transform.rotation.y = quaternion['y']
        transform.transform.rotation.z = quaternion['z']
        transform.transform.rotation.w = quaternion['w']

        self.tf_broadcaster.sendTransform(transform)

    def publish_odom(self, now, quaternion):
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        odom.pose.pose.orientation.x = quaternion['x']
        odom.pose.pose.orientation.y = quaternion['y']
        odom.pose.pose.orientation.z = quaternion['z']
        odom.pose.pose.orientation.w = quaternion['w']

        odom.twist.twist.linear.x = self.linear_speed
        odom.twist.twist.angular.z = self.angular_speed

        self.odom_publisher.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = CircleMotionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
