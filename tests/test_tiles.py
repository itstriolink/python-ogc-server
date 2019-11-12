import unittest

from Geometry import Point

import classes.tiles


class TestTiles(unittest.TestCase):

    def test_tile_empty(self):
        tile = classes.tiles.Tile()
        result = tile.to_png()

        self.assertEqual(result, classes.tiles.EMPTY_PNG)

    def test_tile_draw_point(self):
        tile = classes.tiles.Tile()
        tile.draw_point(Point(7.02, 22.95))

        img = tile.to_png()
        # TODO
