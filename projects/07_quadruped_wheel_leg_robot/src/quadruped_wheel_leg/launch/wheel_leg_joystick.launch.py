import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('quadruped_wheel_leg')
    urdf_path = os.path.join(package_share, 'urdf', 'wheel_leg_quadruped.urdf')
    rviz_config_path = os.path.join(package_share, 'rviz', 'wheel_leg_quadruped.rviz')

    with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    use_rviz = LaunchConfiguration('use_rviz')
    use_joystick = LaunchConfiguration('use_joystick')
    cmd_topic = LaunchConfiguration('cmd_topic')

    rviz_safe_env = {
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
            'use_joystick',
            default_value='true',
            description='Whether to start the on-screen circular joystick.',
        ),
        DeclareLaunchArgument(
            'cmd_topic',
            default_value='cmd_vel',
            description='Velocity command topic for the quadruped.',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='quadruped_robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'publish_frequency': 60.0,
            }],
        ),
        Node(
            package='quadruped_wheel_leg',
            executable='wheel_leg_motion_node',
            name='wheel_leg_motion_node',
            output='screen',
            parameters=[{
                'cmd_topic': cmd_topic,
            }],
        ),
        Node(
            package='quadruped_wheel_leg',
            executable='on_screen_joystick_node',
            name='quadruped_on_screen_joystick_node',
            output='screen',
            parameters=[{
                'cmd_topic': cmd_topic,
            }],
            condition=IfCondition(use_joystick),
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
