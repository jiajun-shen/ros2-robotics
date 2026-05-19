import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """启动 Project 03 第一节：最小仓库导航 demo。"""
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
    goal_x_m = LaunchConfiguration('goal_x_m')
    goal_y_m = LaunchConfiguration('goal_y_m')
    goal_yaw_rad = LaunchConfiguration('goal_yaw_rad')
    rviz_safe_env = {
        # WSLg sometimes creates an RViz window but leaves it blank with GPU GL.
        # Software rendering is slower but much more reliable for this course.
        'LIBGL_ALWAYS_SOFTWARE': '1',
        'GALLIUM_DRIVER': 'llvmpipe',
        'QT_QPA_PLATFORM': 'xcb',
        'QT_X11_NO_MITSHM': '1',
    }

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
            'goal_x_m',
            default_value='2.0',
            description='Navigation goal x in odom frame.',
        ),
        DeclareLaunchArgument(
            'goal_y_m',
            default_value='0.6',
            description='Navigation goal y in odom frame.',
        ),
        DeclareLaunchArgument(
            'goal_yaw_rad',
            default_value='0.0',
            description='Final robot yaw at the goal.',
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
            executable='warehouse_map_node',
            name='warehouse_map_node',
            output='screen',
        ),
        Node(
            package='warehouse_navigation',
            executable='warehouse_scene_node',
            name='warehouse_scene_node',
            output='screen',
            parameters=[{
                'goal_x_m': ParameterValue(goal_x_m, value_type=float),
                'goal_y_m': ParameterValue(goal_y_m, value_type=float),
                'goal_yaw_rad': ParameterValue(goal_yaw_rad, value_type=float),
            }],
        ),
        Node(
            package='warehouse_navigation',
            executable='clicked_point_goal_node',
            name='clicked_point_goal_node',
            output='screen',
        ),
        Node(
            package='warehouse_navigation',
            executable='simple_goal_follower_node',
            name='simple_goal_follower_node',
            output='screen',
            parameters=[{
                'goal_x_m': ParameterValue(goal_x_m, value_type=float),
                'goal_y_m': ParameterValue(goal_y_m, value_type=float),
                'goal_yaw_rad': ParameterValue(goal_yaw_rad, value_type=float),
                'cmd_topic': 'cmd_vel_raw',
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path],
            additional_env=rviz_safe_env,
            condition=IfCondition(use_rviz),
        ),
    ])
