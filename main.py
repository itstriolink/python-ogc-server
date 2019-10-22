from fastapi import FastAPI

from index import make_index

app = FastAPI()
CASTLES_PATH = r'C:\Users\labia\Desktop\HSR\Semester 1\Courses\Z_ProjektArbeit\python-wfs-server\osm-castles-CH.geojson'
WEB_HOST_URL = r'http://127.0.0.1:8000'


def main():
    coll = {'castles': CASTLES_PATH}

    index = make_index(coll, WEB_HOST_URL)


@app.get("/")
def index():
    return "This is the index page!"


@app.get("/hello/world")
def hello_world():
    return "Hello " + "World"


@app.get("/tiles/castles/{x}/{y}/{z}")
def get_raster_tile(x: int, y: int, z: int):
    return {"x": x, "y": y, "z": z}


@app.get("/collections/castles/items")
def get_castles(bbox: str, limit: int = None):
    bounding_box = bbox.split(",")
    return {"bbox": bounding_box, "limit": limit}


if __name__ == "__main__":
    main()
