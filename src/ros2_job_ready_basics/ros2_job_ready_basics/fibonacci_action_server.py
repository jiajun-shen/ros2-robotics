import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    """演示 action server：接收目标，持续反馈，最后返回结果。"""

    def __init__(self):
        super().__init__('fibonacci_action_server')

        # action 适合“需要运行一段时间，而且中途想看到进度”的任务。
        # 这里使用 ROS 2 自带的 Fibonacci action 作为入门示例。
        self.action_server = ActionServer(
            self,
            Fibonacci,
            'calculate_fibonacci',
            self.execute_callback,
        )

        self.get_logger().info('Action server is ready: /calculate_fibonacci')

    def execute_callback(self, goal_handle):
        order = goal_handle.request.order
        self.get_logger().info(f'Received action goal: order={order}')

        feedback = Fibonacci.Feedback()
        feedback.sequence = [0, 1]

        # order 表示要计算多少步。
        # 每算出一步，就发布一次 feedback。
        for index in range(2, max(order, 2)):
            next_number = feedback.sequence[index - 1] + feedback.sequence[index - 2]
            feedback.sequence.append(next_number)

            goal_handle.publish_feedback(feedback)
            self.get_logger().info(f'Feedback: {feedback.sequence}')

            # 故意等 0.5 秒，让你能看到 action 的“进行中反馈”。
            time.sleep(0.5)

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.sequence = feedback.sequence[:order]
        self.get_logger().info(f'Result: {result.sequence}')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
