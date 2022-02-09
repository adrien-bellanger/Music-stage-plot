from typing import Final, List, NoReturn, Sequence, Tuple, Union
import math


class Position:
    """A position on the stage."""
    def __init__(self, x: float, y: float) -> None:
        self.x: Final[float] = x
        self.y: Final[float] = y

    def __sub__(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y)

    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

    def distance(self, other: 'Position') -> float:
        """Distance between 2 position."""
        return math.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))

    def normal(self) -> 'Position':
        length: float = math.sqrt(pow(self.x, 2) + pow(self.y, 2))
        return Position(self.x / length, self.y / length)

    def scale(self, s: float) -> 'Position':
        """Calculate the scaled position."""
        return Position(self.x * s, self.y * s)


class Dimension:
    """Representation of a dimension."""
    def __init__(self, length: int, width: int) -> None:
        self.length: Final[int] = length
        self.width: Final[int] = width

    def __add__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(self.length + other.length, self.width + other.width)


class ArcAngles:
    """Define begin and end angles of an arc."""
    def __init__(self, start_angle: int, end_angle: int) -> None:
        self.start_angle: Final[int] = start_angle
        self.end_angle: Final[int] = end_angle


class Circle:
    """Representation of a circle."""
    def __init__(self, center: Position, radius: float) -> None:
        self.center: Final[Position] = center
        self.radius: Final[float] = radius

    def intersections(self, other: 'Circle', clockwise: bool) -> Position:
        """Calculate the intersection point between 2 circles."""
        dist: Final[float] = self.center.distance(other.center)
        a: Final[float] = (pow(self.radius, 2) - pow(other.radius, 2) +
                           pow(dist, 2)) / (2 * dist)
        h: Final[float] = math.sqrt(pow(self.radius, 2) - pow(a, 2))
        p2: Final[Position] = (other.center - self.center).scale(a / dist) + self.center
        if clockwise:
            return Position(p2.x - h * (other.center.y - self.center.y) / dist,
                            p2.y + h * (other.center.x - self.center.x) / dist)

        return Position(p2.x + h * (other.center.y - self.center.y) / dist,
                        p2.y - h * (other.center.x - self.center.x) / dist)

    def position(self, angle_in_degrees: float) -> Position:
        """Calculate the position of the circle corresponding to the given angle."""
        from math import cos, sin, pi
        angle_in_radians = angle_in_degrees * pi / 180
        x = self.center.x + (self.radius * cos(angle_in_radians))
        y = self.center.y + (self.radius * sin(angle_in_radians))

        return Position(x, y)

    def perimeter(self, angles: ArcAngles) -> float:
        from math import pi

        circle_perimeter: Final[float] = 2 * pi * float(self.radius)

        percent: Final[float] = (abs(angles.end_angle - angles.start_angle)) / 360

        return circle_perimeter * percent


def create_rectangle(center: Position,
                     dim: Dimension) -> Sequence[Union[int, Tuple[int, int]]]:
    """Create a rectangle with given center and dimension."""
    return (int(center.x - dim.length / 2), int(center.y - dim.width / 2),
            int(center.x + dim.length / 2), int(center.y + dim.width / 2))
