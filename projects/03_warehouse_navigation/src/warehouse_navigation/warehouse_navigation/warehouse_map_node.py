import math

import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


class WarehouseMapNode(Node):
    """发布一个教学用仓库 OccupancyGrid 地图。"""

    def __init__(self):
        super().__init__('warehouse_map_node')

        self.declare_parameter('map_topic', 'map')
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('publish_rate_hz', 1.0)
        self.declare_parameter('resolution_m_per_cell', 0.05)
        self.declare_parameter('width_m', 4.2)
        self.declare_parameter('height_m', 3.4)
        self.declare_parameter('origin_x_m', -0.6)
        self.declare_parameter('origin_y_m', -1.7)

        self.map_topic = self.get_parameter('map_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)
        self.resolution = float(self.get_parameter('resolution_m_per_cell').value)
        self.width_m = float(self.get_parameter('width_m').value)
        self.height_m = float(self.get_parameter('height_m').value)
        self.origin_x = float(self.get_parameter('origin_x_m').value)
        self.origin_y = float(self.get_parameter('origin_y_m').value)

        self.width_cells = int(math.ceil(self.width_m / self.resolution))
        self.height_cells = int(math.ceil(self.height_m / self.resolution))

        self.map_data = self.build_map_data()

        # 地图通常是“最后一张也很重要”的数据。
        # transient local 类似 ROS 1 里的 latched topic，RViz 晚一点打开也能拿到地图。
        map_qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self.map_publisher = self.create_publisher(
            OccupancyGrid,
            self.map_topic,
            map_qos,
        )
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_map)

        self.get_logger().info(
            f'Warehouse map publishing /{self.map_topic}: '
            f'{self.width_cells}x{self.height_cells}, resolution={self.resolution} m'
        )

    def build_map_data(self):
        """创建一张二维占据栅格地图。"""
        data = [0] * (self.width_cells * self.height_cells)

        # 地图边界墙。
        self.fill_rect(data, -0.55, -1.65, 4.10, -1.55, 100)
        self.fill_rect(data, -0.55, 1.55, 4.10, 1.65, 100)
        self.fill_rect(data, -0.55, -1.65, -0.45, 1.65, 100)
        self.fill_rect(data, 3.45, -1.65, 3.55, 1.65, 100)

        # 仓库货架，和 warehouse_scene_node 里的蓝色货架位置保持一致。
        shelves = [
            (1.20, 1.25, 1.60, 0.22),
            (1.20, -1.25, 1.60, 0.22),
            (2.75, 1.25, 1.30, 0.22),
            (2.75, -1.25, 1.30, 0.22),
        ]
        for center_x, center_y, length, width in shelves:
            self.fill_box_from_center(data, center_x, center_y, length, width, 100)

        # 未知区域示例：真实 SLAM 里还没探索过的位置常用 -1。
        self.fill_rect(data, 3.10, -0.25, 3.40, 0.25, -1)

        return data

    def fill_box_from_center(self, data, center_x, center_y, length, width, value):
        """用中心点和长宽填充矩形。"""
        min_x = center_x - length * 0.5
        max_x = center_x + length * 0.5
        min_y = center_y - width * 0.5
        max_y = center_y + width * 0.5
        self.fill_rect(data, min_x, min_y, max_x, max_y, value)

    def fill_rect(self, data, min_x, min_y, max_x, max_y, value):
        """把世界坐标中的矩形区域写进 OccupancyGrid。"""
        min_col, min_row = self.world_to_grid(min_x, min_y)
        max_col, max_row = self.world_to_grid(max_x, max_y)

        min_col = max(0, min(min_col, self.width_cells - 1))
        max_col = max(0, min(max_col, self.width_cells - 1))
        min_row = max(0, min(min_row, self.height_cells - 1))
        max_row = max(0, min(max_row, self.height_cells - 1))

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                data[self.to_index(col, row)] = value

    def world_to_grid(self, x, y):
        """把 odom 世界坐标转换成地图格子坐标。"""
        col = int((x - self.origin_x) / self.resolution)
        row = int((y - self.origin_y) / self.resolution)
        return col, row

    def to_index(self, col, row):
        """OccupancyGrid 的 data 是一维数组，按 row-major 顺序存储。"""
        return row * self.width_cells + col

    def publish_map(self):
        map_message = OccupancyGrid()
        map_message.header.stamp = self.get_clock().now().to_msg()
        map_message.header.frame_id = self.frame_id

        map_message.info.resolution = self.resolution
        map_message.info.width = self.width_cells
        map_message.info.height = self.height_cells
        map_message.info.origin.position.x = self.origin_x
        map_message.info.origin.position.y = self.origin_y
        map_message.info.origin.position.z = 0.0
        map_message.info.origin.orientation.w = 1.0
        map_message.data = self.map_data

        self.map_publisher.publish(map_message)


def main(args=None):
    rclpy.init(args=args)
    node = WarehouseMapNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
