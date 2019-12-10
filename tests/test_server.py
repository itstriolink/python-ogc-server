from starlette.testclient import TestClient

from ogc_api import tiles
from ogc_api.main import app

client = TestClient(app)


class TestServer:
    def test_home(self):
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.content.decode('utf8').find("title") > 0 \
               and response.content.decode('utf8').find("links") > 0

    def test_list_collections(self):
        response = client.get("/collections")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_collection_items(self):
        response = client.get("/collections/castles/items?bbox=11.183467,47.910413,11.183469,47.910415")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert response.content.decode('utf8').find("FeatureCollection") \
               and response.content.decode('utf8').find("bbox") >= 0

    def test_collection_not_found(self):
        response = client.get("/collections/no-such-collection/items?bbox=11.183467,47.910413,11.183469,47.910415")

        assert response.status_code == 404
        assert response.content.decode('utf8') is None \
               or response.content.decode('utf8') == ""

    def test_collection_feature(self):
        response = client.get("/collections/castles/items/N3256406527")

        assert response.status_code == 200
        assert response.content.decode('utf8').find("N3256406527") > 0

    def test_collection_feature_not_found(self):
        response = client.get("/collections/castles/items/no-such-feature")

        assert response.status_code == 404
        assert response.content.decode('utf8') is None \
               or response.content.decode('utf8') == ""

    def test_collection_feature_collection_not_found(self):
        response = client.get("/collections/no-such-collection/items/N3256406527")

        assert response.status_code == 404
        assert response.content.decode('utf8') is None \
               or response.content.decode('utf8') == ""

    def test_tile_feature_info(self):
        response = client.get("/tiles/castles/9/266/180/137/209.geojson")

        assert response.status_code == 200
        assert response.content.decode('utf8').find("W387544802") > 0

    def test_tile_feature_info_no_such_feature(self):
        response = client.get("/collections/castles/17/69585/46595/10/5.geojson")

        assert response.status_code == 404
        assert response.content.decode('utf8') is None \
               or response.content.decode('utf8') == ""

    def test_tile_feature_info_no_such_collection(self):
        response = client.get("/tiles/no-such-collection/9/266/180/137/209.geojson")

        assert response.status_code == 404
        assert response.content.decode('utf8') is None \
               or response.content.decode('utf8') == ""

    def test_collection_items_bad_request(self):
        response = client.get("/collections/castles/items?limit=1001")
        response_2 = client.get("/collections/castles/items?bbox=weird-string")

        assert response.status_code == 400 and response_2.status_code == 400
        assert (response.content.decode('utf8') is None or response.content.decode('utf8') == "") \
               and (response_2.content.decode('utf8') is None or response_2.content.decode('utf8') == "")

    def test_empty_raster_tile(self):
        response = client.get("tiles/castles/1/1/1.png")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content == tiles.EMPTY_PNG

    def test_not_empty_raster_tile(self):
        response = client.get("tiles/castles/9/268/179.png")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content != tiles.EMPTY_PNG
