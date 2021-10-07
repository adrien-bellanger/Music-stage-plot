
from PIL import Image, ImageDraw, ImageFont

from typing import Final, List, NoReturn, Sequence, Tuple, Union

from math import sqrt, pow

# Python program to demonstrate
# main() function

n_seats = 0

class Position:
    def __init__(self, x:int, y:int) -> NoReturn:
        self.x: Final[int] = x
        self.y: Final[int] = y

    def sub(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y)
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)
        
    def distance(self, other: 'Position') -> 'Position':
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))
    
    def normal(self)-> 'Position':
        length: float = sqrt(pow(self.x, 2) + pow(self.y, 2))
        return Position(self.x/length, self.y/length)

    def scale(self, s: float) -> 'Position':
        return Position(self.x*s, self.y*s)

class Dimension:
    def __init__(self, length:int, width: int) -> NoReturn:
        self.length: Final[int] = length
        self.width: Final[int] = width

    def __add__(self, other: 'Dimension')->'Dimension':
        return Dimension(self.length + other.length, self.width + other.width)

def create_xy(pos: Position, dim: Dimension)->Sequence[Union[float, Tuple[float, float]]]:
    return (pos.x - dim.length/2, pos.y - dim.width/2, pos.x + dim.length/2, pos.y + dim.width/2)

def point_on_circle(center: Position, radius: int, angle_in_degrees: float):
    from math import cos, sin, pi
    angle_in_radians = angle_in_degrees * pi / 180
    x = center.x + (radius * cos(angle_in_radians))
    y = center.y + (radius * sin(angle_in_radians))

    return Position(x,y)


class Circle:
    def __init__(self, center: Position, radius: int) -> NoReturn:
        self.center: Final[Position] = center
        self.radius: Final[int] = radius

    def Intersections(self, other: 'Circle', clockwise: bool) -> Position:
        dist: Final[float] = self.center.distance(other.center)
        a: Final[float] = (pow(self.radius, 2) - pow(other.radius, 2) + pow(dist, 2)) / (2* dist)
        h: Final[float] = sqrt(pow(self.radius, 2) - pow(a, 2))
        p2: Final[Position] = other.center.sub(self.center).scale(a/dist) + self.center
        if clockwise:
            return Position(p2.x - h*(other.center.y - self.center.y)/dist, p2.y + h*(other.center.x - self.center.x)/dist)
        
        return Position(p2.x + h*(other.center.y - self.center.y)/dist, p2.y - h*(other.center.x - self.center.x)/dist)

class Hall:
    def __init__(self, name: str, stage: Dimension, row_radius: List[int], 
                 hidden_areas: Sequence[Union[float, Tuple[float, float]]], hidden_seats: int) -> NoReturn:
        self.name: Final[str] = name
        self.stage: Final[Dimension] = stage
        self.row_radius: Final[List[int]] = row_radius
        self.hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = hidden_areas
        self.hidden_seats: Final[int] = hidden_seats

    def draw(self, distancing: int) -> NoReturn:
        font = ImageFont.truetype("arial.ttf", 20)

        podest: Final[Dimension] = Dimension(200, 200)

        center: Final[Position] = Position(self.stage.length / 2, self.stage.width)
        podest_center: Final[Position] = Position(center.x, center.y - podest.width/2)

        im = Image.new('RGB', (self.stage.length, self.stage.width), (255, 255, 255))
        draw = ImageDraw.Draw(im)

        podest_xy = create_xy(podest_center, podest)
        draw.rectangle(podest_xy, fill=None, outline=(0,0,0))

        start_angle: Final[int] = 190
        end_angle: Final[int] = 350

        for radius in self.row_radius:
            create_row(draw, center, radius, start_angle, end_angle, distancing)

        for hidden_area in self.hidden_areas:
            draw.polygon(hidden_area, fill=(200,200,200))

        draw.text((10,10), "Number of seats " + str(n_seats - self.hidden_seats), fill=(0,0,0), font=font)
        draw.text((10, 40), "scale: 1m", fill=(0,0,0), font=font)
        draw.line(((10,65), (110, 65)), fill=(0,0,0), width=3)

        im.save('export/'+ self.name + '_Abstand_' + str(distancing) + '.jpg', quality=95)

def draw_seat(draw: ImageDraw, pos: Position) -> NoReturn:
    global n_seats
    n_seats = n_seats + 1
    draw.ellipse(create_xy(pos, Dimension(50,50)), fill=(255, 0, 0))
    return

def create_row(draw: ImageDraw, center: Position, radius: int, start_angle: int, end_angle:int, distancing: int)-> NoReturn:
    draw.arc(create_xy(center, Dimension(radius*2, radius*2)), start= start_angle, end=end_angle, fill=(255,255,0))

    row_center: Final[Position] = Position(center.x, center.y - radius)

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

        current_left = Circle(center, radius).Intersections(Circle(current_left, distancing), True)
        current_right = Circle(center, radius).Intersections(Circle(current_right, distancing), False)

        if current_left.distance(current_right) < distancing:
            draw_seat(draw, row_center)
            return

plenarsaal: Final[Hall] = Hall("Plenarsaal", Dimension(1460, 840), [250], [((0,0), (0,100), (100,100), (100,0))], 0)

plenarsaal.draw(150)
riesa: Final[Hall] = Hall("Riesa", Dimension(1580, 960), [250, 450, 650], 
                          [((0,0), (0,600), (290, 600), (290, 200), (540, 0), (1040, 0), (1290, 200), (1290, 600), (1580, 600), (1580, 0), (0,0))], 
                          2)
riesa.draw(100)
riesa.draw(150)

