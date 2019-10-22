import io
import os
import tempfile
import time
from datetime import datetime

import geojson

import geometry
from tiles import TileCache


class CollectionMetadata:
    name: str
    path: str
    last_modified: str


class Collection:
    metadata: CollectionMetadata
    tile_cache: TileCache
    data_file: io.FileIO  # not sure yet
    offset: [] = []
    bbox: [] = []  # Can't find it yet
    web_mercator: [] = []
    id: [] = []
    by_id: {} = {}


class Index:
    collections: {} = {}
    public_path: str


def make_index(collections: dict, public_path):
    index = Index()
    index.public_path = public_path

    for name, path in collections.items():
        coll = read_collection(name, path, None)
        index.collections[name] = coll

    return index


def close(c: Collection):
    if c.data_file is not None:
        c.data_file.close()
        os.remove(c.data_file.name)


def get_collections(index):
    collection_metadata = CollectionMetadata()
    collection_metadata.name = "CM"
    collection_metadata.path = "CMP"
    collection_metadata.last_modified = time.strftime()

    return collection_metadata


def get_item(collection, collection_id):
    result = None
    return result


def get_tile(collection, zoom, x, y):
    return None


def get_collection_metadata(path):
    return None


def read_collection(name, path, if_modified_since):
    abs_path = os.path.abspath(path)

    mod_time = datetime.fromtimestamp(os.path.getmtime(path))

    with open(abs_path, "r", encoding='utf8') as file:
        data = file.read()

    coll = Collection()
    coll_metadata = CollectionMetadata()

    coll_metadata.last_modified = mod_time
    coll_metadata.name = name
    coll_metadata.path = path

    coll.metadata = coll_metadata
    feature_collection = geojson.FeatureCollection(geojson.loads(data))

    data_file = tempfile.NamedTemporaryFile(prefix="miniwfs-", suffix=".geojson")

    coll.data_file = data_file

    num_features = len(feature_collection.features)
    # coll.bbox = dict(list[s2sphere.LatLngRect], num_features)
    # coll.id = dict(list[str], num_features)
    # coll.web_mercator = dict(s2sphere.Point, num_features)
    # coll.offset = dict()
    # coll.by_id = dict()

    for i, f in enumerate(feature_collection.features):
        coll.id.append(f.id)
        coll.by_id[f.id] = i
        coll.bbox.append(geometry.compute_bounds(f.geometry))

        center = coll.bbox[i].get_center()
        coll.web_mercator.append(geometry.project_web_mercator(center))

        # if i > 0:
        #     data_file.write()
    return coll

