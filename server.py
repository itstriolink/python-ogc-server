import io

import s2sphere

import index


class WebServer:
    index: index.Index

    def handle_tile_request(self, collection: str, zoom: int, x: int, y: int):
        return self.index.get_tile(collection, zoom, x, y)

    def handle_collection_request(self, collection: str, bbox: str, limit: int = None):
        bbox = parse_bbox(bbox)
        start_id = ''
        start = 0
        features = io.BytesIO()
        if limit is None:
            limit = 10000

        metadata, features = self.index.get_items(collection, start_id, start, limit, bbox, features)
        return features.getvalue()


def make_web_server(idx: index.Index):
    s = WebServer()
    s.index = idx
    return s


def parse_bbox(s: str):
    bbox = s2sphere.LatLngRect()
    s = str.strip(s)

    if len(s) == 0:
        return bbox

    parts = str.split(s, ",")
    n = []

    for part in parts:
        n.append(float(str.strip(part)))

    if len(n) == 4:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(n[1], n[0]), s2sphere.LatLng.from_degrees(n[3], n[2]))

        if bbox.is_valid:
            return bbox

    if len(n) == 6:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(n[1], n[0]), s2sphere.LatLng.from_degrees(n[4], n[3]))

        if bbox.is_valid():
            return bbox

    return s2sphere.LatLngRect()
