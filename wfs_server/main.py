import logging
import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, HTMLResponse

from wfs_server.index import make_index
from wfs_server.server_handler import make_web_server

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

COLLECTIONS_ENV = os.environ.get('COLLECTIONS')
PORT_ENV = os.environ.get('PORT')

LOCAL_WEB_URL = "http://127.0.0.1"
DOCKER_WEB_URL = "http://0.0.0.0"

CASTLES_PATH = os.path.join(".", "osm-castles-CH.geojson")
WEB_HOST_URL = str.format('{0}:{1}/', DOCKER_WEB_URL if PORT_ENV else LOCAL_WEB_URL, PORT_ENV if PORT_ENV else '8000')

SHORT_INDEX_MESSAGE = 'This is a MiniWFS server compliant with WFS3, written in Python ' \
                      '<a href=\"https://gitlab.com/labiangashi/python-wfs-server\" ' \
                      'target="_blank" title="Repository">here</a> ' \
                      'that serves GeoJSON objects and PNG raster tiles. <br />'

INDEX_MESSAGE = f'{SHORT_INDEX_MESSAGE}' \
                '<br/>' \
                '<strong>Available API methods: </strong><br/>' \
                '<ol>' \
                '<strong><i>WFS Endpoints: </i></strong><br/>' \
                '<li><i>/collections</i></li>' \
                '<li><i>/collections/{collection_name}</i></li>' \
                '<li><i>/collections/{collection_name}/items?{bbox}{limit} </i></li>' \
                '<li><i>/collections{collection_name}/items/{feature_id}</i></li>' \
                '</ol>' \
                '<ol>' \
                '<strong><i>Other Endpoints: </i></strong><br/>' \
                '<li><i>/tiles/{collection_name}/{zoom}/{x}/{y}.png</i></li>' \
                '<li><i>/tiles/{collection_name}/{zoom}/{x}/{y}/{a}/{b}.geojson</i></li>' \
                '</ol>'


def main():
    collections = {}

    if COLLECTIONS_ENV:
        for collection_object in str.split(COLLECTIONS_ENV, ","):
            value = str.split(collection_object, "=")
            if value is None or len(value) != 2:
                return logging.fatal('Malformed parameters for the --collections argument, '
                                     'pass something like: "COLLECTIONS=castles=path/to/c.geojson,'
                                     'lakes=path/to/l.geojson"')

            collections[value[0]] = value[1]
    else:
        collections['castles'] = CASTLES_PATH

    idx = make_index(collections, WEB_HOST_URL)
    server = make_web_server(idx)

    @app.get("/")
    def index():
        return HTMLResponse(content=INDEX_MESSAGE)

    # region WFS endpoints
    @app.get("/collections")
    def get_collections():
        api_response = server.handle_collections_request()

        return Response(content=api_response.content,
                        headers={
                            "content-type": "application/json",
                            "content-length": str(len(api_response.content))
                        })

    @app.get("/collections/{collection}")
    def get_collection(collection: str):
        api_response = server.handle_collections_request(collection)

        if api_response.http_response is not None:
            return Response(content=None, status_code=api_response.http_response.status_code)

        return Response(content=api_response.content,
                        headers={
                            "content-type": "application/json",
                            "content-length": str(len(api_response.content))
                        })

    @app.get("/collections/{collection}/items")
    def get_collection_items(collection: str, bbox: str = '', limit=None):
        api_response = server.handle_items_request(collection, bbox, limit)

        if api_response.http_response is not None:
            return Response(content=None, status_code=api_response.http_response.status_code)

        return Response(content=api_response.content,
                        headers={
                            "content-type": "application/geo+json",
                            "content-length": str(len(api_response.content))

                        })

    @app.get("/collections/{collection}/items/{feature_id}")
    def get_feature_info(collection: str, feature_id: str):
        api_response = server.handle_item_request(collection, feature_id)

        if api_response.http_response is not None:
            return Response(content=None, status_code=api_response.http_response.status_code)

        return Response(content=api_response.content,
                        headers={
                            "content-type": "application/geo+json",
                            "content-length": str(len(api_response.content))
                        })

    # endregion

    # region Tile endpoints
    @app.get("/tiles/{collection}/{zoom}/{x}/{y}.png")
    def get_raster_tile(collection: str, zoom: int, x: int, y: int):
        api_response = server.handle_tile_request(collection, zoom, x, y)

        if api_response.http_response is not None:
            return Response(content=None, status_code=api_response.http_response.status_code)

        return Response(content=api_response.content,
                        headers={
                            "content-type": "image/png",
                            "content-length": str(len(api_response.content))
                        })

    @app.get("/tiles/{collection}/{zoom}/{x}/{y}/{a}/{b}.geojson")
    def get_tile_feature_info(collection: str, zoom: int, x: int, y: int, a: int, b: int):
        api_response = server.handle_tile_feature_info_request(collection, zoom, x, y, a, b)

        if api_response.http_response is not None:
            return Response(content=None, status_code=api_response.http_response.status_code)

        return Response(content=api_response.content,
                        headers={
                            "content-type": "application/geo+json",
                            "content-length": str(len(api_response.content))
                        })

    # endregion

    @app.get('/{path:path}', include_in_schema=False)
    def raise_404():
        return Response(content=None, status_code=404)


if __name__ == 'wfs_server.main':
    main()
