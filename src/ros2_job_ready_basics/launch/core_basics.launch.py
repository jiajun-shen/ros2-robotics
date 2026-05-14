from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """一次启动多个 ROS 2 节点。"""
    return LaunchDescription([
        Node(
            package='ros2_job_ready_basics',
            executable='goal_publisher',
            name='goal_publisher',
            output='screen',
        ),
        Node(
            package='ros2_job_ready_basics',
            executable='goal_subscriber',
            name='goal_subscriber',
            output='screen',
        ),
        Node(
            package='ros2_job_ready_basics',
            executable='robot_status_publisher',
            name='robot_status_publisher',
            output='screen',
            parameters=[{
                'robot_name': 'shenbot',
                'current_task': 'ros2_core_basics',
                'battery_level_percent': 88,
            }],
        ),
    ])
