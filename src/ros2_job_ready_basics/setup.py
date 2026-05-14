from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ros2_job_ready_basics'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shenjj',
    maintainer_email='shenjj@todo.todo',
    description='Beginner ROS 2 Python nodes for job-ready robotics practice.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'goal_publisher = ros2_job_ready_basics.goal_publisher:main',
            'goal_subscriber = ros2_job_ready_basics.goal_subscriber:main',
            'robot_status_publisher = ros2_job_ready_basics.robot_status_publisher:main',
            'mission_service_server = ros2_job_ready_basics.mission_service_server:main',
            'mission_service_client = ros2_job_ready_basics.mission_service_client:main',
            'fibonacci_action_server = ros2_job_ready_basics.fibonacci_action_server:main',
            'fibonacci_action_client = ros2_job_ready_basics.fibonacci_action_client:main',
        ],
    },
)
