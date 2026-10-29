#!/usr/bin/env bash
# Run INSIDE Ubuntu 24.04 (WSL or native), not PowerShell.
set -euo pipefail
source /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 ]]; then
  echo 'This apt installer requires Ubuntu 24.04. Use WSL Ubuntu-24.04 on Windows.' >&2
  exit 1
fi
if [[ $(id -u) == 0 ]]; then SUDO=(); else SUDO=(sudo); fi
"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y locales curl ca-certificates software-properties-common
"${SUDO[@]}" locale-gen en_US.UTF-8
"${SUDO[@]}" update-locale LANG=en_US.UTF-8
export LANG=en_US.UTF-8
"${SUDO[@]}" add-apt-repository -y universe

if ! dpkg-query -W -f='${Status}' ros2-apt-source 2>/dev/null | grep -q 'install ok installed'; then
  # Official ROS repository configuration package; HTTPS verification stays on.
  # Follow github.com's release redirect; no GitHub API token is needed.
  release_url="$(curl --fail --silent --show-error --location --output /dev/null \
    --write-out '%{url_effective}' https://github.com/ros-infrastructure/ros-apt-source/releases/latest)"
  release="${release_url##*/}"
  [[ "$release" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo 'Cannot resolve ROS apt source release' >&2; exit 1; }
  download_dir="$(mktemp -d)"
  trap 'rm -rf -- "$download_dir"' EXIT
  curl --fail --location --show-error \
    "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${release}/ros2-apt-source_${release}.noble_all.deb" \
    -o "$download_dir/ros2-apt-source.deb"
  "${SUDO[@]}" dpkg -i "$download_dir/ros2-apt-source.deb"
fi
"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y ros-jazzy-desktop ros-dev-tools python3-pytest
echo 'ROS 2 Jazzy installed. Next: ./scripts/build.sh then ./scripts/run.sh'
