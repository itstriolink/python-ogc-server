import io
import json
import os

import s2sphere
from fastapi import HTTPException

from classes import index

DEFAULT_LIMIT = 50
MAX_LIMIT = 1000


class HTTPResponses:
    ITEM_NOT_FOUND = HTTPException(status_code=404, detail="Collection not found")
    WRONG_PARAMETER_FORMAT = HTTPException(status_code=400, detail="Malformed parameters")


class WebServer:
    index: index.Index

    def handle_collection_request(self, collection: str, bbox: str, limit: str):
        bbox, http_response = parse_bbox(bbox)

        if http_response is not None:
            return http_response

        start_id = ''
        start = 0
        features = io.BytesIO()

        if limit is None:
            limit = DEFAULT_LIMIT
        elif not limit.isdigit():
            return None, HTTPResponses.WRONG_PARAMETER_FORMAT

        limit = int(limit)

        if limit <= 0:
            limit = 1
        elif not limit > 0 and limit < MAX_LIMIT:
            return None, HTTPResponses.WRONG_PARAMETER_FORMAT
        else:
            limit = int(limit)

        metadata, features, response = self.index.get_items(collection, start_id, start, limit, bbox, features)

        return json.dumps(features,
                          ensure_ascii=False,
                          allow_nan=False,
                          indent=None,
                          separators=(",", ":"),
                          ).encode("utf-8"), response

    def handle_tile_request(self, collection: str, zoom: int, x: int, y: int):
        tile, metadata, response = self.index.get_tile(collection, zoom, x, y)
        return tile, metadata, response

    def handle_feature_request(self, collection: str, feature_id: str):
        feature, response = self.index.get_item(collection, feature_id)
        return json.dumps(feature,
                          ensure_ascii=False,
                          allow_nan=False,
                          indent=None,
                          separators=(",", ":"),
                          ).encode("utf-8"), response

    def exit_handler(self):
        collections = self.index.collections.values()
        for collection in collections:
            file_name = collection.data_file.name
            if os.path.exists(file_name):
                os.remove(file_name)


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
            return bbox, None

    if len(n) == 6:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(n[1], n[0]), s2sphere.LatLng.from_degrees(n[4], n[3]))

        if bbox.is_valid():
            return bbox, None

    return s2sphere.LatLngRect(), HTTPResponses.WRONG_PARAMETER_FORMAT
