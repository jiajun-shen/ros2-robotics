import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class MissionServiceServer(Node):
    """提供一个 service，用来启动或停止机器人任务。"""

    def __init__(self):
        super().__init__('mission_service_server')
        self.mission_active = False

        # service 适合“请求一次，回复一次”的场景。
        # 这里的服务名是 /set_mission_active，接口类型是 std_srvs/SetBool。
        self.service = self.create_service(
            SetBool,
            'set_mission_active',
            self.handle_set_mission_active,
        )

        self.get_logger().info('Mission service is ready: /set_mission_active')

    def handle_set_mission_active(self, request, response):
        # request.data 是客户端发来的 bool 值。
        # True 表示启动任务，False 表示停止任务。
        self.mission_active = request.data

        response.success = True
        if self.mission_active:
            response.message = 'Mission started.'
        else:
            response.message = 'Mission stopped.'

        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = MissionServiceServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
