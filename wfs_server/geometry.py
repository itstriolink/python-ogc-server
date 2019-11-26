import math

import Geometry
import geojson
import s2sphere


def compute_bounds(geometry: geojson.geometry.Geometry):
    feature = s2sphere.LatLngRect()

    if geometry is None:
        return feature

    if isinstance(geometry, geojson.geometry.Point):
        if len(geometry['coordinates']) >= 2:
            feature = feature.from_point(s2sphere.LatLng.from_degrees(geometry['coordinates'][1],
                                                                      geometry['coordinates'][0]))
        return feature

    if isinstance(geometry, geojson.geometry.Point):
        for point in geometry['coordinates']:
            if len(point) >= 2:
                feature = feature.from_point(s2sphere.LatLng.from_degrees(point[1], point[0]))
        return feature

    if isinstance(geometry, geojson.geometry.LineString):
        return compute_line_bounds(geometry['coordinates'])

    if isinstance(geometry, geojson.geometry.MultiLineString):
        for line in geometry['coordinates']:
            feature = feature.union((compute_line_bounds(line)))
        return feature

    if isinstance(geometry, geojson.geometry.Polygon):
        for ring in geometry['coordinates']:
            feature = feature.union(compute_line_bounds(ring))

        return feature

    if isinstance(geometry, geojson.geometry.MultiPolygon):
        for poly in geometry['coordinates']:
            for ring in poly:
                feature = feature.union(compute_line_bounds(ring))
        return feature

    if isinstance(geometry, geojson.geometry.GeometryCollection):
        for geometry_object in geometry['Geometries']:
            feature = feature.union(compute_bounds(geometry_object))
        return feature

    return feature


def compute_line_bounds(line):
    rect = s2sphere.LatLngRect()
    for p in line:
        if len(p) >= 2:
            rect = rect.from_point(s2sphere.LatLng.from_degrees(p[1], p[0]))
    return rect


def encode_bbox(rect: s2sphere.LatLngRect):
    if rect.is_empty():
        return None

    rect = [rect.lo().lng().degrees,
            rect.lo().lat().degrees,
            rect.hi().lng().degrees,
            rect.hi().lat().degrees]
    return rect[0:4]


def get_tile_bounds(zoom: int, x: int, y: int):
    return s2sphere.LatLngRect.from_point_pair(unproject_web_mercator(zoom, float(x), float(y)),
                                               unproject_web_mercator(zoom, float(x + 1), float(y + 1)))


def project_web_mercator(p: s2sphere.LatLng):
    siny = math.sin(p.lat().radians)
    siny = min(max(siny, -0.9999), 0.9999)
    x = 256 * (0.5 + p.lng().degrees / 360)
    y = 256 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))

    return Geometry.Point(x=x, y=y)


def unproject_web_mercator(zoom: int, x: float, y: float):
    n = math.pi - 2.0 * math.pi * y / 2 ** (float(zoom))
    lat = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    lng = x / 2 ** (float(zoom)) * 360.0 - 180.0

    return s2sphere.LatLng.from_degrees(lat, lng)
