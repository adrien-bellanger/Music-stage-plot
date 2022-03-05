import math
import unittest

import sympy

import geometry


class TestCircle(unittest.TestCase):
    def test_intersection(self):
        c1: geometry.Circle = geometry.Circle(sympy.Point(0, 0), 100)
        c2: geometry.Circle = geometry.Circle(sympy.Point(0, 100), math.sqrt(2) * 100)
        p1: sympy.Point = c1.intersections(c2, False)
        p2: sympy.Point = c1.intersections(c2, True)
        self.assertAlmostEqual(0, p1.y, 6)
        self.assertAlmostEqual(-100, p1.x, 6)
        self.assertAlmostEqual(0, p2.y, 6)
        self.assertAlmostEqual(100, p2.x, 6)

    def test_angle(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(center, radius)
        p180: sympy.Point = sympy.Point(center.x - radius, center.y)
        self.assertAlmostEqual(180, circle.angle(p180))
        p0: sympy.Point = sympy.Point(center.x + radius, center.y)
        self.assertAlmostEqual(0, circle.angle(p0))
        p90: sympy.Point = sympy.Point(center.x, center.y + radius)
        self.assertAlmostEqual(90, circle.angle(p90))
        p270: sympy.Point = sympy.Point(center.x, center.y - radius)
        self.assertAlmostEqual(270, circle.angle(p270))

    def test_point(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(center, radius)
        p180: sympy.Point = circle.point(180)
        self.assertAlmostEqual(center.x - radius, p180.x)
        self.assertAlmostEqual(center.y, p180.y)
        p0: sympy.Point = circle.point(0)
        self.assertAlmostEqual(center.x + radius, p0.x)
        self.assertAlmostEqual(center.y, p0.y)
        p90: sympy.Point = circle.point(90)
        self.assertAlmostEqual(center.x, p90.x)
        self.assertAlmostEqual(center.y + radius, p90.y)
        p270: sympy.Point = circle.point(270)
        self.assertAlmostEqual(center.x, p270.x)
        self.assertAlmostEqual(center.y - radius, p270.y)

    def test_point_and_angle(self):
        center: sympy.Point = sympy.Point(10000, 10000)
        radius: float = 5000
        circle: geometry.Circle = geometry.Circle(center, radius)
        original_angle = 195
        point: sympy.Point = circle.point(original_angle)
        self.assertAlmostEqual(original_angle, circle.angle(point), 2)


if __name__ == '__main__':
    unittest.main()
