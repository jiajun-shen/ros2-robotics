import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """启动小车、世界障碍物雷达、安全过滤器、运动节点和 RViz。"""
    description_share = get_package_share_directory('mini_amr_description')
    urdf_path = os.path.join(description_share, 'urdf', 'mini_amr.urdf')
    rviz_config_path = os.path.join(
        description_share,
        'rviz',
        'mini_amr_obstacles.rviz',
    )

    with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    use_rviz = LaunchConfiguration('use_rviz')
    obstacle_layout = LaunchConfiguration('obstacle_layout')
    stop_distance_m = LaunchConfiguration('stop_distance_m')
    front_angle_rad = LaunchConfiguration('front_angle_rad')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Whether to start RViz.',
        ),
        DeclareLaunchArgument(
            'obstacle_layout',
            default_value='slalom',
            description='Obstacle layout: single_front, slalom, wide_gap, left_wall, open.',
        ),
        DeclareLaunchArgument(
            'stop_distance_m',
            default_value='0.65',
            description='Forward commands are blocked below this front obstacle distance.',
        ),
        DeclareLaunchArgument(
            'front_angle_rad',
            default_value='0.45',
            description='Front lidar sector half-angle used by the safety filter.',
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
                'front_angle_rad': ParameterValue(
                    front_angle_rad,
                    value_type=float,
                ),
                'stop_distance_m': ParameterValue(
                    stop_distance_m,
                    value_type=float,
                ),
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
