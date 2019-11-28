from Geometry import Point

import wfs_server.tiles


class TestTiles:

    def test_tile_empty(self):
        tile = wfs_server.tiles.Tile()
        result = tile.to_png()

        assert result == wfs_server.tiles.EMPTY_PNG

    def test_tile_draw_point(self):
        tile = wfs_server.tiles.Tile()
        tile.draw_point(Point(7.02, 22.95))
        result = tile.to_png()

        assert result != wfs_server.tiles.EMPTY_PNG
