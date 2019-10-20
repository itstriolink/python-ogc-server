import time
from tiles import TileCache
from os import tmpfile
import geojson
from pydantic import BaseModel


class CollectionMetadata(BaseModel):
    name: str
    path: str
    last_modified: time.time()


class Collection(BaseModel):
    metadata: CollectionMetadata
    tile_cache: TileCache
    data_file: tmpfile()  # not sure yet
    offset: list[int]
    bbox: list[geojson.Rect]  # Can't find it yet
    web_mercator: list[geojson.Point]
    id: list[str]
    by_id: dict()


class Index(BaseModel):
    collections: Collection
    public_path: str


def make_index(collections, public_path):
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
