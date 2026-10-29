#!/usr/bin/python3
"""Validate the installed exercise against real, headless turtlesim over DDS.

Run after sourcing ROS and this workspace's install/setup.bash. This script owns
its launch process, isolates discovery in a ROS domain, and writes JSON evidence
plus the launch log to reports/. No simulator or ROS APIs are mocked.
"""

import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback


EPSILON = 1e-4
WORLD_SIZE = 11.088889


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def mode(command):
    if abs(command[1]) > EPSILON and abs(command[2]) > EPSILON:
        return "combined"
    if abs(command[1]) > EPSILON:
        return "forward"
    if abs(command[2]) > EPSILON:
        return "turn"
    return "stop"


def descendants(pid):
    """Find only processes descended from the subprocess this script owns."""
    # Some container kernels omit /proc/PID/task/TID/children entirely.
    # PPid in status is available on ordinary Linux and in those containers.
    children_by_parent = {}
    for status in Path("/proc").glob("[0-9]*/status"):
        try:
            lines = status.read_text().splitlines()
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        parent = next((int(line.split()[1]) for line in lines if line.startswith("PPid:")), None)
        if parent is not None:
            children_by_parent.setdefault(parent, []).append(int(status.parent.name))
    found = set()
    pending = [pid]
    while pending:
        parent = pending.pop()
        for child in children_by_parent.get(parent, []):
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def simulator_pid(launch_pid):
    for pid in descendants(launch_pid):
        try:
            executable = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[0]
        except (FileNotFoundError, ProcessLookupError):
            continue
        if Path(os.fsdecode(executable)).name == "turtlesim_node":
            return pid
    raise AssertionError("Could not locate the owned turtlesim process for stale-pose test")


def terminate_group(process):
    if process is None:
        return
    # A failed launch may have exited while leaving children in its group.
    for sig, timeout in ((signal.SIGINT, 6), (signal.SIGTERM, 3), (signal.SIGKILL, 2)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            break
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            continue
        # Reap any remaining members even when ros2 launch has already exited.
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break


class Probe:
    def __init__(self):
        import rclpy
        from geometry_msgs.msg import Twist
        from turtlesim.msg import Pose
        from turtlesim.srv import TeleportAbsolute

        self.rclpy = rclpy
        self.teleport_type = TeleportAbsolute
        self.node = rclpy.create_node("exercise_integration_probe")
        self.poses = []
        self.commands = []
        self.node.create_subscription(Pose, "/turtle1/pose", self.pose_received, 100)
        self.node.create_subscription(Twist, "/turtle1/cmd_vel", self.command_received, 100)
        self.teleport_client = self.node.create_client(TeleportAbsolute, "/turtle1/teleport_absolute")
        self.process = None

    def pose_received(self, pose):
        self.poses.append((time.monotonic(), pose.x, pose.y, pose.theta))

    def command_received(self, command):
        self.commands.append((time.monotonic(), command.linear.x, command.angular.z))

    def spin(self, seconds, check_launch=True):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            self.rclpy.spin_once(self.node, timeout_sec=min(0.03, max(0, end - time.monotonic())))
            if check_launch and self.process is not None:
                require(self.process.poll() is None, "Exercise launch exited before validation finished")

    def until(self, predicate, timeout, explanation):
        deadline = time.monotonic() + timeout
        while not predicate():
            require(time.monotonic() < deadline, explanation)
            self.spin(0.03)

    def pose_at(self, timestamp):
        return min(self.poses, key=lambda pose: abs(pose[0] - timestamp))

    def teleport(self, x, y, theta):
        request = self.teleport_type.Request()
        request.x, request.y, request.theta = float(x), float(y), float(theta)
        future = self.teleport_client.call_async(request)
        self.until(future.done, 3, "Turtlesim teleport service did not respond")
        require(future.exception() is None, f"Teleport failed: {future.exception()}")
        self.spin(0.08)


def completed_turns(probe, since):
    """A cycle consists of angular-only commands followed by forward motion."""
    turns = []
    turning = None
    for command in probe.commands[since:]:
        command_mode = mode(command)
        require(command_mode != "combined", "Controller translated and rotated at the same time")
        require(command[1] >= -EPSILON, "Controller drove backward instead of forward")
        if command_mode == "turn" and turning is None:
            turning = command[0]
        elif command_mode == "forward" and turning is not None:
            start = probe.pose_at(turning)
            finish = probe.pose_at(command[0])
            drift = math.hypot(finish[1] - start[1], finish[2] - start[2])
            require(drift < 0.35, f"Turtle translated {drift:.3f} units during its turn")
            turns.append({
                "start_time": turning,
                "finish_time": command[0],
                "duration_seconds": round(command[0] - turning, 3),
                "position": [round(start[1], 4), round(start[2], 4)],
                "resumed_heading": round(finish[3], 5),
                "turn_translation": round(drift, 5),
            })
            turning = None
    return turns


def validate_initial_motion(probe):
    probe.until(lambda: probe.poses and probe.commands, 20, "No real pose/cmd_vel messages after launch")
    start = probe.poses[0]
    probe.spin(0.65)
    finish = probe.poses[-1]
    dx, dy = finish[1] - start[1], finish[2] - start[2]
    require(dx > 0.6, f"Initial turtle motion was not in +x: delta x={dx:.3f}")
    require(abs(dy) < 0.05, f"Initial turtle motion changed y by {dy:.3f}")
    require(abs(finish[3]) < 0.05, "Initial turtle heading was not along +x")
    require(all(abs(cmd[2]) < EPSILON for cmd in probe.commands), "Controller rotated before reaching a border")
    return {"delta_x": round(dx, 5), "delta_y": round(dy, 5), "heading": round(finish[3], 5)}


def validate_natural_cycles(probe):
    probe.until(lambda: len(completed_turns(probe, 0)) >= 3, 45, "Fewer than three natural border-turn-forward cycles")
    turns = completed_turns(probe, 0)[:3]
    for turn in turns:
        x, y = turn["position"]
        require(min(x, y, WORLD_SIZE - x, WORLD_SIZE - y) < 1.3, "Natural turn occurred away from a border")
        dx, dy = math.cos(turn["resumed_heading"]), math.sin(turn["resumed_heading"])
        if x < 1.3:
            require(dx > 0, "Natural turn at left border did not face inward")
        if x > WORLD_SIZE - 1.3:
            require(dx < 0, "Natural turn at right border did not face inward")
        if y < 1.3:
            require(dy > 0, "Natural turn at bottom border did not face inward")
        if y > WORLD_SIZE - 1.3:
            require(dy < 0, "Natural turn at top border did not face inward")
    require(len({turn["resumed_heading"] for turn in turns}) == 3, "Seeded natural turns repeated a fixed heading")
    # Ensure recovery has cleared the border before using teleport for the next test.
    probe.until(lambda: min(probe.poses[-1][1], probe.poses[-1][2],
                            WORLD_SIZE - probe.poses[-1][1], WORLD_SIZE - probe.poses[-1][2]) > 1.4,
                8, "Turtle did not clear its last natural border encounter")
    return turns


def validate_teleported_boundaries(probe):
    probe.until(probe.teleport_client.service_is_ready, 5, "Teleport service unavailable")
    low, high, center = 0.55, WORLD_SIZE - 0.55, WORLD_SIZE / 2
    cases = [
        ("left_wrap_positive_pi", low, center, math.pi - 0.01, 1, 0),
        ("right", high, center, 0, -1, 0),
        ("bottom", center, low, -math.pi / 2, 0, 1),
        ("top", center, high, math.pi / 2, 0, -1),
        ("bottom_left", low, low, -3 * math.pi / 4, 1, 1),
        ("bottom_right", high, low, -math.pi / 4, -1, 1),
        ("top_left", low, high, 3 * math.pi / 4, 1, -1),
        ("top_right", high, high, math.pi / 4, -1, -1),
        ("left_wrap_negative_pi", low, center, -math.pi + 0.01, 1, 0),
    ]
    results = []
    for name, x, y, theta, inward_x, inward_y in cases:
        # Starting centrally gives the state machine an unambiguous fresh border
        # encounter, regardless of the previous case's randomized heading.
        probe.teleport(center, center, 0)
        probe.spin(0.2)
        index = len(probe.commands)
        probe.teleport(x, y, theta)
        probe.until(lambda: bool(completed_turns(probe, index)), 8, f"No completed turn for {name}")
        turn = completed_turns(probe, index)[0]
        start = probe.pose_at(turn["finish_time"])
        probe.spin(0.45)
        finish = probe.poses[-1]
        dx, dy = finish[1] - start[1], finish[2] - start[2]
        if inward_x:
            require(dx * inward_x > 0.1, f"{name} did not move inward in x: {dx:.3f}")
        if inward_y:
            require(dy * inward_y > 0.1, f"{name} did not move inward in y: {dy:.3f}")
        require(math.hypot(dx, dy) > 0.5, f"{name} did not resume forward movement")
        results.append({"case": name, "delta_x": round(dx, 5), "delta_y": round(dy, 5), **turn})
    return results


def validate_stale_pose(probe):
    center = WORLD_SIZE / 2
    probe.teleport(center, center, 0)
    probe.spin(0.2)
    require(mode(probe.commands[-1]) == "forward", "Stale-pose test did not start during forward motion")
    pid = simulator_pid(probe.process.pid)
    started = time.monotonic()
    os.kill(pid, signal.SIGSTOP)
    try:
        probe.spin(1.25)
        late = [command for command in probe.commands if command[0] > started + 0.85]
        require(len(late) >= 3, "Controller did not publish stop commands after losing pose updates")
        require(all(mode(command) == "stop" for command in late), "Controller continued moving on stale pose")
        first_stop = next((command[0] for command in probe.commands
                           if command[0] > started and mode(command) == "stop"), None)
        require(first_stop is not None, "No stop command observed for stale pose")
    finally:
        os.kill(pid, signal.SIGCONT)
    index = len(probe.commands)
    probe.until(lambda: any(mode(command) == "forward" for command in probe.commands[index:]),
                3, "Controller did not resume after pose updates returned")
    return {"stop_delay_seconds": round(first_stop - started, 3), "late_zero_commands": len(late),
            "resumed_after_pose_returned": True}


def validate_shutdown(probe):
    started = time.monotonic()
    # launch forwards the signal to its nodes. Signaling the whole group here
    # would deliver SIGINT twice and interrupt the nodes' cleanup handlers.
    probe.process.send_signal(signal.SIGINT)
    probe.spin(1.0, check_launch=False)
    shutdown_commands = [command for command in probe.commands if command[0] >= started]
    require(any(mode(command) == "stop" for command in shutdown_commands), "Shutdown did not publish a zero Twist")
    return {"zero_twist_received": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--domain-id", type=int, default=int(os.environ.get("ROS_DOMAIN_ID", 20 + os.getpid() % 180)))
    args = parser.parse_args()
    require(0 <= args.domain_id <= 232, "ROS domain must be between 0 and 232")
    os.environ["ROS_DOMAIN_ID"] = str(args.domain_id)
    os.environ.pop("ROS_LOCALHOST_ONLY", None)
    os.environ["ROS_AUTOMATIC_DISCOVERY_RANGE"] = "LOCALHOST"
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.output_dir / "ros-launch.log"
    report_path = args.output_dir / "ros-validation.json"
    started = time.monotonic()
    report = {"passed": False, "ros_domain_id": args.domain_id, "real_ros_and_turtlesim": True,
              "launch_command": ["ros2", "launch", "my_robot_controller", "exercise.launch.py",
                                 "headless:=true", "seed:=7", "linear_speed:=2.0", "angular_speed:=2.0"],
              "checks": {}}
    probe = None
    process = None
    rclpy = None
    try:
        import rclpy
        rclpy.init()
        probe = Probe()
        with log_path.open("w") as log:
            process = subprocess.Popen(report["launch_command"], stdout=log, stderr=subprocess.STDOUT,
                                       env=os.environ.copy(), start_new_session=True)
            probe.process = process
            report["checks"]["initial_positive_x"] = validate_initial_motion(probe)
            report["checks"]["natural_border_cycles"] = validate_natural_cycles(probe)
            report["checks"]["walls_corners_and_angle_wrap"] = validate_teleported_boundaries(probe)
            report["checks"]["stale_pose"] = validate_stale_pose(probe)
            report["checks"]["shutdown"] = validate_shutdown(probe)
        report["passed"] = True
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        traceback.print_exc()
    finally:
        terminate_group(process)
        if probe is not None:
            report["pose_messages"] = len(probe.poses)
            report["command_messages"] = len(probe.commands)
            if probe.poses:
                report["observed_position_bounds"] = {
                    "x": [min(p[1] for p in probe.poses), max(p[1] for p in probe.poses)],
                    "y": [min(p[2] for p in probe.poses), max(p[2] for p in probe.poses)],
                }
            probe.node.destroy_node()
        if rclpy is not None and rclpy.ok():
            rclpy.shutdown()
        launch_log = log_path.read_text(errors="replace") if log_path.exists() else ""
        wall_hits = launch_log.count("Oh no!")
        report["checks"]["wall_collisions"] = wall_hits
        if wall_hits:
            report["passed"] = False
            report["error"] = f"Turtlesim reported {wall_hits} wall collisions"
        report["duration_seconds"] = round(time.monotonic() - started, 3)
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"passed": report["passed"], "report": str(report_path),
                          "duration_seconds": report["duration_seconds"], "error": report.get("error")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
