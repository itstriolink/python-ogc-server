from pydantic import BaseModel


class TileKey(BaseModel):
    x: int
    y: int
    zoom: int


class TileCache(BaseModel):
    # locks: mutex
    # lists: list.List
    content: dict()
    size: int
    max_size: int


class TileCacheEntry(BaseModel):
    key: TileKey
    value: bytearray


def new_tile_cache(max_size):
    tile_cache = TileCache()
    tile_cache.max_size = max_size

    return tile_cache


def get_shard(tile_key):
    return tile_key


def get(tile_key):
    shard = get_shard(tile_key)

    return shard


def put(tile_key, value):
    shard = get_shard(tile_key)

    return shard

