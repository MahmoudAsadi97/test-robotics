from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_controller'
setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robotics lab maintainer',
    maintainer_email='maintainer@example.com',
    description='Introductory ROS 2 Jazzy nodes and border-turning turtle exercise.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={'console_scripts': [
        'test_node = my_robot_controller.my_first_node:main',
        'hello_publisher = my_robot_controller.hello_publisher:main',
        'draw_circle = my_robot_controller.draw_circle:main',
        'pose_subscriber = my_robot_controller.pose_subscriber:main',
        'border_controller = my_robot_controller.border_controller:main',
    ]},
)
