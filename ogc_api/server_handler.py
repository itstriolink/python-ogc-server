import io
import json

import s2sphere

from ogc_api import index, geometry
from ogc_api.data_structures import WFSLink, APIResponse, HTTP_RESPONSES
from ogc_api.tiles import TileKey

DEFAULT_LIMIT = 10
MAX_LIMIT = 1000
MAX_SIGNATURE_WIDTH = 8.0


class WebServer:
    index: index.Index

    def handle_collections_request(self, collection: str = None):
        collections = []

        if collection is None:
            collections = self.index.get_collections()
        else:
            response = self.index.get_collection(collection)
            if response.http_response is not None:
                return APIResponse(None, response.http_response)

            collections.append(response.content)

        wfs_collections = []

        class WFSCollection:
            name: str
            title: str
            links: [] = []

            def to_json(self):
                return dict(name=self.name, title=self.title, links=self.links)

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
            wfs_collection.title = collection.name
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

        return APIResponse(content, None)

    def handle_items_request(self, collection: str, bbox: str, limit: str):
        response = parse_bbox(bbox)

        if response.http_response is not None:
            return APIResponse(None, response.http_response)

        features = io.BytesIO()

        if limit is None:
            limit = DEFAULT_LIMIT
        elif not limit.isdigit():
            return APIResponse(None, HTTP_RESPONSES["BAD_REQUEST"])

        limit = int(limit)

        if limit <= 0:
            limit = 1
        elif not (0 < limit <= MAX_LIMIT):
            return APIResponse(None, HTTP_RESPONSES["BAD_REQUEST"])

        include_links = True
        api_response = self.index.get_items(collection, limit, response.content, include_links, features)
        api_response.content = json_dumps_for_response(api_response.content)

        return api_response

    def handle_tile_request(self, collection: str, zoom: int, x: int, y: int):
        api_response = self.index.get_tile(collection, zoom, x, y)
        return api_response

    def handle_item_request(self, collection: str, feature_id: str):
        api_response = self.index.get_item(collection, feature_id)
        api_response.content = json_dumps_for_response(api_response.content)

        return api_response

    def handle_tile_feature_info_request(self, collection: str,
                                         zoom: int, x: int, y: int,
                                         a: int, b: int):
        tile = TileKey(x, y, zoom)

        if a < 0 or a > 256 or b < 0 or b >= 256:
            return APIResponse(None, HTTP_RESPONSES["BAD_REQUEST"])

        tile_bounds = tile.bounds()
        tile_size = tile_bounds.get_size()

        pixel_size = s2sphere.LatLng(lat=tile_size.lat().radians / 256,
                                     lng=tile_size.lng().radians / 256)

        center = s2sphere.LatLng(
            lat=s2sphere.Angle(tile_bounds.hi().lat().radians
                               - pixel_size.lat().radians * float(b)).radians,
            lng=s2sphere.Angle(tile_bounds.lo().lng().radians
                               + pixel_size.lng().radians * float(a)).radians)

        bbox_size = s2sphere.LatLng(lat=s2sphere.Angle(pixel_size.lat().radians
                                                       * MAX_SIGNATURE_WIDTH).radians,
                                    lng=s2sphere.Angle(pixel_size.lng().radians
                                                       * MAX_SIGNATURE_WIDTH).radians)

        bbox = s2sphere.LatLngRect.from_center_size(center, bbox_size)

        features = io.BytesIO()
        include_links = False

        api_response = self.index.get_items(collection, 10, bbox, include_links, features)
        api_response.content = json_dumps_for_response(api_response.content)

        return api_response


def make_web_server(idx: index.Index):
    server = WebServer()
    server.index = idx

    return server


def parse_bbox(bbox_string: str):
    bbox = s2sphere.LatLngRect()
    bbox_string = str.strip(bbox_string)

    if len(bbox_string) == 0:
        return APIResponse(bbox, None)

    edges = str.split(bbox_string, ",")
    float_edges = []

    for edge in edges:
        try:
            float_edges.append(float(str.strip(edge)))
        except ValueError:
            return APIResponse(None, HTTP_RESPONSES["BAD_REQUEST"])

    if len(float_edges) == 4:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(float_edges[1], float_edges[0]),
                                    s2sphere.LatLng.from_degrees(float_edges[3], float_edges[2]))

        if bbox.is_valid:
            return APIResponse(bbox, None)

    if len(float_edges) == 6:
        bbox = bbox.from_point_pair(s2sphere.LatLng.from_degrees(float_edges[1], float_edges[0]),
                                    s2sphere.LatLng.from_degrees(float_edges[4], float_edges[3]))

        if bbox.is_valid():
            return APIResponse(bbox, None)

    return APIResponse(s2sphere.LatLngRect(), HTTP_RESPONSES["BAD_REQUEST"])


def format_items_url(path: str, collection: str, bbox: s2sphere.LatLngRect, limit: int):
    params = []

    if not bbox.is_empty():
        bbox_str = geometry.encode_bbox(bbox)
        bbox_params = str.format("bbox={0},{1},{2},{3}", bbox_str[0], bbox_str[1], bbox_str[2], bbox_str[3])
        params.append(bbox_params)

    if limit != DEFAULT_LIMIT:
        params.append(str.format("limit={0}", str(limit)))

    url = str.format("{0}collections/{1}/items", path, collection)

    if len(params) > 0:
        url += "?" + "&".join(params)

    return url


def json_dumps_for_response(data):
    return json.dumps(data,
                      ensure_ascii=False,
                      allow_nan=False,
                      indent=None,
                      separators=(",", ":"),
                      ).encode("utf-8")
