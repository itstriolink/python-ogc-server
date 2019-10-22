import io
import os
import tempfile
from datetime import datetime

import geojson
import s2sphere

import geometry
import tiles


class CollectionMetadata:
    name: str
    path: str
    last_modified: str

    def __init__(self, name, path, last_modified):
        self.name = name
        self.path = path
        self.last_modified = last_modified


class Collection:
    metadata: CollectionMetadata
    tile_cache: tiles.TileCache
    data_file: io.FileIO  # not sure yet
    offset: [] = []
    bbox: [] = []  # Can't find it yet
    web_mercator: [] = []
    id: [] = []
    by_id: {} = {}

    def close(self):
        if self.data_file is not None:
            self.data_file.close()
            os.remove(self.data_file.name)


class Index:
    collections: {} = {}
    public_path: str

    def get_collection_metadata(self, path: str):
        for coll in self.collections:
            if coll.metadata.path == path:
                return coll.metadata

        return None

    def replace_collection(self, coll: Collection):
        old = self.collections.get(coll.metadata.name)

        if old is not None:
            old.close()

        self.collections[coll.metadata.name] = coll

    def get_tile(self, collection: str, zoom: int, x: int, y: int):
        if x < 0 or y < 0 or zoom < 0 or zoom > 30:
            return None

        tile_key = tiles.TileKey(x=x, y=y, zoom=zoom)

        coll = self.collections.get(collection)

        if coll is None:
            return None

        scale = 1 << zoom

        tile_bounds = geometry.get_tile_bounds(zoom, x, y)
        tile_origin = s2sphere.Point(x=float(x) * 256.0 / float(scale), y=float(y) * 256.0 / float(scale))

        # tile = Tile


def make_index(collections: dict, public_path):
    index = Index()
    index.public_path = public_path

    for name, path in collections.items():
        coll = read_collection(name, path, None)
        index.collections[name] = coll

    return index


def get_collections():
    pass


def get_item(collection_name: str, collection_id: str):
    coll = Index.collections[collection_name]
    if coll is None:
        return None

    i = coll.by_id[collection_id]
    offset = coll.offset[i]

    result = geojson.Feature

    return result


def get_tile(collection, zoom, x, y):
    return None


def read_collection(name, path, if_modified_since):
    abs_path = os.path.abspath(path)

    mod_time = datetime.fromtimestamp(os.path.getmtime(path))

    with open(abs_path, "r", encoding='utf8') as file:
        data = file.read()

    coll = Collection()
    coll.tile_cache = tiles.new_tile_cache(10000)
    coll.metadata = CollectionMetadata(name, path, mod_time)

    feature_collection = geojson.FeatureCollection(geojson.loads(data))

    data_file = tempfile.NamedTemporaryFile(prefix="miniwfs-", suffix=".geojson")

    coll.data_file = data_file

    num_features = len(feature_collection.features)

    for i, f in enumerate(feature_collection.features):
        coll.id.append(f.id)
        coll.by_id[f.id] = i
        coll.bbox.append(geometry.compute_bounds(f.geometry))

        center = coll.bbox[i].get_center()
        coll.web_mercator.append(geometry.project_web_mercator(center))

        # if i > 0:
        #     data_file.write()
    return coll

