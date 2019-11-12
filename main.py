from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from classes.index import make_index
from classes.server import make_web_server

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

CASTLES_PATH = r'.\osm-castles-CH.geojson'
WEB_HOST_URL = r'http://127.0.0.1:8000'

SHORT_INDEX_MESSAGE = 'This is a WFS server written in Python that serves GeoJSON objects and PNG raster tiles'
INDEX_MESSAGE = f'{SHORT_INDEX_MESSAGE}' \
                'Available API methods: </br>' \
                '1. /collections/{collection_type}/items?{bbox}{limit} </br>' \
                '2. /tiles/castles/{zoom}/{x}/{y}.png/ </br>' \
                '3. /collections{collection_type}/items/{feature_id}'


def main():
    server = None

    coll = {'castles': CASTLES_PATH}

    try:
        idx = make_index(coll, WEB_HOST_URL)
        server = make_web_server(idx)
    except Exception:
        raise RuntimeError("Something went wrong while trying to create the collection")
    finally:
        pass

    @app.get("/")
    def index():
        return Response(content=SHORT_INDEX_MESSAGE)

    @app.get("/collections/{collection}/items")
    def get_collection_items(collection: str, bbox: str, limit=None):
        content, http_response = server.handle_collection_request(collection, bbox, limit)

        if http_response is not None:
            raise HTTPException(status_code=http_response.status_code, detail=http_response.detail)
        else:
            return Response(content=content,
                            headers={
                                "content-type": "application/geo+json",
                                "content-length": str(len(content))
                            }
                            )

    @app.get("/tiles/{collection}/{zoom}/{x}/{y}.png")
    def get_raster_tile(collection: str, zoom: int, x: int, y: int):
        content, metadata, http_response = server.handle_tile_request(collection, zoom, x, y)

        if http_response is not None:
            raise HTTPException(status_code=http_response.status_code, detail=http_response.detail)
        else:
            return Response(content=content, media_type="image/png")

    @app.get("/collections/{collection}/items/{feature_id}")
    def get_feature_info(collection: str, feature_id: str):
        content, http_response = server.handle_feature_request(collection, feature_id)

        if http_response is not None:
            raise HTTPException(status_code=http_response.status_code, detail=http_response.detail)
        else:
            return Response(content=content,
                            headers={
                                "content-type": "application/geo+json",
                                "content-length": str(len(content))
                            }
                            )


main()
