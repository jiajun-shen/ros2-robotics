from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'mini_amr_sensors'

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
    description='Beginner sensor simulation package for the mini AMR project.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fake_lidar_node = mini_amr_sensors.fake_lidar_node:main',
            'world_lidar_node = mini_amr_sensors.world_lidar_node:main',
            'lidar_safety_filter_node = mini_amr_sensors.lidar_safety_filter_node:main',
        ],
    },
)
