import s2sphere

import index


class WebServer:
    index: index.Index

    def handle_tile_request(self, collection: str, zoom: int, x: int, y: int):
        return self.index.get_tile(collection, zoom, x, y)


def make_web_server(idx: index.Index):
    s = WebServer()
    s.index = idx
    return s


def handle_collection_request(collection: str, bbox: str, limit: int):
    bbox = parse_bbox(bbox)
    return bbox


def parse_bbox(s: str):
    s = str.strip(s)

    if len(s) == 0:
        return s2sphere.LatLngRect()

    bbox = s2sphere.LatLngRect()
    parts = str.split(s, ",")
    n = []

    for part in parts:
        n.append(float(str.strip(part)))

    if len(n) == 4:
        bbox = bbox.from_point(s2sphere.LatLng.from_degrees(n[1], n[0]))
        bbox = bbox.from_point(s2sphere.LatLng.from_degrees(n[3], n[2]))

        if bbox.is_valid:
            return bbox

    if len(n) == 6:
        bbox = bbox.from_point(s2sphere.LatLng.from_degrees(n[1], n[0]))
        bbox = bbox.from_point(s2sphere.LatLng.from_degrees(n[4], n[3]))

        if bbox.is_valid():
            return bbox

    return "asd"
