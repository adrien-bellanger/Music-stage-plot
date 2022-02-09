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

    def draw(self, im: Image, center: geometry.Position) -> None:
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
    def __init__(self, angles: geometry.ArcAngles, instruments: List[Instrument]) -> None:
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
             center: geometry.Position, radius: int, min_distancing: int) -> None:

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
                 n_distancing_row: int) -> None:
        self.rows_with_angles: Final[List[Row]] = rows
        self.n_distancing_delta_first_row: Final[int] = \
            n_distancing_delta_first_row
        self.n_distancing_row: Final[int] = n_distancing_row

    def draw(self, im: Image, center:
             geometry.Position, distancing: int) -> None:
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
                 text_top_left: geometry.Position) -> None:
        self.name: Final[str] = name
        self.stage: Final[geometry.Dimension] = stage
        self.rows: Final[Rows] = rows
        self.percussion_area: Final[Union[Tuple[float, float]]] = percussion_area
        self.hidden_areas: Final[Sequence[Union[Tuple[float, float]]]] \
            = hidden_areas
        self.text_top_left: Final[geometry.Position] = text_top_left

    def draw_percussion_area(self, image: Image) -> None:
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

    def draw(self, distancing: int) -> None:
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
