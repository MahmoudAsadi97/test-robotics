#!/usr/bin/env bash
set -eo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
source_overlay
case "${1:-exercise}" in
  exercise)
    if [[ $# -gt 0 ]]; then shift; fi
    exec ros2 launch my_robot_controller exercise.launch.py "$@"
    ;;
  test_node|hello_publisher|draw_circle|pose_subscriber|border_controller)
    executable="$1"
    shift
    exec ros2 run my_robot_controller "$executable" "$@"
    ;;
  *) echo 'Usage: ./scripts/run.sh [exercise|test_node|hello_publisher|draw_circle|pose_subscriber|border_controller] [ROS arguments]' >&2; exit 2 ;;
esac
