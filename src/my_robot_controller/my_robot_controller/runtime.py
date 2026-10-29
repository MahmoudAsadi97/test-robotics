"""Shared, clean lifetime management for the educational nodes."""
import signal
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.signals import SignalHandlerOptions


def run(node_factory, args=None):
    # Python handles Ctrl+C first; keep DDS alive long enough to publish stop.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    try:
        node = node_factory()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if node is not None:
                if rclpy.ok() and hasattr(node, 'stop'):
                    node.stop()
                    time.sleep(0.1)  # Allow the DDS writer to transmit before teardown.
                node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
        finally:
            signal.signal(signal.SIGINT, previous_handler)
