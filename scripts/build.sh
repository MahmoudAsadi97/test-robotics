#!/usr/bin/env bash
set -eo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
if [[ $(id -u) == 0 && ${ROBOTICS_ALLOW_ROOT:-0} != 1 ]]; then
  echo 'Do not sudo colcon build. Use your normal WSL user.' >&2
  exit 1
fi
colcon build --symlink-install --packages-select my_robot_controller --event-handlers console_direct+
