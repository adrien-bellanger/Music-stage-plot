import math
import sympy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from typing import Final, Dict, List, Optional
import geometry

n_seats = 0

DEFAULT_ANGLES: Final[geometry.ArcAngles] = geometry.ArcAngles(190, 350)


class Instrument:
    def __init__(self, path: Optional[Path]) -> None:
        self.path: Final[Optional[Path]] = path

    @staticmethod
    def from_dict(list_dct: Optional[List[Optional[str]]]) -> Optional[List["Instrument"]]:
        global INSTRUMENTS
        if list_dct is None:
            return None

        list_instruments: List["Instrument"]
        for s_instrument in list_dct:
            instrument: Optional[Instrument] = INSTRUMENTS.get(s_instrument)
            if instrument is not None:
                list_instruments.append(instrument)
            else:
                print(f"The chosen instrument {s_instrument} does not exist, only the following are accepted: "
                      f"{INSTRUMENTS.keys}.")
                list_instruments.append(INSTRUMENTS[None])

        if len(list_instruments) == 0:
            print(f"An empty list of instrument was specified, it is not valid (will be replaced by None).")
            return None

        return list_instruments

    def draw(self, im: Image, center: sympy.Point) -> None:
        global n_seats
        n_seats = n_seats + 1

        if self.path is None:
            radius: Final[int] = 25
            ImageDraw.Draw(im).ellipse((center.x - radius, center.y - radius,
                                        center.x + radius, center.y + radius),
                                       outline=(0, 0, 0), width=2)
            return

        instrument_image_original = Image.open(self.path)
        n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
        instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
        im.alpha_composite(instrument_image, (max(0, int(center.x - instrument_image.size[0] / 2)),
                                              max(0, int(center.y - instrument_image.size[1] / 2))))


PATH: Final[str] = "Instruments/"
INSTRUMENTS: Final[Dict[Optional[str], "Instrument"]] = {
    None: Instrument(None),
    "BassClarinet": Instrument(Path(PATH + "BKLARINETTE.png")),
    "Bassoon": Instrument(Path(PATH + 'FAGOTTE.png')),
    "Clarinet": Instrument(Path(PATH + "KLARINETTE.png")),
    "Euphonium": Instrument(Path(PATH + "EUPHONIUM.png")),
    "Flute": Instrument(Path(PATH + "FLOETE.png")),
    "Horn": Instrument(Path(PATH + "HORN.png")),
    "NoInstrument": Instrument(Path(PATH + 'NO_INSTRUMENT.png')),
    "Oboe": Instrument(Path(PATH + 'OBOE.png')),
    "Piccolo": Instrument(Path(PATH + "PICCOLO.png")),
    "Trombone": Instrument(Path(PATH + "POSAUNE.png")),
    "Sax": Instrument(Path(PATH + "SAX.png")),
    "Trumpet": Instrument(Path(PATH + "TROMPETE.png")),
    "Tuba": Instrument(Path(PATH + "TUBA.png"))
}


class Row:
    def __init__(self, angles: Optional[geometry.ArcAngles], instruments: Optional[List[Instrument]]) -> None:
        self.angles: Final[geometry.ArcAngles] = DEFAULT_ANGLES if angles is None else angles
        self.instruments: Final[Optional[List[Instrument]]] = instruments

    @staticmethod
    def from_dict(dct: dict) -> Optional["Row"]:
        angles: Optional[geometry.ArcAngles] = geometry.ArcAngles.from_dict(dct.get("angles"))
        instruments: Optional[List[Instrument]] = Instrument.from_dict(dct.get("instruments"))

        return Row(angles=angles, instruments=instruments)

    def get_instruments_to_use(self, perimeter: float, distancing: int) -> List[Instrument]:
        n_max_number_of_instruments: Final[int] = math.floor(float(perimeter) / distancing) + 1
        if self.instruments is None:
            return [INSTRUMENTS[None]] * n_max_number_of_instruments

        if len(self.instruments) > n_max_number_of_instruments:
            print("A row has to many instruments for its length")
            return [INSTRUMENTS[None]] * n_max_number_of_instruments

        return self.instruments

    def draw(self, im: Image, center: sympy.Point, radius: int, min_distancing: int) -> None:

        # ImageDraw.Draw(im).arc(create_xy(center, Dimension(radius*2, radius*2)),
        #                        start=self.angles.start_angle, end=self.angles.end_angle, fill=(255, 255, 0))

        circle: Final[geometry.Circle] = geometry.Circle(center, radius)

        perimeter: Final[float] = circle.perimeter(self.angles)

        instruments: Final[List[Instrument]] = self.get_instruments_to_use(perimeter, min_distancing)

        current_point: sympy.Point = circle.point(self.angles.start_angle) if len(instruments) > 1 \
            else circle.point((self.angles.start_angle + self.angles.end_angle) / 2)

        second_point: Final[sympy.Point] = \
            circle.point(self.angles.start_angle + (abs(self.angles.end_angle - self.angles.start_angle)
                                                    / (len(instruments) - 1))) if len(instruments) > 1 \
            else current_point
        distancing: Final[float] = current_point.distance(second_point)

        print(f"radius: {radius}cm distancing: {int(distancing)}cm.")

        for instrument in instruments:
            instrument.draw(im, current_point)
            if distancing > 0:
                current_point = circle.intersections(
                    geometry.Circle(current_point, distancing), True)


DEFAULT_ROW: Final[Row] = Row(None, None)


class Rows:
    def __init__(self, rows: List[Optional[List[Row]]],
                 n_distancing_delta_first_row: int,
                 n_distancing_row: int) -> None:
        self.rows_with_angles: Final[List[Optional[List[Row]]]] = rows
        self.n_distancing_delta_first_row: Final[int] = \
            n_distancing_delta_first_row
        self.n_distancing_row: Final[int] = n_distancing_row

    @staticmethod
    def from_dict(dct: dict) -> Optional["Rows"]:
        list_rows: List[Optional[List[Row]]] = list()
        for dict_row in dct.get("list"):
            if dict_row is None:
                list_rows.append(None)
            else:
                list_sub_rows: List[Row] = list()
                for dict_sub_row in dict_row:
                    new_row: Optional[Row] = Row.from_dict(dict_sub_row)
                    if new_row is None:
                        return None

                    list_sub_rows.append(new_row)
                if len(list_sub_rows) == 0:
                    print(f"A row does not have any sub row, but it is not null.")
                    return None

                list_rows.append(list_sub_rows)

        if len(list_rows) == 0:
            print(f"No valid row is found.")
            return None

        distancing_row: Final[Optional[int]] = dct.get("distancing")
        distancing_first_row: Final[Optional[int]] = dct.get("distancingFirstRow")

        return Rows(rows=list_rows, n_distancing_delta_first_row=distancing_first_row, n_distancing_row=distancing_row)

    def draw(self, im: Image, center: sympy.Point, distancing: int) -> None:
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
                 distancing: int, percussion_area: geometry.Areas,
                 hidden_areas: geometry.Areas,
                 text_top_left: sympy.Point) -> None:
        self.name: Final[str] = name
        self.stage: Final[geometry.Dimension] = stage
        self.rows: Final[Rows] = rows
        self.distancing: Final[int] = distancing
        self.percussion_areas: Final[geometry.Areas] = percussion_area
        self.hidden_areas: Final[geometry.Areas] \
            = hidden_areas
        self.text_top_left: Final[sympy.Point] = text_top_left

    @staticmethod
    def from_dict(dct: dict) -> Optional["Hall"]:
        name: Final[Optional[str]] = dct.get("name")
        if name is None:
            print("The hall does not have a name.")
            return None

        stage_dimension: Final[Optional[geometry.Dimension]] = geometry.Dimension.from_dict(dct.get("stage"))
        if stage_dimension is None:
            print(f"The hall {name} does not have dimension.")
            return None

        rows: Final[Optional[Rows]] = Rows.from_dict(dct.get("rows"))
        if rows is None:
            print(f"The hall {name} does not have any rows, or they are invalid {dct.get('rows')}")
            return None

        distancing: Final[Optional[int]] = dct.get("distancing")
        if distancing is None:
            print(f"There is no distancing {distancing}.")
            return None

        percussion_areas: Final[geometry.Areas] = geometry.Areas.from_dict(dct.get("percussion"))
        hidden_areas: Final[geometry.Areas] = geometry.Areas.from_dict(dct.get("hidden"))

        legend_top_left: Final[Optional[sympy.Point]] = geometry.Point.from_dict(dct.get("legend"))

        return Hall(name=name, stage=stage_dimension, rows=rows, distancing=distancing,
                    percussion_area=percussion_areas, hidden_areas=hidden_areas,
                    text_top_left=legend_top_left)

    def draw_percussion_area(self, image: Image) -> None:
        for area in self.percussion_areas:
            if isinstance(area, geometry.Polygon):
                ImageDraw.Draw(image).polygon(area.get_as_sequence(), outline="black", fill=(240, 240, 240))
                n_min_x: float = self.stage.length
                n_max_x: float = 0
                n_min_y: float = self.stage.width
                n_max_y: float = 0
                for pos in area.points:
                    if pos.x < n_min_x:
                        n_min_x = pos.x
                    if pos.x > n_max_x:
                        n_max_x = pos.x
                    if pos.y < n_min_y:
                        n_min_y = pos.y
                    if pos.y > n_max_y:
                        n_max_y = pos.y

                center: sympy.Point = sympy.Point((n_min_x + n_max_x)/2, (n_min_y + n_max_y)/2)
                instrument_image_original = Image.open(Path(PATH + 'PAUKE.png'))
                n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
                instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
                image.alpha_composite(instrument_image, (max(0, round(center.x - instrument_image.size[0] / 2)),
                                                         max(0, round(center.y - instrument_image.size[1] / 2))))

    def draw(self) -> None:
        global n_seats
        n_seats = 0

        font = ImageFont.truetype("arial.ttf", 20)

        podest: Final[geometry.Dimension] = geometry.Dimension(100, 100)

        center: Final[sympy.Point] = sympy.Point(self.stage.length / 2, self.stage.width)
        podest_center: Final[sympy.Point] = sympy.Point(center.x, center.y - podest.width/2)

        im = Image.new("RGBA", (self.stage.length, self.stage.width),
                       (255, 255, 255))
        draw = ImageDraw.Draw(im)

        podest_xy = geometry.Polygon.create_rectangle(podest_center, podest)
        draw.polygon(podest_xy.get_as_sequence(), fill=None, outline=(0, 0, 0))

        # Draw "Percussion line"
        self.draw_percussion_area(im)

        for hidden_area in self.hidden_areas:
            if isinstance(hidden_area, geometry.Polygon):
                draw.polygon(hidden_area.get_as_sequence(), fill=(160, 160, 160))

        print("Hall " + self.name)

        self.rows.draw(im, center, self.distancing)

        draw.text((self.text_top_left.x, self.text_top_left.y), str(self.name) + "\n" +
                  "Number of seats " + str(n_seats) + "\n" +
                  "distancing: " + str(self.distancing) + " cm\n" +
                  "row distancing: " + str(self.rows.n_distancing_row) + "cm\n" +
                  "scale 1m", fill=(0, 0, 0), font=font)
        n_top_line: Final[int] = 120
        draw.line(((self.text_top_left.x, self.text_top_left.y + n_top_line),
                   (self.text_top_left.x + 100, self.text_top_left.y + n_top_line)), fill=(0, 0, 0),
                  width=3)

        im.save('export/' + self.name + '_distancing_' + str(self.distancing) + '_row_distancing_'
                + str(self.rows.n_distancing_row) + '.png')
