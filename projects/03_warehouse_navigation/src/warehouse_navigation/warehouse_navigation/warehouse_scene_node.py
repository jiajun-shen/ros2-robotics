import math

from geometry_msgs.msg import Point, PoseStamped
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray


def yaw_from_quaternion(orientation):
    """把 PoseStamped 里的四元数方向转换成 yaw 角。"""
    siny_cosp = 2.0 * (
        orientation.w * orientation.z + orientation.x * orientation.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        orientation.y * orientation.y + orientation.z * orientation.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class WarehouseSceneNode(Node):
    """发布仓库货架、目标点和参考路径的 RViz marker。"""

    def __init__(self):
        super().__init__('warehouse_scene_node')

        self.declare_parameter('marker_topic', 'warehouse_scene')
        self.declare_parameter('goal_topic', 'goal_pose')
        self.declare_parameter('goal_x_m', 2.0)
        self.declare_parameter('goal_y_m', 0.6)
        self.declare_parameter('goal_yaw_rad', 0.0)
        self.declare_parameter('publish_rate_hz', 2.0)

        self.marker_topic = self.get_parameter('marker_topic').value
        self.goal_topic = self.get_parameter('goal_topic').value
        self.goal_x = float(self.get_parameter('goal_x_m').value)
        self.goal_y = float(self.get_parameter('goal_y_m').value)
        self.goal_yaw = float(self.get_parameter('goal_yaw_rad').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.goal_subscriber = self.create_subscription(
            PoseStamped,
            self.goal_topic,
            self.goal_callback,
            10,
        )
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            self.marker_topic,
            10,
        )
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_scene)

        self.get_logger().info(
            f'Warehouse scene publishing /{self.marker_topic} markers.'
        )

    def goal_callback(self, goal):
        """收到新目标点后，更新 RViz 里的绿色目标点和参考线。"""
        self.goal_x = goal.pose.position.x
        self.goal_y = goal.pose.position.y
        self.goal_yaw = yaw_from_quaternion(goal.pose.orientation)
        self.get_logger().info(
            f'Warehouse scene goal updated: ({self.goal_x:.2f}, {self.goal_y:.2f})'
        )

    def publish_scene(self):
        marker_array = MarkerArray()
        marker_array.markers.extend(self.create_shelf_markers())
        marker_array.markers.append(self.create_goal_marker())
        marker_array.markers.append(self.create_goal_arrow_marker())
        marker_array.markers.append(self.create_reference_path_marker())
        self.marker_publisher.publish(marker_array)

    def create_shelf_markers(self):
        """用几个长方体表示仓库货架，只用于 RViz 视觉参考。"""
        shelves = [
            (1.20, 1.25, 1.60, 0.22),
            (1.20, -1.25, 1.60, 0.22),
            (2.75, 1.25, 1.30, 0.22),
            (2.75, -1.25, 1.30, 0.22),
        ]

        markers = []
        for index, (x, y, length, width) in enumerate(shelves):
            marker = Marker()
            marker.header.frame_id = 'odom'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'warehouse_shelves'
            marker.id = index
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.20
            marker.pose.orientation.w = 1.0
            marker.scale.x = length
            marker.scale.y = width
            marker.scale.z = 0.40
            marker.color.r = 0.18
            marker.color.g = 0.30
            marker.color.b = 0.75
            marker.color.a = 0.72
            markers.append(marker)

        return markers

    def create_goal_marker(self):
        """绿色圆柱表示导航目标点。"""
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'warehouse_goal'
        marker.id = 100
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        marker.pose.position.x = self.goal_x
        marker.pose.position.y = self.goal_y
        marker.pose.position.z = 0.04
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.22
        marker.scale.y = 0.22
        marker.scale.z = 0.08
        marker.color.r = 0.10
        marker.color.g = 0.85
        marker.color.b = 0.35
        marker.color.a = 0.9
        return marker

    def create_goal_arrow_marker(self):
        """绿色箭头表示到达目标点后希望车头朝向哪里。"""
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'warehouse_goal'
        marker.id = 101
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose.position.x = self.goal_x
        marker.pose.position.y = self.goal_y
        marker.pose.position.z = 0.18
        marker.pose.orientation.z = math.sin(self.goal_yaw * 0.5)
        marker.pose.orientation.w = math.cos(self.goal_yaw * 0.5)
        marker.scale.x = 0.42
        marker.scale.y = 0.06
        marker.scale.z = 0.06
        marker.color.r = 0.10
        marker.color.g = 0.95
        marker.color.b = 0.40
        marker.color.a = 0.95
        return marker

    def create_reference_path_marker(self):
        """一条从起点到目标点的参考线，帮助初学者看懂导航目标。"""
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'warehouse_reference_path'
        marker.id = 200
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.035
        marker.color.r = 0.10
        marker.color.g = 0.85
        marker.color.b = 0.35
        marker.color.a = 0.85

        start = Point()
        start.x = 0.0
        start.y = 0.0
        start.z = 0.03

        goal = Point()
        goal.x = self.goal_x
        goal.y = self.goal_y
        goal.z = 0.03

        marker.points.append(start)
        marker.points.append(goal)

        return marker


def main(args=None):
    rclpy.init(args=args)
    node = WarehouseSceneNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
