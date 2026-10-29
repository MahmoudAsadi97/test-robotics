# Introduction to Robotics & ROS 2 Jazzy — slide-by-slide guide

This guide follows all **56 slides** of `Introduction_Robotics&ROS2_Jazzy.pptx` by Arne Bauwens (Howest), dated 26 October 2026. It explains the concepts, restores fragmented code formatting, includes the commands, and connects the exercises to the working Python package in this repository.

The slide text, speaker notes, slide relationships, and embedded instructional screenshots were inspected. Slides 28–29 contain headings and an official installation link, **but no embedded installation-command screenshots or code blocks** in the supplied file. Their installation steps below are explicitly reconstructed. Corrections to the slides are marked **Correction**; extra implementation advice is marked **Implementation note**.

## How to use this guide

The target machine is **Windows with WSL 2 and Ubuntu 24.04**, with VS Code connected to that Ubuntu distribution. PowerShell blocks run on Windows; Bash blocks run in the Ubuntu terminal. Terminal prompts such as `root@...#` in screenshots are not part of commands. Use your ordinary Ubuntu account; use `sudo` only where shown for system installation.

The repository itself is the ROS workspace. Its `src/my_robot_controller/` directory is a ROS package, and the inner `src/my_robot_controller/my_robot_controller/` directory contains Python code. The slides call the workspace `~/ros2_ws`; your clone can have a different name. Run repository scripts from the repository root:

```bash
./scripts/install_ros_jazzy.sh   # one-time ROS installation on Ubuntu 24.04
./scripts/build.sh              # build the workspace
./scripts/run.sh test_node      # run one packaged exercise
```

See [README.md](../README.md) for the complete setup and VS Code run instructions. Shell environment changes made inside a script do not persist in its parent terminal; when using raw `ros2` commands, source ROS and this workspace in that terminal:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_DOMAIN_ID=0
```

These discovery settings match the run scripts' local-lab defaults. If you deliberately select a different domain, use that same value in every terminal.

The runnable exercises are:

| Slides | Executable | Purpose |
| --- | --- | --- |
| 46–48 | `test_node` | First node, one-second timer, and counter |
| 49–50 | `hello_publisher` | Publish `std_msgs/msg/String` messages |
| 51–53 | `draw_circle` | Publish forward and angular turtle velocity |
| 54–55 | `pose_subscriber` | Subscribe to and log the turtle pose |
| 56 | `border_controller` | Drive, detect borders, turn randomly inward, and resume |

## Slide 1 — Robotics & Edge AI: Introduction to Robotics & ROS 2

The course combines robotics fundamentals with ROS 2 software. This lecture progresses from manipulators and coordinate systems to writing Python ROS nodes. The practical work uses turtlesim, so it does not require a physical robot.

## Slide 2 — Table of contents

The six parts are: introduction to robotics; what ROS is; WSL/VS Code/Jazzy setup; prebuilt nodes, command line, and rqt; workspaces and packages; and writing nodes. Read the first sections for terminology, then use the later sections as a hands-on lab.

## Slide 3 — What is a robot?

The slide quotes the Oxford definition: a machine that can automatically carry out a complex series of actions, especially when programmable by a computer. The pictures illustrate that robots can take many forms; a robot need not resemble a human. The useful connection to this lab is the loop from sensing to computation to actuation: read a pose, decide a motion, and command a velocity.

## Slide 4 — Industrial robots

Industrial applications include manufacturing, welding, painting, pick-and-place, packaging/palletizing, and quality inspection. These tasks differ in their tooling and sensors, but frequently reuse motion control and automation ideas. A camera-based quality-inspection station and a welding arm can therefore share parts of a robotics software architecture.

## Slide 5 — Advantages of industrial robots

The slide lists speed, precision, reduced exposure to dangerous work, and lower cost over time. Robots can perform repetitive tasks continuously, but the practical benefits depend on uptime, integration, tooling, maintenance, and the task. High purchase cost can be justified by sustained use.

## Slide 6 — Industrial robot cost

The slide presents an approximate lifetime-cost split of one third purchase and two thirds maintenance, and notes that small production volumes and industrial requirements raise prices.

**Correction:** treat the split as a teaching estimate rather than a universal cost model. Integration, programming, safety equipment, energy, maintenance, downtime, and production volume vary substantially between installations.

## Slide 7 — Terminology

| Term | Meaning |
| --- | --- |
| Manipulator | Mechanical arm that positions and orients the tool |
| End effector | Gripper or other tool attached to the arm |
| Controller | Computes and controls joint motion and processes inputs/outputs |
| Teach pendant | Operator interface for programming, jogging, and operating the robot |

The pictured system makes the distinction between the physical arm, its tool, its controller, and its user interface.

## Slide 8 — Manipulator

The manipulator moves the end effector and its payload. Its task involves both **position** and **orientation** (called “attitude” on the slide). Rigid links and movable joints determine its geometry. Actuators drive motion, and sensors provide feedback so the controller can compare desired motion with actual motion.

## Slide 9 — Links and joints

A link is a rigid component in the kinematic chain. Link 0 is the base, and the final link connects to the end effector. A joint permits relative motion between neighboring links. Joint types, their arrangement, and link geometry determine the robot configuration.

**Correction:** the slide's “every joint = 1 DOF” describes common single-axis revolute and prismatic robot joints. It is not a general statement about every possible mechanical joint. The base is fixed in this arm model; a mobile manipulator can have a moving base.

## Slide 10 — Joint count and degrees of freedom

A degree of freedom (DOF) is an independent motion variable. One revolute joint sweeps a circular path; one prismatic joint moves along a line. Additional independent joints enlarge the reachable set. In a typical six-axis arm, the first three joints primarily place the wrist, and the wrist joints primarily orient the tool.

The **TCP** is the tool center point. Its position and orientation are the quantities the robot is usually asked to control.

**Correction:** two joints do not guarantee a flat planar workspace, and three joints do not automatically provide unrestricted 3D motion. Geometry, joint limits, coupled motion, and singularities matter. Arbitrary spatial pose generally requires six independent task-space DOFs: three position and three orientation components.

## Slide 11 — Kinematics

**Forward kinematics:** given joint positions, compute the tool pose in a chosen reference frame. **Inverse kinematics:** given a desired tool pose, find joint positions that achieve it. Frames allow the same point or pose to be expressed relative to the base, world, tool, or a sensor.

Inverse kinematics can have no solution, one solution, or several solutions. In the turtlesim exercise, `Pose.x`, `Pose.y`, and `Pose.theta` are already available, so no arm inverse-kinematics solver is needed.

## Slide 12 — External or redundant axes

Additional axes can extend reach or offer alternative configurations. Examples include a robot moving along a rail and an arm with an extra joint. Redundancy can help avoid undesirable postures, obstacles, and some singular configurations.

**Correction:** the slide title says “Joint types,” but its content concerns extra/redundant axes. An external axis that extends a work volume and an internally redundant arm joint are related but distinct ideas. Extra axes do not eliminate every singularity.

## Slide 13 — What is a cobot?

A collaborative industrial robot is intended for applications in which people and robots share a workspace. The slide describes it as a “cage-free” industrial robot and gives manufacturer examples.

**Correction:** “cobot” does not itself guarantee that an application can safely run without guarding. The tool, payload, speed, workpiece, surroundings, and application determine the safety measures needed.

## Slide 14 — Cobot technical design

The slide emphasizes easy integration and operation: low-code programming, hand-guided teaching, a clear pendant interface, and plug-and-play end effectors or safety devices. The pictured OnRobot tooling illustrates that the end effector is a separate choice from the arm.

## Slide 15 — Transition: what is ROS?

This table-of-contents slide begins the software section. Keep the earlier physical decomposition in mind: sensors, computation, and actuators will become communicating software components.

## Slide 16 — What is ROS?

ROS means **Robot Operating System**, but ROS 2 is a collection of middleware, libraries, tools, and conventions running on an operating system such as Ubuntu. It lets components exchange messages without each component implementing its own communication stack.

A **node** is a participant in the ROS graph. Nodes can publish and subscribe to **topics**, and act as **service** clients or servers. A node may have several of these roles simultaneously. Topic communication does not have a built-in request/reply pairing; services do.

## Slide 17 — Why use ROS?

ROS provides reusable components for sensing, control, mapping, navigation, and other tasks. Python and C++ are widely used client languages. Gazebo and Webots are simulators; RViz visualizes robot models, coordinate transforms, and sensor data.

**Implementation note:** RViz is not a physics simulator. Turtlesim is a simpler teaching simulator used here to make the communication concepts visible.

## Slide 18 — ROS 2 distributions

The deck lists these releases:

| Distribution | Release in deck | Ubuntu in deck | Support end in deck |
| --- | --- | --- | --- |
| Humble Hawksbill | May 2022 | 22.04 | May 2027 |
| Jazzy Jalisco | May 2024 | 24.04 | May 2029 |
| Kilted Kaiju | May 2025 | 24.04 | November 2026 |
| Lyrical Luth | May 2026 | 26.04 | May 2031 |

This project targets **Jazzy on Ubuntu 24.04**. Names such as `ros-jazzy-desktop`, `/opt/ros/jazzy`, and `/en/jazzy/` in documentation all refer to that distribution. Follow documentation for the same distribution as your installed software.

**Correction:** “each built for one Ubuntu version” and “Jazzy only runs on Ubuntu 24.04” simplify the support matrix. Ubuntu 24.04 is the supported Ubuntu target for Jazzy's binary packages used in this lab. ROS 2 also supports other platforms through specified support tiers and installation methods. Consult the [official distributions page](https://docs.ros.org/en/rolling/Releases.html) for current names and lifecycle details; the other releases are not requirements for this repository.

## Slide 19 — Transition: installation

This table-of-contents slide introduces WSL, VS Code, and ROS 2 setup. On native Ubuntu 24.04, skip the Windows/WSL steps and begin with the Ubuntu installation instructions.

## Slide 20 — Our setup

The architecture is:

```text
Windows
  ├── VS Code user interface
  └── WSL 2: Ubuntu 24.04
        ├── VS Code Server and Linux extensions
        ├── ROS 2 Jazzy
        └── repository / ROS workspace / Python nodes
```

The VS Code interface is on Windows, while the code, terminal, interpreter, and ROS installation used by this project are in Ubuntu. Keep the workspace in the Linux filesystem, such as `~/test-robotics`, for Linux permissions and faster filesystem operations. Webots on Windows and a networked Limo Pro robot appear later in the course; this lab runs locally inside WSL.

## Slide 21 — Setup in five steps

The five steps are WSL, networking, VS Code, ROS, and a workspace. Use **PowerShell as administrator** for system-level Windows setup; use **Bash in Ubuntu** for ROS installation and development. Understanding which shell owns a command prevents many setup problems.

## Slide 22 — Install or update WSL

In Windows PowerShell:

```powershell
wsl --version
```

If WSL is not installed:

```powershell
wsl --install --no-distribution
```

Restart Windows if requested. If WSL is already installed:

```powershell
wsl --update
```

The screenshot contains `wsl --version` and reports WSL 3.0.3.0, its kernel/WSLg versions, and a Windows build. Those exact component versions are examples, not required outputs. The Linux distribution must run as **WSL version 2**, which is a different version number from the WSL application version.

Error `0x80370102` or a virtualization-disabled message usually calls for checking hardware virtualization in BIOS/UEFI (Intel VT-x or AMD-V/SVM) and Windows virtualization support. See [Microsoft's WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install).

## Slide 23 — Install Ubuntu 24.04

In PowerShell:

```powershell
wsl --list --online
wsl --install -d Ubuntu-24.04
wsl -l -v
wsl --set-default Ubuntu-24.04
```

Create your Ubuntu username/password when prompted. Password entry is invisible; that is normal. Open that distribution later with:

```powershell
wsl -d Ubuntu-24.04
```

`wsl -l -v` should show `Ubuntu-24.04` with version `2`. If an existing installation uses WSL 1, convert it with:

```powershell
wsl --set-version Ubuntu-24.04 2
```

**Correction:** explicitly selecting `Ubuntu-24.04` is reliable; the unversioned `Ubuntu` alias does not mean “the required version.” Its resolved release depends on the currently published distribution.

## Slide 24 — Mirrored networking

The default NAT mode gives WSL a virtual network. Mirrored networking can simplify communication between WSL, Windows applications, and other machines, where supported by the Windows/WSL version.

For the later networked labs, the slide shows **WSL Settings → Networking → Mirrored**. Alternatively, edit the Windows user configuration from PowerShell:

```powershell
notepad $env:USERPROFILE\.wslconfig
```

Merge this section with any existing settings:

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

Apply it with PowerShell, then reopen Ubuntu:

```powershell
wsl --shutdown
```

The slide compares these commands:

```bash
hostname -I
```

```powershell
ipconfig
```

**Correction:** mirrored networking is useful for the later robot/network tasks, but is not required for this local turtlesim lab. Exact equality between the complete `hostname -I` and `ipconfig` outputs is not a universal health check: hosts can have several adapters and addresses. Verify the selected mode, internet access, and actual ROS communication. The screenshot's Auto Proxy toggle is off while the supplied configuration sets it to true; that setting should follow the network's proxy requirements.

## Slide 25 — Firewall rules

The slide provides the following **administrator PowerShell** commands for a networked lab:

```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultOutboundAction Allow
New-NetFirewallRule -DisplayName "ROS2 UDP 7400-7600" -Direction Inbound -Action Allow -Protocol UDP -LocalPort 7400-7600
New-NetFirewallRule -DisplayName "ROS2 UDP 7400-7600 Outbound" -Direction Outbound -Action Allow -Protocol UDP -LocalPort 7400-7600
```

The first two change default Hyper-V firewall policy for WSL; the second two allow a UDP port range through Windows Firewall.

**Correction:** these are broad teaching-lab rules, not prerequisites for this local exercise. Apply network-access changes only when needed on an appropriate trusted lab network, following the institution's policy. Scoped rules are preferable for a real network. DDS port usage depends on the middleware, domain ID, participant count, and configuration; `7400–7600` is not a universal complete ROS 2 port range. Outbound policies may already permit the needed traffic.

## Slide 26 — Troubleshoot networking

The screenshot shows:

```text
Error code: RegisterDistro/CreateVm/ConfigureNetworking/0x8007054f
wsl: Failed to configure network (networkingMode Mirrored), falling back to networkingMode None.
```

This particular fallback is **None**, so Ubuntu may have no internet. It is not a screenshot of a successful NAT fallback. First update WSL in PowerShell:

```powershell
wsl --update
wsl --shutdown
```

If mirrored mode still fails, set `.wslconfig` to:

```ini
[wsl2]
networkingMode=NAT
dnsTunneling=true
autoProxy=true
```

Then run `wsl --shutdown` again and reopen Ubuntu. Check package-server access with `sudo apt update`. All exercises in this repository can run locally using NAT. Later Windows-simulator or robot connections may need additional configuration; tell the teacher about the fallback.

## Slide 27 — Connect VS Code to WSL

1. Install [VS Code on Windows](https://code.visualstudio.com/).
2. Install Microsoft's **WSL** extension.
3. Press `Ctrl+Shift+P`, choose **WSL: Connect to WSL using Distro...**, and select **Ubuntu-24.04**.
4. Confirm the lower-left indicator identifies that WSL distribution.
5. Open the repository folder and **Terminal → New Terminal**. It should be an Ubuntu Bash terminal.
6. Install Microsoft's **Python** extension into WSL. The slide also recommends **Robot Developer Extensions for ROS 2** by Ranch Hand Robotics; the older Microsoft ROS extension is deprecated.

From the Ubuntu terminal inside the repository, this opens the folder in VS Code:

```bash
code .
```

The screenshot shows a Linux prompt and the `build`, `install`, `log`, and `src` directories. Use the Linux Python interpreter associated with system ROS (`/usr/bin/python3` in the standard Jazzy installation), not a Windows Python executable. See the repository README for its provided build/run tasks.

## Slide 28 — Install Jazzy: locale and package repository

The actual slide contains: “a) Make sure Ubuntu uses UTF-8,” “b) Add the ROS 2 package repository,” and the [official Jazzy Ubuntu binary installation guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html). It does not contain a command screenshot in the supplied PowerPoint.

**Reconstructed commands:** the repository supplies the full installation sequence in [scripts/install_ros_jazzy.sh](../scripts/install_ros_jazzy.sh):

```bash
./scripts/install_ros_jazzy.sh
```

The locale step in the official procedure has this shape:

```bash
locale
sudo apt update
sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale
```

Any properly configured UTF-8 locale can be suitable; the example uses `en_US.UTF-8`. The package-source step enables Ubuntu's `universe` repository and installs the official **`ros2-apt-source`** package from its GitHub release. That package configures the apt source and signing material. Use the installation script or the official guide for the complete release-specific download commands; the slide itself does not specify them.

## Slide 29 — Install Jazzy: development tools and desktop packages

**Reconstructed package-installation commands**, after the repository setup on slide 28:

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-dev-tools ros-jazzy-desktop
ls /opt/ros
```

Review the package-manager prompts before accepting. The final command should show `jazzy`. `apt` manages Ubuntu packages; `sudo` runs the requested command with administrator privileges. `ros-dev-tools` provides development tools such as colcon and rosdep; `ros-jazzy-desktop` supplies ROS, graphical tools, demos, and teaching packages.

ROS distribution files live under `/opt/ros/jazzy`; general development tools may be installed elsewhere in the system. An installation error is not solved by continuing to the next step: read the last error lines, repair network/repository/package problems, then rerun the failed step. The installation script combines slides 28–29; do not rerun the full process simply because you open a new terminal.

## Slide 30 — Source ROS 2

Installation puts files on disk. **Sourcing** a setup file configures the current shell so it can find those files and their dependencies:

```bash
source /opt/ros/jazzy/setup.bash
printenv ROS_DISTRO
```

The expected distribution is `jazzy`. The slide appends the following to Bash startup:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "ros2 daemon start > /dev/null 2>&1" >> ~/.bashrc
source ~/.bashrc
printenv ROS_DISTRO
```

`>>` appends; `>` overwrites. Run append commands only once, or edit with `code ~/.bashrc` and keep one copy of each intended line. Starting the daemon automatically is a workaround for the issue discussed on slide 32; normal ROS use usually starts it as needed.

The diagram shows the daemon caching the ROS graph for commands such as `ros2 topic list`. **The daemon is not a central message broker:** publisher/subscriber data does not have to flow through it.

## Slide 31 — Test the installation

Open two Ubuntu terminals and source ROS in each if it is not already sourced.

Terminal 1:

```bash
ros2 run demo_nodes_cpp talker
```

Terminal 2:

```bash
ros2 run demo_nodes_py listener
```

The C++ talker publishes “Hello World” messages, and the Python listener logs received messages. This checks that the language clients interoperate. The screenshot also shows an earlier `ros2 topic echo` session; that output is a separate inspection tool, not the listener executable. Stop each process with `Ctrl+C`.

## Slide 32 — Troubleshoot hanging ROS commands

The slide describes `ros2 node list` or `ros2 topic list` hanging for about two minutes and reporting a localhost timeout. Try:

```bash
ros2 daemon start
ros2 node list
```

If the daemon has stale settings, prefer its normal restart commands:

```bash
ros2 daemon stop
ros2 daemon start
```

The slide's fallback, when normal daemon control is stuck, is:

```bash
pkill -f _ros2_daemon
ros2 daemon start
```

That stops matching daemon processes owned by your user. It is troubleshooting, not a routine step in every run. You can inspect without the daemon:

```bash
ros2 node list --no-daemon --spin-time 5
```

To isolate local discovery from wider network problems, set this in **both/all relevant terminals before starting their nodes**, then restart the nodes and daemon:

```bash
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
```

**Correction:** a timeout alone does not prove the particular mirrored-networking cause described in the slide. Also check matching `ROS_DOMAIN_ID`, ROS distribution, middleware settings, and whether the nodes are running. `LOCALHOST` is appropriate for local testing but prevents discovery of a robot on another machine. Remove it with `unset ROS_AUTOMATIC_DISCOVERY_RANGE` when moving to a networked lab, then restart affected processes.

## Slide 33 — Create a workspace

The slide's commands, for a new workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
```

`src/` contains source packages. Builds generate `build/`, `install/`, and `log/`. **Do not run `sudo colcon build`**: generated files should belong to your normal user.

The slide sources the workspace and enables completion in `.bashrc`:

```bash
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc
source ~/.bashrc
code ~/ros2_ws
```

**Implementation note:** this repository already is the workspace; do not create a second nested `ros2_ws` around its `src/` folder. Build it with `./scripts/build.sh`. When adding startup sources, use the actual clone location and guard files that may not exist yet. For a clone at `~/test-robotics`, add these lines once to `.bashrc`, after sourcing `/opt/ros/jazzy/setup.bash`:

```bash
[ -f "$HOME/test-robotics/install/setup.bash" ] && source "$HOME/test-robotics/install/setup.bash"
[ -f /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash ] && source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
```

The supplied run script handles sourcing for its own process, so automatic workspace sourcing is optional.

## Slide 34 — Setup checklist

Verify that WSL reports Ubuntu 24.04 using version 2; VS Code connects to that distribution; a sourced new terminal prints `jazzy`; and the demo talker/listener communicate. After building this repository, verify that `src`, `build`, `install`, and `log` exist at the repository root.

**Correction:** the slide's matching-IP checklist item applies to its intended mirrored-network setup, not to the success of this local lab. A functioning NAT configuration is sufficient here.

## Slide 35 — Transition: prebuilt nodes, CLI, and rqt

The setup is complete. The next section uses existing nodes to learn the ROS graph before writing new code. Every long-running node normally occupies one terminal; use additional terminals for inspection.

## Slide 36 — ROS 2 nodes

A node implements a focused computational role. Different nodes can run independently, can communicate across machines, and can be reused in other systems. Examples include a camera driver, pose estimator, and motion controller.

**Correction:** a node is not necessarily one operating-system process. Several composable nodes can share a process; a process crash can then affect all of them. Independently launched processes generally remain alive if another process crashes, although a dependent component may no longer have useful input.

The linked [Jazzy nodes tutorial](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html) explains graph inspection.

## Slide 37 — Communication mechanisms

| Mechanism | Appropriate use | Example |
| --- | --- | --- |
| Topic | Asynchronous streams, many publishers/subscribers | Turtle pose and velocity |
| Service | A bounded request and response | Reset the simulation |
| Action | A longer task with progress and cancellation | Rotate to a target orientation |
| Parameter | Node configuration | Controller speed |

**Correction:** services describe a request/response interaction; ROS clients can call them asynchronously. Calling all service use “synchronous” is too restrictive. Parameter updates at runtime also depend on what the node permits and implements.

## Slide 38 — `ros2 run`, executable names, and node names

General syntax:

```text
ros2 run <package_name> <executable_name>
```

Examples (each long-running executable in a separate terminal):

```bash
ros2 run turtlesim turtlesim_node
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_py listener
```

Inspect from another terminal:

```bash
ros2 node list
```

The screenshot answers the slide's “Node name = ?” question: package `turtlesim`, executable `turtlesim_node`, and default node name **`/turtlesim`**. These three names need not match. The other defaults are `/talker` and `/listener`.

## Slide 39 — Packages and topic output

A ROS package groups related nodes, libraries, configuration, and other resources. The talker executable publishes messages on `/chatter`; its terminal log comes from logging calls in its code.

To see actual topic messages:

```bash
ros2 topic echo /chatter
```

The slide's `ros2 topic echo $topic` is a shell-variable pattern: it only works if `topic` has been assigned. A concrete topic name is clearer for this lab. The screenshot shows:

```yaml
data: 'Hello World: 14'
---
data: 'Hello World: 15'
---
```

**Correction:** contrary to the slide's parenthetical statement, `ros2 topic echo` creates a ROS node with a subscription. Running it can change the subscriber count and the visible graph. Console logs and received topic messages are different observations.

## Slide 40 — rqt and rqt_graph

`rqt` is a framework for graphical ROS tools. `rqt_graph` displays node/topic relationships. With the talker and listener running:

```bash
rqt_graph
```

The slide's diagram is `/talker → /chatter → /listener`. Depending on the view, topics can appear as labels on arrows or their own boxes. Graph filters affect which topics/nodes are visible; refresh the graph after starting processes. Diagram colors in the teaching illustration are not a universal semantic color scheme for all rqt views.

## Slide 41 — Turtlesim and keyboard control

Terminal 1:

```bash
ros2 run turtlesim turtlesim_node
```

Terminal 2:

```bash
ros2 run turtlesim turtle_teleop_key
```

Terminal 3:

```bash
rqt_graph
```

Focus **the teleop terminal** and use its arrow keys. The graph shows `/teleop_turtle` sending `/turtle1/cmd_vel` to `/turtlesim`. It also shows action feedback/status topics for `/turtle1/rotate_absolute`; those are part of the teleop node's action support, not alternative velocity commands.

Stop teleop before running an autonomous velocity publisher, so the turtle receives a single intended source of velocity commands.

## Slide 42 — Transition: workspaces and packages

Now move from installed ROS packages to the package in this repository. Building and sourcing an overlay makes your own executables discoverable alongside the system-installed ROS packages.

## Slide 43 — Workspace and colcon

Build from the workspace root, where `src/` is located:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

The slide's layout is:

```text
workspace/
├── src/       # packages you edit
├── build/     # build intermediates
├── install/   # installed packages and setup.bash
└── log/       # build logs
```

**Correction:** the slide also suggests `echo "source install/setup.bash " >> ~/.bashrc`. Do not use that relative path in `.bashrc`: it resolves relative to whichever directory the new shell starts in. Use the actual workspace path as shown on slide 33.

`--symlink-install` makes many Python source edits available without rebuilding. Restart a running process to load edits. Rebuild after changing entry points, package metadata, dependencies, or installed resources; symlinking is not a replacement for all builds. The repository wrapper is `./scripts/build.sh`.

## Slide 44 — Create a Python package

For a fresh workspace, the slide creates a package with:

```bash
cd ~/ros2_ws/src
ros2 pkg create my_robot_controller --build-type ament_python --dependencies rclpy
cd ~/ros2_ws
colcon build
```

**Implementation note:** this repository already contains `my_robot_controller`; do not run package creation over it. The complete exercises also need `std_msgs`, `geometry_msgs`, and `turtlesim`, which are declared in its manifest.

| Path inside the package | Role |
| --- | --- |
| `package.xml` | ROS package identity, dependencies, and build type |
| `setup.py` | Python packaging and executable entry points |
| `setup.cfg` | Install scripts where `ros2 run` expects them |
| `resource/my_robot_controller` | Package marker for the ament resource index |
| `my_robot_controller/` | Importable Python package and node code |
| `my_robot_controller/__init__.py` | Marks the directory as a Python package |

The outer directory is the ROS package; the identically named inner directory is the Python package.

## Slide 45 — Transition: write your own nodes

The remaining slides build incrementally: create a node, add a timer, publish strings, publish velocity, subscribe to pose, and combine publishing/subscribing in a controller. The repository keeps each demonstration as a separate runnable executable.

## Slide 46 — First Python node

The slide's code, with its formatting restored:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__('first_node')
        self.get_logger().info('Hello from ROS2')


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

The shebang selects Python when running the file directly. `rclpy.init()` initializes the ROS context, the constructor sets the node name and logs once, and `rclpy.shutdown()` ends the context. This first version intentionally exits immediately.

To run that file directly, the slide uses these commands from the **inner Python directory**, with ROS already sourced:

```bash
chmod +x my_first_node.py
./my_first_node.py
```

The repository's `test_node` includes the timer/counter extension from slide 48, so it stays alive. The executable wrapper created by packaging removes the need to manually run or mark the source file executable for normal `ros2 run` use. The repository also performs explicit node cleanup.

## Slide 47 — Register an executable entry point

The slide adds this mapping to `setup.py`:

```python
entry_points={
    'console_scripts': [
        'test_node = my_robot_controller.my_first_node:main',
    ],
},
```

Read it as: create an executable named `test_node`; import `my_robot_controller.my_first_node`; call its `main` function. A module name omits the `.py` suffix.

Build/source/run from the workspace root:

```bash
colcon build --symlink-install
source install/setup.bash
ros2 run my_robot_controller test_node
```

The repository shortcut, which sources the needed environment, is:

```bash
./scripts/run.sh test_node
```

**Implementation note:** an executable name, Python class name, module filename, and ROS node name are separate identifiers. The repository's `setup.py` is the authoritative mapping if its module filenames differ from the lecture's illustrative names.

## Slide 48 — Add a timer and counter

The slide adds a one-second timer:

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('first_node')
        self.get_logger().info('Hello from ROS2')
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info('hello again')
```

Its `main` function now spins:

```python
def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
```

`rclpy.spin(node)` lets the executor service callbacks, including timer and subscription callbacks. Without a spin/executor, this program finishes before its timer can run.

The slide's exercise is to count how many times the repeated greeting has been printed. The essential change is:

```python
# In __init__:
self.counter = 0

# In timer_callback:
self.counter += 1
self.get_logger().info(f'hello again: {self.counter}')
```

This counts timer greetings, excluding the one-time startup message. Run `test_node` and use another sourced terminal:

```bash
ros2 node list
```

Expect `/first_node`. Stop with `Ctrl+C`. A running node needs to be restarted after code edits even with `--symlink-install`.

## Slide 49 — Inspect a topic and message type

Run the demo talker and listener again, then inspect:

```bash
ros2 topic info /chatter
ros2 interface show std_msgs/msg/String
ros2 topic echo /chatter
```

The full message type is **`std_msgs/msg/String`**: package `std_msgs`, interface category `msg`, message `String`. Its payload field is:

```text
string data
```

Construct a message in Python:

```python
from std_msgs.msg import String

msg = String()
msg.data = 'Hello World: 1'
```

The screenshot also lists `Int32`, `Float64`, and `Bool` as examples of standard message names and diagrams `msg/`, `srv/`, and `action/` as interface categories. It is a conceptual layout, not a claim that every interface package implements all three categories.

The slide's `{ "data": "" }` comment illustrates the field content; a generated ROS `String` object is not a Python dictionary. `ros2 interface show` displays an interface definition and its comments, rather than logs from the running talker.

## Slide 50 — Publish your own string topic

Add the runtime dependency to `package.xml`:

```xml
<depend>std_msgs</depend>
```

The slide's `$type`, `$topic`, and `queue_size` are placeholders, not runnable Python. A concrete publisher looks like:

```python
from std_msgs.msg import String

# In a Node subclass's __init__:
self.publisher = self.create_publisher(String, '/hello', 10)

# In its timer callback, after updating self.counter:
msg = String()
msg.data = f'Timer callback triggered: {self.counter}'
self.publisher.publish(msg)
```

The last argument, `10`, is a queue-depth shorthand for the quality-of-service configuration. Message type and topic name must agree with the intended subscribers.

Run the repository's implementation:

```bash
./scripts/run.sh hello_publisher
```

In another sourced terminal inspect the publisher's `/hello` topic:

```bash
ros2 topic list
ros2 node info /hello_publisher
ros2 topic info /hello
ros2 topic echo /hello
```

Its message type is `std_msgs/msg/String`, so the same `ros2 interface show` command from slide 49 applies. The complete executable includes the timer, initialization, spin, and shutdown omitted from this short teaching fragment.

## Slide 51 — Find the turtle's control topic

Start turtlesim and keyboard teleop as on slide 41, then:

```bash
ros2 topic list
ros2 node info /teleop_turtle
ros2 topic info /turtle1/cmd_vel
ros2 interface show geometry_msgs/msg/Twist
ros2 topic echo /turtle1/cmd_vel
```

Press an arrow key in the teleop terminal and observe the message in the echo terminal. The control topic is **`/turtle1/cmd_vel`**. Its type is **`geometry_msgs/msg/Twist`**. Stop teleop before testing the later autonomous controllers.

## Slide 52 — Understand `Twist`

Inspect its definition:

```bash
ros2 interface show geometry_msgs/msg/Twist
```

The structure is:

```text
Vector3 linear
    float64 x
    float64 y
    float64 z
Vector3 angular
    float64 x
    float64 y
    float64 z
```

`linear` describes translational velocity; `angular` describes rotational velocity. In conventional robotics use, the units are metres per second and radians per second. Turtlesim uses its simulated coordinate scale. For this exercise, `linear.x` means **forward in the turtle's body frame**, and `angular.z` means turning in the screen plane. Positive `angular.z` turns counterclockwise. `Twist` itself has no frame-id field: the topic's receiver defines the interpretation.

The slide gives three payloads. These are runnable Bash commands using the same values (all omitted fields remain zero):

```bash
# Forward. Ctrl+C stops this publisher; send the zero command below afterward.
ros2 topic pub --rate 10 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.0}}'

# Rotate in place.
ros2 topic pub --rate 10 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0}, angular: {z: 0.5}}'

# Forward and turn together.
ros2 topic pub --rate 10 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}, angular: {z: 0.2}}'
```

Run one command at a time, stopping it with `Ctrl+C` before the next. An explicit stop command is:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{}'
```

With zero angular velocity and the default starting orientation `theta = 0`, forward motion follows the world's positive x-axis. After rotation, forward motion no longer necessarily follows the world's x-axis.

## Slide 53 — Write a circle publisher

The slide asks for a new node that creates a `Twist` publisher and repeatedly sends a command from a timer. Required imports/dependencies:

```python
from geometry_msgs.msg import Twist
```

```xml
<depend>geometry_msgs</depend>
<depend>turtlesim</depend>
```

A concrete version of its publisher fragment is:

```python
# In __init__:
self._cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
self.timer = self.create_timer(0.1, self.timer_callback)

# As a method of the node:
def timer_callback(self):
    msg = Twist()
    msg.linear.x = 0.5
    msg.angular.z = 0.2
    self._cmd_vel_pub.publish(msg)
```

Nonzero constant forward velocity and nonzero constant turn rate trace a circle. In an unconstrained plane its radius is `abs(linear.x / angular.z)`; these illustrative values give a radius of 2.5 simulated distance units. A wall can clip the path if the selected circle does not fit.

Run turtlesim in one terminal and the completed publisher in another:

```bash
./scripts/run.sh draw_circle
```

The repository executable uses `linear.x = 2.0`, `angular.z = 1.0`, and a 0.05-second timer, giving a radius of 2 simulated distance units. These are implementation choices; the slide does not prescribe the speed or radius. The important axes are `linear.x` and `angular.z`; setting only `angular.z` rotates in place, while setting only `linear.x` drives straight.

## Slide 54 — Inspect all topics in rqt

The embedded rqt screenshot explicitly shows:

| Direction | Topic |
| --- | --- |
| `/teleop_turtle` → `/turtlesim` | `/turtle1/cmd_vel` |
| `/turtlesim` → subscribers | `/turtle1/pose` (highlighted in yellow) |
| `/turtlesim` → subscribers | `/turtle1/color_sensor` |
| `/turtlesim` → `/teleop_turtle` | `/turtle1/rotate_absolute/_action/status` and feedback |

Select a view such as **Nodes/Topics (all)** and check the hide/filter options if a topic is missing from the display. A topic without a subscriber can be hidden by the graph settings. `ros2 topic list` is a useful companion check.

The highlighted pose topic is the feedback needed for the final controller. The action status/feedback paths shown here do not need to be implemented for the exercise.

## Slide 55 — Write a pose subscriber

Inspect the topic:

```bash
ros2 topic list
ros2 topic echo /turtle1/pose
ros2 topic info /turtle1/pose
ros2 interface show turtlesim/msg/Pose
```

The pose contains `x`, `y`, `theta`, `linear_velocity`, and `angular_velocity`. The heading `theta` is in radians. The slide's subscriber fragment, with formatting restored, is:

```python
from turtlesim.msg import Pose

# In a Node subclass's __init__:
self._pose_subscriber = self.create_subscription(
    Pose, '/turtle1/pose', self.pose_callback, 10
)

# As a method of the node:
def pose_callback(self, msg: Pose):
    self.get_logger().info(str(msg))
```

Declare `<depend>turtlesim</depend>` in `package.xml`. The callback runs when messages arrive while the node is spinning. Keep a reference to the subscription, and avoid long blocking operations in callbacks.

With turtlesim running, start the completed example:

```bash
./scripts/run.sh pose_subscriber
```

This provides observation only; subscribing does not by itself send any motion command.

## Slide 56 — Final exercise: border controller

The exact task is:

> Create a controller (node) for the turtlesim that starts moving along the x-axis. When it reaches the border of the screen it should rotate in a random direction and start moving forward. You'll need a publisher to cmd_vel and a subscriber to pose.

For turtle 1, these names resolve to:

| Role | Topic | Message |
| --- | --- | --- |
| Read current position/orientation | `/turtle1/pose` | `turtlesim/msg/Pose` |
| Command motion | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |

The implemented `border_controller` combines the earlier exercises. It starts with the default turtle facing the positive x direction, drives forward, detects a border using pose feedback, turns toward a randomly chosen inward heading, then resumes driving. Choosing an inward heading preserves randomness while avoiding repeated commands straight into the wall. A margin inside the visible wall allows the controller time to react.

A useful conceptual state machine is:

```text
wait for pose → drive forward → border detected → rotate in place
                     ↑                              |
                     └──── target heading reached ──┘
```

While turning, forward velocity is zero. When driving, turn velocity is zero. The controller uses pose feedback to decide when the desired rotation has been reached; it does not block the subscription with a long sleep. Internally, an `escaping` state keeps it moving away from an edge until it has cleared the border margin, avoiding repeated turns at the same edge.

Run a fresh turtlesim in terminal 1:

```bash
ros2 run turtlesim turtlesim_node
```

Run the completed exercise from the repository root in terminal 2:

```bash
./scripts/run.sh border_controller
```

Stop teleop, `draw_circle`, and any manual `ros2 topic pub` commands before starting the controller. ROS permits multiple publishers on the same topic, so leaving them running can create competing motion commands.

In a third sourced terminal:

```bash
ros2 node list
ros2 node info /border_controller
ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/pose
rqt_graph
```

Observe an initial horizontal segment, a turn near an edge, and a new straight segment into the available area. Let it encounter several borders and a corner to inspect continued behavior. Repeating the run should allow different turn choices. The repository README documents the executable's parameters, launch option, and verification commands.

**Implementation note:** turning randomly inward is an explicit interpretation of the slide's under-specified “random direction.” Purely random headings over the full circle can aim outside the screen and leave a naïve implementation stuck. The additional margin, turn state, corner handling, and cleanup support the requested behavior without requiring any physical robot hardware.

## Corrections to remember while studying

- Jazzy's Ubuntu binary target for this lab is Ubuntu 24.04; that is more precise than claiming ROS runs on only one operating system/version.
- NAT is sufficient for local turtlesim. Mirrored networking and broad firewall changes are not required merely to run this repository.
- The ROS daemon caches graph information for tools; it is not the route through which all topic messages pass.
- `ros2 topic echo` creates a subscriber, so using it changes the graph.
- Use an actual workspace path when sourcing from `.bashrc`; a relative `source install/setup.bash` only works from the correct working directory.
- `--symlink-install` helps with Python source edits; entry-point/metadata changes still need a rebuild, and running nodes still need a restart.
- `linear.x` is the turtle's forward axis. It equals the world's positive x direction only when the turtle's heading is zero.
- The final controller must combine **pose feedback**, **velocity output**, and **state over time**. Publishing a fixed circle alone does not satisfy slide 56.
