import math

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换成 PoseStamped 需要的四元数。"""
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


class ClickedPointGoalNode(Node):
    """把 RViz 鼠标点击的 /clicked_point 转换成导航用的 /goal_pose。"""

    def __init__(self):
        super().__init__('clicked_point_goal_node')

        self.declare_parameter('clicked_point_topic', 'clicked_point')
        self.declare_parameter('goal_topic', 'goal_pose')
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('goal_frame_id', 'odom')
        self.declare_parameter('face_clicked_point', True)

        self.clicked_point_topic = self.get_parameter('clicked_point_topic').value
        self.goal_topic = self.get_parameter('goal_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value
        self.goal_frame_id = self.get_parameter('goal_frame_id').value
        self.face_clicked_point = bool(
            self.get_parameter('face_clicked_point').value
        )

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.have_odom = False

        self.odom_subscriber = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            10,
        )
        self.clicked_point_subscriber = self.create_subscription(
            PointStamped,
            self.clicked_point_topic,
            self.clicked_point_callback,
            10,
        )
        self.goal_publisher = self.create_publisher(PoseStamped, self.goal_topic, 10)

        self.get_logger().info(
            f'Click RViz Publish Point -> /{self.clicked_point_topic}; '
            f'publishing goals to /{self.goal_topic}'
        )

    def odom_callback(self, odom):
        """保存小车当前位置，用来计算到点击点的朝向。"""
        self.robot_x = odom.pose.pose.position.x
        self.robot_y = odom.pose.pose.position.y
        self.robot_yaw = yaw_from_quaternion(odom.pose.pose.orientation)
        self.have_odom = True

    def clicked_point_callback(self, clicked_point):
        """收到 RViz 点击点以后，发布一个 PoseStamped 导航目标。"""
        if clicked_point.header.frame_id != self.goal_frame_id:
            self.get_logger().warn(
                'Clicked point frame is '
                f'"{clicked_point.header.frame_id}", expected "{self.goal_frame_id}". '
                'For this beginner demo, keep RViz Fixed Frame as odom.'
            )

        goal_x = clicked_point.point.x
        goal_y = clicked_point.point.y

        if self.face_clicked_point and self.have_odom:
            goal_yaw = math.atan2(goal_y - self.robot_y, goal_x - self.robot_x)
        else:
            goal_yaw = self.robot_yaw

        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = self.goal_frame_id
        goal.pose.position.x = goal_x
        goal.pose.position.y = goal_y
        goal.pose.position.z = 0.0

        quaternion = quaternion_from_yaw(goal_yaw)
        goal.pose.orientation.x = quaternion['x']
        goal.pose.orientation.y = quaternion['y']
        goal.pose.orientation.z = quaternion['z']
        goal.pose.orientation.w = quaternion['w']

        self.goal_publisher.publish(goal)
        self.get_logger().info(
            f'Published clicked goal: ({goal_x:.2f}, {goal_y:.2f})'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ClickedPointGoalNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
