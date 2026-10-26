from contextlib import asynccontextmanager
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from .database import get_connection, initialize_database
from .schemas import StudentCreate, StudentUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="Students Database CRUD API",
    description="A beginner-friendly student records API using FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")

@app.post("/students", status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    data = student.model_dump(mode="json")
    try:
        with get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO students
                (name, date_of_birth, email, phone, course, address, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"].strip(), data["date_of_birth"], data["email"],
                data["phone"], data["course"], data["address"], data["enrollment_date"]
            ))
            row = connection.execute("SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        if "students.email" in str(exc):
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
        raise HTTPException(status_code=400, detail="Could not create student.") from exc

@app.get("/students", tags=["Students"])
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by part of a student's name"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
    born_after: Optional[str] = Query(default=None, description="Filter students born after YYYY-MM-DD"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conditions, parameters = [], []
    if name:
        conditions.append("name LIKE ?")
        parameters.append(f"%{name}%")
    if course:
        conditions.append("course LIKE ?")
        parameters.append(f"%{course}%")
    if born_after:
        try:
            from datetime import date
            date.fromisoformat(born_after)
        except ValueError:
            raise HTTPException(status_code=422, detail="born_after must use YYYY-MM-DD format.")
        conditions.append("date_of_birth > ?")
        parameters.append(born_after)

    sql = "SELECT * FROM students"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    parameters.extend([limit, offset])
    with get_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
        total_sql = "SELECT COUNT(*) FROM students"
        if conditions:
            total_sql += " WHERE " + " AND ".join(conditions)
        total = connection.execute(total_sql, parameters[:-2]).fetchone()[0]
    return {"total": total, "limit": limit, "offset": offset, "students": [row_to_dict(row) for row in rows]}

@app.get("/students/{student_id}", tags=["Students"])
def get_student(student_id: int):
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return row_to_dict(row)

@app.put("/students/{student_id}", tags=["Students"])
def replace_student(student_id: int, student: StudentCreate):
    data = student.model_dump(mode="json")
    try:
        with get_connection() as connection:
            cursor = connection.execute("""
                UPDATE students SET name=?, date_of_birth=?, email=?, phone=?, course=?,
                address=?, enrollment_date=? WHERE id=?
            """, (
                data["name"].strip(), data["date_of_birth"], data["email"], data["phone"],
                data["course"], data["address"], data["enrollment_date"], student_id
            ))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Student not found.")
            row = connection.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists.") from exc

@app.patch("/students/{student_id}", tags=["Students"])
def update_student(student_id: int, student: StudentUpdate):
    updates = student.model_dump(exclude_unset=True, mode="json")
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update.")
    if "name" in updates and updates["name"] is not None:
        updates["name"] = updates["name"].strip()
    allowed_columns = {"name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"}
    if not set(updates).issubset(allowed_columns):
        raise HTTPException(status_code=400, detail="Invalid field.")
    try:
        with get_connection() as connection:
            exists = connection.execute("SELECT id FROM students WHERE id=?", (student_id,)).fetchone()
            if exists is None:
                raise HTTPException(status_code=404, detail="Student not found.")
            assignments = ", ".join(f"{column} = ?" for column in updates)
            values = list(updates.values()) + [student_id]
            connection.execute(f"UPDATE students SET {assignments} WHERE id = ?", values)
            row = connection.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists.") from exc

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM students WHERE id=?", (student_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
