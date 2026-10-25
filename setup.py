from setuptools import find_packages, setup

name = 'imu_radial_guard'

setup(
    name=name,
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + name]),
        ('share/' + name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Project Maintainer',
    maintainer_email='maintainer@example.com',
    description='Simple ROS 2 IMU-based radial distance stopper',
    license='Apache-2.0',
    entry_points={'console_scripts': ['radial_guard = imu_radial_guard.runner:main']},
)
