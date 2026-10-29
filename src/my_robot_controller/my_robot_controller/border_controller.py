"""Slide 56: translate pose feedback into forward/turn velocity commands."""
import math
import random
import time

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.node import Node
from turtlesim.msg import Pose

from my_robot_controller.motion import BorderMotion, Config, Pose2D
from my_robot_controller.runtime import run


class BorderController(Node):
    def __init__(self, **kwargs):
        super().__init__('border_controller', **kwargs)
        try:
            defaults = {
                'world_size': 11.0889, 'margin': 0.8,
                'linear_speed': 2.0, 'angular_speed': 2.0,
                'turn_tolerance': 0.04, 'control_rate': 30.0,
                'pose_timeout': 0.5, 'seed': -1,
            }
            # Startup-only configuration avoids silently ignoring runtime changes.
            for name, value in defaults.items():
                self.declare_parameter(name, value, ParameterDescriptor(read_only=True))
            values = {name: self.get_parameter(name).value for name in defaults}
            for name in ('control_rate', 'pose_timeout'):
                if not math.isfinite(values[name]) or values[name] <= 0.0:
                    raise ValueError(f'{name} must be finite and positive')
            if values['control_rate'] < 10.0:
                raise ValueError('control_rate must be at least 10 Hz for stable pose feedback')
            config = Config(**{name: values[name] for name in (
                'world_size', 'margin', 'linear_speed', 'angular_speed', 'turn_tolerance')})
            # Margin must cover multiple control/simulator frames before a stop.
            if config.linear_speed * (1.0 / values['control_rate'] + 0.05) >= config.margin:
                raise ValueError('speed/control_rate combination is too fast for margin')
            seed = values['seed']
            self.motion = BorderMotion(config, random.Random(None if seed < 0 else seed))
            self.pose_timeout = values['pose_timeout']
            self.pose = None
            self.last_pose_time = None
            self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
            self.subscription = self.create_subscription(
                Pose, '/turtle1/pose', self.pose_callback, 10)
            self.timer = self.create_timer(1.0 / values['control_rate'], self.timer_callback)
            self.get_logger().info('Waiting for /turtle1/pose; initial motion is forward (+x).')
        except Exception:
            self.destroy_node()
            raise

    def pose_callback(self, msg):
        if not all(math.isfinite(v) for v in (msg.x, msg.y, msg.theta)):
            self.pose = None
            self.last_pose_time = None
            return
        self.pose = Pose2D(msg.x, msg.y, msg.theta)
        self.last_pose_time = time.monotonic()

    def command_for_now(self):
        msg = Twist()
        if (self.pose is None or self.last_pose_time is None or
                time.monotonic() - self.last_pose_time > self.pose_timeout):
            return msg
        old_count = self.motion.turn_count
        velocity = self.motion.update(self.pose)
        msg.linear.x = velocity.linear
        msg.angular.z = velocity.angular
        if self.motion.turn_count != old_count:
            self.get_logger().info(
                f'Border turn {self.motion.turn_count}: random heading '
                f'{self.motion.target_heading:.3f} rad')
        return msg

    def timer_callback(self):
        self.publisher.publish(self.command_for_now())

    def stop(self):
        self.timer.cancel()
        self.publisher.publish(Twist())


def main(args=None):
    run(BorderController, args)
