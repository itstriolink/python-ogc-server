import s2sphere
from Geometry import Point

import wfs_server.geometry
import wfs_server.server_handler


class TestGeometry:
    def test_encode_bounding_box(self):
        response = wfs_server.server_handler.parse_bbox("1.4,45.3,8.9,49.2")

        received = wfs_server.geometry.encode_bbox(response.content)
        expected = [1.4, 45.3, 8.9, 49.2]

        assert received == expected

    def test_encode_bounding_box_empty(self):
        received = wfs_server.geometry.encode_bbox(s2sphere.LatLngRect())

        assert received is None

    def test_get_tile_bounds(self):
        bounding_box = wfs_server.geometry.encode_bbox(wfs_server.geometry.get_tile_bounds(12, 2148, 1436))
        expected_bbox = [8.789062, 47.219568, 8.876953, 47.279229]

        for index, edge in enumerate(bounding_box):
            if not round(edge, 6) == expected_bbox[index]:
                assert False

        assert True

    def test_project_web_mercator(self):
        received = wfs_server.geometry.project_web_mercator(s2sphere.LatLng.from_degrees(41.850, -87.650))
        expected = Point(65.671111111111113, 95.17492654697409)

        delta = received.__sub__(expected)

        # assert math.fabs(delta.x)+math.fabs(delta.y) > 1e-9
