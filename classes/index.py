import io
import json
import os
import tempfile
from datetime import datetime

import geojson
import s2sphere
from Geometry import Point

from classes import wfs, tiles, geometry


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
    data_file: io.FileIO
    offset: [] = []
    bbox: [] = []
    web_mercator: [] = []
    id: [] = []
    by_id: {} = {}

    def close(self):
        if self.data_file is not None:
            self.data_file.close()
            os.remove(self.data_file.name)


class Footer:
    links: [] = []
    bbox: [] = []


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

    def get_collections(self):
        pass

    def get_items(self,
                  collection: str, start_id: str, start: int, limit: int,
                  bbox: s2sphere.LatLngRect, writer: io.BytesIO):
        if collection not in self.collections:
            return None, None, f"The collection type \"{collection}\" does not exist"

        coll = self.collections[collection]

        bounds = s2sphere.LatLngRect()
        skip = start
        num_features = 0

        writer.write(bytearray('{"type":"FeatureCollection","features":[', 'utf8'))

        buffer = bytearray(50 * 1024)
        for i, feature_bounds in enumerate(coll.bbox):
            if not bbox.intersects(feature_bounds):
                continue

            if num_features >= limit:
                next_id = coll.id[i]
                next_index = i
                break

            if skip > 0:
                skip = skip - 1
                break

            if num_features > 0:
                writer.write(bytearray(',', 'utf8'))

            b = buffer

            json_len = int(coll.offset[i + 1] - coll.offset[i] - 2)

            if json_len > len(b):
                b = bytearray(json_len)

            with open(coll.data_file.name, 'rb') as f:
                f.seek(coll.offset[i])
                writer.write(f.read(len(b[0:json_len])))

            # writer.write(b[0:json_len])

            num_features += 1

            bounds = bounds.union(feature_bounds)

        writer.write(bytearray('],', 'utf8'))

        footer = Footer()

        self_link = wfs.WFSLink()
        self_link.rel = "self"
        self_link.title = "self"
        self_link.type = "application/geo+json"

        footer.bbox = geometry.encode_bbox(bounds)
        encoded_footer = json.dumps(footer.__dict__)

        writer.write(bytearray(encoded_footer[1:], 'utf8'))

        features = geojson.loads(writer.getvalue().decode('utf8'))

        return coll.metadata, features, None

    def get_item(self, collection: str, feature_id: str):
        if collection not in self.collections:
            return f"The collection type \"{collection}\" does not exist"

        coll = self.collections[collection]

        if feature_id not in coll.by_id:
            return f"This feature does not exist in the {collection} collection"

        i = coll.by_id[feature_id]
        offset = coll.offset[i]

        json_len = int(coll.offset[i + 1] - offset - 2)
        writer = io.BytesIO()
        b = bytearray(json_len)

        with open(coll.data_file.name, 'rb') as f:
            f.seek(coll.offset[i])
            writer.write(f.read(len(b[0:json_len])))

        feature = geojson.loads(writer.getvalue().decode('utf8'))

        return feature

    def get_tile(self, collection: str, zoom: int, x: int, y: int):
        if x < 0 or y < 0 or zoom < 0 or zoom > 30:
            return "Wrong parameters in the x, y, z", CollectionMetadata()

        tile_key = tiles.TileKey(x=x, y=y, zoom=zoom)
        if collection not in self.collections:
            return f"The collection type \"{collection}\" does not exist", CollectionMetadata()

        coll = self.collections.get(collection)

        scale = 1 << zoom

        tile_bounds = geometry.get_tile_bounds(zoom, x, y)
        tile_origin = Point(x=(float(x) * 256.0 / float(scale)), y=(float(y) * 256.0 / float(scale)))
        tile = tiles.Tile()

        for i, feature_bounds in enumerate(coll.bbox):
            if not tile_bounds.intersects(feature_bounds):
                continue

            p = coll.web_mercator[i].__sub__(tile_origin).__mul__(float(scale))
            tile.draw_point(p)

        png = tile.to_png()

        return png, coll.metadata


def make_index(collections: dict, public_path: str):
    index = Index()
    index.public_path = public_path

    for name, path in collections.items():
        coll = read_collection(name, path, None)
        index.collections[name] = coll

    # TODO
    return index


def read_collection(name, path, if_modified_since):
    abs_path = os.path.abspath(path)

    mod_time = datetime.fromtimestamp(os.path.getmtime(path))

    if not os.path.exists(abs_path):
        return None

    with open(abs_path, "rb") as file:
        feature_collection = geojson.load(file)

    coll = Collection()
    coll.tile_cache = tiles.new_tile_cache(10000)
    coll.metadata = CollectionMetadata(name, path, mod_time)

    file = tempfile.NamedTemporaryFile(prefix="wfs-", suffix=".geojson", mode="wb", delete=False)

    coll.data_file = file

    header_size = file.write(bytearray('{"type":"FeatureCollection","features":[\n', 'utf8'))

    pos = int(header_size)
    num_features = len(feature_collection.features)

    for i, f in enumerate(feature_collection.features):
        coll.id.append(f.id)
        coll.by_id[f.id] = i

        coll.bbox.append(geometry.compute_bounds(f.geometry))

        center = coll.bbox[i].get_center()
        coll.web_mercator.append(geometry.project_web_mercator(center))

        if i > 0:
            file.write(bytearray(',\n', 'utf8'))
            pos += 2

        coll.offset.append(pos)

        encoded = geojson.dumps(f, ensure_ascii=False, separators=(',', ':'))
        encoded_bytes = file.write(bytearray(encoded, 'utf8'))

        pos = pos + int(encoded_bytes)

    coll.offset[len(coll.offset) - 1] = pos + 2

    file.write(bytearray("\n]}\n", 'utf8'))
    file.close()

    return coll
