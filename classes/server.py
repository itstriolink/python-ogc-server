import io
import json

import s2sphere
from fastapi import HTTPException

from classes import index
from classes.tiles import TileKey
from classes.wfs import WFSLink

DEFAULT_LIMIT = 10
MAX_LIMIT = 1000
MAX_SIGNATURE_WIDTH = 8.0


class HTTPResponses:
    NOT_FOUND = HTTPException(status_code=404, detail="Collection not found")
    BAD_REQUEST = HTTPException(status_code=400, detail="Malformed parameters")


class WebServer:
    index: index.Index

    def handle_collections_request(self):
        collections = self.index.get_collections()
        wfs_collections = []

        class WFSCollection:
            name: str
            links: [] = []

            def to_json(self):
                return dict(name=self.name, links=self.links)

        class WFSCollectionResponse:
            links: [] = []
            collections: [] = []

            def to_json(self):
                return dict(links=self.links, collections=self.collections)

        for collection in collections:
            link = WFSLink()
            link.href = self.index.public_path + "collections/" + collection.name
            link.rel = "item"
            link.type = "application/geo+json"
            link.title = collection.name

            wfs_collection = WFSCollection()
            wfs_collection.name = collection.name
            wfs_collection.links.append(link.to_json())

            wfs_collections.append(wfs_collection.to_json())

        self_link = WFSLink()
        self_link.href = self.index.public_path + "collections"
        self_link.rel = "self"
        self_link.type = "application/json"
        self_link.title = "Collections"

        result = WFSCollectionResponse()
        result.collections = wfs_collections
        result.links.append(self_link.to_json())

        content = json.dumps(result.to_json(), separators=(',', ':'))

        return content

    def handle_items_request(self, collection: str, bbox: str, limit: str):
        bbox, http_response = parse_bbox(bbox)

        if http_response is not None:
            return None, http_response

        start_id = ''
        start = 0
        features = io.BytesIO()

        if limit is None:
            limit = DEFAULT_LIMIT
        elif not limit.isdigit():
            return None, HTTPResponses.BAD_REQUEST

        limit = int(limit)

        if limit <= 0:
            limit = 1
        elif not (0 < limit <= MAX_LIMIT):
            return None, HTTPResponses.BAD_REQUEST

        metadata, features, response = self.index.get_items(collection, start_id, start, limit, bbox, features)

        return json_dumps_for_response(features), response

    def handle_tile_request(self, collection: str, zoom: int, x: int, y: int):
        tile, metadata, response = self.index.get_tile(collection, zoom, x, y)
        return tile, metadata, response

    def handle_item_request(self, collection: str, feature_id: str):
        feature, response = self.index.get_item(collection, feature_id)
        return json_dumps_for_response(feature), response

    def handle_tile_feature_info_request(self, collection: str, zoom: int, x: int, y: int, a: int, b: int):
        tile = TileKey(x, y, zoom)

        if a < 0 or a > 256 or b < 0 or b >= 256:
            from classes.server import HTTPResponses
            return None, HTTPResponses.BAD_REQUEST

        tile_bounds = tile.bounds()
        tile_size = tile_bounds.get_size()

        pixel_size = s2sphere.LatLng(lat=tile_size.lat().radians / 256, lng=tile_size.lng().radians / 256)

        center = s2sphere.LatLng(
            lat=s2sphere.Angle(tile_bounds.hi().lat().radians - pixel_size.lat().radians * float(b)).radians,
            lng=s2sphere.Angle(tile_bounds.lo().lng().radians + pixel_size.lng().radians * float(a)).radians)

        bbox_size = s2sphere.LatLng(lat=s2sphere.Angle(pixel_size.lat().radians * MAX_SIGNATURE_WIDTH).radians,
                                    lng=s2sphere.Angle(pixel_size.lng().radians * MAX_SIGNATURE_WIDTH).radians)

        bbox = s2sphere.LatLngRect.from_center_size(center, bbox_size)

        features = io.BytesIO()

        metadata, features, response = self.index.get_items(collection, "", 0, 10, bbox, features)

        return json_dumps_for_response(features), response


def make_web_server(idx: index.Index):
    s = WebServer()
    s.index = idx
    return s


def parse_bbox(s: str):
    bbox = s2sphere.LatLngRect()
    s = str.strip(s)

    if len(s) == 0:
        return bbox

    edges = str.split(s, ",")
    n = []

    for edge in edges:
        try:
            n.append(float(str.strip(edge)))
        except ValueError:
            return None, HTTPResponses.BAD_REQUEST

    if len(n) == 4:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(n[1], n[0]), s2sphere.LatLng.from_degrees(n[3], n[2]))

        if bbox.is_valid:
            return bbox, None

    if len(n) == 6:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(n[1], n[0]), s2sphere.LatLng.from_degrees(n[4], n[3]))

        if bbox.is_valid():
            return bbox, None

    return s2sphere.LatLngRect(), HTTPResponses.BAD_REQUEST


def json_dumps_for_response(data):
    return json.dumps(data,
                      ensure_ascii=False,
                      allow_nan=False,
                      indent=None,
                      separators=(",", ":"),
                      ).encode("utf-8")
