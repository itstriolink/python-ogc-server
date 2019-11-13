import unittest

import s2sphere
from Geometry import Point

import classes.geometry
import classes.server


class TestGeometry(unittest.TestCase):
    def test_encode_bounding_box(self):
        bounding_box, response = classes.server.parse_bbox("1.4,45.3,8.9,49.2")

        received = classes.geometry.encode_bbox(bounding_box)
        expected = [1.4, 45.3, 8.9, 49.2]

        self.assertListEqual(received, expected)

    def test_encode_bounding_box_empty(self):
        received = classes.geometry.encode_bbox(s2sphere.LatLngRect())

        self.assertIsNone(received)

    def test_get_tile_bounds(self):
        bounding_box = classes.geometry.encode_bbox(classes.geometry.get_tile_bounds(12, 2148, 1436))
        # TODO

    def test_project_web_mercator(self):
        received = classes.geometry.project_web_mercator(s2sphere.LatLng.from_degrees(41.850, -87.650))
        expected = Point(65.67111111111113, 95.17492654697409)

        delta = received.__sub__(expected)

        # self.assertGreater(math.fabs(delta.x) + math.fabs(delta.y), 1e-9)
