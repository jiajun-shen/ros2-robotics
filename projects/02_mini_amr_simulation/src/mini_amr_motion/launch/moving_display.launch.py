import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """启动小车模型、运动节点和 RViz。"""
    description_share = get_package_share_directory('mini_amr_description')
    urdf_path = os.path.join(description_share, 'urdf', 'mini_amr.urdf')
    rviz_config_path = os.path.join(description_share, 'rviz', 'mini_amr.rviz')

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
            executable='circle_motion_node',
            name='circle_motion_node',
            output='screen',
            parameters=[{
                'linear_speed_mps': 0.25,
                'angular_speed_radps': 0.45,
                'update_rate_hz': 30.0,
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
