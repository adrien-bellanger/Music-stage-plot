import math
import unittest

import sympy

import geometry


class TestCircle(unittest.TestCase):
    def test_intersection(self):
        c1: geometry.Circle = geometry.Circle(geometry.Position.from_xy(0, 0), 100)
        c2: geometry.Circle = geometry.Circle(geometry.Position.from_xy(0, 100), math.sqrt(2) * 100)
        p1: geometry.Position = c1.intersections(c2, False)
        p2: geometry.Position = c1.intersections(c2, True)
        self.assertAlmostEqual(0, p1.point.y, 6)
        self.assertAlmostEqual(100, p1.point.x, 6)
        self.assertAlmostEqual(0, p2.point.y, 6)
        self.assertAlmostEqual(-100, p2.point.x, 6)

    def test_angle(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(geometry.Position(center), radius)
        p180: geometry.Position = geometry.Position.from_xy(center.x - radius, center.y)
        self.assertAlmostEqual(180, circle.angle(p180))
        p0: geometry.Position = geometry.Position.from_xy(center.x + radius, center.y)
        self.assertAlmostEqual(0, circle.angle(p0))
        p90: geometry.Position = geometry.Position.from_xy(center.x, center.y + radius)
        self.assertAlmostEqual(90, circle.angle(p90))
        p270: geometry.Position = geometry.Position.from_xy(center.x, center.y - radius)
        self.assertAlmostEqual(270, circle.angle(p270))

    def test_position(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(geometry.Position(center), radius)
        p180: geometry.Position = circle.position(180)
        self.assertAlmostEqual(center.x - radius, p180.point.x)
        self.assertAlmostEqual(center.y, p180.point.y)
        p0: geometry.Position = circle.position(0)
        self.assertAlmostEqual(center.x + radius, p0.point.x)
        self.assertAlmostEqual(center.y, p0.point.y)
        p90: geometry.Position = circle.position(90)
        self.assertAlmostEqual(center.x, p90.point.x)
        self.assertAlmostEqual(center.y + radius, p90.point.y)
        p270: geometry.Position = circle.position(270)
        self.assertAlmostEqual(center.x, p270.point.x)
        self.assertAlmostEqual(center.y - radius, p270.point.y)

    def test_position_and_angle(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(geometry.Position(center), radius)
        original_angle = 195
        position: geometry.Position = circle.position(original_angle)
        self.assertAlmostEqual(original_angle, circle.angle(position))


if __name__ == '__main__':
    unittest.main()
