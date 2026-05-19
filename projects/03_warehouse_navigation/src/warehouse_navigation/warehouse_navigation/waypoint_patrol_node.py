import math

import rclpy
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray


def normalize_angle(angle):
    """把角度限制到 -pi 到 pi。"""
    return math.atan2(math.sin(angle), math.cos(angle))


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换成四元数。"""
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


def yaw_from_quaternion(orientation):
    """把 odom 里的四元数方向转换成平面 yaw 角。"""
    siny_cosp = 2.0 * (
        orientation.w * orientation.z + orientation.x * orientation.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        orientation.y * orientation.y + orientation.z * orientation.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class WaypointPatrolNode(Node):
    """按顺序把多个仓库航点发布到 /goal_pose。"""

    def __init__(self):
        super().__init__('waypoint_patrol_node')

        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('goal_topic', 'goal_pose')
        self.declare_parameter('marker_topic', 'waypoint_route')
        self.declare_parameter('route_name', 'aisle_inspection')
        self.declare_parameter('goal_tolerance_m', 0.18)
        self.declare_parameter('yaw_tolerance_rad', 0.35)
        self.declare_parameter('publish_rate_hz', 2.0)
        self.declare_parameter('loop_route', False)

        self.odom_topic = self.get_parameter('odom_topic').value
        self.goal_topic = self.get_parameter('goal_topic').value
        self.marker_topic = self.get_parameter('marker_topic').value
        self.route_name = str(self.get_parameter('route_name').value).strip().lower()
        self.goal_tolerance = float(self.get_parameter('goal_tolerance_m').value)
        self.yaw_tolerance = float(self.get_parameter('yaw_tolerance_rad').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)
        self.loop_route = bool(self.get_parameter('loop_route').value)

        self.waypoints = self.build_route(self.route_name)
        self.current_index = 0
        self.have_odom = False
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.route_finished = False

        self.odom_subscriber = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            10,
        )
        self.goal_publisher = self.create_publisher(PoseStamped, self.goal_topic, 10)
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            self.marker_topic,
            10,
        )
        self.timer = self.create_timer(1.0 / self.publish_rate, self.update_patrol)

        self.get_logger().info(
            f'Waypoint patrol started: route={self.route_name}, '
            f'waypoints={len(self.waypoints)}, loop={self.loop_route}'
        )

    def build_route(self, route_name):
        """创建教学用仓库路线。每个航点格式是 (x, y, yaw)。"""
        routes = {
            'short_demo': [
                (0.80, 0.00, 0.0),
                (1.55, 0.45, 0.0),
                (2.25, 0.45, 0.0),
            ],
            'aisle_inspection': [
                (0.80, 0.00, 0.0),
                (1.45, 0.55, 0.0),
                (2.45, 0.55, 0.0),
                (2.70, -0.45, -math.pi / 2.0),
                (1.40, -0.55, math.pi),
                (0.55, -0.15, math.pi),
            ],
        }

        if route_name not in routes:
            self.get_logger().warn(
                f'Unknown route_name "{route_name}", using "aisle_inspection".'
            )
            self.route_name = 'aisle_inspection'

        return routes[self.route_name]

    def odom_callback(self, odom):
        """保存小车当前位置，用来判断是否到达当前航点。"""
        self.robot_x = odom.pose.pose.position.x
        self.robot_y = odom.pose.pose.position.y
        self.robot_yaw = yaw_from_quaternion(odom.pose.pose.orientation)
        self.have_odom = True

    def update_patrol(self):
        """定时发布当前航点，并在到达后切到下一个航点。"""
        self.publish_route_markers()

        if not self.have_odom or self.route_finished:
            return

        if self.current_waypoint_reached():
            self.advance_waypoint()

        if not self.route_finished:
            self.publish_current_goal()

    def current_waypoint_reached(self):
        waypoint_x, waypoint_y, waypoint_yaw = self.waypoints[self.current_index]
        distance = math.hypot(waypoint_x - self.robot_x, waypoint_y - self.robot_y)
        yaw_error = abs(normalize_angle(waypoint_yaw - self.robot_yaw))
        return distance < self.goal_tolerance and yaw_error < self.yaw_tolerance

    def advance_waypoint(self):
        """当前航点到达后，切换到下一个航点。"""
        self.get_logger().info(
            f'Waypoint {self.current_index + 1}/{len(self.waypoints)} reached.'
        )
        self.current_index += 1

        if self.current_index < len(self.waypoints):
            return

        if self.loop_route:
            self.current_index = 0
            self.get_logger().info('Restarting waypoint route.')
            return

        self.route_finished = True
        self.get_logger().info('Waypoint route finished.')

    def publish_current_goal(self):
        """把当前航点作为 /goal_pose 发给 simple_goal_follower_node。"""
        waypoint_x, waypoint_y, waypoint_yaw = self.waypoints[self.current_index]

        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = 'odom'
        goal.pose.position.x = waypoint_x
        goal.pose.position.y = waypoint_y
        goal.pose.position.z = 0.0

        quaternion = quaternion_from_yaw(waypoint_yaw)
        goal.pose.orientation.x = quaternion['x']
        goal.pose.orientation.y = quaternion['y']
        goal.pose.orientation.z = quaternion['z']
        goal.pose.orientation.w = quaternion['w']

        self.goal_publisher.publish(goal)

    def publish_route_markers(self):
        """在 RViz 里显示航点、路线和当前目标。"""
        marker_array = MarkerArray()
        marker_array.markers.append(self.create_route_line_marker())

        for index, waypoint in enumerate(self.waypoints):
            marker_array.markers.append(self.create_waypoint_marker(index, waypoint))
            marker_array.markers.append(self.create_waypoint_label(index, waypoint))

        self.marker_publisher.publish(marker_array)

    def create_route_line_marker(self):
        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'odom'
        marker.ns = 'waypoint_route'
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.04
        marker.color.r = 0.15
        marker.color.g = 0.72
        marker.color.b = 1.0
        marker.color.a = 0.85

        for waypoint_x, waypoint_y, _ in self.waypoints:
            point = Point()
            point.x = waypoint_x
            point.y = waypoint_y
            point.z = 0.05
            marker.points.append(point)

        return marker

    def create_waypoint_marker(self, index, waypoint):
        waypoint_x, waypoint_y, _ = waypoint

        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'odom'
        marker.ns = 'waypoints'
        marker.id = 100 + index
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = waypoint_x
        marker.pose.position.y = waypoint_y
        marker.pose.position.z = 0.10
        marker.pose.orientation.w = 1.0

        is_active = index == self.current_index and not self.route_finished
        marker.scale.x = 0.20 if is_active else 0.14
        marker.scale.y = marker.scale.x
        marker.scale.z = marker.scale.x

        if is_active:
            marker.color.r = 1.0
            marker.color.g = 0.95
            marker.color.b = 0.20
        elif index < self.current_index or self.route_finished:
            marker.color.r = 0.20
            marker.color.g = 0.80
            marker.color.b = 0.35
        else:
            marker.color.r = 0.15
            marker.color.g = 0.72
            marker.color.b = 1.0

        marker.color.a = 0.90
        return marker

    def create_waypoint_label(self, index, waypoint):
        waypoint_x, waypoint_y, _ = waypoint

        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'odom'
        marker.ns = 'waypoint_labels'
        marker.id = 200 + index
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.x = waypoint_x
        marker.pose.position.y = waypoint_y
        marker.pose.position.z = 0.35
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.22
        marker.color.r = 0.95
        marker.color.g = 0.95
        marker.color.b = 0.95
        marker.color.a = 0.95
        marker.text = f'WP{index + 1}'
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = WaypointPatrolNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
