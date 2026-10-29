"""Behavior tests for the motion controller; these also run without ROS 2."""

import math
import random
import unittest

from my_robot_controller.motion import BorderMotion, Config, Pose2D, Velocity


class MotionTests(unittest.TestCase):
    def controller(self, seed=17, **config):
        return BorderMotion(Config(**config), random.Random(seed))

    def test_default_turtle_starts_straight_along_positive_x(self):
        controller = self.controller()
        velocity = controller.update(Pose2D(5.54445, 5.54445, 0.0))
        self.assertEqual(velocity, Velocity(2.0, 0.0))
        self.assertEqual(controller.state, "forward")
        self.assertIsNone(controller.target_heading)
        self.assertEqual(controller.turn_count, 0)

    def test_each_border_stops_and_selects_an_inward_heading(self):
        cases = [
            (0.75, 5.5, math.pi, 1, 0),
            (10.4, 5.5, 0, -1, 0),
            (5.5, 0.75, -math.pi / 2, 0, 1),
            (5.5, 10.4, math.pi / 2, 0, -1),
        ]
        for x, y, theta, inward_x, inward_y in cases:
            with self.subTest(x=x, y=y):
                controller = self.controller()
                velocity = controller.update(Pose2D(x, y, theta))
                self.assertEqual(velocity.linear, 0.0)
                self.assertNotEqual(velocity.angular, 0.0)
                self.assertEqual(controller.state, "turning")
                self.assertEqual(controller.turn_count, 1)
                heading = controller.target_heading
                self.assertGreater(
                    inward_x * math.cos(heading) + inward_y * math.sin(heading),
                    0.0,
                )

    def test_each_corner_heading_moves_away_from_both_walls(self):
        for x, dx in [(0.75, 1), (10.4, -1)]:
            for y, dy in [(0.75, 1), (10.4, -1)]:
                for seed in range(40):
                    with self.subTest(x=x, y=y, seed=seed):
                        controller = self.controller(seed)
                        theta = math.atan2(-dy, -dx)
                        command = controller.update(Pose2D(x, y, theta))
                        self.assertEqual(command.linear, 0.0)
                        self.assertGreater(dx * math.cos(controller.target_heading), 0)
                        self.assertGreater(dy * math.sin(controller.target_heading), 0)

    def test_nearby_border_does_not_interrupt_motion_away_from_it(self):
        for pose in [
            Pose2D(0.7, 5.5, 0), Pose2D(10.5, 5.5, math.pi),
            Pose2D(5.5, 0.7, math.pi / 2), Pose2D(5.5, 10.5, -math.pi / 2),
        ]:
            with self.subTest(pose=pose):
                controller = self.controller()
                self.assertEqual(controller.update(pose), Velocity(2.0, 0.0))
                self.assertEqual(controller.turn_count, 0)

    def test_tangential_motion_does_not_trigger_spurious_turns(self):
        controller = self.controller()
        self.assertEqual(
            controller.update(Pose2D(0.7, 5.5, math.pi / 2)),
            Velocity(2.0, 0.0),
        )

    def test_turn_target_is_selected_once_while_rotating(self):
        controller = self.controller()
        pose = Pose2D(10.4, 5.5, 0)
        controller.update(pose)
        target = controller.target_heading
        for _ in range(100):
            velocity = controller.update(pose)
            self.assertEqual(velocity.linear, 0.0)
            self.assertEqual(controller.target_heading, target)
            self.assertEqual(controller.turn_count, 1)

    def test_rotate_then_escape_then_resume_regular_forward_motion(self):
        controller = self.controller()
        controller.update(Pose2D(10.4, 5.5, 0))
        target = controller.target_heading
        self.assertEqual(
            controller.update(Pose2D(10.4, 5.5, target)), Velocity(2.0, 0.0)
        )
        self.assertEqual(controller.state, "escaping")
        for x in [10.35, 10.30, 10.25]:
            self.assertEqual(
                controller.update(Pose2D(x, 5.5, target)), Velocity(2.0, 0.0)
            )
            self.assertEqual(controller.state, "escaping")
            self.assertEqual(controller.turn_count, 1)
        self.assertEqual(
            controller.update(Pose2D(9.9, 5.5, target)), Velocity(2.0, 0.0)
        )
        self.assertEqual(controller.state, "forward")
        controller.update(Pose2D(0.7, 5.5, math.pi))
        self.assertEqual(controller.state, "turning")
        self.assertEqual(controller.turn_count, 2)

    def test_escaping_stops_if_heading_is_changed_toward_wall(self):
        controller = self.controller()
        controller.update(Pose2D(10.4, 5.5, 0))
        controller.update(Pose2D(10.4, 5.5, controller.target_heading))
        velocity = controller.update(Pose2D(10.4, 5.5, 0))
        self.assertEqual(velocity.linear, 0.0)
        self.assertEqual(controller.state, "turning")
        self.assertEqual(controller.turn_count, 2)

    def test_changed_position_during_turn_cannot_release_unsafe_forward_command(self):
        controller = self.controller()
        controller.update(Pose2D(10.4, 5.5, 0))
        velocity = controller.update(Pose2D(0.7, 5.5, controller.target_heading))
        self.assertEqual(velocity.linear, 0.0)
        self.assertEqual(controller.state, "turning")

    def test_wrapped_angles_choose_signed_shortest_rotation(self):
        for error, direction in [(0.2, 1), (-0.2, -1)]:
            with self.subTest(error=error):
                controller = self.controller()
                controller.update(Pose2D(10.4, 5.5, 0))
                target = controller.target_heading
                velocity = controller.update(Pose2D(10.4, 5.5, target + 2 * math.pi - error))
                self.assertGreater(direction * velocity.angular, 0.0)
                self.assertEqual(velocity.linear, 0.0)
                self.assertLessEqual(abs(velocity.angular), 2.0)

    def test_turn_finishes_within_tolerance_across_angle_wrap(self):
        controller = self.controller()
        controller.update(Pose2D(10.4, 5.5, 0))
        target = controller.target_heading
        self.assertEqual(
            controller.update(Pose2D(10.4, 5.5, target + 2 * math.pi + 0.02)),
            Velocity(2.0, 0.0),
        )

    def test_configured_tolerance_controls_when_translation_resumes(self):
        for tolerance, should_rotate in [(0.01, True), (0.1, False)]:
            with self.subTest(tolerance=tolerance):
                controller = self.controller(turn_tolerance=tolerance)
                controller.update(Pose2D(10.4, 5.5, 0))
                velocity = controller.update(
                    Pose2D(10.4, 5.5, controller.target_heading + 0.08)
                )
                if should_rotate:
                    self.assertEqual(velocity.linear, 0)
                    self.assertLess(velocity.angular, 0)
                else:
                    self.assertEqual(velocity, Velocity(2.0, 0.0))

    def test_seed_reproduces_random_sequence_and_encounters_vary(self):
        def headings(seed):
            controller = self.controller(seed)
            result = []
            for _ in range(8):
                controller.update(Pose2D(10.4, 5.5, 0))
                result.append(controller.target_heading)
                controller.update(Pose2D(10.4, 5.5, controller.target_heading))
                controller.update(Pose2D(5.5, 5.5, controller.target_heading))
            return result

        sequence = headings(17)
        self.assertEqual(sequence, headings(17))
        self.assertNotEqual(sequence, headings(18))
        self.assertEqual(len(set(sequence)), 8)

    def test_default_constructors_do_not_reuse_a_fixed_seed(self):
        headings = []
        for _ in range(10):
            controller = BorderMotion()
            controller.update(Pose2D(10.4, 5.5, 0))
            headings.append(controller.target_heading)
        self.assertGreater(len(set(headings)), 1)

    def test_configured_world_margin_and_speeds_control_behavior(self):
        controller = self.controller(
            world_size=20.0, margin=2.0, linear_speed=0.5, angular_speed=0.25
        )
        self.assertEqual(controller.update(Pose2D(10, 10, 0)), Velocity(0.5, 0))
        self.assertEqual(controller.update(Pose2D(17.9, 10, 0)), Velocity(0.5, 0))
        velocity = controller.update(Pose2D(18.0, 10, 0))
        self.assertEqual(velocity.linear, 0)
        self.assertAlmostEqual(abs(velocity.angular), 0.25)

    def test_invalid_config_values_are_rejected(self):
        for field in ["world_size", "margin", "linear_speed", "angular_speed", "turn_tolerance"]:
            for value in [0.0, -1.0, math.nan, math.inf, -math.inf]:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        Config(**{field: value})
        for values in [
            {"world_size": 1.0, "margin": 0.5},
            {"world_size": 1.0, "margin": 0.6},
            {"turn_tolerance": math.pi / 4},
            {"turn_tolerance": math.pi},
        ]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    Config(**values)

    def test_nonfinite_pose_stops_without_losing_the_active_turn(self):
        controller = self.controller()
        controller.update(Pose2D(10.4, 5.5, 0))
        target = controller.target_heading
        for field in ["x", "y", "theta"]:
            for value in [math.nan, math.inf, -math.inf]:
                pose = {"x": 10.4, "y": 5.5, "theta": 0.0, field: value}
                with self.subTest(field=field, value=value):
                    self.assertEqual(controller.update(Pose2D(**pose)), Velocity(0, 0))
                    self.assertEqual(controller.target_heading, target)
                    self.assertEqual(controller.turn_count, 1)

    def test_many_step_traversal_stays_inside_world_and_keeps_turning(self):
        starts = [
            (5.54445, 5.54445, 0.0),
            (0.4, 0.4, -3 * math.pi / 4),
            (0.4, 10.6, 3 * math.pi / 4),
            (10.6, 0.4, -math.pi / 4),
            (10.6, 10.6, math.pi / 4),
        ]
        for seed in range(20):
            for start in starts:
                with self.subTest(seed=seed, start=start):
                    controller = self.controller(seed)
                    x, y, theta = start
                    for _ in range(3000):
                        velocity = controller.update(Pose2D(x, y, theta))
                        self.assertTrue(math.isfinite(velocity.linear))
                        self.assertTrue(math.isfinite(velocity.angular))
                        self.assertLessEqual(abs(velocity.linear), 2.0)
                        self.assertLessEqual(abs(velocity.angular), 2.0)
                        if controller.state == "turning":
                            self.assertEqual(velocity.linear, 0.0)
                        x += velocity.linear * math.cos(theta) * 0.05
                        y += velocity.linear * math.sin(theta) * 0.05
                        theta = math.atan2(
                            math.sin(theta + velocity.angular * 0.05),
                            math.cos(theta + velocity.angular * 0.05),
                        )
                        self.assertGreaterEqual(x, 0.0)
                        self.assertLessEqual(x, 11.0889)
                        self.assertGreaterEqual(y, 0.0)
                        self.assertLessEqual(y, 11.0889)
                    self.assertGreater(controller.turn_count, 8)


if __name__ == "__main__":
    unittest.main()
