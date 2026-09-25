"""
FastAPI 101 - a tiny CRUD API to teach two things at once:

1. What an API is:
   A program (the frontend, another script, Postman, your browser) sends an
   HTTP request to a URL ("endpoint"). This server reads the request, does
   something (read/write data), and sends back a response - usually JSON.
   That request/response contract is the "API".

2. What FastAPI gives you:
   - You describe your data once with a Pydantic model (`Student` below).
   - FastAPI validates every incoming request against that model for free.
   - It generates interactive docs for you automatically at /docs (Swagger UI)
     and /redoc - no extra work needed.

Run it with:
    uvicorn main:app --reload

Then open:
    http://127.0.0.1:8000/docs   <- Swagger UI, try every endpoint from the browser
    http://127.0.0.1:8000/redoc  <- an alternative read-only docs page
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Student API",
    description="A minimal CRUD example for teaching FastAPI + APIs.",
    version="1.0.0",
)

# CORS = Cross-Origin Resource Sharing.
# The frontend.html file in this folder is opened directly in a browser
# (a different "origin" than this server), so without this, the browser
# would block its fetch() calls. allow_origins=["*"] is fine for a local
# teaching demo - never use "*" for a real production API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Data model -------------------------------------------------------
# This is the "shape" every student record must have. FastAPI uses it to:
#   - validate incoming POST/PUT bodies (reject bad data automatically)
#   - build the request/response schemas you see in Swagger UI
class Student(BaseModel):
    name: str = Field(examples=["Asha Rao"])
    age: int = Field(ge=5, le=100, examples=[16])
    grade: str = Field(examples=["10th"])


class StudentOut(Student):
    id: int


# ---- "Database" ---------------------------------------------------------
# A real app would use Postgres/MySQL/etc. For teaching CRUD concepts, a
# plain dict in memory is enough - it resets every time you restart the
# server, which is fine here.
students: dict[int, Student] = {}
next_id = 1


@app.get("/")
def root():
    """Landing endpoint - just points you to the interactive docs."""
    return {"message": "Student API is running. Open /docs to try it out."}


# ---- CREATE -------------------------------------------------------------
@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(student: Student):
    global next_id
    student_id = next_id
    students[student_id] = student
    next_id += 1
    return StudentOut(id=student_id, **student.model_dump())


# ---- READ (all) -----------------------------------------------------------
@app.get("/students", response_model=list[StudentOut])
def list_students():
    return [
        StudentOut(id=student_id, **student.model_dump())
        for student_id, student in students.items()
    ]


# ---- READ (one) -----------------------------------------------------------
@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    student = students.get(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentOut(id=student_id, **student.model_dump())


# ---- UPDATE -----------------------------------------------------------
@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: Student):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    students[student_id] = student
    return StudentOut(id=student_id, **student.model_dump())


# ---- DELETE -----------------------------------------------------------
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=1234, reload=True)
