import time
import geojson
import s2sphere
from tiles import TileCache
import os
import io
from pydantic import BaseModel


class CollectionMetadata(BaseModel):
    name: str
    path: str
    last_modified: time.time()


class Collection(BaseModel):
    metadata: CollectionMetadata
    tile_cache: TileCache
    data_file: io.FileIO  # not sure yet
    offset: list[int]
    bbox: list[s2sphere.LatLngRect]  # Can't find it yet
    web_mercator: list[s2sphere.Point]
    id: list[str]
    by_id: dict()


class Index(BaseModel):
    collections: Collection
    public_path: str


def make_index(collections: dict, public_path):
    index = Index(collections=dict[str, Collection], public_path=public_path)
    pass


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

    features = geojson.FeatureCollection

    features = geojson.loads(data)

    data_file = os.tmpfile("", "miniwfs-*.geojson")

    coll.data_file = data_file

    num_features = len(features.items())
    coll.bbox = dict(list[s2sphere.LatLngRect], num_features)
    coll.id = dict(list[str], num_features)
    coll.web_mercator = dict(s2sphere.Point, num_features)
    coll.offset = dict()
    coll.by_id = dict()
