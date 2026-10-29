"""Actual rclpy node tests; run with sourced ROS, without starting turtlesim."""
import time

import pytest
import rclpy
from rclpy.parameter import Parameter
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from my_robot_controller.border_controller import BorderController
from my_robot_controller.my_first_node import MyNode
from my_robot_controller.hello_publisher import HelloPublisher
from my_robot_controller.draw_circle import DrawCircle
from my_robot_controller.pose_subscriber import PoseSubscriber


@pytest.fixture(autouse=True)
def context():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_controller_stops_without_pose_and_after_pose_expiry():
    node = BorderController()
    try:
        assert node.command_for_now().linear.x == 0.0
        node.pose_callback(Pose(x=5.5, y=5.5, theta=0.0))
        assert node.command_for_now().linear.x > 0.0
        node.last_pose_time = time.monotonic() - 2.0
        cmd = node.command_for_now()
        assert cmd.linear.x == cmd.angular.z == 0.0
    finally:
        node.destroy_node()


def test_nonfinite_pose_stops_controller():
    node = BorderController()
    try:
        node.pose_callback(Pose(x=float('nan'), y=5.5, theta=0.0))
        assert node.command_for_now().linear.x == 0.0
    finally:
        node.destroy_node()


@pytest.mark.parametrize('name,value', [('pose_timeout', 0.0), ('control_rate', 0.0), ('control_rate', 2.0),
                                        ('linear_speed', -1.0)])
def test_bad_ros_parameters_rejected(name, value):
    with pytest.raises(ValueError):
        BorderController(parameter_overrides=[Parameter(name, value=value)])


def test_examples_have_expected_topics_and_counter():
    nodes = [MyNode(), HelloPublisher(), DrawCircle(), PoseSubscriber()]
    try:
        first, hello, circle, pose = nodes
        first.timer_callback()
        first.timer_callback()
        assert first.counter == 2
        hello.timer_callback()
        assert hello.counter == 1
        assert hello.publisher.topic_name == '/hello'
        assert circle.publisher.topic_name == '/turtle1/cmd_vel'
        assert pose.subscription.topic_name == '/turtle1/pose'
        cmd = circle.make_command()
        assert cmd.linear.x == 2.0 and cmd.angular.z == 1.0
    finally:
        for node in nodes:
            node.destroy_node()


@pytest.mark.parametrize('factory,topic,msg_type', [
    (HelloPublisher, '/hello', String),
    (DrawCircle, '/turtle1/cmd_vel', Twist),
])
def test_example_publishes_real_dds_messages(factory, topic, msg_type):
    publisher = factory()
    observer = Node('example_test_observer')
    messages = []
    subscription = observer.create_subscription(msg_type, topic, messages.append, 10)
    executor = SingleThreadedExecutor()
    executor.add_node(publisher)
    executor.add_node(observer)
    try:
        deadline = time.monotonic() + 6.0
        while not messages and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.1)
        assert messages, f'No actual DDS message received on {topic}'
        if msg_type is String:
            assert messages[0].data.startswith('Timer callback triggered: ')
        else:
            assert messages[0].linear.x == 2.0
            assert messages[0].angular.z == 1.0
    finally:
        executor.shutdown()
        observer.destroy_subscription(subscription)
        observer.destroy_node()
        publisher.destroy_node()
