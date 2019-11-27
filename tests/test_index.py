import io
import os.path

import s2sphere

import wfs_server.index
from wfs_server.data_structures import HTTP_RESPONSES


def create_test_index():
    collection_castles = os.path.join("tests", "test_data", "castles.geojson")
    collection_lakes = os.path.join("tests", "test_data", "lakes.geojson")

    public_path = r"https://test.example.org/wfs/"
    index = wfs_server.index.make_index({"castles": collection_castles, "lakes": collection_lakes}, public_path)

    return index


class TestIndex:
    def test_get_items_empty_bbox(self):
        index = create_test_index()
        response = get_items(index, "castles", 100, s2sphere.LatLngRect())

        # assert response.content == ""

    def test_get_item_existing_item(self):
        index = create_test_index()
        received = index.get_item("castles", "W418392510")

        assert received.content is not None and received.content.properties["name"] == "Castello Scaligero"

    def test_get_item_no_such_collection(self):
        index = create_test_index()
        received = index.get_item("no-such-collection", "123")

        assert received.http_response is not None and received.http_response == HTTP_RESPONSES["NOT_FOUND"]

    def test_get_item_no_such_item(self):
        index = create_test_index()
        received = index.get_item("castles", "no-such-feature-id")

        assert received.http_response is not None and received.http_response == HTTP_RESPONSES["NOT_FOUND"]


def get_items(index: wfs_server.index.Index, collection: str, limit: int,
              bounding_box: s2sphere.LatLngRect):
    writer = io.BytesIO()

    response = index.get_items(collection, limit, bounding_box, writer)

    return response
