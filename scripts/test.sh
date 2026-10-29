#!/usr/bin/env bash
set -eo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
source_overlay
export ROS_DOMAIN_ID="${ROBOTICS_TEST_DOMAIN:-42}"
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
colcon test --packages-select my_robot_controller --event-handlers console_direct+ --return-code-on-test-failure
colcon test-result --verbose
if [[ "${1:-}" == '--integration' ]]; then
  # Dedicated DDS domain prevents other running lab nodes influencing the test.
  exec /usr/bin/python3 "$ROBOTICS_ROOT/scripts/verify_ros.py"
elif [[ $# -gt 0 ]]; then
  echo 'Usage: ./scripts/test.sh [--integration]' >&2
  exit 2
fi
