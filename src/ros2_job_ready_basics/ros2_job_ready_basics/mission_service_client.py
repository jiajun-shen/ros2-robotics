import sys

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class MissionServiceClient(Node):
    """调用 /set_mission_active service 的客户端。"""

    def __init__(self):
        super().__init__('mission_service_client')

        # client 不直接控制 server，而是向 server 发出请求。
        self.client = self.create_client(SetBool, 'set_mission_active')

    def send_request(self, active):
        # 等待 service server 启动。
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /set_mission_active service...')

        request = SetBool.Request()
        request.data = active

        # 异步发送请求。future 代表“未来会返回的结果”。
        return self.client.call_async(request)


def parse_active_argument():
    # 支持几种容易记的输入方式：
    # start / true / 1 表示启动任务。
    # stop / false / 0 表示停止任务。
    if len(sys.argv) < 2:
        return True

    value = sys.argv[1].lower()
    if value in ('start', 'true', '1', 'on'):
        return True
    if value in ('stop', 'false', '0', 'off'):
        return False

    raise ValueError('Use start/stop, true/false, 1/0, or on/off.')


def main(args=None):
    active = parse_active_argument()

    rclpy.init(args=args)
    node = MissionServiceClient()

    future = node.send_request(active)
    rclpy.spin_until_future_complete(node, future)

    response = future.result()
    node.get_logger().info(
        f'success={response.success}, message="{response.message}"'
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
