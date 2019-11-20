import io
import json
import os

import s2sphere
from fastapi import HTTPException

from classes import index
from classes.tiles import TileKey
from classes.wfs import WFSLink

DEFAULT_LIMIT = 10
MAX_LIMIT = 1000


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
        feature, response = self.index.get_tile_feature_info(collection, tile, a, b)

        return json_dumps_for_response(feature), response

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
