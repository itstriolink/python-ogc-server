import io
import os.path

import s2sphere

import wfs_server.index
from wfs_server.data_structures import APIResponse


def create_test_index():
    collection_castles = os.path.join("test_data", "castles.geojson")
    collection_lakes = os.path.join("test_data", "lakes.geojson")
    public_path = r"https://test.example.org/wfs/"

    index = wfs_server.index.make_index({"castles": collection_castles, "lakes": collection_lakes}, public_path)

    return index


class TestIndex():
    # def test_get_items_empty_bbox(self):
    #    index = create_test_index(self)
    #    items, _, _ = get_items(index, "castles", '', 0, 100, s2sphere.LatLngRect)
    #    TODO
    pass


def get_items(index: wfs_server.index.Index, collection: str, start_id: str, start_index: int, limit: int,
              bounding_box: s2sphere.LatLngRect):
    writer = io.BytesIO()

    response = index.get_items(collection, start_id, start_index, limit, bounding_box, writer)

    if response.http_response is not None:
        return APIResponse(None, response.http_response)

    return APIResponse(response.content, response.http_response)
