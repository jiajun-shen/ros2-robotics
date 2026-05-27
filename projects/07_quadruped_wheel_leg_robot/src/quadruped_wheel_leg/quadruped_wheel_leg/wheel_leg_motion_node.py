import math

import rclpy
from geometry_msgs.msg import Point, PoseStamped, TransformStamped, Twist
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
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
DRIVE_MODES = ('walk', 'wheel', 'hybrid')


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
        self.declare_parameter('drive_mode_topic', 'quadruped_drive_mode')
        self.declare_parameter('drive_mode', 'hybrid')
        self.declare_parameter('update_rate_hz', 40.0)
        self.declare_parameter('cmd_timeout_sec', 0.7)
        self.declare_parameter('max_linear_speed_mps', 0.75)
        self.declare_parameter('max_lateral_speed_mps', 0.45)
        self.declare_parameter('max_angular_speed_radps', 1.45)
        self.declare_parameter('robot_mass_kg', 12.3)
        self.declare_parameter('track_width_m', 0.44)
        self.declare_parameter('wheel_radius_m', 0.075)
        self.declare_parameter('path_publish_stride', 4)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.drive_mode_topic = self.get_parameter('drive_mode_topic').value
        self.drive_mode = self.sanitize_drive_mode(
            self.get_parameter('drive_mode').value
        )
        self.update_rate = float(self.get_parameter('update_rate_hz').value)
        self.cmd_timeout = float(self.get_parameter('cmd_timeout_sec').value)
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_lateral = float(self.get_parameter('max_lateral_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)
        self.robot_mass = float(self.get_parameter('robot_mass_kg').value)
        self.track_width = float(self.get_parameter('track_width_m').value)
        self.wheel_radius = float(self.get_parameter('wheel_radius_m').value)
        self.path_publish_stride = int(self.get_parameter('path_publish_stride').value)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.gait_phase = 0.0
        self.body_bob = 0.0
        self.forward_speed = 0.0
        self.lateral_speed = 0.0
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
        self.drive_mode_subscriber = self.create_subscription(
            String,
            self.drive_mode_topic,
            self.drive_mode_callback,
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
            f'Wheel-leg quadruped started. Listening to /{self.cmd_topic}; '
            f'drive mode={self.drive_mode}.'
        )

    def sanitize_drive_mode(self, mode):
        mode_text = str(mode).strip().lower()
        if mode_text not in DRIVE_MODES:
            return 'hybrid'
        return mode_text

    def cmd_vel_callback(self, message):
        """接收速度命令：linear.x 前后，linear.y 横移，angular.z 原地转向。"""
        self.forward_speed = clamp(
            message.linear.x,
            -self.max_linear,
            self.max_linear,
        )
        self.lateral_speed = clamp(
            message.linear.y,
            -self.max_lateral,
            self.max_lateral,
        )
        self.angular_speed = clamp(
            message.angular.z,
            -self.max_angular,
            self.max_angular,
        )
        self.last_cmd_time = self.get_clock().now()

    def drive_mode_callback(self, message):
        """切换步行/轮行/混合模式。"""
        next_mode = self.sanitize_drive_mode(message.data)
        if next_mode != self.drive_mode:
            self.drive_mode = next_mode
            self.get_logger().info(f'Drive mode changed to {self.drive_mode}.')

    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1e9
        self.last_update_time = now
        self.tick_count += 1

        forward, lateral, angular = self.get_active_command(now)
        self.integrate_base_motion(dt, forward, lateral, angular)
        moving_strength = self.update_gait(dt, forward, lateral, angular)

        quaternion = quaternion_from_yaw(self.yaw)
        self.publish_tf(now, quaternion)
        self.publish_odom(now, quaternion, forward, lateral, angular)
        self.publish_joint_states(now, dt, forward, lateral, angular, moving_strength)
        self.publish_path(now)
        self.publish_markers(now, forward, lateral, angular, moving_strength)

    def get_active_command(self, now):
        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_timeout:
            return 0.0, 0.0, 0.0
        return self.forward_speed, self.lateral_speed, self.angular_speed

    def integrate_base_motion(self, dt, forward, lateral, angular):
        # ROS 机器人坐标系里 x 是前方，y 是左方。这里把机体坐标速度转换到 odom 坐标。
        self.x += (forward * math.cos(self.yaw) - lateral * math.sin(self.yaw)) * dt
        self.y += (forward * math.sin(self.yaw) + lateral * math.cos(self.yaw)) * dt
        self.yaw += angular * dt
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

    def update_gait(self, dt, forward, lateral, angular):
        leg_blend, _ = self.drive_mode_blend()
        translation_speed = math.hypot(forward, lateral)
        command_strength = min(
            1.0,
            translation_speed / 0.60 + 0.45 * abs(angular) / self.max_angular,
        )
        gait_strength = command_strength * leg_blend

        if command_strength > 0.02:
            gait_frequency_hz = 1.05 + 1.35 * max(gait_strength, 0.28 * command_strength)
            if abs(forward) > 0.03:
                direction = -1.0 if forward < 0.0 else 1.0
            elif abs(lateral) > 0.03:
                direction = -1.0 if lateral < 0.0 else 1.0
            else:
                direction = -1.0 if angular < 0.0 else 1.0
            self.gait_phase += direction * 2.0 * math.pi * gait_frequency_hz * dt
            spring_wave = max(0.0, math.sin(self.gait_phase * 2.0))
            self.body_bob = 0.006 + 0.026 * gait_strength * spring_wave
        else:
            self.body_bob *= 0.85

        self.gait_phase = math.atan2(math.sin(self.gait_phase), math.cos(self.gait_phase))
        return command_strength

    def drive_mode_blend(self):
        """返回腿部步态权重和轮足滚动权重。"""
        if self.drive_mode == 'walk':
            return 1.0, 0.18
        if self.drive_mode == 'wheel':
            return 0.18, 1.0
        return 0.68, 1.0

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

    def publish_odom(self, now, quaternion, forward, lateral, angular):
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
        odom.twist.twist.linear.x = forward
        odom.twist.twist.linear.y = lateral
        odom.twist.twist.angular.z = angular
        self.odom_publisher.publish(odom)

    def publish_joint_states(self, now, dt, forward, lateral, angular, moving_strength):
        joint_state = JointState()
        joint_state.header.stamp = now.to_msg()

        names = []
        positions = []
        forward_ratio = forward / self.max_linear if self.max_linear > 0.0 else 0.0
        lateral_ratio = lateral / self.max_lateral if self.max_lateral > 0.0 else 0.0
        turn_ratio = angular / self.max_angular if self.max_angular > 0.0 else 0.0
        leg_blend, wheel_blend = self.drive_mode_blend()
        gait_strength = moving_strength * leg_blend
        forward_step = min(1.0, abs(forward_ratio))
        lateral_step = min(1.0, abs(lateral_ratio))
        turn_step = min(1.0, abs(turn_ratio))

        for leg in LEG_ORDER:
            leg_phase = self.gait_phase + LEG_PHASE_OFFSETS[leg]
            swing_lift = max(0.0, math.sin(leg_phase))
            side_sign = 1.0 if leg.endswith('left') else -1.0
            fore_sign = 1.0 if leg.startswith('front') else -1.0

            hip_abduction = (
                0.07 * side_sign
                + 0.38 * gait_strength * lateral_ratio * math.sin(leg_phase)
                + 0.13 * gait_strength * side_sign * turn_step * math.cos(leg_phase)
            )
            hip_pitch = (
                0.50 * gait_strength * forward_step * math.sin(leg_phase) * (1.0 if forward >= 0.0 else -1.0)
                + 0.12 * gait_strength * lateral_step * side_sign * math.cos(leg_phase)
                + 0.40 * gait_strength * side_sign * turn_ratio * math.sin(leg_phase)
                + 0.06 * (1.0 - leg_blend) * forward_ratio
            )
            knee_angle = (
                -0.66
                + 0.12 * gait_strength * math.cos(leg_phase)
                - 0.31 * gait_strength * swing_lift
                - 0.05 * gait_strength * turn_step * fore_sign * side_sign
                + 0.04 * (1.0 - leg_blend) * abs(forward_ratio)
            )

            # 履轮/轮足负责前后滚动和差速转向；横移仍主要靠腿部侧摆步态完成。
            wheel_linear_speed = (
                forward - angular * side_sign * self.track_width * 0.5
            ) * wheel_blend
            self.wheel_angles[leg] += wheel_linear_speed * dt / self.wheel_radius

            names.extend([
                f'{leg}_hip_abduction_joint',
                f'{leg}_hip_joint',
                f'{leg}_knee_joint',
                f'{leg}_wheel_joint',
            ])
            positions.extend([
                hip_abduction,
                hip_pitch,
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

    def publish_markers(self, now, forward, lateral, angular, moving_strength):
        markers = MarkerArray()
        markers.markers.append(self.make_ground_marker(now))
        markers.markers.append(self.make_command_arrow_marker(now, forward, lateral, angular))
        markers.markers.append(
            self.make_status_text_marker(now, forward, lateral, angular, moving_strength)
        )
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

    def make_command_arrow_marker(self, now, forward, lateral, angular):
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
        translation = math.hypot(forward, lateral)
        if translation > 0.03:
            end.x = forward * 0.95
            end.y = lateral * 1.15
        else:
            end.x = 0.0
            end.y = 0.24 * (1.0 if angular >= 0.0 else -1.0)
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

    def make_status_text_marker(self, now, forward, lateral, angular, moving_strength):
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
            f'wheel-leg quadruped | mode={self.drive_mode} | mass={self.robot_mass:.1f} kg | '
            f'vx={forward:+.2f} vy={lateral:+.2f} wz={angular:+.2f} | '
            f'gait={moving_strength:.2f}'
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
