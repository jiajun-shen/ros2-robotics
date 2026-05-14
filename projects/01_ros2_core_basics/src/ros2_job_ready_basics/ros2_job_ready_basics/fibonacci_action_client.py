import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):
    """演示 action client：发送目标，接收反馈，等待最终结果。"""

    def __init__(self):
        super().__init__('fibonacci_action_client')
        self.action_client = ActionClient(self, Fibonacci, 'calculate_fibonacci')

    def send_goal(self, order):
        goal = Fibonacci.Goal()
        goal.order = order

        self.action_client.wait_for_server()
        self.get_logger().info(f'Sending action goal: order={order}')

        # feedback_callback 用来接收 action server 中途发回来的进度。
        send_goal_future = self.action_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback,
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal was rejected.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal was accepted.')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_message):
        feedback = feedback_message.feedback
        self.get_logger().info(f'Feedback: {feedback.sequence}')

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()


def parse_order_argument():
    if len(sys.argv) < 2:
        return 8
    return int(sys.argv[1])


def main(args=None):
    order = parse_order_argument()

    rclpy.init(args=args)
    node = FibonacciActionClient()
    node.send_goal(order)

    rclpy.spin(node)


if __name__ == '__main__':
    main()
