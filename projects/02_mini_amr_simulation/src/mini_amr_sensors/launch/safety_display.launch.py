import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


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

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Whether to start RViz.',
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
                'stop_distance_m': 0.65,
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
