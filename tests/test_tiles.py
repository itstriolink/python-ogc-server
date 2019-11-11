import unittest

import classes.tiles


class TestTiles(unittest.TestCase):

    def test_empty_tile(self):
        tile = classes.tiles.Tile()
        result = tile.to_png()

        self.assertEqual(result, classes.tiles.EMPTY_PNG)
