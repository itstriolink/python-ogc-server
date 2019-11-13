import io
import os.path
import unittest

import s2sphere

import classes.index


def create_test_index(test: unittest.TestCase):
    collection_castles = os.path.join("test_data", "castles.geojson")
    collection_lakes = os.path.join("test_data", "lakes.geojson")
    public_path = r"https://test.example.org/wfs/"

    index = classes.index.make_index({"castles": collection_castles, "lakes": collection_lakes}, public_path)

    test.assertTrue(index)

    return index


class TestIndex(unittest.TestCase):
    # def test_get_items_empty_bbox(self):
    #    index = create_test_index(self)
    #    items, _, _ = get_items(index, "castles", '', 0, 100, s2sphere.LatLngRect)
    #    # TODO
    pass


def get_items(index: classes.index.Index, collection: str, start_id: str, start_index: int, limit: int,
              bounding_box: s2sphere.LatLngRect):
    writer = io.BytesIO()

    metadata, features, info = index.get_items(collection, start_id, start_index, limit, bounding_box, writer)

    if info is not None:
        return None, None, info

    return metadata, features, None
