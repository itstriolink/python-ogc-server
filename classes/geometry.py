import math

import Geometry
import geojson
import s2sphere
from numpy import exp2


def compute_bounds(g: geojson.geometry.Geometry):
    r = s2sphere.LatLngRect()
    if g is None:
        return r

    if type(g) == geojson.geometry.Point:
        if len(g['coordinates']) >= 2:
            r = r.from_point(s2sphere.LatLng.from_degrees(g['coordinates'][1], g['coordinates'][0]))
        return r

    elif type(g) == geojson.geometry.MultiPoint:
        for p in g['coordinates']:
            if len(p) >= 2:
                r = r.from_point(s2sphere.LatLng.from_degrees(p[1], p[0]))
        return r

    elif type(g) == geojson.geometry.LineString:
        return compute_line_bounds(g['coordinates'])

    elif type(g) == geojson.geometry.MultiLineString:
        for line in g['coordinates']:
            r = r.union((compute_line_bounds(line)))
        return r

    elif type(g) == geojson.geometry.Polygon:
        for ring in g['coordinates']:
            r = r.union(compute_line_bounds(ring))
        # s2sphere.exp
        return r

    elif type(g) == geojson.geometry.MultiPolygon:
        for poly in g['coordinates']:
            for ring in poly:
                r = r.union(compute_line_bounds(ring))
        return r

    elif type(g) == geojson.geometry.GeometryCollection:
        for geometry in g.Geometries:
            r = r.union(compute_bounds(geometry))
        return r

    else:
        return r


def compute_line_bounds(line):
    r = s2sphere.LatLngRect()
    for p in line:
        if len(p) >= 2:
            r = r.from_point(s2sphere.LatLng.from_degrees(p[1], p[0]))
    return r


def encode_bbox(r: s2sphere.LatLngRect):
    if r.is_empty():
        return None
    else:
        bbox = [r.lo().lng().degrees,
                r.lo().lat().degrees,
                r.hi().lng().degrees,
                r.hi().lat().degrees]
        return bbox[0:4]


def get_tile_bounds(zoom: int, x: int, y: int):
    return s2sphere.LatLngRect(unproject_web_mercator(zoom, float(x + 1), float(y + 1)),
                               unproject_web_mercator(zoom, float(x), float(y)))


def project_web_mercator(p: s2sphere.LatLng):
    siny = math.sin(p.lat().radians)
    siny = min(max(siny, -0.9999), 0.9999)
    x = 256 * (0.5 + p.lng().degrees / 360)
    y = 256 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))

    return Geometry.Point(x=x, y=y)


def unproject_web_mercator(zoom: int, x: float, y: float):
    n = math.pi - 2.0 * math.pi * y / exp2(float(zoom))
    lat = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    lng = x / math.exp(float(zoom)) * 360.0 - 180.0

    return s2sphere.LatLng.from_degrees(lat, lng)
