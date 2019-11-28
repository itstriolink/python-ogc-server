from starlette.testclient import TestClient

from wfs_server.main import WEB_HOST_URL
from wfs_server.main import app

client = TestClient(app)


class TestServer:
    def test_home(self):
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

    def test_list_collections(self):
        response = client.get("/collections")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json() == {"links": [
            {"href": str.format("{0}collections", WEB_HOST_URL), "rel": "self", "type": "application/json",
             "title": "Collections"}], "collections": [{"name": "castles", "links": [
            {"href": str.format("{0}collections/castles", WEB_HOST_URL), "rel": "item", "type": "application/geo+json",
             "title": "castles"}]}]}

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
        assert response.content.decode('utf8') == '{"type":"Feature","id":"N3256406527","geometry":{"type":"Point",' \
                                                  '"coordinates":[9.021746,46.192902]},"properties":{' \
                                                  '"castle_type":"defensive","heritage":"1",' \
                                                  '"heritage:operator":"whc","historic":"castle",' \
                                                  '"historic:civilization":"medieval","name":"Castelgrande",' \
                                                  '"name:ru":"Кастельгранде","ref:whc":"884-001",' \
                                                  '"tourism":"attraction","whc:inscription_date":"2000",' \
                                                  '"wikidata":"Q664376","wikipedia":"it:Castelgrande (castello)"}}'

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
        response = client.get("tiles/castles/9/266/180/137/209.geojson")

        assert response.status_code == 200
        assert response.content.decode('utf8') == '{"type":"FeatureCollection","bbox":[7.406668,46.649168,7.406668,' \
                                                  '46.649168],"features":[{"type":"Feature","id":"W387544802",' \
                                                  '"geometry":{"type":"Polygon","coordinates":[[[7.406668,46.649168],' \
                                                  '[7.406333,46.649],[7.406405,46.648945],[7.406735,46.649107],' \
                                                  '[7.406668,46.649168]]]},"properties":{"historic":"castle",' \
                                                  '"name":"Festi","wikidata":"Q67772651"}}]}'

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

    def test_raster_tile(self):
        response = client.get("tiles/castles/9/268/179.png")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
