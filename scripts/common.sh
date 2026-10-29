#!/usr/bin/env bash
# Source this from repository scripts. ROS setup scripts are not nounset-safe.
set -eo pipefail
ROBOTICS_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo 'ROS 2 Jazzy is missing. In Ubuntu 24.04 run: ./scripts/install_ros_jazzy.sh' >&2
  return 1
fi
source /opt/ros/jazzy/setup.bash
# Use apt-installed system Python (rclpy requires the matching interpreter).
export PATH="/usr/bin:$PATH"
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
cd "$ROBOTICS_ROOT"

source_overlay() {
  if [[ ! -f "$ROBOTICS_ROOT/install/setup.bash" ]]; then
    echo 'Build the workspace first: ./scripts/build.sh' >&2
    return 1
  fi
  source "$ROBOTICS_ROOT/install/setup.bash"
}
