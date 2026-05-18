from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'mini_amr_motion'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jiajun Shen',
    maintainer_email='jiajun-shen@users.noreply.github.com',
    description='Lightweight odometry and TF motion demo for the mini AMR project.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'circle_motion_node = mini_amr_motion.circle_motion_node:main',
            'cmd_vel_motion_node = mini_amr_motion.cmd_vel_motion_node:main',
            'keyboard_teleop_node = mini_amr_motion.keyboard_teleop_node:main',
        ],
    },
)
