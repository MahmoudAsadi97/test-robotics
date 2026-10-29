"""Start the final exercise; use headless:=true for automated checks."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    declarations = [
        DeclareLaunchArgument('headless', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('seed', default_value='-1', description='-1: random; >=0: reproducible'),
        DeclareLaunchArgument('linear_speed', default_value='2.0'),
        DeclareLaunchArgument('angular_speed', default_value='2.0'),
    ]
    simulator = Node(
        package='turtlesim', executable='turtlesim_node', name='turtlesim', output='screen',
        additional_env={'QT_QPA_PLATFORM': PythonExpression([
            "'offscreen' if '", LaunchConfiguration('headless'), "' == 'true' else 'xcb'"])})
    controller = Node(
        package='my_robot_controller', executable='border_controller', output='screen',
        parameters=[{
            'seed': ParameterValue(LaunchConfiguration('seed'), value_type=int),
            'linear_speed': ParameterValue(LaunchConfiguration('linear_speed'), value_type=float),
            'angular_speed': ParameterValue(LaunchConfiguration('angular_speed'), value_type=float),
        }])
    # One failed/exited component should not leave the other silently running.
    handlers = [RegisterEventHandler(OnProcessExit(
        target_action=node, on_exit=[EmitEvent(event=Shutdown(reason='Exercise node exited'))]))
        for node in (simulator, controller)]
    return LaunchDescription(declarations + handlers + [simulator, controller])
