import s2sphere
import geojson
import math


def compute_bounds(g: geojson.geometry.Geometry):
    r = s2sphere.LatLngRect()
    if g is None:
        return r

    if g.Type == geojson.geometry.Point:
        if len(g.Point) >= 2:
            r = r.from_point(s2sphere.LatLng(g.Point[1], g.Point[0]))
        return r

    elif g.Type == geojson.geometry.MultiPoint:
        for p in g.MultiPoint:
            if len(p) >= 2:
                r = r.from_point(s2sphere.LatLng(p[1], p[0]))
        return r

    elif g.Type == geojson.geometry.LineString:
        return compute_line_bounds(g.LineString)

    elif g.Type == geojson.geometry.MultiLineString:
        for line in g.MultiLineString:
            r = r.union((compute_line_bounds(line)))
        return r

    elif g.Type == geojson.geometry.Polygon:
        for ring in g.Polygon:
            r = r.union(compute_line_bounds(ring))
        # s2sphere.expandforsubregions(r)
        return r

    elif g.Type == geojson.geometry.MultiPolygon:
        for poly in g.MultiPolygon:
            for ring in poly:
                r = r.union(compute_line_bounds(ring))
            # s2sphere.expandforsubregions(r)
        return r

    elif g.Type == geojson.geometry.GeometryCollection:
        for geometry in g.Geometries:
            r = r.union(compute_bounds(geometry))
        return r

    else:
        return r


def compute_line_bounds(line):
    r = s2sphere.LatLngRect()
    for p in line:
        if len(p) >= 2:
            r = r.from_point(s2sphere.LatLng(p[1], p[0]))
    return r


def encode_bbox(r: s2sphere.LatLngRect):
    if r.is_empty():
        return None
    else:
        bbox = list[r.lo().lng().degrees(),
                    r.lo().lat().degrees(),
                    r.hi().lng().degrees(),
                    r.hi().lat().degrees()]
        return bbox


def get_tile_bounds(zoom: int, x: int, y: int):
    r = s2sphere.LatLngRect(unproject_web_mercator(zoom, float(x), float(y)))
    return r.from_point(unproject_web_mercator((zoom, float(x+1), float(y+1))))


def project_web_mercator(p: s2sphere.LatLng):
    siny = math.sin(p.lat().radians())
    siny = min(max(siny, -0.9999), 0.9999)
    x = 256 * (0.5 + p.lng().degrees() / 360)
    y = 256 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))

    return s2sphere.Point(x=x, y=y)


def unproject_web_mercator(zoom: int, x: float, y: float):
    n = math.pi - 2.0 * math.pi * y / math.exp(float(zoom))
    lat = 100.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    lng = x / math.exp(float(zoom)) * 360.0 - 180.0

    return s2sphere.LatLng(lat, lng)
