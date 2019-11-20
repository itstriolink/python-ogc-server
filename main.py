from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, HTMLResponse

from classes.index import make_index
from classes.server import make_web_server

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

CASTLES_PATH = r'.\osm-castles-CH.geojson'
WEB_HOST_URL = r'http://127.0.0.1:8000/'

SHORT_INDEX_MESSAGE = 'This is a MiniWFS server compliant with WFS3, written in Python ' \
                      '<a href=\"https://gitlab.com/labiangashi/python-wfs-server\" ' \
                      'target="_blank" title="Repository">here</a> ' \
                      'that serves GeoJSON objects and PNG raster tiles. <br />'

INDEX_MESSAGE = f'{SHORT_INDEX_MESSAGE}' \
                '<br/>' \
                '<strong>Available API methods: </strong>' \
                '<ol>' \
                '<li><i>/collections</i></li>' \
                '<li><i>/collections/{collection_name}/items?{bbox}{limit} </i></li>' \
                '<li><i>/collections{collection_name}/items/{feature_id}</i></li>' \
                '<li><i>/tiles/{collection_name}/{zoom}/{x}/{y}.png</i></li>' \
                '</ol>'


def main():
    try:
        coll = {'castles': CASTLES_PATH}

        idx = make_index(coll, WEB_HOST_URL)
        server = make_web_server(idx)

        @app.get("/")
        def index():
            return HTMLResponse(content=INDEX_MESSAGE)

        @app.get("/collections")
        def get_collections():
            content = server.handle_collections_request()

            return Response(content=content,
                            headers={
                                "content-type": "application/json",
                                "content-length": str(len(content))
                            })

        @app.get("/collections/{collection}/items")
        def get_collection_items(collection: str, bbox: str, limit=None):
            content, http_response = server.handle_items_request(collection, bbox, limit)

            if http_response is not None:
                return Response(content=None, status_code=http_response.status_code)
            else:
                return Response(content=content,
                                headers={
                                    "content-type": "application/geo+json",
                                    "content-length": str(len(content))
                                })

        @app.get("/tiles/{collection}/{zoom}/{x}/{y}.png")
        def get_raster_tile(collection: str, zoom: int, x: int, y: int):
            content, metadata, http_response = server.handle_tile_request(collection, zoom, x, y)

            if http_response is not None:
                return Response(content=None, status_code=http_response.status_code)
            else:
                return Response(content=content,
                                headers={
                                    "content-type": "image/png",
                                    "content-length": str(len(content))
                                })

        @app.get("/collections/{collection}/items/{feature_id}")
        def get_feature_info(collection: str, feature_id: str):
            content, http_response = server.handle_item_request(collection, feature_id)

            if http_response is not None:
                return Response(content=None, status_code=http_response.status_code)
            else:
                return Response(content=content,
                                headers={
                                    "content-type": "application/geo+json",
                                    "content-length": str(len(content))
                                })

        @app.get("/tiles/{collection}/{zoom}/{x}/{y}/{a}/{b}.geojson")
        def get_tile_feature_info(collection: str, zoom: int, x: int, y: int, a: int, b: int):
            content, http_response = server.handle_tile_feature_info_request(collection, zoom, x, y, a, b)

            if http_response is not None:
                return Response(content=None, status_code=http_response.status_code)
            else:
                return Response(content=content,
                                headers={
                                    "content-type": "application/geo+json",
                                    "content-length": str(len(content))
                                })

        @app.get('/{path:path}', include_in_schema=False)
        def raise_400():
            return Response(content=None, status_code=404)
    except:
        return Response(content=None, status_code=500)


main()
