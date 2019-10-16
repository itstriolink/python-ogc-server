import geojson
from fastapi import FastAPI
from pydantic import BaseModel

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

