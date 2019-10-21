import s2sphere
import geojson

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