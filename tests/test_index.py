import io
import os.path

import s2sphere

import ogc_api.index
from ogc_api.data_structures import HTTP_RESPONSES


def create_test_index():
    collection_castles = os.path.join("tests", "test_data", "castles.geojson")
    collection_lakes = os.path.join("tests", "test_data", "lakes.geojson")

    public_path = r"https://test.example.org/wfs/"
    index = ogc_api.index.make_index({"castles": collection_castles, "lakes": collection_lakes}, public_path)

    return index


class TestIndex:
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


def get_items(index: ogc_api.index.Index, collection: str, limit: int,
              bounding_box: s2sphere.LatLngRect):
    writer = io.BytesIO()

    include_links = True
    response = index.get_items(collection, "", 0, limit, bounding_box, include_links, writer)

    return response
