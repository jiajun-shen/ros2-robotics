import math

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node


def quaternion_from_yaw(yaw):
    """把平面 yaw 角转换成 PoseStamped 里需要的四元数。"""
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


class SendGoalNode(Node):
    """向 /goal_pose 发布一个导航目标点，然后自动退出。"""

    def __init__(self):
        super().__init__('send_goal_node')

        self.declare_parameter('goal_topic', 'goal_pose')
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('goal_x_m', 2.0)
        self.declare_parameter('goal_y_m', 0.6)
        self.declare_parameter('goal_yaw_rad', 0.0)
        self.declare_parameter('publish_count', 10)
        self.declare_parameter('publish_rate_hz', 5.0)

        self.goal_topic = self.get_parameter('goal_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.goal_x = float(self.get_parameter('goal_x_m').value)
        self.goal_y = float(self.get_parameter('goal_y_m').value)
        self.goal_yaw = float(self.get_parameter('goal_yaw_rad').value)
        self.remaining_publishes = int(self.get_parameter('publish_count').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.publisher = self.create_publisher(PoseStamped, self.goal_topic, 10)
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_goal)
        self.done = False

        self.get_logger().info(
            f'Sending goal ({self.goal_x:.2f}, {self.goal_y:.2f}) to /{self.goal_topic}'
        )

    def publish_goal(self):
        """连续发布几次，避免一次性消息太快导致订阅端错过。"""
        if self.remaining_publishes <= 0:
            self.done = True
            return

        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = self.frame_id
        goal.pose.position.x = self.goal_x
        goal.pose.position.y = self.goal_y
        goal.pose.position.z = 0.0

        quaternion = quaternion_from_yaw(self.goal_yaw)
        goal.pose.orientation.x = quaternion['x']
        goal.pose.orientation.y = quaternion['y']
        goal.pose.orientation.z = quaternion['z']
        goal.pose.orientation.w = quaternion['w']

        self.publisher.publish(goal)
        self.remaining_publishes -= 1

        if self.remaining_publishes == 0:
            self.get_logger().info('Goal sent.')
            self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = SendGoalNode()

    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
