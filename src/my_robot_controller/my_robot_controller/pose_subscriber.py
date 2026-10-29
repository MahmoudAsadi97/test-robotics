"""Slide 55: observe the pose published by turtlesim."""
from rclpy.node import Node
from turtlesim.msg import Pose
from my_robot_controller.runtime import run


class PoseSubscriber(Node):
    def __init__(self):
        super().__init__('pose_subscriber')
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

    def pose_callback(self, msg):
        self.get_logger().info(str(msg))


def main(args=None):
    run(PoseSubscriber, args)
