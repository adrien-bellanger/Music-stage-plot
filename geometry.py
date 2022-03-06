from typing import Final, List, Sequence, Tuple, Union, Optional
import sympy


class Point:
    @staticmethod
    def round_point(point: sympy.Point) -> sympy.Point:
        return sympy.Point(round(point.x), round(point.y))

    @staticmethod
    def from_dict(dct: dict) -> Optional[sympy.Point]:
        x: Optional[float] = dct.get("x")
        y: Optional[float] = dct.get("y")
        if x is None or y is None:
            print(f"A point is not valid {dct}.")
            return None

        return sympy.Point(x, y)


class Polygon(sympy.Polygon):
    """Representation of a polygon."""
    @staticmethod
    def from_dict(dct: dict) -> Optional["Polygon"]:
        list_polygon: Optional[List[dict]] = dct.get("polygon")
        if list_polygon is not None:
            points: Sequence[sympy.Point] = []
            for pos in list_polygon:
                new_pos: Optional[sympy.Point] = Point.from_dict(pos)

                if new_pos is not None:
                    points.append(new_pos)

            return Polygon(*points)

        return None

    def get_as_sequence(self) -> Sequence[Tuple[int, int]]:
        seq: Sequence[Tuple[int, int]] = []
        for pos in self.vertices:
            seq.append((pos.x, pos.y))

        return seq


class Dimension:
    """Representation of a dimension."""
    @staticmethod
    def from_dict(dct: dict) -> Optional["Polygon"]:
        if dct is None or "x" not in dct or "y" not in dct:
            print(f"A dimension is not valid {dct}.")
            return None

        x_max: Final[int] = dct["x"]
        y_max: Final[int] = dct["y"]
        p0: Final[sympy.Point] = sympy.Point(0, 0)
        p1: Final[sympy.Point] = sympy.Point(0, y_max)
        p2: Final[sympy.Point] = sympy.Point(x_max, y_max)
        p3: Final[sympy.Point] = sympy.Point(x_max, 0)

        return Polygon(p0, p1, p2, p3)


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


class Circle(sympy.Circle):
    """Representation of a circle."""
    def sort_points(self, points: List[sympy.Point], clockwise: bool) -> List[sympy.Point]:
        return sorted(points, key=self.angle, reverse=clockwise)
    
    def get_first_intersection(self, intersections: List[sympy.Point], clockwise: bool) -> Optional[sympy.Point]:
        """Get the first intersection from the given points in clockwise direction."""
        if len(intersections) == 0:
            return None
        elif len(intersections) == 1:
            return Point.round_point(intersections[0])

        sorted_intersections: Final[List[sympy.Point]] = self.sort_points(intersections, clockwise)
        return Point.round_point(sorted_intersections[0])

    def point(self, angle_in_degrees: float) -> sympy.Point:
        """Calculate the point of the circle corresponding to the given angle."""
        from math import cos, sin, pi
        angle_in_radians = angle_in_degrees * pi / 180
        x = self.center.x + (self.radius * cos(angle_in_radians))
        y = self.center.y + (self.radius * sin(angle_in_radians))

        return sympy.Point(round(x), round(y))

    def angle(self, pos: sympy.Point) -> float:
        """Calculate the angle corresponding to the given point."""
        from math import atan2, degrees
        angle_in_radius = atan2(-(self.center.y - pos.y), pos.x - self.center.x)
        angle_in_degrees = degrees(angle_in_radius)
        if angle_in_degrees > 0:
            return angle_in_degrees
        else:
            return 360 + angle_in_degrees

    def perimeter(self, angles: ArcAngles) -> float:
        percent: Final[float] = (abs(angles.end_angle - angles.start_angle)) / 360

        return self.circumference * percent
