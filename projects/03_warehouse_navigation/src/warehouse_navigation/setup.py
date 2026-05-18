from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'warehouse_navigation'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jiajun Shen',
    maintainer_email='jiajun-shen@users.noreply.github.com',
    description='Beginner warehouse navigation demos for the ROS 2 robotics portfolio.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple_goal_follower_node = warehouse_navigation.simple_goal_follower_node:main',
            'warehouse_scene_node = warehouse_navigation.warehouse_scene_node:main',
        ],
    },
)
