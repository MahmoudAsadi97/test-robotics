#!/usr/bin/env python3
"""Slides 46–48: a node, timer, and counter."""
from rclpy.node import Node
from my_robot_controller.runtime import run


class MyNode(Node):
    def __init__(self):
        super().__init__('first_node')
        self.counter = 0
        self.get_logger().info('Hello from ROS2')
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.counter += 1
        self.get_logger().info(f'hello again: {self.counter}')


def main(args=None):
    run(MyNode, args)


if __name__ == '__main__':
    main()
