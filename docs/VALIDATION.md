# Validation record

Validated on 29 October 2026 against actual **ROS 2 Jazzy / Ubuntu 24.04**, Python 3.12.3 and turtlesim 1.8.4. The cloud host runs Debian, so the supported Ubuntu runtime was provided by the official `osrf/ros:jazzy-desktop` image. Image digest:

```text
sha256:2f520187e84304fffb60d19c9a7d8e2e79d563a6e579a090427e5994eb1b8c45
```

## Reproducible commands

Inside Ubuntu 24.04 with Jazzy installed, at the repository root:

```bash
./scripts/build.sh
./scripts/test.sh --integration
```

The final cloud run used `ROBOTICS_TEST_DOMAIN=157 ./scripts/test.sh --integration` to keep it separate from other verification commands. The same scripts ran inside the Ubuntu container at `/work`. The container build alone used `ROBOTICS_ALLOW_ROOT=1` because that container was running as root; normal WSL development must use the regular user.

## Results

- Colcon build: **1 package succeeded**.
- Package suite: **27 passed, 0 failed, 0 errors, 0 skipped**.
- Pure motion suite includes all borders/corners, random seeds, shortest-angle rotation, transition/escape behavior, invalid values, and **300,000 kinematic simulation steps**.
- ROS tests exercise actual rclpy construction and DDS messages for the string/circle examples, counter behavior, invalid parameters, and absent/stale/nonfinite pose.
- Full acceptance test: **passed**, **45.212 seconds**, default linear/angular speeds 2.0, seed 7.
- Actual telemetry received: **2,650 pose messages**, **1,305 velocity commands**.
- Initial motion: **+1.312 x**, **0 y**, heading 0 radians.
- **Three natural border → turn → forward cycles** completed with different inward headings.
- **Nine forced scenarios** passed: all four sides, all four corners, and both +π/−π wrap approaches at the left border.
- Pose feed deliberately paused: zero command after **0.516 seconds**, 12 late zero commands observed, movement resumed when pose returned.
- Ctrl+C: final zero Twist received; simulator and controller exited cleanly.
- **Zero wall collisions** reported by real turtlesim; no leftover exercise processes.

Inspect the retained [machine-readable evidence](validation/ros-validation.json) and [actual launch log](validation/ros-launch.log). New runs write `reports/`, which is ignored by Git; these documentation copies preserve this run. Message timestamps and durations vary between runs.

## Bugs found and corrected during verification

The first harness could not locate the simulator because this runtime lacks `/proc/.../children`. It now derives the owned process tree from `PPid` in `/proc/.../status`.

Real DDS testing exposed that default rclpy SIGINT handling destroyed the context before a final stop could publish. Shutdown now retains the context through the stop publication and then tears it down; the failing check subsequently passed. Tests use their own local ROS domain before any test publisher starts, so they do not command the normal exercise's turtle.

## Installation and documentation checks

- All 56 slide sections are present in order; embedded screenshots and notes were inspected.
- 45 Bash code blocks passed syntax validation; 10 Python snippets parsed.
- VS Code JSON files parsed; helper shell scripts passed `bash -n`.
- The installer correctly refused this Debian host, rather than adding Ubuntu repositories to it.
- Its official GitHub release lookup resolved to `1.3.0`; the verified-HTTPS download of `ros2-apt-source_1.3.0.noble_all.deb` succeeded, with package metadata `ros2-apt-source`, version `1.3.0~noble`, architecture `all`.
- Original uploaded presentation is preserved byte-for-byte in `docs/source/`; SHA-256: `542928f72bbf7915e08b67c27c42fb0e0ff8da2f518bd0c0e772d5b42dd2b38c`.

## Scope of confidence

The final exercise has been executed against real ROS messages and real turtlesim, with Qt in offscreen mode. This is more than a syntax check or a mocked simulator. It does not establish that every possible machine is configured correctly. Windows installation, WSLg window display, local firewall settings, VS Code UI interactions, and a full fresh apt installation on the user's laptop were not executed in this cloud environment. Follow the README and run the same verification command locally to confirm those prerequisites. Webots and physical robots are outside slide 56's exercise.
