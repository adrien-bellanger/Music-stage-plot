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


class Polygon:
    """Representation of a polygon."""
    def __init__(self, *args) -> None:
        self.polygon: Final[sympy.Polygon] = sympy.Polygon(*args)

    @staticmethod
    def from_dict(dct: dict) -> Optional["Polygon"]:
        list_polygon: Optional[List[dict]] = dct.get("polygon")
        if list_polygon is not None:
            points: List[sympy.Point] = []
            for pos in list_polygon:
                new_pos: Optional[sympy.Point] = Point.from_dict(pos)

                if new_pos is not None:
                    points.append(new_pos)

            return Polygon(*points)

        return None

    def get_points(self) -> List[sympy.Point]:
        if isinstance(self.polygon, sympy.Segment):
            return self.polygon.points
        else:
            return self.polygon.vertices

    def get_as_sequence(self) -> Sequence[Tuple[int, int]]:
        seq: List[Tuple[int, int]] = []
        for pos in self.get_points():
            seq.append((pos.x, pos.y))

        return seq

    def enlarge(self, extra: int) -> "Polygon":
        new_vertices: List[sympy.Point] = []

        for point in self.get_points():
            extended_points: List[sympy.Point] = [sympy.Point(point.x + extra, point.y + extra),
                                                  sympy.Point(point.x + extra, point.y - extra),
                                                  sympy.Point(point.x - extra, point.y + extra),
                                                  sympy.Point(point.x - extra, point.y - extra)]
            sorted_points = sorted(extended_points, key=self.polygon.distance, reverse=True)
            new_vertices.append(sorted_points[0])
            # TODO understand why this code deos not work
            # for extended_point in extended_points:
            #     if self.polygon.distance(extended_point) >= extra:
            #         new_vertices.append(extended_point)

        return Polygon(*new_vertices)


class ArcAngles:
    """Define begin and end angles of an arc."""
    def __init__(self, start_angle: float, end_angle: float) -> None:
        self.start_angle: Final[float] = start_angle
        self.end_angle: Final[float] = end_angle

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

    @staticmethod
    def from_list(list_angles: Optional[List[Optional[dict]]]) -> Optional[List[Optional["ArcAngles"]]]:
        if list_angles is None:
            return None

        list_arc_angles: List[Optional[ArcAngles]] = []
        for dct in list_angles:
            list_arc_angles.append(ArcAngles.from_dict(dct))
        return list_arc_angles

    @staticmethod
    def reduce_to(sorted_arcs: List["ArcAngles"], sorted_allowed_arcs: List["ArcAngles"]) -> List["ArcAngles"]:
        if len(sorted_allowed_arcs) == 0:
            return sorted_arcs

        new_arcs: List["ArcAngles"] = []

        for arc in sorted_arcs:
            for allowed_arc in sorted_allowed_arcs:
                if allowed_arc.start_angle >= arc.end_angle:
                    break
                elif allowed_arc.end_angle <= arc.start_angle:
                    continue

                new_arcs.append(ArcAngles(max(arc.start_angle, allowed_arc.start_angle),
                                          min(arc.end_angle, allowed_arc.end_angle)))

        return new_arcs

    @staticmethod
    def exclude(sorted_arcs: List["ArcAngles"], sorted_excluded_arcs: List["ArcAngles"]) -> List["ArcAngles"]:
        if len(sorted_excluded_arcs) == 0:
            return sorted_arcs

        current_arcs: List["ArcAngles"] = sorted_arcs

        for excluded_arc in sorted_excluded_arcs:
            new_arcs: List["ArcAngles"] = []
            for arc in current_arcs:
                if excluded_arc.start_angle >= arc.end_angle:
                    new_arcs.append(arc)
                elif excluded_arc.end_angle <= arc.start_angle:
                    new_arcs.append(arc)
                elif excluded_arc.start_angle <= arc.start_angle:
                    new_arcs.append(ArcAngles(excluded_arc.end_angle, arc.end_angle))
                elif excluded_arc.end_angle >= arc.end_angle:
                    new_arcs.append(ArcAngles(arc.start_angle, excluded_arc.start_angle))
                else:
                    new_arcs.append(ArcAngles(arc.start_angle, excluded_arc.start_angle))
                    new_arcs.append(ArcAngles(excluded_arc.end_angle, arc.end_angle))
            current_arcs = new_arcs

        return current_arcs


class Arc:
    """Representation of an arc, for example a step on the stage."""
    def __init__(self, circle: sympy.Circle, angles: ArcAngles) -> None:
        self.circle: Final[sympy.Circle] = circle
        self.angles: Final[ArcAngles] = angles

    @staticmethod
    def from_dict(dct: dict, stage_center: sympy.Point) -> Optional["Arc"]:
        arc: Optional[dict] = dct.get("arc")
        if arc is None:
            return None

        radius: Final[Optional[int]] = arc.get("radius")
        if radius is None:
            print(f"An arc has to contain a radius ({dct})")
            return None

        angles: Final[Optional[ArcAngles]] = ArcAngles.from_dict(arc.get("angles"))
        if angles is None:
            print(f"An arc has to contain angles ({dct})")
            return None

        dct_center: Optional[dict] = arc.get("center")
        center_from_dict: Final[Optional[Point]] = Point.from_dict(dct_center) if dct_center is not None else None
        center: Final[Point] = center_from_dict if center_from_dict is not None else stage_center

        return Arc(sympy.Circle(center, radius), angles)

    def get_bounds_as_sequence(self) -> Sequence[Tuple[int, int]]:
        seq: List[Tuple[int, int]] = []
        print(f"bounds = {self.circle.bounds}")
        for pos in self.circle.bounds:
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


class Areas(List[Union[Polygon, Arc]]):
    @staticmethod
    def from_dict(list_areas: List[dict], stage_center: sympy.Point) -> "Areas":
        areas: List[Union[Polygon, Arc]] = list()
        for dict_area in list_areas:
            new_area: Optional[Union[Polygon, Arc]] = None
            if "polygon" in dict_area:
                new_area = Polygon.from_dict(dict_area)
            elif "arc" in dict_area:
                new_area = Arc.from_dict(dict_area, stage_center)

            if new_area is not None:
                areas.append(new_area)

        return Areas(areas)

    def enlarge(self, extra: int) -> "Areas":
        new_areas: List[Union[Polygon, Arc]] = []
        for area in self:
            if isinstance(area, Polygon):
                new_areas.append(area.enlarge(extra))

        return Areas(new_areas)


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

    def intersection_arc_angles(self, polygon: Polygon) -> List[ArcAngles]:
        angles: List[ArcAngles] = []
        intersections_with_stage = self.sort_points(self.intersection(polygon.polygon), False)
        number_of_intersection: Final[int] = len(intersections_with_stage)
        if number_of_intersection == 0:
            return angles

        i: int = 1
        while i < number_of_intersection:
            current_angle: float = self.angle(intersections_with_stage[i])
            is_last: bool = i == number_of_intersection - 1
            other_angle: float = self.angle(intersections_with_stage[i-1])  # start with i = 1
            arc_middle: sympy.Point = self.point((other_angle + current_angle) / 2)
            if polygon.polygon.encloses_point(arc_middle):
                angles.append(ArcAngles(other_angle, current_angle))
                i = i + 2
            else:
                i = i + 1

            if is_last:
                other_angle = 360
                arc_middle = self.point((other_angle + current_angle) / 2)
                if polygon.polygon.encloses_point(arc_middle):
                    angles.append(ArcAngles(current_angle, 360))
                break

        return angles

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
        if angle_in_degrees > 90:
            return angle_in_degrees
        else:
            return 360 + angle_in_degrees

    def perimeter(self, angles: ArcAngles) -> float:
        percent: Final[float] = (abs(angles.end_angle - angles.start_angle)) / 360

        return self.circumference * percent
