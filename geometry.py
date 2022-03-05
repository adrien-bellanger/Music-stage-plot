import math
from typing import Final, List, Sequence, Tuple, Union, Optional
import sympy


class Position:
    """A position on the stage."""
    def __init__(self, point: sympy.Point) -> None:
        self.point: Final[sympy.Point] = point

    @staticmethod
    def round_point(point: sympy.Point) -> "Position":
        return Position.from_xy(round(point.x), round(point.y))

    @staticmethod
    def from_xy(x: int, y: int) -> "Position":
        return Position(sympy.Point(x, y))

    @staticmethod
    def from_dict(dct: dict) -> Optional["Position"]:
        x: Optional[float] = dct.get("x")
        y: Optional[float] = dct.get("y")
        if x is None or y is None:
            print(f"A position is not valid {dct}.")
            return None

        return Position.from_xy(x, y)

    def __sub__(self, other: 'Position') -> 'Position':
        return Position.from_xy(self.point.x - other.point.x, self.point.y - other.point.y)

    def __add__(self, other: 'Position') -> 'Position':
        return Position.from_xy(self.point.x + other.point.x, self.point.y + other.point.y)

    def distance(self, other: 'Position') -> float:
        """Distance between 2 position."""
        return self.point.distance(other.point)

    def scale(self, s: float) -> 'Position':
        """Calculate the scaled position."""
        return Position.from_xy(self.point.x * s, self.point.y * s)


class Dimension:
    """Representation of a dimension."""
    def __init__(self, length: int, width: int) -> None:
        self.length: Final[int] = length
        self.width: Final[int] = width

    @staticmethod
    def from_dict(dct: dict) -> Optional["Dimension"]:
        if dct is None or "length" not in dct or "width" not in dct:
            print(f"A dimension is not valid {dct}.")
            return None

        return Dimension(dct["length"], dct["width"])

    def __add__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(self.length + other.length, self.width + other.width)


class Polygon:
    """Representation of a polygon."""
    def __init__(self, points: List[Position]) -> None:
        self.points: Final[List[Position]] = points

    @staticmethod
    def from_dict(dct: dict) -> Optional["Polygon"]:
        list_polygon: Optional[List[dict]] = dct.get("polygon")
        if list_polygon is not None:
            polygon: List[Position] = list()
            for pos in list_polygon:
                new_pos: Optional[Position] = Position.from_dict(pos)

                if new_pos is not None:
                    polygon.append(new_pos)

            return Polygon(polygon)

        return None

    @staticmethod
    def create_rectangle(center: Position, dim: Dimension) -> "Polygon":
        """Create a rectangle with given center and dimension."""
        p1: Final[Position] = Position.from_xy(int(center.point.x - dim.length / 2),
                                               int(center.point.y - dim.width / 2))
        p2: Final[Position] = Position.from_xy(int(center.point.x - dim.length / 2),
                                               int(center.point.y + dim.width / 2))
        p3: Final[Position] = Position.from_xy(int(center.point.x + dim.length / 2),
                                               int(center.point.y + dim.width / 2))
        p4: Final[Position] = Position.from_xy(int(center.point.x + dim.length / 2),
                                               int(center.point.y - dim.width / 2))
        return Polygon([p1, p2, p3, p4])

    def get_as_sequence(self) -> Sequence[Tuple[int, int]]:
        seq: Sequence[Tuple[int, int]] = []
        for pos in self.points:
            seq.append((pos.point.x, pos.point.y))

        return seq


class Area(Union[Polygon]):
    @staticmethod
    def from_dict(dct: dict) -> Optional["Area"]:
        if "polygon" in dct:
            return Polygon.from_dict(dct)

        return None


class Areas(List[Area]):
    @staticmethod
    def from_dict(list_areas: List[dict]) -> "Areas":
        areas: Areas = list()
        for dict_area in list_areas:
            new_area: Optional[Area] = Area.from_dict(dict_area)
            if new_area is not None:
                areas.append(new_area)

        return areas


class ArcAngles:
    """Define begin and end angles of an arc."""
    def __init__(self, start_angle: int, end_angle: int) -> None:
        self.start_angle: Final[int] = start_angle
        self.end_angle: Final[int] = end_angle

    @staticmethod
    def from_dict(dct: Optional[dict]) -> Optional["ArcAngles"]:
        if dct is None:
            return None

        start: Optional[int] = dct.get("start")
        end: Optional[int] = dct.get("end")

        if start is None or end is None:
            print(f"An arc angles is not valid {dct}.")
            return None

        return ArcAngles(start_angle=start, end_angle=end)


class Circle:
    """Representation of a circle."""
    def __init__(self, center: Position, radius: float) -> None:
        self.circle: Final[sympy.Circle] = sympy.Circle(center.point, radius)

    def intersections(self, other: 'Circle', clockwise: bool) -> Optional[Position]:
        """Calculate the intersection point between 2 circles."""
        intersections: Final[List[sympy.Point]] = self.circle.intersection(other.circle)

        if len(intersections) == 0:
            return None
        elif len(intersections) == 1:
            return Position.round_point(intersections[0])
        elif len(intersections) == 2:
            p1: Final[Position] = Position.round_point(intersections[0])
            p2: Final[Position] = Position.round_point(intersections[1])
            angle_p1: float = self.angle(p1)
            angle_p2: float = self.angle(p2)
            are_clockwise: Final[bool] = (angle_p1 < angle_p2) if abs(angle_p2 - angle_p1) < 180 \
                else not (angle_p1 < angle_p2)

            if are_clockwise == clockwise:
                return p2
            else:
                return p1

    def position(self, angle_in_degrees: float) -> Position:
        """Calculate the position of the circle corresponding to the given angle."""
        from math import cos, sin, pi
        angle_in_radians = angle_in_degrees * pi / 180
        x = self.circle.center.x + (self.circle.radius * cos(angle_in_radians))
        y = self.circle.center.y + (self.circle.radius * sin(angle_in_radians))

        return Position.from_xy(x, y)

    def angle(self, pos: Position) -> float:
        """Calculate the angle corresponding to the given position."""
        from math import atan2, degrees
        angle_in_radius = atan2(-(self.circle.center.y - pos.point.y), pos.point.x - self.circle.center.x)
        angle_in_degrees = degrees(angle_in_radius)
        if angle_in_degrees >= 0:
            return angle_in_degrees
        else:
            return 360 + angle_in_degrees

    def perimeter(self, angles: ArcAngles) -> float:
        from math import pi

        circle_perimeter: Final[float] = 2 * pi * float(self.circle.radius)

        percent: Final[float] = (abs(angles.end_angle - angles.start_angle)) / 360

        return circle_perimeter * percent
