"""ROS-independent forward / turn / escape logic for the turtlesim exercise.

All distances use turtlesim world units; headings are radians. Call ``update``
at a steady rate with fresh pose feedback. This class does not own a clock:
the ROS adapter is responsible for stopping when pose feedback is stale.
"""

from dataclasses import dataclass
import math
import random
from typing import Optional


@dataclass(frozen=True)
class Pose2D:
    """Current turtle position and heading in the world frame."""

    x: float
    y: float
    theta: float


@dataclass(frozen=True)
class Velocity:
    """Forward speed and signed angular speed for a Twist command."""

    linear: float
    angular: float


@dataclass(frozen=True)
class Config:
    """Positive motion limits and the distance at which a border triggers."""

    world_size: float = 11.0889
    margin: float = 0.8
    linear_speed: float = 2.0
    angular_speed: float = 2.0
    turn_tolerance: float = 0.04

    def __post_init__(self) -> None:
        for name in (
            "world_size", "margin", "linear_speed", "angular_speed", "turn_tolerance"
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and greater than zero")
        if self.margin >= self.world_size / 2:
            raise ValueError("margin must be less than half of world_size")
        if self.turn_tolerance >= math.pi / 4:
            raise ValueError("turn_tolerance must be less than pi/4 radians")


class BorderMotion:
    """Choose one random inward heading at each outward border encounter.

    ``state`` is ``forward``, ``turning``, or ``escaping``. ``target_heading``
    is initially None and subsequently retains the most recent chosen heading.
    ``turn_count`` counts selections, not update calls. Inject ``random.Random``
    with a seed when repeatable motion is useful.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.config = config if config is not None else Config()
        self._rng = rng if rng is not None else random.Random()
        self.state = "forward"
        self.target_heading: Optional[float] = None
        self.turn_count = 0

        # A separate release boundary avoids repeatedly triggering at the edge.
        half_width = self.config.world_size / 2
        hysteresis = min(0.2, (half_width - self.config.margin) / 2)
        self._clearance = self.config.margin + hysteresis

    def update(self, pose: Pose2D) -> Velocity:
        """Return a bounded command, stopping on nonfinite pose feedback."""
        if not all(math.isfinite(value) for value in (pose.x, pose.y, pose.theta)):
            return Velocity(0.0, 0.0)

        if self.state == "turning":
            error = self._heading_error(pose.theta)
            if abs(error) > self.config.turn_tolerance:
                return self._rotation(error)
            self.state = "escaping"

        # Check even during escape: a teleport or another velocity publisher
        # must not make the controller drive outward through a nearby wall.
        if self._heading_toward_border(pose):
            self._begin_turn(pose)
            return self._rotation(self._heading_error(pose.theta))

        if self.state == "escaping" and self._clear_of_borders(pose):
            self.state = "forward"
        return Velocity(self.config.linear_speed, 0.0)

    def _heading_toward_border(self, pose: Pose2D) -> bool:
        dx = math.cos(pose.theta)
        dy = math.sin(pose.theta)
        lower = self.config.margin
        upper = self.config.world_size - lower
        # Ignore floating-point residue at exactly tangential headings.
        epsilon = 1e-12
        return (
            (pose.x <= lower and dx < -epsilon)
            or (pose.x >= upper and dx > epsilon)
            or (pose.y <= lower and dy < -epsilon)
            or (pose.y >= upper and dy > epsilon)
        )

    def _begin_turn(self, pose: Pose2D) -> None:
        # A random point in the central region gives a new inward direction
        # at every side and at corners, without unbounded rejection sampling.
        center = self.config.world_size / 2
        radius = (center - self._clearance) / 2
        target_x = self._rng.uniform(center - radius, center + radius)
        target_y = self._rng.uniform(center - radius, center + radius)
        self.target_heading = math.atan2(target_y - pose.y, target_x - pose.x)
        self.turn_count += 1
        self.state = "turning"

    def _heading_error(self, theta: float) -> float:
        assert self.target_heading is not None
        difference = self.target_heading - theta
        return math.atan2(math.sin(difference), math.cos(difference))

    def _rotation(self, error: float) -> Velocity:
        # Slow near the target so discrete pose updates do not cause repeated
        # overshoot. The configured angular speed remains a hard upper bound.
        angular = max(
            -self.config.angular_speed,
            min(self.config.angular_speed, 4.0 * error),
        )
        return Velocity(0.0, angular)

    def _clear_of_borders(self, pose: Pose2D) -> bool:
        upper = self.config.world_size - self._clearance
        return (
            self._clearance <= pose.x <= upper
            and self._clearance <= pose.y <= upper
        )
