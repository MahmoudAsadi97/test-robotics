"""Slides 49–50: publish String messages once per second."""
from rclpy.node import Node
from std_msgs.msg import String
from my_robot_controller.runtime import run


class HelloPublisher(Node):
    def __init__(self):
        super().__init__('hello_publisher')
        self.counter = 0
        self.publisher = self.create_publisher(String, '/hello', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.counter += 1
        msg = String(data=f'Timer callback triggered: {self.counter}')
        self.publisher.publish(msg)
        self.get_logger().info(msg.data)


def main(args=None):
    run(HelloPublisher, args)
