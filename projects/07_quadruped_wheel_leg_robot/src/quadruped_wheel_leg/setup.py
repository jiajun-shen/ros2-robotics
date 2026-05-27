from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'quadruped_wheel_leg'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jiajun Shen',
    maintainer_email='jiajun-shen@users.noreply.github.com',
    description=(
        'RViz simulation of a wheel-legged quadruped robot with gait animation '
        'and cmd_vel teleoperation.'
    ),
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'demo_command_node = quadruped_wheel_leg.demo_command_node:main',
            'virtual_joystick_node = quadruped_wheel_leg.virtual_joystick_node:main',
            'wheel_leg_motion_node = quadruped_wheel_leg.wheel_leg_motion_node:main',
        ],
    },
)
