import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from typing import Final, List, NoReturn, Sequence, Tuple, Union

from math import sqrt, pow

n_seats = 0


class Position:
    def __init__(self, x: float, y: float) -> NoReturn:
        self.x: Final[float] = x
        self.y: Final[float] = y

    def sub(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y)
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)
        
    def distance(self, other: 'Position') -> float:
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
              dim: Dimension) -> Sequence[Union[int, Tuple[int, int]]]:
    return (int(pos.x - dim.length/2), int(pos.y - dim.width/2),
            int(pos.x + dim.length/2), int(pos.y + dim.width/2))


class RowAngles:
    def __init__(self, start_angle: int, end_angle: int) -> NoReturn:
        self.start_angle: Final[int] = start_angle
        self.end_angle: Final[int] = end_angle


DEFAULT_ANGLES: Final[RowAngles] = RowAngles(190, 350)


class Circle:
    def __init__(self, center: Position, radius: float) -> NoReturn:
        self.center: Final[Position] = center
        self.radius: Final[float] = radius

    def intersections(self, other: 'Circle', clockwise: bool) -> Position:
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

    def position(self, angle_in_degrees: float) -> Position:
        from math import cos, sin, pi
        angle_in_radians = angle_in_degrees * pi / 180
        x = self.center.x + (self.radius * cos(angle_in_radians))
        y = self.center.y + (self.radius * sin(angle_in_radians))

        return Position(x, y)

    def perimeter(self, angles: RowAngles) -> float:
        from math import pi

        circle_perimeter: Final[float] = 2 * pi * float(self.radius)

        percent: Final[float] = (abs(angles.end_angle - angles.start_angle)) / 360

        return circle_perimeter * percent


class Instrument:
    def __init__(self, path: Path) -> NoReturn:
        self.path: Final[Path] = path

    def draw(self, im: Image, center: Position) -> NoReturn:
        global n_seats
        n_seats = n_seats + 1

        if self.path is None:
            ImageDraw.Draw(im).ellipse(create_xy(center, Dimension(50, 50)), outline=(0, 0, 0), width=2)
            return

        instrument_image_original = Image.open(self.path)
        n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
        instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
        im.alpha_composite(instrument_image, (max(0, int(center.x - instrument_image.size[0] /2)),
                                              max(0, int(center.y - instrument_image.size[1] / 2))))


INSTRUMENT_DEFAULT: Final[Instrument] = Instrument(None)
INSTRUMENT_PATH: Final[str] = "Instruments/"
INSTRUMENT_BASS_CLARINET: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "BKLARINETTE.png"))
INSTRUMENT_BASSOON: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + 'FAGOTTE.png'))
INSTRUMENT_CLARINET: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "KLARINETTE.png"))
INSTRUMENT_EUPHONIUM: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "EUPHONIUM.png"))
INSTRUMENT_FLUTE: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "FLOETE.png"))
INSTRUMENT_HORN: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "HORN.png"))
INSTRUMENT_NOTHING: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + 'NO_INSTRUMENT.png'))
INSTRUMENT_OBOE: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + 'OBOE.png'))
INSTRUMENT_PICOLO: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "PICCOLO.png"))
INSTRUMENT_TROMBONE: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "POSAUNE.png"))
INSTRUMENT_SAX: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "SAX.png"))
INSTRUMENT_TRuMPET: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "TROMPETE.png"))
INSTRUMENT_TUBA: Final[Instrument] = Instrument(Path(INSTRUMENT_PATH + "TUBA.png"))


class Row:
    def __init__(self, angles: RowAngles, instruments: List[Instrument]) -> NoReturn:
        self.angles: Final[RowAngles] = DEFAULT_ANGLES if angles is None else angles
        self.instruments: Final[List[Instrument]] = instruments

    def get_instruments_to_use(self, perimeter: float, distancing: int) -> List[Instrument]:
        n_max_number_of_instruments: Final[int] = math.floor(float(perimeter) / distancing) + 1
        if self.instruments is None:
            return [INSTRUMENT_DEFAULT] * n_max_number_of_instruments

        if len(self.instruments) > n_max_number_of_instruments:
            print("A row has to many instruments for its length")
            return [INSTRUMENT_DEFAULT] * n_max_number_of_instruments

        return self.instruments

    def draw(self, im: Image,
             center: Position, radius: int, min_distancing: int) -> NoReturn:

        # ImageDraw.Draw(im).arc(create_xy(center, Dimension(radius*2, radius*2)),
        #                        start=self.angles.start_angle, end=self.angles.end_angle, fill=(255, 255, 0))

        circle: Final[Circle] = Circle(center, radius)

        perimeter: Final[float] = circle.perimeter(self.angles)

        instruments: Final[List[Instrument]] = self.get_instruments_to_use(perimeter, min_distancing)

        current_position: Position = circle.position(self.angles.start_angle) if len(instruments) > 1 \
            else circle.position((self.angles.start_angle + self.angles.end_angle) / 2)

        second_position: Final[Position] = circle.position(self.angles.start_angle +
                                                           (abs(self.angles.end_angle - self.angles.start_angle) /
                                                            (len(instruments) - 1))) if len(instruments) > 1 \
            else current_position
        distancing: Final[float] = current_position.distance(second_position)

        for instrument in instruments:
            instrument.draw(im, current_position)
            if distancing > 0:
                current_position = circle.intersections(
                    Circle(current_position, distancing), True)


DEFAULT_ROW: Final[Row] = Row(None, None)


class Rows:
    def __init__(self, rows: List[Row],
                 n_distancing_delta_first_row: int,
                 n_distancing_row: int) -> NoReturn:
        self.rows_with_angles: Final[List[Row]] = rows
        self.n_distancing_delta_first_row: Final[int] = \
            n_distancing_delta_first_row
        self.n_distancing_row: Final[int] = n_distancing_row

    def draw(self, im: Image, center:
             Position, distancing: int) -> NoReturn:
        radius: int = self.n_distancing_delta_first_row
        for row_with_angles in self.rows_with_angles:
            radius = radius + max(distancing, self.n_distancing_row)
            if row_with_angles is None:
                DEFAULT_ROW.draw(im, center, radius, distancing)
            else:
                for row_pats in row_with_angles:
                    row_pats.draw(im, center, radius, distancing)


class Hall:
    def __init__(self, name: str, stage: Dimension, rows: Rows,
                 percussion_area: Union[Tuple[float, float]],
                 hidden_areas: Sequence[Union[Tuple[float, float]]],
                 text_top_left: Position) -> NoReturn:
        self.name: Final[str] = name
        self.stage: Final[Dimension] = stage
        self.rows: Final[Rows] = rows
        self.percussion_area: Final[Union[Tuple[float, float]]] = percussion_area
        self.hidden_areas: Final[Sequence[Union[Tuple[float, float]]]] \
            = hidden_areas
        self.text_top_left: Final[Position] = text_top_left

    def draw_percussion_area(self, image: Image) -> NoReturn:
        ImageDraw.Draw(image).polygon(self.percussion_area, outline="black", fill=(240, 240, 240))
        n_min_x: float = self.stage.length
        n_max_x: float = 0
        n_min_y: float = self.stage.width
        n_max_y: float = 0
        for (x,y) in self.percussion_area:
            if x < n_min_x:
                n_min_x = x
            if x > n_max_x:
                n_max_x = x
            if y < n_min_y:
                n_min_y = y
            if y > n_max_y:
                n_max_y = y

        center: Final[Position] = Position((n_min_x + n_max_x)/2, (n_min_y + n_max_y)/2)
        instrument_image_original = Image.open(Path(INSTRUMENT_PATH + 'PAUKE.png'))
        n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
        instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
        image.alpha_composite(instrument_image, (max(0, int(center.x - instrument_image.size[0] / 2)),
                                              max(0, int(center.y - instrument_image.size[1] / 2))))

    def draw(self, distancing: int) -> NoReturn:
        global n_seats
        n_seats = 0

        font = ImageFont.truetype("arial.ttf", 20)

        podest: Final[Dimension] = Dimension(100, 100)

        center: Final[Position] = Position(self.stage.length / 2,
                                           self.stage.width)
        podest_center: Final[Position] = Position(center.x,
                                                  center.y - podest.width/2)

        im = Image.new("RGBA", (self.stage.length, self.stage.width),
                       (255, 255, 255))
        draw = ImageDraw.Draw(im)

        podest_xy = create_xy(podest_center, podest)
        draw.rectangle(podest_xy, fill=None, outline=(0, 0, 0))

        # Draw "Percussion line"
        self.draw_percussion_area(im)

        for hidden_area in self.hidden_areas:
            draw.polygon(hidden_area, fill=(160, 160, 160))

        self.rows.draw(im, center, distancing)

        draw.text((self.text_top_left.x, self.text_top_left.y), str(self.name) + "\n" +
                  "Number of seats " + str(n_seats) + "\n" +
                  "distancing: " + str(distancing) + " cm\n" +
                  "scale 1m", fill=(0, 0, 0), font=font)
        n_top_line: Final[int] = 95
        draw.line(((self.text_top_left.x, self.text_top_left.y + n_top_line),
                   (self.text_top_left.x + 100, self.text_top_left.y + n_top_line)), fill=(0, 0, 0),
                  width=3)

        im.save('export/' + self.name + '_distancing_' + str(distancing) +'.png')


if False:
    im = Image.new("RGBA", (100, 100))
    im.save(INSTRUMENT_PATH + 'NO_INSTRUMENT.png')

def create_polygon_from_line(start_x: int, start_y: int, end_x:int, end_y:int, half_width_x: int, half_width_y: int) -> Union[float, Tuple[float, float]]:
    return (start_x - half_width_x, start_y - half_width_y), (end_x - half_width_x, end_y - half_width_y), (end_x + half_width_x, end_y + half_width_y), (start_x + half_width_x, start_y + half_width_y)

elsterwerda_stage: Final[Dimension] = Dimension(1330, 600)
elsterwerda_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
    ((0, 0), (0, 600), (340, 600), (340, 0)),
    ((1330, 0), (1330, 600), (990, 600), (990, 0))
    ]

# elsterwerda_600: Final[Hall] = Hall("Elsterwerda_600", elsterwerda_stage + Dimension(0, 600),
#                                 Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
#                                                   INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
#                                       [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
#                                                   INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE,
#                                                   INSTRUMENT_PICOLO, INSTRUMENT_SAX])],
#                                       [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
#                                                   INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
#                                                   INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
#                                                   INSTRUMENT_SAX, INSTRUMENT_SAX])],
#                                 [Row(RowAngles(222, 222), [INSTRUMENT_HORN]),
#                                  Row(RowAngles(248, 292), [INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
#                                                            INSTRUMENT_TRuMPET, INSTRUMENT_TUBA]),
#                                  Row(RowAngles(318, 318), [INSTRUMENT_EUPHONIUM])],
#                                 [Row(RowAngles(252, 252), [INSTRUMENT_TROMBONE]),
#                                  Row(RowAngles(288, 288), [INSTRUMENT_TUBA])]
#                                 ], 48, 200), 210,
#                                 elsterwerda_hidden_areas)
# elsterwerda_600.draw(200)

elsterwerda_650: Final[Hall] = Hall("2021_11_13_Elsterwerda", elsterwerda_stage + Dimension(0, 650),
                                Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                  INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                      [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASSOON,
                                                  INSTRUMENT_OBOE, INSTRUMENT_OBOE, INSTRUMENT_FLUTE, INSTRUMENT_SAX])],
                                      [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                                  INSTRUMENT_HORN, INSTRUMENT_HORN,
                                                  INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
                                                  INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                [Row(RowAngles(218, 232), [INSTRUMENT_CLARINET]),
                                 Row(RowAngles(248, 292), [INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                           INSTRUMENT_TUBA]),
                                 Row(RowAngles(308, 322), [INSTRUMENT_TUBA, INSTRUMENT_TUBA])],
                                [Row(RowAngles(252, 288), [INSTRUMENT_TRuMPET,
                                                           INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE])]
                                ], 48, 200),
                                ((340, 0), (340, 210), (990, 210), (990, 0)),
                                elsterwerda_hidden_areas, Position(10, 10))
elsterwerda_650.draw(200)

plenarsaal: Final[Hall] = Hall("2021_11_07_Plenarsaal", Dimension(1460, 740),
                               Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_NOTHING,
                                                 INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                     [Row(RowAngles(190, 190), [INSTRUMENT_CLARINET]),
                                      Row(RowAngles(215, 305), [INSTRUMENT_CLARINET, INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE, INSTRUMENT_OBOE]),
                                      Row(RowAngles(325, 350), [INSTRUMENT_PICOLO, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 300), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_BASS_CLARINET,
                                                                INSTRUMENT_HORN, INSTRUMENT_HORN,
                                                                INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
                                                                INSTRUMENT_TUBA]),
                                      Row(RowAngles(318, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 315), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
                                                                INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE]),
                                      Row(RowAngles(327, 327), [INSTRUMENT_TUBA]),
                                      Row(RowAngles(337, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX])]],
                                    100, 150),
                               ((0, 100), (0,400), (400, 0), (100, 0), (100,100)),
                               [((0, 0), (0, 100), (100, 100), (100, 0)), 
                               ((1460, 0), (1240, 0), (1240, 200), (1460, 200)),
                               create_polygon_from_line(0, 460, 260, 460, 0, 2),
                               create_polygon_from_line(0, 605, 260, 605, 0, 2),
                               create_polygon_from_line(260, 460, 260, 605, 2, 0),
                               create_polygon_from_line(260, 540, 675, 505, 0, 2),
                               create_polygon_from_line(675, 505, 1090, 405, 0, 2),
                               create_polygon_from_line(1150, 325, 1460, 325, 0, 2),
                               create_polygon_from_line(1150, 430, 1460, 480, 0, 2)], Position(1240, 10))
plenarsaal.draw(150)

plenarsaal.draw(150)
riesa: Final[Hall] = Hall("2021_11_14_Riesa", Dimension(1580, 960),
                          Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                            INSTRUMENT_NOTHING, INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                            INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE, INSTRUMENT_FLUTE,
                                            INSTRUMENT_SAX])],
                                [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_HORN,
                                            INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                            INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
                                            INSTRUMENT_TUBA, INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                [Row(RowAngles(190, 205), [INSTRUMENT_CLARINET, INSTRUMENT_HORN]),
                                 Row(RowAngles(226, 314), [INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                           INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
                                                           INSTRUMENT_TROMBONE, INSTRUMENT_TUBA]),
                                 Row(RowAngles(335, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX])],
                                [Row(RowAngles(203, 203), [INSTRUMENT_CLARINET]),
                                 Row(RowAngles(337, 337), [INSTRUMENT_TUBA])]], 90, 150),
                          ((540, 0), (290, 200), (290, 235), (1290, 235), (1290, 200), (1040, 0)),
                          [((0, 0), (0, 600), (290, 600), (290, 200), (540, 0),
                            (1040, 0), (1290, 200), (1290, 600), (1580, 600),
                            (1580, 0), (0, 0))], Position(10, 10))
riesa.draw(150)


glauchau: Final[Hall] = Hall("Glauchau", Dimension(920, 1150),
                             Rows([None, None, [Row(RowAngles(210, 330), None)],
                                   [Row(RowAngles(230, 310), None)], [Row(RowAngles(238.5, 301.5), None)]], 70, 150),
                             ((173, 300), (460, 0), (747, 300)),
                             [((0, 480), (460, 0), (0,0)), ((460, 0), (920, 0), (920, 480))], Position(10, 10))
glauchau.draw(150)