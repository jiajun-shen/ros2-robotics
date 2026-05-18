import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def clamp(value, min_value, max_value):
    """把速度限制在安全范围内。"""
    return max(min_value, min(value, max_value))


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换为四元数。"""
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


class CmdVelMotionNode(Node):
    """订阅 /cmd_vel，并发布 /odom 和 odom->base_footprint TF。"""

    def __init__(self):
        super().__init__('cmd_vel_motion_node')

        # update_rate_hz：位置更新频率。
        # cmd_timeout_sec：超过这个时间没收到速度命令，就自动停车。
        # max_*：限制速度，避免键盘误操作导致数值太大。
        self.declare_parameter('update_rate_hz', 30.0)
        self.declare_parameter('cmd_timeout_sec', 0.6)
        self.declare_parameter('max_linear_speed_mps', 0.6)
        self.declare_parameter('max_angular_speed_radps', 1.5)

        self.update_rate = float(self.get_parameter('update_rate_hz').value)
        self.cmd_timeout = float(self.get_parameter('cmd_timeout_sec').value)
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)

        # 小车在 odom 坐标系下的位姿。
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # 当前收到的速度命令。
        self.linear_speed = 0.0
        self.angular_speed = 0.0

        self.last_update_time = self.get_clock().now()
        self.last_cmd_time = self.get_clock().now()

        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10,
        )
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.timer = self.create_timer(1.0 / self.update_rate, self.update_motion)

        self.get_logger().info('cmd_vel motion node started. Waiting for /cmd_vel...')

    def cmd_vel_callback(self, message):
        # /cmd_vel 里最常用的是：
        # linear.x：前进/后退速度
        # angular.z：左转/右转角速度
        self.linear_speed = clamp(
            message.linear.x,
            -self.max_linear,
            self.max_linear,
        )
        self.angular_speed = clamp(
            message.angular.z,
            -self.max_angular,
            self.max_angular,
        )
        self.last_cmd_time = self.get_clock().now()

    def update_motion(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1e9
        self.last_update_time = now

        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_timeout:
            linear_speed = 0.0
            angular_speed = 0.0
        else:
            linear_speed = self.linear_speed
            angular_speed = self.angular_speed

        # 差速小车的简化平面运动模型：
        # 沿当前朝向前进，并根据 angular.z 改变方向。
        self.x += linear_speed * math.cos(self.yaw) * dt
        self.y += linear_speed * math.sin(self.yaw) * dt
        self.yaw += angular_speed * dt
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

        quaternion = quaternion_from_yaw(self.yaw)
        self.publish_tf(now, quaternion)
        self.publish_odom(now, quaternion, linear_speed, angular_speed)

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

    def publish_odom(self, now, quaternion, linear_speed, angular_speed):
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

        odom.twist.twist.linear.x = linear_speed
        odom.twist.twist.angular.z = angular_speed

        self.odom_publisher.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelMotionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
