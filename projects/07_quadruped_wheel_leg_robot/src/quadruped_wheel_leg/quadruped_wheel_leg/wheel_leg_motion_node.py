import math

import rclpy
from geometry_msgs.msg import Point, PoseStamped, TransformStamped, Twist
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker, MarkerArray


LEG_PHASE_OFFSETS = {
    # Trot 步态：左前 + 右后同相，右前 + 左后同相。
    'front_left': 0.0,
    'rear_right': 0.0,
    'front_right': math.pi,
    'rear_left': math.pi,
}

LEG_ORDER = ['front_left', 'front_right', 'rear_left', 'rear_right']


def clamp(value, min_value, max_value):
    """把速度限制在安全范围内，避免输入过大导致 RViz 里运动太快。"""
    return max(min_value, min(value, max_value))


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换成四元数。"""
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


class WheelLegMotionNode(Node):
    """轮腿式四足机器人 RViz 仿真核心节点。"""

    def __init__(self):
        super().__init__('wheel_leg_motion_node')

        self.declare_parameter('cmd_topic', 'cmd_vel')
        self.declare_parameter('update_rate_hz', 40.0)
        self.declare_parameter('cmd_timeout_sec', 0.7)
        self.declare_parameter('max_linear_speed_mps', 0.75)
        self.declare_parameter('max_angular_speed_radps', 1.45)
        self.declare_parameter('track_width_m', 0.44)
        self.declare_parameter('wheel_radius_m', 0.075)
        self.declare_parameter('path_publish_stride', 4)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.update_rate = float(self.get_parameter('update_rate_hz').value)
        self.cmd_timeout = float(self.get_parameter('cmd_timeout_sec').value)
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)
        self.track_width = float(self.get_parameter('track_width_m').value)
        self.wheel_radius = float(self.get_parameter('wheel_radius_m').value)
        self.path_publish_stride = int(self.get_parameter('path_publish_stride').value)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.gait_phase = 0.0
        self.body_bob = 0.0
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.wheel_angles = {leg: 0.0 for leg in LEG_ORDER}

        self.last_update_time = self.get_clock().now()
        self.last_cmd_time = self.get_clock().now()
        self.tick_count = 0

        self.path = Path()
        self.path.header.frame_id = 'odom'

        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            self.cmd_topic,
            self.cmd_vel_callback,
            10,
        )
        self.joint_publisher = self.create_publisher(JointState, 'joint_states', 10)
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.path_publisher = self.create_publisher(Path, 'quadruped_path', 10)
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            'quadruped_status',
            10,
        )
        self.tf_broadcaster = TransformBroadcaster(self)

        self.timer = self.create_timer(1.0 / self.update_rate, self.update)

        self.get_logger().info(
            f'Wheel-leg quadruped started. Listening to /{self.cmd_topic}.'
        )

    def cmd_vel_callback(self, message):
        """接收速度命令：linear.x 控制前后，angular.z 控制左右转。"""
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

    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1e9
        self.last_update_time = now
        self.tick_count += 1

        linear, angular = self.get_active_command(now)
        self.integrate_base_motion(dt, linear, angular)
        moving_strength = self.update_gait(dt, linear, angular)

        quaternion = quaternion_from_yaw(self.yaw)
        self.publish_tf(now, quaternion)
        self.publish_odom(now, quaternion, linear, angular)
        self.publish_joint_states(now, dt, linear, angular, moving_strength)
        self.publish_path(now)
        self.publish_markers(now, linear, angular, moving_strength)

    def get_active_command(self, now):
        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_timeout:
            return 0.0, 0.0
        return self.linear_speed, self.angular_speed

    def integrate_base_motion(self, dt, linear, angular):
        self.x += linear * math.cos(self.yaw) * dt
        self.y += linear * math.sin(self.yaw) * dt
        self.yaw += angular * dt
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

    def update_gait(self, dt, linear, angular):
        command_strength = min(1.0, abs(linear) / 0.55 + abs(angular) / 1.8)

        if command_strength > 0.02:
            gait_frequency_hz = 1.15 + 1.25 * command_strength
            direction = -1.0 if linear < -0.03 else 1.0
            self.gait_phase += direction * 2.0 * math.pi * gait_frequency_hz * dt
            self.body_bob = 0.020 * command_strength * max(
                0.0,
                math.sin(self.gait_phase * 2.0),
            )
        else:
            self.body_bob *= 0.85

        self.gait_phase = math.atan2(math.sin(self.gait_phase), math.cos(self.gait_phase))
        return command_strength

    def publish_tf(self, now, quaternion):
        transform = TransformStamped()
        transform.header.stamp = now.to_msg()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = self.body_bob
        transform.transform.rotation.x = quaternion['x']
        transform.transform.rotation.y = quaternion['y']
        transform.transform.rotation.z = quaternion['z']
        transform.transform.rotation.w = quaternion['w']
        self.tf_broadcaster.sendTransform(transform)

    def publish_odom(self, now, quaternion, linear, angular):
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = self.body_bob
        odom.pose.pose.orientation.x = quaternion['x']
        odom.pose.pose.orientation.y = quaternion['y']
        odom.pose.pose.orientation.z = quaternion['z']
        odom.pose.pose.orientation.w = quaternion['w']
        odom.twist.twist.linear.x = linear
        odom.twist.twist.angular.z = angular
        self.odom_publisher.publish(odom)

    def publish_joint_states(self, now, dt, linear, angular, moving_strength):
        joint_state = JointState()
        joint_state.header.stamp = now.to_msg()

        names = []
        positions = []

        for leg in LEG_ORDER:
            leg_phase = self.gait_phase + LEG_PHASE_OFFSETS[leg]
            hip_angle = 0.46 * moving_strength * math.sin(leg_phase)
            knee_angle = -0.62 + 0.24 * moving_strength * math.cos(leg_phase)

            side_sign = 1.0 if leg.endswith('left') else -1.0
            wheel_linear_speed = linear - angular * side_sign * self.track_width * 0.5
            self.wheel_angles[leg] += wheel_linear_speed * dt / self.wheel_radius

            names.extend([
                f'{leg}_hip_joint',
                f'{leg}_knee_joint',
                f'{leg}_wheel_joint',
            ])
            positions.extend([
                hip_angle,
                knee_angle,
                self.wheel_angles[leg],
            ])

        joint_state.name = names
        joint_state.position = positions
        self.joint_publisher.publish(joint_state)

    def publish_path(self, now):
        if self.tick_count % max(1, self.path_publish_stride) != 0:
            return

        pose = PoseStamped()
        pose.header.stamp = now.to_msg()
        pose.header.frame_id = 'odom'
        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        pose.pose.position.z = 0.02
        quaternion = quaternion_from_yaw(self.yaw)
        pose.pose.orientation.x = quaternion['x']
        pose.pose.orientation.y = quaternion['y']
        pose.pose.orientation.z = quaternion['z']
        pose.pose.orientation.w = quaternion['w']

        self.path.header.stamp = now.to_msg()
        self.path.poses.append(pose)
        self.path.poses = self.path.poses[-700:]
        self.path_publisher.publish(self.path)

    def publish_markers(self, now, linear, angular, moving_strength):
        markers = MarkerArray()
        markers.markers.append(self.make_ground_marker(now))
        markers.markers.append(self.make_command_arrow_marker(now, linear, angular))
        markers.markers.append(self.make_status_text_marker(now, linear, angular, moving_strength))
        self.marker_publisher.publish(markers)

    def make_ground_marker(self, now):
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = now.to_msg()
        marker.ns = 'quadruped_scene'
        marker.id = 1
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = -0.035
        marker.scale.x = 6.0
        marker.scale.y = 4.0
        marker.scale.z = 0.02
        marker.color.r = 0.10
        marker.color.g = 0.12
        marker.color.b = 0.13
        marker.color.a = 0.45
        return marker

    def make_command_arrow_marker(self, now, linear, angular):
        marker = Marker()
        marker.header.frame_id = 'base_footprint'
        marker.header.stamp = now.to_msg()
        marker.ns = 'quadruped_status'
        marker.id = 2
        marker.type = Marker.ARROW
        marker.action = Marker.ADD

        start = Point()
        start.x = 0.0
        start.y = 0.0
        start.z = 0.16

        end = Point()
        end.x = max(0.18, abs(linear) * 1.0) * (1.0 if linear >= 0.0 else -1.0)
        end.y = angular * 0.22
        end.z = 0.16

        marker.points = [start, end]
        marker.scale.x = 0.035
        marker.scale.y = 0.075
        marker.scale.z = 0.11
        marker.color.r = 0.00
        marker.color.g = 0.85
        marker.color.b = 1.00
        marker.color.a = 0.85
        return marker

    def make_status_text_marker(self, now, linear, angular, moving_strength):
        marker = Marker()
        marker.header.frame_id = 'base_footprint'
        marker.header.stamp = now.to_msg()
        marker.ns = 'quadruped_status'
        marker.id = 3
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.z = 0.92
        marker.scale.z = 0.11
        marker.color.r = 0.92
        marker.color.g = 0.96
        marker.color.b = 1.00
        marker.color.a = 0.95
        marker.text = (
            f'wheel-leg quadruped | v={linear:+.2f} m/s '
            f'w={angular:+.2f} rad/s | gait={moving_strength:.2f}'
        )
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = WheelLegMotionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
