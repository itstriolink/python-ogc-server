import unittest

import s2sphere
from Geometry import Point

import wfs_server.geometry
import wfs_server.server_handler


class TestGeometry(unittest.TestCase):
    def test_encode_bounding_box(self):
        response = wfs_server.server_handler.parse_bbox("1.4,45.3,8.9,49.2")

        received = wfs_server.geometry.encode_bbox(response.content)
        expected = [1.4, 45.3, 8.9, 49.2]

        self.assertListEqual(received, expected)

    def test_encode_bounding_box_empty(self):
        received = wfs_server.geometry.encode_bbox(s2sphere.LatLngRect())

        self.assertIsNone(received)

    def test_get_tile_bounds(self):
        bounding_box = wfs_server.geometry.encode_bbox(wfs_server.geometry.get_tile_bounds(12, 2148, 1436))
        # TODO

    def test_project_web_mercator(self):
        received = wfs_server.geometry.project_web_mercator(s2sphere.LatLng.from_degrees(41.850, -87.650))
        expected = Point(65.67111111111113, 95.17492654697409)

        delta = received.__sub__(expected)

        # self.assertGreater(math.fabs(delta.x) + math.fabs(delta.y), 1e-9)
