import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker, MarkerArray


def yaw_from_quaternion(orientation):
    """把 odom 里的四元数方向转换成平面 yaw 角。"""
    siny_cosp = 2.0 * (
        orientation.w * orientation.z + orientation.x * orientation.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        orientation.y * orientation.y + orientation.z * orientation.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class WorldLidarNode(Node):
    """根据小车在 odom 里的位置，生成更接近真实场景的 /scan。

    这里仍然是轻量级教学仿真，不是 Gazebo 那种完整物理仿真。
    但是障碍物已经固定在世界坐标 odom 里，所以小车移动、转向以后，
    雷达读数会跟着变化。
    """

    def __init__(self):
        super().__init__('world_lidar_node')

        self.declare_parameter('scan_topic', 'scan')
        self.declare_parameter('obstacle_topic', 'obstacles')
        self.declare_parameter('frame_id', 'lidar_link')
        self.declare_parameter('scan_rate_hz', 10.0)
        self.declare_parameter('range_min_m', 0.12)
        self.declare_parameter('range_max_m', 4.0)
        self.declare_parameter('num_readings', 181)
        self.declare_parameter('lidar_offset_x_m', 0.12)
        self.declare_parameter('lidar_offset_y_m', 0.0)

        self.scan_topic = self.get_parameter('scan_topic').value
        self.obstacle_topic = self.get_parameter('obstacle_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.scan_rate_hz = float(self.get_parameter('scan_rate_hz').value)
        self.range_min = float(self.get_parameter('range_min_m').value)
        self.range_max = float(self.get_parameter('range_max_m').value)
        self.num_readings = int(self.get_parameter('num_readings').value)
        self.lidar_offset_x = float(self.get_parameter('lidar_offset_x_m').value)
        self.lidar_offset_y = float(self.get_parameter('lidar_offset_y_m').value)

        self.angle_min = -math.pi
        self.angle_max = math.pi
        self.angle_increment = (self.angle_max - self.angle_min) / (
            self.num_readings - 1
        )

        # 小车当前位姿。cmd_vel_motion_node 会持续发布 /odom。
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0

        # 障碍物固定在 odom 世界坐标系中：(x, y, radius)。
        # 第一个障碍物在车正前方，后两个障碍物放在左右侧，方便你练习绕行。
        self.obstacles = [
            (1.60, 0.00, 0.28),
            (2.20, 0.85, 0.25),
            (2.20, -0.85, 0.25),
        ]

        self.odom_subscriber = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10,
        )
        self.scan_publisher = self.create_publisher(LaserScan, self.scan_topic, 10)
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            self.obstacle_topic,
            10,
        )
        self.timer = self.create_timer(1.0 / self.scan_rate_hz, self.publish_world)

        self.get_logger().info(
            f'World lidar publishing /{self.scan_topic} and /{self.obstacle_topic}'
        )

    def odom_callback(self, odom):
        """保存小车在 odom 世界坐标系里的最新位置和朝向。"""
        self.robot_x = odom.pose.pose.position.x
        self.robot_y = odom.pose.pose.position.y
        self.robot_yaw = yaw_from_quaternion(odom.pose.pose.orientation)

    def publish_world(self):
        """定时发布雷达扫描和 RViz 障碍物 marker。"""
        now = self.get_clock().now().to_msg()
        self.publish_scan(now)
        self.publish_obstacle_markers(now)

    def publish_scan(self, stamp):
        """把世界坐标里的圆形障碍物，转换成 lidar_link 下的一圈距离。"""
        lidar_x, lidar_y = self.lidar_origin_in_world()

        ranges = []
        for index in range(self.num_readings):
            scan_angle = self.angle_min + index * self.angle_increment
            world_angle = self.robot_yaw + scan_angle
            distance = self.cast_ray(lidar_x, lidar_y, world_angle)
            ranges.append(distance)

        scan = LaserScan()
        scan.header.stamp = stamp
        scan.header.frame_id = self.frame_id
        scan.angle_min = self.angle_min
        scan.angle_max = self.angle_max
        scan.angle_increment = self.angle_increment
        scan.time_increment = 0.0
        scan.scan_time = 1.0 / self.scan_rate_hz
        scan.range_min = self.range_min
        scan.range_max = self.range_max
        scan.ranges = ranges
        scan.intensities = [1.0] * self.num_readings

        self.scan_publisher.publish(scan)

    def lidar_origin_in_world(self):
        """根据车体位姿，算出雷达原点在 odom 里的位置。"""
        cos_yaw = math.cos(self.robot_yaw)
        sin_yaw = math.sin(self.robot_yaw)

        lidar_x = (
            self.robot_x
            + self.lidar_offset_x * cos_yaw
            - self.lidar_offset_y * sin_yaw
        )
        lidar_y = (
            self.robot_y
            + self.lidar_offset_x * sin_yaw
            + self.lidar_offset_y * cos_yaw
        )
        return lidar_x, lidar_y

    def cast_ray(self, ray_start_x, ray_start_y, ray_angle):
        """从雷达出发打一条射线，返回它碰到最近圆形障碍物的距离。"""
        ray_dx = math.cos(ray_angle)
        ray_dy = math.sin(ray_angle)
        closest_distance = self.range_max

        for obstacle_x, obstacle_y, radius in self.obstacles:
            hit_distance = self.ray_circle_intersection(
                ray_start_x,
                ray_start_y,
                ray_dx,
                ray_dy,
                obstacle_x,
                obstacle_y,
                radius,
            )
            if hit_distance is None:
                continue
            closest_distance = min(closest_distance, hit_distance)

        return closest_distance

    def ray_circle_intersection(
        self,
        ray_start_x,
        ray_start_y,
        ray_dx,
        ray_dy,
        circle_x,
        circle_y,
        radius,
    ):
        """计算射线和圆的最近交点距离，没有交点就返回 None。"""
        offset_x = ray_start_x - circle_x
        offset_y = ray_start_y - circle_y

        b = ray_dx * offset_x + ray_dy * offset_y
        c = offset_x * offset_x + offset_y * offset_y - radius * radius
        discriminant = b * b - c

        if discriminant < 0.0:
            return None

        sqrt_discriminant = math.sqrt(discriminant)
        near_distance = -b - sqrt_discriminant
        far_distance = -b + sqrt_discriminant

        for distance in (near_distance, far_distance):
            if self.range_min <= distance <= self.range_max:
                return distance

        return None

    def publish_obstacle_markers(self, stamp):
        """发布 RViz 可见的红色圆柱障碍物。"""
        marker_array = MarkerArray()

        for index, (obstacle_x, obstacle_y, radius) in enumerate(self.obstacles):
            marker = Marker()
            marker.header.stamp = stamp
            marker.header.frame_id = 'odom'
            marker.ns = 'world_obstacles'
            marker.id = index
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD

            marker.pose.position.x = obstacle_x
            marker.pose.position.y = obstacle_y
            marker.pose.position.z = 0.18
            marker.pose.orientation.w = 1.0

            marker.scale.x = radius * 2.0
            marker.scale.y = radius * 2.0
            marker.scale.z = 0.36

            marker.color.r = 1.0
            marker.color.g = 0.28
            marker.color.b = 0.08
            marker.color.a = 0.85

            marker_array.markers.append(marker)

        self.marker_publisher.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = WorldLidarNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
