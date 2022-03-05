import math
import unittest

import geometry


class TestCircle(unittest.TestCase):
    def test_something(self):
        c1: geometry.Circle = geometry.Circle(geometry.Position.from_xy(0, 0), 100)
        c2: geometry.Circle = geometry.Circle(geometry.Position.from_xy(0, 100), math.sqrt(2) * 100)
        p1: geometry.Position = c1.intersections(c2, False)
        p2: geometry.Position = c1.intersections(c2, True)
        self.assertAlmostEqual(0, p1.point.y, 6)
        self.assertAlmostEqual(100, p1.point.x, 6)
        self.assertAlmostEqual(0, p2.point.y, 6)
        self.assertAlmostEqual(-100, p2.point.x, 6)


if __name__ == '__main__':
    unittest.main()
