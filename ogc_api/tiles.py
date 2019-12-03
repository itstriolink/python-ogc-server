from io import BytesIO

import Geometry
import s2sphere
from PIL import Image, ImageDraw

from ogc_api.geometry import unproject_web_mercator

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
    image: Image.Image()

    def __init__(self):
        self.image = None

    def draw_point(self, point: Geometry.Point):
        if self.image is None:
            self.image = Image.new('RGBA', SIZE, color=TRANSPARENT_COLOR)

        image = self.image
        draw = ImageDraw.Draw(image)
        draw.ellipse((point.x - 2, point.y - 2, point.x + 2, point.y + 2), fill=PEN_COLOR, outline=PEN_COLOR, width=0)

    def to_png(self):
        image = self.image
        byte_io = BytesIO()

        if image is not None:
            image.save(byte_io, format='PNG')
            byte_value = byte_io.getvalue()
            byte_io.close()

            return byte_value

        byte_io.write(EMPTY_PNG)
        byte_value = byte_io.getvalue()
        byte_io.close()

        return byte_value


class TileKey:
    x: int
    y: int
    zoom: int

    def __init__(self, x, y, zoom):
        self.x = x
        self.y = y
        self.zoom = zoom

    def bounds(self):
        return s2sphere.LatLngRect.from_point_pair(unproject_web_mercator(self.zoom, float(self.x), float(self.y)),
                                                   unproject_web_mercator(self.zoom, float(self.x + 1),
                                                                          float(self.y + 1)))
