import os
import time
from io import FileIO

import geojson
import s2sphere

from tiles import TileCache


class CollectionMetadata:
    name: str
    path: str
    last_modified: time.time()


class Collection:
    metadata: CollectionMetadata
    tile_cache: TileCache
    data_file: FileIO  # not sure yet
    offset: list()
    bbox: list()  # Can't find it yet
    web_mercator: list()
    id: list()
    by_id: dict()


class Index:
    collections: dict()
    public_path: str


def make_index(collections: dict, public_path):
    index = Index()
    index.public_path = public_path

    for name, path in collections.items():
        coll = read_collection(name, path, None)
        index.collections[name] = coll

    return index


def close():
    pass


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
    abs_path, err = os.path.abspath(path)

    stat = os.stat(abs_path)

    with open(abs_path, "r") as file:
        data = file.read()

    coll = Collection()

    coll.metadata.last_modified = stat.st_mtime
    coll.metadata.name = name
    coll.metadata.path = abs_path

    features = geojson.FeatureCollection(data['features'])

    data_file = os.tmpfile("", "miniwfs-*.geojson")

    coll.data_file = data_file

    num_features = len(features)
    coll.bbox = dict(list[s2sphere.LatLngRect], num_features)
    coll.id = dict(list[str], num_features)
    coll.web_mercator = dict(s2sphere.Point, num_features)
    coll.offset = dict()
    coll.by_id = dict()

    for i, f in enumerate(features.Features):
        feature = geojson.geometry.Geometry

    return coll
