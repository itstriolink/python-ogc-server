import tempfile

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from index import make_index
from server import make_web_server

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

CASTLES_PATH = r'C:\Users\labia\Desktop\HSR\Semester 1\Courses\Z_ProjektArbeit\python-wfs-server\osm-castles-CH.geojson'
WEB_HOST_URL = r'http://127.0.0.1:8000'


def main():
    coll = {'castles': CASTLES_PATH}

    idx = make_index(coll, WEB_HOST_URL)

    server = make_web_server(idx)

    @app.get("/")
    def index():
        return "This is the index page!"

    @app.get("/hello/world")
    def hello_world():
        return "Hello " + "World"

    @app.get("/tiles/{collection}/{zoom}/{x}/{y}.png")
    def get_raster_tile(collection: str, zoom: int, x: int, y: int):
        tile, metadata = server.handle_tile_request(collection, zoom, x, y)

        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".png", delete=False) as FOUT:
            FOUT.write(tile)
            return FileResponse(FOUT.name, media_type="image/png")

    @app.get("/collections/{collection}/items")
    def get_items(collection: str, bbox: str, limit: int = None):
        bbox = server.handle_collection_request(collection, bbox, limit)
        return bbox


main()
