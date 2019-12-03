from Geometry import Point

import ogc_api.tiles


class TestTiles:

    def test_tile_empty(self):
        tile = ogc_api.tiles.Tile()
        result = tile.to_png()

        assert result == ogc_api.tiles.EMPTY_PNG

    def test_tile_draw_point(self):
        tile = ogc_api.tiles.Tile()
        tile.draw_point(Point(7.02, 22.95))
        result = tile.to_png()

        assert result != ogc_api.tiles.EMPTY_PNG
