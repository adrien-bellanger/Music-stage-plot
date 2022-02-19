from typing import Final, List, Sequence, Tuple, Union, Optional
import math


class Position:
    """A position on the stage."""
    def __init__(self, x: float, y: float) -> None:
        self.x: Final[float] = x
        self.y: Final[float] = y

    @staticmethod
    def from_dict(dct: dict) -> Optional["Position"]:
        x: Optional[float] = dct.get("x")
        y: Optional[float] = dct.get("y")
        if x is None or y is None:
            print(f"A position is not valid {dct}.")
            return None

        return Position(x=x, y=y)

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
        p1: Final[Position] = Position(int(center.x - dim.length / 2),
                                       int(center.y - dim.width / 2))
        p2: Final[Position] = Position(int(center.x - dim.length / 2),
                                       int(center.y + dim.width / 2))
        p3: Final[Position] = Position(int(center.x + dim.length / 2),
                                       int(center.y + dim.width / 2))
        p4: Final[Position] = Position(int(center.x + dim.length / 2),
                                       int(center.y - dim.width / 2))
        return Polygon([p1, p2, p3, p4])

    def get_as_sequence(self) -> Sequence[Tuple[int, int]]:
        seq: Sequence[Tuple[int, int]] = []
        for pos in self.points:
            seq.append((pos.x, pos.y))

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
