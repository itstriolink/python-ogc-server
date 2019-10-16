import geojson
from fastapi import FastAPI
from pydantic import BaseModel

# Another test commit

app = FastAPI()


class Student(BaseModel):
    name: str
    year: int
    is_master: bool = False


@app.get("/")
def index():
    return "This is the index page!"


@app.get("/hello")
def hello_world():
    return "Hello " + "World"


@app.get("/students")
def students():
    return "Students"


@app.get("/students/{student_id}")
def get_student(student_id: int, q: str = None):
    return {"student_id": student_id, "q": q}


@app.put("/students/{student_id}")
def save_student(student_id: int, student: Student):
    return {"student_name": student.name, "student_id": student_id}


@app.get("/tiles/castles/{x}/{y}/{z}")
def raster_tile(x: int, y: int, z: int):
    return {"x": x, "y": y, "z": z}


@app.get("/collections/castles/items")
def get_castles(bbox: str, limit: int = None):
    bounding_box = bbox.split(",")
    return {"bbox": bounding_box, "limit": limit}