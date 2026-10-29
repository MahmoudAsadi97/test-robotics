# Introduction to Robotics & ROS 2 Jazzy

A runnable companion to the [supplied presentation](docs/source/Introduction_Robotics_ROS2_Jazzy.pptx) (56 slides), including the final turtlesim exercise. The turtle starts forward along +x, stops translating near a border, turns toward a randomly selected inward heading, then moves forward again. It repeats this at every border, including corners.

## Start in VS Code on Windows + WSL 2

### 1. Prepare Windows once

In **PowerShell as administrator**, check `wsl --version`. If WSL is absent:

```powershell
wsl --install --no-distribution
```

Restart Windows if requested. Then:

```powershell
wsl --update
wsl --install -d Ubuntu-24.04
wsl --set-default Ubuntu-24.04
wsl -l -v
```

Create your Linux username/password when Ubuntu asks. The last command must show Ubuntu-24.04 using version 2; use `wsl --set-version Ubuntu-24.04 2` if needed. Skip installation when that distribution already exists. Install **VS Code on Windows** and Microsoft's **WSL** extension. An up-to-date WSL installation with WSLg displays the turtlesim window. NAT networking is sufficient for this local exercise; the slide guide explains mirrored networking for later robot/Webots work.

### 2. Open the project inside Ubuntu

Open **Ubuntu-24.04**, then clone the repository once the files have been pushed to GitHub, or copy the supplied repository into your Linux home folder:

```bash
cd ~
git clone https://github.com/MahmoudAsadi97/test-robotics.git
cd test-robotics
code .
```

If you already have the populated checkout, open that folder instead of cloning again. Keep it under Linux home, for example `~/test-robotics`, rather than `/mnt/c`. In VS Code, check the bottom-left shows **WSL: Ubuntu-24.04**. Install the suggested Python and Robot Developer Extensions for ROS 2 extensions **in WSL**. Use `/usr/bin/python3` as the Python interpreter.

### 3. Install, build, and run

In **VS Code → Terminal → New Terminal** (Ubuntu bash):

```bash
./scripts/install_ros_jazzy.sh   # first time only; asks for sudo password
./scripts/build.sh
./scripts/run.sh
```

The installer uses Ubuntu's signed apt repositories and the official ROS apt-source package over verified HTTPS. It installs ROS 2 Jazzy Desktop, development tools and pytest. Installation may take several minutes. If apt asks for a reboot or reports an interrupted system upgrade, complete your Ubuntu maintenance before continuing. Do not run the build with sudo.

**Expected:** a turtlesim window appears, the turtle initially travels right, rotates near the edge, then travels in a new direction. Stop with **Ctrl+C** in the launch terminal. Only one velocity controller should run for `/turtle1` at a time; stop teleop/circle publishers before running the final exercise.

The scripts source ROS and this workspace automatically. VS Code also provides **Terminal → Run Task → ROS: Build / ROS: Run exercise / ROS: Full verification**. `Ctrl+Shift+B` builds. Source files are under `src/my_robot_controller/my_robot_controller/`. Avoid the Python “Run File” button for ROS nodes; use the tasks or `ros2 run` so ROS dependencies are available.

### 4. Verify locally

```bash
./scripts/test.sh                 # unit tests + actual ROS message tests
./scripts/test.sh --integration   # real headless turtlesim acceptance test
```

All tests use a separate local DDS domain (42 by default). The integration check creates its own simulator/controller and stops those processes afterwards. It writes `reports/ros-validation.json` and `reports/ros-launch.log`. A failed assertion returns a nonzero exit code. See [validation evidence](docs/VALIDATION.md) for what was actually executed in the cloud and what still depends on your laptop.

## Learn the slides and run the examples

Read the [slide-by-slide guide](docs/SLIDE_GUIDE.md) for all 56 slides, commands, code explanations, and corrections to ambiguous slide instructions.

| Slides | Executable | Purpose |
| --- | --- | --- |
| 46–48 | `test_node` | Log hello every second and count callbacks |
| 49–50 | `hello_publisher` | Publish `std_msgs/String` on `/hello` |
| 51–53 | `draw_circle` | Publish `Twist`: linear.x=2, angular.z=1 |
| 54–55 | `pose_subscriber` | Log every `/turtle1/pose` message |
| 56 | `border_controller` | Use pose feedback for repeated random border turns |

For example:

```bash
./scripts/run.sh test_node
# Ctrl+C, then:
./scripts/run.sh hello_publisher
```

In a second terminal, prepare the environment before using raw ROS commands:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_DOMAIN_ID=0
ros2 topic echo /hello
```

For the circle exercise, start `ros2 run turtlesim turtlesim_node` in that sourced terminal, then `./scripts/run.sh draw_circle` in another. `./scripts/run.sh pose_subscriber` can observe either the circle or border exercise. Use `rqt_graph` to see the topic connections.

## Final exercise configuration

```bash
./scripts/run.sh exercise seed:=7              # repeatable random choices
./scripts/run.sh exercise linear_speed:=3.0    # faster movement
./scripts/run.sh exercise headless:=true       # no visible window
```

Launch defaults: linear speed 2 units/s, angular speed at most 2 rad/s, safety margin 0.8 units, control rate 30 Hz, stale-pose timeout 0.5 s. Default seed `-1` uses fresh randomness. Random headings are constrained inward to avoid immediately driving into the same wall. The margin compensates for message/control latency: the turtle turns **near** the border without requiring a collision. The controller alternates `forward → turning → escaping → forward`; `escaping` prevents selecting a new turn before it clears the edge.

All controller settings are startup-only ROS parameters. Advanced example, with turtlesim started separately:

```bash
./scripts/run.sh border_controller --ros-args -p margin:=1.0 -p seed:=7
```

Restart the node to change settings. Invalid/nonfinite values fail clearly. Missing or stale pose produces zero velocity. This controller is specifically for turtlesim; it is not a hardware navigation or safety controller.

## Project layout

```text
test-robotics/                 colcon workspace root
├── .vscode/                   tasks, interpreter and extension recommendations
├── docs/                      all slides, design and measured validation
├── scripts/                   install, build, run and verification commands
├── src/my_robot_controller/
│   ├── package.xml            ROS dependencies
│   ├── setup.py, setup.cfg    Python package / ros2 run entry points
│   ├── resource/              ament package registration
│   ├── launch/                simulator + controller launch
│   ├── my_robot_controller/   educational nodes + motion state machine
│   └── test/                  motion, parameter, timeout and DDS tests
└── build/, install/, log/, reports/   generated and ignored by Git
```

The repository is already a workspace; there is no need to create another `src` directory above it. `--symlink-install` makes Python edits available immediately; rebuild after changing entry points, dependencies or launch metadata.

## Troubleshooting

- **`ros2: command not found`:** use the scripts, or source `/opt/ros/jazzy/setup.bash` in each terminal.
- **Package/executable not found:** run `./scripts/build.sh`; source `install/setup.bash` in raw-command terminals.
- **No window / Qt display error:** confirm VS Code is connected to Ubuntu 24.04 and run `echo "$DISPLAY"`. Update WSL, then `wsl --shutdown` from PowerShell and reopen Ubuntu. Headless verification still runs with `headless:=true`.
- **No movement:** stop other controllers, use the same `ROS_DOMAIN_ID` and `ROS_AUTOMATIC_DISCOVERY_RANGE` in all terminals, then check `ros2 topic echo /turtle1/pose` and `/turtle1/cmd_vel`. The controller intentionally waits for pose.
- **CLI hangs:** run `ros2 daemon stop`, `ros2 daemon start`, or `ros2 node list --no-daemon --spin-time 5` in the same configured terminal.
- **Build permission errors:** do not use sudo for builds. A previously root-owned workspace needs its ownership corrected; copying/cloning into your Linux home as your normal user avoids this.
- **Python import errors:** use system `/usr/bin/python3`, not a Windows, Conda, or unrelated virtual-environment Python.
- **Integration domain already in use:** stop unrelated test processes or use `ROBOTICS_TEST_DOMAIN=43 ./scripts/test.sh --integration`.

Official references: [ROS 2 Jazzy installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html), [ROS tutorials](https://docs.ros.org/en/jazzy/Tutorials.html), [WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install), [VS Code WSL](https://code.visualstudio.com/docs/remote/wsl).

The implementation code uses the Apache-2.0 license. The supplied teaching presentation remains attributed to its author; the repository code license does not relicense the presentation.
