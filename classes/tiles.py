from base64 import b64encode
from io import BytesIO

import Geometry
from PIL import Image, ImageDraw

PEN_COLOR = (195, 66, 244)
SIZE = (256, 256)
TRANSPARENT_COLOR = (255, 255, 255, 0)

EMPTY_PNG = bytearray([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
    0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4,
    0x89, 0x00, 0x00, 0x00, 0x0a, 0x49, 0x44, 0x41,
    0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00,
    0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae,
    0x42, 0x60, 0x82
])


class Tile:
    dc: Image.Image()

    def __init__(self):
        self.dc = None

    def draw_point(self, p: Geometry.Point):
        if self.dc is None:
            self.dc = Image.new('RGBA', SIZE, color=TRANSPARENT_COLOR)

        dc = self.dc
        draw = ImageDraw.Draw(dc)
        draw.ellipse((p.x - 2, p.y - 2, p.x + 2, p.y + 2), fill=PEN_COLOR, outline=PEN_COLOR, width=0)

    def to_png(self):
        dc = self.dc
        if dc is not None:
            byteIO = BytesIO()
            dc.save(byteIO, format='PNG')
            byte_value = byteIO.getvalue()
            byteIO.close()

            return byte_value
        else:
            return EMPTY_PNG


class TileKey:
    x: int
    y: int
    zoom: int

    def __init__(self, x, y, zoom):
        self.x = x
        self.y = y
        self.zoom = zoom


class TileCache:
    content: {} = {}
    size: int
    max_size: int


class TileCacheEntry:
    key: TileKey
    value: bytearray


def new_tile_cache(max_size):
    tile_cache = TileCache()
    tile_cache.max_size = max_size

    return tile_cache


def get_shard(tile_key):
    return tile_key


def get(tile_key):
    shard = get_shard(tile_key)

    return shard


def put(tile_key, value):
    shard = get_shard(tile_key)

    return shard


def encode_png(png):
    return b64encode(png)
