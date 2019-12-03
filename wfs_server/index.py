import io
import json
import os
from collections import OrderedDict
from datetime import datetime

import geojson
import s2sphere
from Geometry import Point
from apscheduler.schedulers.background import BackgroundScheduler

from wfs_server import tiles, geometry
from wfs_server.data_structures import Collection, CollectionMetadata, WFSLink, APIResponse, HTTP_RESPONSES


class Footer:
    links: []
    bbox: []

    def __init__(self):
        self.bbox = []


class Index:
    collections: {}
    public_path: str

    def __init__(self):
        self.collections = {}

    def get_collection_metadata(self, path: str):
        for coll in self.collections:
            if coll.metadata.path == path:
                return coll.metadata

        return None

    def replace_collection(self, coll: Collection):
        old = self.collections.get(coll.metadata.name)

        if old is not None:
            self.collections[coll.metadata.name] = coll

    def get_collections(self):
        collections = []

        for collection in self.collections.values():
            collections.append(collection.metadata)

        return collections

    def get_collection(self, collection_name: str):
        collection = self.collections.get(collection_name)
        if collection is None:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        return APIResponse(collection.metadata, None)

    def get_items(self,
                  collection: str, limit: int,
                  bbox: s2sphere.LatLngRect, include_links: bool, writer: io.BytesIO):
        if collection not in self.collections:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        coll = self.collections[collection]

        bounds = s2sphere.LatLngRect()
        num_features = 0

        writer.write(bytearray('{"type":"FeatureCollection","features":[', 'utf8'))
        for i, feature_bounds in enumerate(coll.bbox):
            if not bbox.is_empty() and not bbox.intersects(feature_bounds):
                continue

            if num_features >= limit:
                break

            if num_features > 0:
                writer.write(bytearray(',', 'utf8'))

            writer.write(bytearray(coll.feature[i], encoding='utf8'))

            num_features += 1

            bounds = bounds.union(feature_bounds)

        writer.write(bytearray('],', 'utf8'))

        footer = Footer()

        if include_links:
            from wfs_server import server_handler
            public_path = self.public_path

            self_link = WFSLink()
            self_link.href = server_handler.format_items_url(public_path, collection, bbox, limit)
            self_link.rel = "self"
            self_link.title = "self"
            self_link.type = "application/geo+json"

            footer.links = []
            footer.links.append(self_link.to_json())

        footer.bbox = geometry.encode_bbox(bounds)
        encoded_footer = json.dumps(footer.__dict__)

        writer.write(bytearray(encoded_footer[1:], 'utf8'))

        features = geojson.loads(writer.getvalue().decode('utf8'), object_hook=OrderedDict)

        return APIResponse(features, None)

    def get_item(self, collection: str, feature_id: str):
        if collection not in self.collections:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        coll = self.collections[collection]

        if feature_id not in coll.by_id:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        writer = io.BytesIO()
        coll_index = coll.by_id[feature_id]
        writer.write(bytearray(coll.feature[coll_index], encoding='utf8'))

        feature = geojson.loads(writer.getvalue().decode('utf8'))

        return APIResponse(feature, None)

    def get_tile(self, collection: str, zoom: int, x: int, y: int):
        if x < 0 or y < 0 or not 0 < zoom < 30:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        if collection not in self.collections:
            return APIResponse(None, HTTP_RESPONSES["NOT_FOUND"])

        coll = self.collections.get(collection)

        scale = 1 << zoom

        tile_bounds = geometry.get_tile_bounds(zoom, x, y)
        tile_origin = Point(x=(float(x) * 256.0 / float(scale)), y=(float(y) * 256.0 / float(scale)))
        tile = tiles.Tile()

        for index, feature_bounds in enumerate(coll.bbox):
            if not tile_bounds.intersects(feature_bounds):
                continue

            point = coll.web_mercator[index].__sub__(tile_origin).__mul__(float(scale))
            tile.draw_point(point)

        png = tile.to_png()

        return APIResponse(png, None)

    def reload_if_changed(self, collection_metadata: CollectionMetadata):
        response = read_collection(collection_metadata.name, collection_metadata.path,
                                   collection_metadata.last_modified)
        if response.http_response is not None and response.http_response is HTTP_RESPONSES["NOT_MODIFIED"]:
            return None

        self.replace_collection(response.content)

    def watch_files(self):
        for collection in self.get_collections():
            self.reload_if_changed(collection)


def make_index(collections: dict, public_path: str):
    index = Index()
    index.public_path = public_path

    scheduler = BackgroundScheduler()

    scheduler.add_job(index.watch_files, 'interval', minutes=5)
    scheduler.start()

    for name, path in collections.items():
        response = read_collection(name, path, datetime.min)
        index.collections[name] = response.content

    return index


def read_collection(name, path, if_modified_since):
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        return None

    mod_time = datetime.fromtimestamp(os.path.getmtime(abs_path))

    if not mod_time > if_modified_since:
        return APIResponse(None, HTTP_RESPONSES["NOT_MODIFIED"])

    with open(abs_path, "rb") as file:
        feature_collection = geojson.load(file)

    collection = Collection()

    collection.metadata = CollectionMetadata(name, path, mod_time)

    for i, f in enumerate(feature_collection.features):
        collection.id.append(f.id)
        collection.by_id[f.id] = i
        collection.feature.append(geojson.dumps(f, ensure_ascii=False, separators=(',', ':')))

        collection.bbox.append(geometry.compute_bounds(f.geometry))

        center = collection.bbox[i].get_center()
        collection.web_mercator.append(geometry.project_web_mercator(center))
    return APIResponse(collection, None)
