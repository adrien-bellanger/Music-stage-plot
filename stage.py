import math
import sympy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from typing import Final, Dict, List, Optional
import geometry

n_seats = 0

DEFAULT_ANGLES: Final[geometry.ArcAngles] = geometry.ArcAngles(190, 350)
RADIUS_SEAT: Final[int] = 25


class Instrument:
    def __init__(self, path: Optional[Path]) -> None:
        self.path: Final[Optional[Path]] = path

    @staticmethod
    def from_dict(list_dct: Optional[List[Optional[List[Optional[str]]]]]) \
            -> Optional[List[Optional[List["Instrument"]]]]:
        global INSTRUMENTS
        if list_dct is None:
            return None

        list_instruments_per_part: List[Optional[List["Instrument"]]] = []
        for s_instruments in list_dct:
            if s_instruments is None:
                list_instruments_per_part.append(None)
            else:
                list_instruments: List["Instrument"] = []
                for s_instrument in s_instruments:
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

                list_instruments_per_part.append(list_instruments)

        return list_instruments_per_part

    def draw(self, im: Image, center: sympy.Point) -> None:
        global n_seats
        n_seats = n_seats + 1

        if self.path is None:
            ImageDraw.Draw(im).ellipse((center.x - RADIUS_SEAT, center.y - RADIUS_SEAT,
                                        center.x + RADIUS_SEAT, center.y + RADIUS_SEAT),
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
    def __init__(self, angles: Optional[List[geometry.ArcAngles]],
                 instruments: Optional[List[Optional[List[Instrument]]]],
                 radius: Optional[int], center: Optional[sympy.Point]) -> None:
        self.angles: Final[List[geometry.ArcAngles]] = [DEFAULT_ANGLES] if angles is None else angles
        self.instruments: Final[Optional[List[Optional[List[Instrument]]]]] = instruments
        self.radius: Final[Optional[int]] = radius
        self.center: Final[Optional[sympy.Point]] = center

    @staticmethod
    def from_dict(dct: dict) -> Optional["Row"]:
        angles: Optional[List[geometry.ArcAngles]] = geometry.ArcAngles.from_list(dct.get("angles"))
        instruments: Optional[List[Optional[List[Instrument]]]] = Instrument.from_dict(dct.get("instruments"))
        radius: Optional[int] = dct.get("radius")
        center: Optional[sympy.Point] = geometry.Point.from_dict(dct.get("center")) if "center" in dct else None

        return Row(angles=angles, instruments=instruments, radius=radius, center=center)

    @staticmethod
    def get_instruments_to_use(perimeter: float, distancing: int, instruments: Optional[List[Instrument]]) \
            -> List[Instrument]:
        n_max_number_of_instruments: Final[int] = math.floor(float(perimeter) / distancing) + 1
        if instruments is None:
            return [INSTRUMENTS[None]] * n_max_number_of_instruments

        if len(instruments) > n_max_number_of_instruments:
            print("A row has to many instruments for its length")
            return [INSTRUMENTS[None]] * n_max_number_of_instruments

        return instruments


class Rows:
    def __init__(self, rows: List[Optional[Row]],
                 n_distancing_delta_first_row: int,
                 n_distancing_row: int, center: geometry.Point) -> None:
        self.rows: Final[List[Optional[Row]]] = rows
        self.n_distancing_delta_first_row: Final[int] = \
            n_distancing_delta_first_row
        self.n_distancing_row: Final[int] = n_distancing_row
        self.center: Final[geometry.Point] = center

    @staticmethod
    def from_dict(dct: dict, stage_dimension: geometry.Polygon) -> Optional["Rows"]:

        center_from_dict: Optional[geometry.Point] = geometry.Point.from_dict(dct.get("center"))
        center: Final[geometry.Point] = center_from_dict if center_from_dict is not None \
            else sympy.Point(round(stage_dimension.polygon.bounds[2] / 2), stage_dimension.polygon.bounds[3])

        list_rows: List[Optional[Row]] = list()
        for dict_row in dct.get("list"):
            if dict_row is None:
                list_rows.append(None)
            else:
                new_row: Optional[Row] = Row.from_dict(dict_row)
                if new_row is None:
                    return None

                list_rows.append(new_row)

        if len(list_rows) == 0:
            print(f"No valid row is found.")
            return None

        distancing_row: Final[Optional[int]] = dct.get("distancing")
        distancing_first_row: Final[Optional[int]] = dct.get("distancingFirstRow")
            
        if distancing_row is None:
            print(f"The distancing between rows should not be None")
            return None

        return Rows(rows=list_rows,
                    n_distancing_delta_first_row=distancing_first_row if distancing_first_row is not None else 0,
                    n_distancing_row=distancing_row, center=center)


class Hall:
    def __init__(self, name: str, stage: geometry.Polygon, rows: Rows,
                 distancing: int, percussion_area: geometry.Areas,
                 hidden_areas: geometry.Areas,
                 text_top_left: sympy.Point) -> None:
        self.name: Final[str] = name
        self.stage: Final[geometry.Polygon] = stage
        self.stage_for_seats: Final[geometry.Polygon] = stage.enlarge(-RADIUS_SEAT)
        self.rows: Final[Rows] = rows
        self.distancing: Final[int] = distancing
        self.percussion_areas: Final[geometry.Areas] = percussion_area
        self.hidden_areas: Final[geometry.Areas] = hidden_areas
        self.hidden_areas_for_seats: Final[geometry.Areas] = self.hidden_areas.enlarge(RADIUS_SEAT)
        self.text_top_left: Final[sympy.Point] = text_top_left

    @staticmethod
    def from_dict(dct: dict) -> Optional["Hall"]:
        name: Final[Optional[str]] = dct.get("name")
        if name is None:
            print("The hall does not have a name.")
            return None

        stage_dimension: Final[Optional[geometry.Polygon]] = geometry.Dimension.from_dict(dct.get("stage"))
        if stage_dimension is None:
            print(f"The hall {name} does not have dimension.")
            return None

        rows: Final[Optional[Rows]] = Rows.from_dict(dct.get("rows"), stage_dimension)
        if rows is None:
            print(f"The hall {name} does not have any rows, or they are invalid {dct.get('rows')}")
            return None

        distancing: Final[Optional[int]] = dct.get("distancing")
        if distancing is None:
            print(f"There is no distancing {distancing}.")
            return None

        percussion_areas: Final[geometry.Areas] = geometry.Areas.from_dict(dct.get("percussion"), rows.center)
        hidden_areas: Final[geometry.Areas] = geometry.Areas.from_dict(dct.get("hidden"), rows.center)

        legend_top_left: Final[Optional[sympy.Point]] = geometry.Point.from_dict(dct.get("legend"))

        return Hall(name=name, stage=stage_dimension, rows=rows, distancing=distancing,
                    percussion_area=percussion_areas, hidden_areas=hidden_areas,
                    text_top_left=legend_top_left)

    def draw_percussion_area(self, image: Image) -> None:
        for area in self.percussion_areas:
            if isinstance(area, geometry.Polygon):
                ImageDraw.Draw(image).polygon(area.get_as_sequence(), outline="black", fill=(240, 240, 240))

                center: sympy.Point = area.polygon.centroid
                instrument_image_original = Image.open(Path(PATH + 'PAUKE.png'))
                n_max_size = max(instrument_image_original.size[0], instrument_image_original.size[1])
                instrument_image = instrument_image_original.reduce(max(1, int(n_max_size / 100)))
                image.alpha_composite(instrument_image, (max(0, round(center.x - instrument_image.size[0] / 2)),
                                                         max(0, round(center.y - instrument_image.size[1] / 2))))

    def draw(self) -> None:
        global n_seats
        n_seats = 0

        font = ImageFont.truetype("arial.ttf", 20)

        podest_x = 100
        podest_y = 100

        stage_x: float = self.stage.polygon.bounds[2]
        stage_y: float = self.stage.polygon.bounds[3]

        podest_bottom_left: Final[sympy.Point] = sympy.Point(self.rows.center.x - podest_x / 2, self.rows.center.y)
        podest_top_left: Final[sympy.Point] = sympy.Point(podest_bottom_left.x, podest_bottom_left.y - podest_y)
        podest_top_right: Final[sympy.Point] = sympy.Point(podest_top_left.x + podest_x, podest_top_left.y)
        podest_bottom_right: Final[sympy.Point] = sympy.Point(podest_top_right.x, podest_bottom_left.y)

        im = Image.new("RGBA", (stage_x, stage_y),
                       (255, 255, 255))
        draw = ImageDraw.Draw(im)

        draw.polygon(geometry.Polygon(podest_bottom_left, podest_top_left,
                                      podest_top_right, podest_bottom_right).get_as_sequence(),
                     fill=None, outline=(0, 0, 0))

        # Draw "Percussion line"
        self.draw_percussion_area(im)

        for hidden_area in self.hidden_areas:
            if isinstance(hidden_area, geometry.Polygon):
                draw.polygon(hidden_area.get_as_sequence(), fill=(160, 160, 160))
            elif isinstance(hidden_area, geometry.Arc):
                draw.arc(hidden_area.circle.bounds, start=hidden_area.angles.start_angle,
                         end=hidden_area.angles.end_angle, fill=(160, 160, 160), width=5)

        print("Hall " + self.name)

        self.draw_rows(im)

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

    def draw_rows(self, im: Image) -> None:
        radius: int = self.rows.n_distancing_delta_first_row
        for row in self.rows.rows:
            min_radius = radius + max(self.distancing, self.rows.n_distancing_row)
            radius = max(min_radius, row.radius if row is not None and row.radius is not None else min_radius)
            print(f"radius: {radius} cm.")
            circle: geometry.Circle = geometry.Circle(
                self.rows.center if row is None or row.center is None else row.center, radius)

            arcs_on_stage: List[geometry.ArcAngles] = geometry.ArcAngles.reduce_to(
                row.angles if row.angles is not None else [DEFAULT_ANGLES],
                circle.intersection_arc_angles(self.stage_for_seats))

            for hidden_area in self.hidden_areas_for_seats:
                if isinstance(hidden_area, geometry.Polygon):
                    arcs_on_stage = geometry.ArcAngles.exclude(
                        arcs_on_stage,
                        circle.intersection_arc_angles(hidden_area)
                    )

            s_arcs_on_stage = "["
            for arc in arcs_on_stage:
                s_arcs_on_stage += f"{{{arc.start_angle}, {arc.end_angle}}},"
            s_arcs_on_stage = s_arcs_on_stage[:-1]
            s_arcs_on_stage += "]"
            print(f"The instruments are placed between the following angles: {s_arcs_on_stage}")
            if row is not None and row.instruments is not None and len(row.instruments) != len(arcs_on_stage):
                print("The list of instruments does not fit the arcs on stage.")
                return

            if row is None:
                for arc in arcs_on_stage:
                    self.draw_row(im, arc, None, circle)
            else:
                i: int = 0
                while i < len(arcs_on_stage):
                    arc_row: geometry.ArcAngles = arcs_on_stage[i]
                    instruments: Optional[List[Instrument]] = row.instruments[i] if row.instruments is not None \
                        else None
                    self.draw_row(im, arc_row, instruments, circle)

                    i = i + 1

    def draw_row(self, im: Image, arc: geometry.ArcAngles, list_instruments: Optional[List[Instrument]],
                 circle: geometry.Circle) -> None:
        # ImageDraw.Draw(im).arc(create_xy(center, Dimension(radius*2, radius*2)),
        #                        start=self.angles.start_angle, end=self.angles.end_angle, fill=(255, 255, 0))

        perimeter: Final[float] = circle.perimeter(arc)

        instruments: Final[List[Instrument]] = Row.get_instruments_to_use(perimeter, self.distancing, list_instruments)

        current_point: sympy.Point = circle.point(arc.start_angle) if len(instruments) > 1 \
            else circle.point((arc.start_angle + arc.end_angle) / 2)

        second_point: Final[sympy.Point] = circle.point(arc.start_angle
                                                        + (abs(arc.end_angle - arc.start_angle)
                                                           / (len(instruments) - 1))) \
            if len(instruments) > 1 \
            else current_point

        distancing: Final[float] = current_point.distance(second_point)

        print(f"distancing: {int(distancing)}cm for {len(instruments)} instruments.")

        for instrument in instruments:
            instrument.draw(im, current_point)
            if distancing > 0:
                current_point = circle.get_first_intersection(circle.intersection(geometry.Circle(current_point,
                                                                                                  distancing)),
                                                              True)
