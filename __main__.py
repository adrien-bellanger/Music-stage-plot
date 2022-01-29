import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from typing import Final, List, NoReturn, Sequence, Tuple, Union

import geometry

n_seats = 0


DEFAULT_ANGLES: Final[geometry.ArcAngles] = geometry.ArcAngles(190, 350)


class Instrument:
    def __init__(self, path: Path) -> NoReturn:
        self.path: Final[Path] = path

    def draw(self, im: Image, center: geometry.Position) -> NoReturn:
        global n_seats
        n_seats = n_seats + 1

        if self.path is None:
            ImageDraw.Draw(im).ellipse(geometry.create_rectangle(center, geometry.Dimension(50, 50)),
                                       outline=(0, 0, 0), width=2)
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
    def __init__(self, angles: geometry.ArcAngles, instruments: List[Instrument]) -> NoReturn:
        self.angles: Final[geometry.ArcAngles] = DEFAULT_ANGLES if angles is None else angles
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
             center: geometry.Position, radius: int, min_distancing: int) -> NoReturn:

        # ImageDraw.Draw(im).arc(create_xy(center, Dimension(radius*2, radius*2)),
        #                        start=self.angles.start_angle, end=self.angles.end_angle, fill=(255, 255, 0))

        circle: Final[geometry.Circle] = geometry.Circle(center, radius)

        perimeter: Final[float] = circle.perimeter(self.angles)

        instruments: Final[List[Instrument]] = self.get_instruments_to_use(perimeter, min_distancing)

        current_position: geometry.Position = circle.position(self.angles.start_angle) if len(instruments) > 1 \
            else circle.position((self.angles.start_angle + self.angles.end_angle) / 2)

        second_position: Final[geometry.Position] = \
            circle.position(self.angles.start_angle + (abs(self.angles.end_angle - self.angles.start_angle)
                                                       / (len(instruments) - 1))) if len(instruments) > 1 \
            else current_position
        distancing: Final[float] = current_position.distance(second_position)

        print("radius: " + str(radius) + " distancing: " + str(distancing))

        for instrument in instruments:
            instrument.draw(im, current_position)
            if distancing > 0:
                current_position = circle.intersections(
                    geometry.Circle(current_position, distancing), True)


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
             geometry.Position, distancing: int) -> NoReturn:
        radius: int = self.n_distancing_delta_first_row
        for row_with_angles in self.rows_with_angles:
            radius = radius + max(distancing, self.n_distancing_row)
            if row_with_angles is None:
                DEFAULT_ROW.draw(im, center, radius, distancing)
            else:
                for row_parts in row_with_angles:
                    row_parts.draw(im, center, radius, distancing)


class Hall:
    def __init__(self, name: str, stage: geometry.Dimension, rows: Rows,
                 percussion_area: Union[Tuple[float, float]],
                 hidden_areas: Sequence[Union[Tuple[float, float]]],
                 text_top_left: geometry.Position) -> NoReturn:
        self.name: Final[str] = name
        self.stage: Final[geometry.Dimension] = stage
        self.rows: Final[Rows] = rows
        self.percussion_area: Final[Union[Tuple[float, float]]] = percussion_area
        self.hidden_areas: Final[Sequence[Union[Tuple[float, float]]]] \
            = hidden_areas
        self.text_top_left: Final[geometry.Position] = text_top_left

    def draw_percussion_area(self, image: Image) -> NoReturn:
        ImageDraw.Draw(image).polygon(self.percussion_area, outline="black", fill=(240, 240, 240))
        n_min_x: float = self.stage.length
        n_max_x: float = 0
        n_min_y: float = self.stage.width
        n_max_y: float = 0
        for (x, y) in self.percussion_area:
            if x < n_min_x:
                n_min_x = x
            if x > n_max_x:
                n_max_x = x
            if y < n_min_y:
                n_min_y = y
            if y > n_max_y:
                n_max_y = y

        center: Final[geometry.Position] = geometry.Position((n_min_x + n_max_x)/2, (n_min_y + n_max_y)/2)
        instrument_image_original = Image.open(Path(INSTRUMENT_PATH + 'PAUKE.png'))
        n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
        instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
        image.alpha_composite(instrument_image, (max(0, int(center.x - instrument_image.size[0] / 2)),
                                              max(0, int(center.y - instrument_image.size[1] / 2))))

    def draw(self, distancing: int) -> NoReturn:
        global n_seats
        n_seats = 0

        font = ImageFont.truetype("arial.ttf", 20)

        podest: Final[geometry.Dimension] = geometry.Dimension(100, 100)

        center: Final[geometry.Position] = geometry.Position(self.stage.length / 2, self.stage.width)
        podest_center: Final[geometry.Position] = geometry.Position(center.x, center.y - podest.width/2)

        im = Image.new("RGBA", (self.stage.length, self.stage.width),
                       (255, 255, 255))
        draw = ImageDraw.Draw(im)

        podest_xy = geometry.create_rectangle(podest_center, podest)
        draw.rectangle(podest_xy, fill=None, outline=(0, 0, 0))

        # Draw "Percussion line"
        self.draw_percussion_area(im)

        for hidden_area in self.hidden_areas:
            draw.polygon(hidden_area, fill=(160, 160, 160))

        print("Hall " + self.name)

        self.rows.draw(im, center, distancing)

        draw.text((self.text_top_left.x, self.text_top_left.y), str(self.name) + "\n" +
                  "Number of seats " + str(n_seats) + "\n" +
                  "distancing: " + str(distancing) + " cm\n" +
                  "row distancing: " + str(self.rows.n_distancing_row) + "cm\n" +
                  "scale 1m", fill=(0, 0, 0), font=font)
        n_top_line: Final[int] = 120
        draw.line(((self.text_top_left.x, self.text_top_left.y + n_top_line),
                   (self.text_top_left.x + 100, self.text_top_left.y + n_top_line)), fill=(0, 0, 0),
                  width=3)

        im.save('export/' + self.name + '_distancing_' + str(distancing) + '_row_distancing_'
                + str(self.rows.n_distancing_row) + '.png')


if False:

    im = Image.new("RGBA", (100, 100))
    im.save(INSTRUMENT_PATH + 'NO_INSTRUMENT.png')

def create_polygon_from_line(start_x: int, start_y: int, end_x:int, end_y:int, half_width_x: int, half_width_y: int) -> Union[float, Tuple[float, float]]:
    return (start_x - half_width_x, start_y - half_width_y), (end_x - half_width_x, end_y - half_width_y), (end_x + half_width_x, end_y + half_width_y), (start_x + half_width_x, start_y + half_width_y)

bautzen_krone_1m_Wall: Final[int] = int(math.sqrt(2) * 50)
bautzen_krone_stage: Final[geometry.Dimension] = geometry.Dimension(1700 + bautzen_krone_1m_Wall * 4 * 2, 1410)
bautzen_krone_middleLength: Final[int] = int(bautzen_krone_stage.length / 2)
bautzen_krone_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
    ((0, 0), (0, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4), (bautzen_krone_middleLength, 0)),
    (
        (bautzen_krone_middleLength, 0),
        (bautzen_krone_stage.length, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4),
        (bautzen_krone_stage.length, 0)),
    (
        (0, bautzen_krone_stage.width), (bautzen_krone_1m_Wall * 4, bautzen_krone_stage.width),
        (0, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4)),
    (
        (bautzen_krone_stage.length, bautzen_krone_stage.width),
        (bautzen_krone_stage.length - bautzen_krone_1m_Wall * 4, bautzen_krone_stage.width),
        (bautzen_krone_stage.length, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4)),
    (
        (bautzen_krone_middleLength, 0),
        (bautzen_krone_middleLength - bautzen_krone_1m_Wall * 2, bautzen_krone_1m_Wall * 2),
        (bautzen_krone_middleLength - bautzen_krone_1m_Wall, bautzen_krone_1m_Wall * 3),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall, bautzen_krone_1m_Wall)),
    (
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * 6, bautzen_krone_1m_Wall * 6),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 - 2), bautzen_krone_1m_Wall * (6 + 2)),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 - 1), bautzen_krone_1m_Wall * (6 + 3)),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 + 1), bautzen_krone_1m_Wall * (6 + 1))),
    (
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * 12, bautzen_krone_1m_Wall * 12),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 - 2), bautzen_krone_1m_Wall * (12 + 2)),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 - 1), bautzen_krone_1m_Wall * (12 + 3)),
        (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 + 1), bautzen_krone_1m_Wall * (12 + 1)))
]

bautzen_krone: Final[Hall] = Hall("Test_Bautzen_Krone", bautzen_krone_stage, Rows([None, None, None, None, None, None], 50, 150),
                                  ((0, 0), (0, 420), (bautzen_krone_stage.length, 420), (bautzen_krone_stage.length, 0)),
                                  bautzen_krone_hidden_areas, geometry.Position(10, 10))
bautzen_krone.draw(100)

if False:
    elsterwerda_stage: Final[Dimension] = Dimension(1330, 600)
    elsterwerda_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
        ((0, 0), (0, 600), (340, 600), (340, 0)),
        ((1330, 0), (1330, 600), (990, 600), (990, 0))
        ]

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

if False:
    plenarsaal: Final[Hall] = Hall("2021_11_07_Plenarsaal", Dimension(1460, 740),
                               Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                 INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                     [Row(RowAngles(190, 190), [INSTRUMENT_CLARINET]),
                                      Row(RowAngles(215, 305), [INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                                                INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE]),
                                      Row(RowAngles(325, 350), [INSTRUMENT_PICOLO, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 300), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_HORN, INSTRUMENT_HORN,
                                                                INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM]),
                                      Row(RowAngles(318, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 315), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
                                                                INSTRUMENT_TROMBONE]),
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

if False:
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

if False:
    glauchau: Final[Hall] = Hall("Glauchau", Dimension(920, 1150),
                             Rows([None, None, [Row(RowAngles(210, 330), None)],
                                   [Row(RowAngles(230, 310), None)], [Row(RowAngles(238.5, 301.5), None)]], 70, 150),
                             ((173, 300), (460, 0), (747, 300)),
                             [((0, 480), (460, 0), (0,0)), ((460, 0), (920, 0), (920, 480))], Position(10, 10))
    glauchau.draw(150)