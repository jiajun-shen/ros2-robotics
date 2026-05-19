import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """启动 Project 03 第二节：仓库航点导航 demo。"""
    description_share = get_package_share_directory('mini_amr_description')
    navigation_share = get_package_share_directory('warehouse_navigation')

    urdf_path = os.path.join(description_share, 'urdf', 'mini_amr.urdf')
    rviz_config_path = os.path.join(
        navigation_share,
        'rviz',
        'warehouse_navigation.rviz',
    )

    with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    use_rviz = LaunchConfiguration('use_rviz')
    obstacle_layout = LaunchConfiguration('obstacle_layout')
    stop_distance_m = LaunchConfiguration('stop_distance_m')
    route_name = LaunchConfiguration('route_name')
    loop_route = LaunchConfiguration('loop_route')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Whether to start RViz.',
        ),
        DeclareLaunchArgument(
            'obstacle_layout',
            default_value='open',
            description='Obstacle layout passed to Project 02 world_lidar_node.',
        ),
        DeclareLaunchArgument(
            'stop_distance_m',
            default_value='0.65',
            description='Safety filter stop distance.',
        ),
        DeclareLaunchArgument(
            'route_name',
            default_value='aisle_inspection',
            description='Waypoint route: short_demo or aisle_inspection.',
        ),
        DeclareLaunchArgument(
            'loop_route',
            default_value='false',
            description='Whether to repeat the waypoint route forever.',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
            }],
        ),
        Node(
            package='mini_amr_motion',
            executable='cmd_vel_motion_node',
            name='cmd_vel_motion_node',
            output='screen',
        ),
        Node(
            package='mini_amr_sensors',
            executable='world_lidar_node',
            name='world_lidar_node',
            output='screen',
            parameters=[{
                'obstacle_layout': obstacle_layout,
            }],
        ),
        Node(
            package='mini_amr_sensors',
            executable='lidar_safety_filter_node',
            name='lidar_safety_filter_node',
            output='screen',
            parameters=[{
                'input_cmd_topic': 'cmd_vel_raw',
                'output_cmd_topic': 'cmd_vel',
                'scan_topic': 'scan',
                'front_angle_rad': 0.45,
                'stop_distance_m': ParameterValue(
                    stop_distance_m,
                    value_type=float,
                ),
            }],
        ),
        Node(
            package='warehouse_navigation',
            executable='warehouse_scene_node',
            name='warehouse_scene_node',
            output='screen',
        ),
        Node(
            package='warehouse_navigation',
            executable='simple_goal_follower_node',
            name='simple_goal_follower_node',
            output='screen',
            parameters=[{
                'goal_x_m': 0.8,
                'goal_y_m': 0.0,
                'goal_yaw_rad': 0.0,
                'cmd_topic': 'cmd_vel_raw',
            }],
        ),
        Node(
            package='warehouse_navigation',
            executable='waypoint_patrol_node',
            name='waypoint_patrol_node',
            output='screen',
            parameters=[{
                'route_name': route_name,
                'loop_route': ParameterValue(loop_route, value_type=bool),
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(use_rviz),
        ),
    ])
