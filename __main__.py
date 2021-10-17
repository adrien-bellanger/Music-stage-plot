
from PIL import Image, ImageDraw, ImageFont

from typing import Final, List, NoReturn, Sequence, Tuple, Union

from math import sqrt, pow

n_seats = 0


class Position:
    def __init__(self, x: int, y: int) -> NoReturn:
        self.x: Final[int] = x
        self.y: Final[int] = y

    def sub(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y)
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)
        
    def distance(self, other: 'Position') -> 'Position':
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))
    
    def normal(self) -> 'Position':
        length: float = sqrt(pow(self.x, 2) + pow(self.y, 2))
        return Position(self.x/length, self.y/length)

    def scale(self, s: float) -> 'Position':
        return Position(self.x*s, self.y*s)


class Dimension:
    def __init__(self, length: int, width: int) -> NoReturn:
        self.length: Final[int] = length
        self.width: Final[int] = width

    def __add__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(self.length + other.length, self.width + other.width)


def create_xy(pos: Position,
              dim: Dimension) -> Sequence[Union[float, Tuple[float, float]]]:
    return (pos.x - dim.length/2, pos.y - dim.width/2,
            pos.x + dim.length/2, pos.y + dim.width/2)


def point_on_circle(center: Position, radius: int, angle_in_degrees: float):
    from math import cos, sin, pi
    angle_in_radians = angle_in_degrees * pi / 180
    x = center.x + (radius * cos(angle_in_radians))
    y = center.y + (radius * sin(angle_in_radians))

    return Position(x, y)


class Circle:
    def __init__(self, center: Position, radius: int) -> NoReturn:
        self.center: Final[Position] = center
        self.radius: Final[int] = radius

    def Intersections(self, other: 'Circle', clockwise: bool) -> Position:
        dist: Final[float] = self.center.distance(other.center)
        a: Final[float] = (pow(self.radius, 2) - pow(other.radius, 2) +
                           pow(dist, 2)) / (2 * dist)
        h: Final[float] = sqrt(pow(self.radius, 2) - pow(a, 2))
        p2: Final[Position] = other.center.sub(self.center).scale(a/dist) +\
            self.center
        if clockwise:
            return Position(p2.x - h*(other.center.y - self.center.y) / dist,
                            p2.y + h*(other.center.x - self.center.x) / dist)
        
        return Position(p2.x + h*(other.center.y - self.center.y)/dist,
                        p2.y - h*(other.center.x - self.center.x)/dist)


class RowAngles:
    def __init__(self, start_angle: int, end_angle: int) -> NoReturn:
        self.start_angle: Final[int] = start_angle
        self.end_angle: Final[int] = end_angle


class Rows:
    def __init__(self, rows_with_angles: List[RowAngles],
                 n_distancing_delta_first_row: int,
                 n_distancing_row: int) -> NoReturn:
        self.rows_with_angles: Final[List[RowAngles]] = rows_with_angles
        self.n_distancing_delta_first_row: Final[int] = \
            n_distancing_delta_first_row
        self.n_distancing_row: Final[int] = n_distancing_row

    def draw(self, draw: ImageDraw, center:
             Position, distancing: int) -> NoReturn:
        start_angle: Final[int] = 190
        end_angle: Final[int] = 350

        radius: int = self.n_distancing_delta_first_row
        for row_with_angles in self.rows_with_angles:
            radius = radius + max(distancing, self.n_distancing_row)
            if row_with_angles is None:
                create_row(draw, center, radius, start_angle, end_angle,
                           distancing)
            else:
                for angles in row_with_angles:
                    create_row(draw, center, radius, angles.start_angle,
                               angles.end_angle, distancing)


class Hall:
    def __init__(self, name: str, stage: Dimension, rows: Rows,
                 n_percussion_deep: int,
                 hidden_areas: Sequence[Union[float, Tuple[float, float]]]) -> NoReturn:
        self.name: Final[str] = name
        self.stage: Final[Dimension] = stage
        self.rows: Final[Rows] = rows
        self.n_percussion_deep: Final[int] = n_percussion_deep
        self.hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] \
            = hidden_areas

    def draw(self, distancing: int) -> NoReturn:
        global n_seats
        n_seats = 0

        font = ImageFont.truetype("arial.ttf", 20)

        podest: Final[Dimension] = Dimension(100, 100)

        center: Final[Position] = Position(self.stage.length / 2,
                                           self.stage.width)
        podest_center: Final[Position] = Position(center.x,
                                                  center.y - podest.width/2)

        im = Image.new('RGB', (self.stage.length, self.stage.width),
                       (255, 255, 255))
        draw = ImageDraw.Draw(im)

        podest_xy = create_xy(podest_center, podest)
        draw.rectangle(podest_xy, fill=None, outline=(0, 0, 0))

        # Draw "Percussion line"
        draw.line(((0, self.n_percussion_deep),
                   (self.stage.length, self.n_percussion_deep)),
                  fill=(0, 0, 0), width=2)

        for hidden_area in self.hidden_areas:
            draw.polygon(hidden_area, fill=(200, 200, 200))

        self.rows.draw(draw, center, distancing)

        draw.text((10, 10), "Number of seats " +
                  str(n_seats) + "\n" +
                  "distancing: " + str(distancing) + "\n" +
                  "Percussion deep: " + str(self.n_percussion_deep) + " cm\n" +
                  "scale 1m", fill=(0, 0, 0), font=font)
        n_top_line: Final[int] = 100
        draw.line(((10, n_top_line), (110, n_top_line)), fill=(0, 0, 0),
                  width=3)

        im.save('export/' + self.name + '_Abstand_' + str(distancing) +
                '_first_row_' + str(self.rows.n_distancing_delta_first_row) +
                '.jpg', quality=95)


def draw_seat(draw: ImageDraw, pos: Position) -> NoReturn:
    global n_seats
    n_seats = n_seats + 1
    draw.ellipse(create_xy(pos, Dimension(50, 50)), fill=(255, 0, 0))
    return


def create_row(draw: ImageDraw, center: Position, radius: int,
               start_angle: int, end_angle: int, distancing: int) -> NoReturn:
    draw.arc(create_xy(center, Dimension(radius*2, radius*2)),
             start=start_angle, end=end_angle, fill=(255, 255, 0))

    row_center: Final[Position] = point_on_circle(center, radius,
                                                  (start_angle + end_angle)/2)


    current_left: Position = point_on_circle(center, radius, start_angle)
    current_right: Position = point_on_circle(center, radius, end_angle)

    if current_left.distance(current_right) < distancing:
        draw_seat(draw, row_center)
        return
    
    while True:
        draw_seat(draw, current_left)
        draw_seat(draw, current_right)
        if current_left.distance(row_center) < distancing:
            return

        current_left = Circle(center, radius).Intersections(
            Circle(current_left, distancing), True)
        current_right = Circle(center, radius).Intersections(
            Circle(current_right, distancing), False)

        if current_left.distance(current_right) < distancing:
            draw_seat(draw, row_center)
            return

def create_polygon_from_line(start_x: int, start_y: int, end_x:int, end_y:int, half_width_x: int, half_width_y: int) -> Union[float, Tuple[float, float]]:
    return (start_x - half_width_x, start_y - half_width_y), (end_x - half_width_x, end_y - half_width_y), (end_x + half_width_x, end_y + half_width_y), (start_x + half_width_x, start_y + half_width_y)

elsterwerda_stage: Final[Dimension] = Dimension(1330, 600)
elsterwerda_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
    ((0, 0), (0, 600), (340, 600), (340, 0)),
    ((1330, 0), (1330, 600), (990, 600), (990, 0))
    ]

elsterwerda_600: Final[Hall] = Hall("Elsterwerda_600", elsterwerda_stage + Dimension(0, 600),
                                Rows([None, None, None, 
                                [RowAngles(222, 222), RowAngles(248, 292), RowAngles(318, 318)],
                                [RowAngles(252, 252), RowAngles(288, 288)]
                                ], 48, 200), 210,
                                elsterwerda_hidden_areas)
elsterwerda_600.draw(200)

elsterwerda_650: Final[Hall] = Hall("Elsterwerda_650", elsterwerda_stage + Dimension(0, 650),
                                Rows([None, None, None, 
                                [RowAngles(218, 232), RowAngles(248, 292), RowAngles(308, 322)],
                                [RowAngles(252, 288)]
                                ], 48, 200), 210,
                                elsterwerda_hidden_areas)
elsterwerda_650.draw(200)

plenarsaal: Final[Hall] = Hall("Plenarsaal", Dimension(1460, 740),
                               Rows([None, [RowAngles(190, 190), RowAngles(215, 305), RowAngles(325, 350)], 
                               [RowAngles(190, 300), RowAngles(318, 350)], 
                               [RowAngles(190, 315), RowAngles(327, 327), RowAngles(337, 350)]], 100, 150), 0,
                               [((0, 0), (0, 100), (100, 100), (100, 0)), 
                               ((1460, 0), (1260, 0), (1260, 200), (1460, 200)),
                               create_polygon_from_line(0, 460, 260, 460, 0, 2),
                               create_polygon_from_line(0, 605, 260, 605, 0, 2),
                               create_polygon_from_line(260, 460, 260, 605, 2, 0),
                               create_polygon_from_line(260, 540, 675, 505, 0, 2),
                               create_polygon_from_line(675, 505, 1090, 405, 0, 2),
                               create_polygon_from_line(1150, 325, 1460, 325, 0, 2),
                               create_polygon_from_line(1150, 430, 1460, 480, 0, 2)])
plenarsaal.draw(150)

plenarsaal.draw(150)
riesa: Final[Hall] = Hall("Riesa", Dimension(1580, 960),
                          Rows([None, None, None, [RowAngles(190, 205), RowAngles(226, 314), RowAngles(335, 350)], [RowAngles(203, 203), RowAngles(337, 337)]], 90, 150), 235,
                          [((0, 0), (0, 600), (290, 600), (290, 200), (540, 0),
                            (1040, 0), (1290, 200), (1290, 600), (1580, 600),
                            (1580, 0), (0, 0))])
riesa.draw(150)


glauchau: Final[Hall] = Hall("Glauchau", Dimension(920, 1150), Rows([None, None, [RowAngles(210, 330)], [RowAngles(230, 310)], [RowAngles(238.5, 301.5)]], 70, 150), 300, [((0, 480), (460, 0), (0,0)), ((460, 0), (920, 0), (920, 480))])
glauchau.draw(150)