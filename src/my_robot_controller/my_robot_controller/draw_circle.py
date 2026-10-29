"""Slide 53: constant linear.x and angular.z draw a radius-2 circle."""
from geometry_msgs.msg import Twist
from rclpy.node import Node
from my_robot_controller.runtime import run


class DrawCircle(Node):
    def __init__(self):
        super().__init__('draw_circle')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.05, self.timer_callback)

    @staticmethod
    def make_command():
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        return msg

    def timer_callback(self):
        self.publisher.publish(self.make_command())

    def stop(self):
        self.timer.cancel()
        self.publisher.publish(Twist())


def main(args=None):
    run(DrawCircle, args)
