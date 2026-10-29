# ROS 2 exercise implementation plan

> Execute within the existing isolated checkout, using native implementation and parallel agents for independent documentation and controller logic.

**Goal:** Deliver all introductory examples and a verified border-turning turtlesim controller with Windows/WSL VS Code instructions.
**Architecture:** colcon workspace with one ament_python package, deterministic-testable motion logic, rclpy adapters, launch file, shell helpers.
**Tech stack:** Ubuntu 24.04, ROS 2 Jazzy, Python 3.12, turtlesim, colcon, pytest.
**Spec:** ../specs/2026-10-29-ros2-exercise-design.md

## Constraints and review focus
- Match slide 56 topics and behavior; document all 56 slides including screenshot commands.
- Verify all four borders and corners; avoid repeatedly selecting headings while turning.
- Validate unsafe/non-finite parameters and stop on missing or stale poses.
- Exercise real ROS discovery, messages, launch, and pose-driven movement, not only simulation of the algorithm.
- Use WSL Linux filesystem and system Python; source underlay and overlay consistently.

## Tasks
- [x] Write boundary/corner/state-transition tests; confirm missing implementation fails, implement core, rerun full core tests.
- [x] Build package metadata, educational nodes, border adapter, launch file, ROS integration tests; build with colcon and run actual turtlesim.
- [x] Prepare install/build/run/test helpers and VS Code settings/tasks; exercise their actual entry points.
- [x] Read images and text from every slide, produce slide guide and corrections.
- [x] Test repeated border encounters, seeded behavior, stale pose and shutdown; review code and resolve findings.
- [x] Record exact evidence, commit deliverables locally, provide VS Code launch instructions and limitations.
