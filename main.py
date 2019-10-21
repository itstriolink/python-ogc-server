from fastapi import FastAPI

from index import make_index

app = FastAPI()


def main():
    coll = dict()
    coll[
        'castles'] = "C:\\Users\\labia\\Desktop\\HSR\\Semester 1\\Courses\\Z_ProjektArbeit\\python-wfs-server\\osm-castles-CH.geojson\\"
    index = make_index(coll, 'http://www.google.com/')


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


if __name__ == "__main__": main()
