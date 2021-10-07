
from PIL import Image, ImageDraw

from typing import Final, NoReturn, Sequence, Tuple, Union

from math import sqrt, pow

# Python program to demonstrate
# main() function
  
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
    '''
        Finding the x,y coordinates on circle, based on given angle
    '''
    from math import cos, sin, pi
    #center of circle, angle in degree and radius of circle
    angle_in_radians = angle_in_degrees * pi / 180
    print("radius " + str(radius) + " radians " + str(angle_in_radians) + " cos(radians) " + str(cos(angle_in_radians)) + " sin(radians) " + str(sin(angle_in_radians)))
    x = center.x + (radius * cos(angle_in_radians))
    y = center.y + (radius * sin(angle_in_radians))

    return Position(x,y)


class Circle:
    def __init__(self, center: Position, radius: int) -> NoReturn:
        self.center: Final[Position] = center
        self.radius: Final[int] = radius

    def Intersections(self, other: 'Circle') -> Position:
        dist: Final[float] = self.center.distance(other.center)
        a: Final[float] = (pow(self.radius, 2) - pow(other.radius, 2) + pow(dist, 2)) / (2* dist)
        h: Final[float] = sqrt(pow(self.radius, 2))
        p2: Final[Position] = other.center.sub(self.center).scale(a/dist) + self.center
        # return Position(p2.x + h*(other.center.y - self.center.y)/dist, p2.y - h*(other.center.x - self.center.x)/dist)
        return Position(p2.x - h*(other.center.y - self.center.y)/dist, p2.y + h*(other.center.x - self.center.x)/dist)

# Defining main function
def main():
    
    stage: Final[Dimension] = Dimension(1580, 960)
    podest: Final[Dimension] = Dimension(200, 200)

    center: Final[Position] = Position(stage.length / 2, stage.width)
    podest_center: Final[Position] = Position(center.x, center.y - podest.width/2)

    im = Image.new('RGB', (stage.length, stage.width), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    draw.polygon(((0,0), (0,600), (290, 600), (290, 200), (540, 0), (1040, 0), (1290, 200), (1290, 600), (1580, 600), (1580, 0), (0,0)), fill=(200,200,200))
   
    podest_xy = create_xy(podest_center, podest)
    draw.rectangle(podest_xy, fill=None, outline=(0,0,0))
    
    print("Podest " + str(podest_xy))
    
    first_rang: Final[Dimension] = Dimension(500, 500)
    first_rang_xy = create_xy(center, first_rang)
    draw.arc(first_rang_xy, start=190, end=350, fill=(255, 255, 0))
    print("First Rang: " + str(first_rang_xy))

    first_cla: Final[Position] = point_on_circle(center, first_rang.length/2, 190)
    print("First Cla: " + str(first_cla.x) + " y " + str(first_cla.y))
    draw.ellipse(create_xy(first_cla, Dimension(50,50)), fill=(255, 0, 0))

    second_cla: Final[Position] = Circle(center, first_rang.width/2).Intersections(Circle(first_cla, 100))
    print("Second Cla: " + str(second_cla.x) + " y " + str(second_cla.y))
    draw.ellipse(create_xy(second_cla, Dimension(50,50)), fill=(255, 0, 0))

    print("Second clarinette to first distance: " + str(first_cla.distance(second_cla)))

    first_fl: Final[Position] = point_on_circle(center, first_rang.length/2, 350)
    print("First Fl: " + str(first_fl.x) + " y " + str(first_fl.y))
    draw.ellipse(create_xy(first_fl, Dimension(50,50)), fill=(255, 0, 0))

    second_rang: Final[Dimension] = first_rang + Dimension(400, 400)
    second_rang_xy = create_xy(center, second_rang)
    draw.arc(second_rang_xy, start=190, end=350, fill=(255, 255, 0))
    print("Second Rang: " + str(second_rang_xy))

    third_rang: Final[Dimension] = second_rang + Dimension(400, 400)
    third_rang_xy = create_xy(center, third_rang)
    draw.arc(third_rang_xy, start=190, end=350, fill=(255, 255, 0))
    print("Third Rang: " + str(third_rang_xy))


    #draw.arc((590, 760, 990, 1160), start=225, end=315, fill=(255, 255, 0))
  
    im.save('/home/famille/Downloads/pillow_imagedraw3.jpg', quality=95)
# Using the special variable 
# __name__
if __name__=="__main__":
    main()