# Students Database CRUD API

A beginner-friendly individual internship project built with **Python**, **FastAPI**, and **SQLite**. It supports creating, listing, filtering, viewing, updating, and deleting student records.

## Features

- Create student records with name, date of birth, and at least one contact method (email or phone).
- List students, with optional name/course/date-of-birth filters and pagination.
- Retrieve one student by ID.
- Replace a record with `PUT` or partially edit it with `PATCH`.
- Delete a student record.
- SQLite database is created automatically on first launch and persists between runs.
- Automatic request validation and clear errors for missing records and duplicate emails.
- Interactive API documentation at `/docs`.

## Requirements

- Python 3.10 or newer
- pip

## Setup and run

Open a terminal in this project folder.

### 1. Create a virtual environment

Windows:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the API

```bash
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to test the endpoints. The SQLite file `students.db` is generated in the project folder when the application starts.

Stop the server with `Ctrl+C`.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/students` | Create a student |
| `GET` | `/students` | List and filter students |
| `GET` | `/students/{student_id}` | Get one student |
| `PUT` | `/students/{student_id}` | Replace all editable fields |
| `PATCH` | `/students/{student_id}` | Update selected fields |
| `DELETE` | `/students/{student_id}` | Delete a student |

### Example: create a student

Send a `POST` request to `/students` with this JSON body:

```json
{
  "name": "Asha Rao",
  "date_of_birth": "2005-04-18",
  "email": "asha.demo@example.com",
  "phone": "9000000001",
  "course": "Computer Science",
  "address": "Bengaluru",
  "enrollment_date": "2025-08-01"
}
```

This is dummy example data. Use the **Try it out** button in `/docs` to send it.

### Example: list and filter

- `GET /students`
- `GET /students?name=Asha`
- `GET /students?course=Computer%20Science`
- `GET /students?born_after=2005-01-01`
- `GET /students?limit=20&offset=0`

### Example: partial update

Send a `PATCH` request to `/students/1`:

```json
{
  "course": "Electronics"
}
```

### Example: delete

Send `DELETE /students/1`. A successful deletion returns HTTP `204 No Content`. A missing student returns HTTP `404 Not Found`.

## Response and error behavior

- `201 Created`: a student was created.
- `200 OK`: a student/list was returned or updated.
- `204 No Content`: a student was deleted.
- `404 Not Found`: the requested student ID does not exist.
- `409 Conflict`: email already exists.
- `422 Unprocessable Entity`: invalid request fields or date formats.

## How it works

- `app/schemas.py` defines and validates incoming request data using Pydantic.
- `app/database.py` creates the SQLite database and provides database connections.
- `app/main.py` defines the API routes and executes parameterized SQL queries.
- SQLite stores records in `students.db`, so data remains after restarting the server.

The API uses parameterized SQL values to reduce SQL injection risk. The dynamic columns in `PATCH` are restricted to an allow-list of supported fields.

## GitHub submission

1. Create a new **public or private** GitHub repository, for example `students-crud-fastapi`.
2. Extract this project ZIP and open a terminal inside the extracted folder.
3. Run:

   ```bash
   git init
   git add .
   git commit -m "Build student CRUD API with FastAPI and SQLite"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/students-crud-fastapi.git
   git push -u origin main
   ```

4. Replace the example remote URL with your actual repository URL.
5. Submit the repository link through the channel specified by your trainer.

Do not commit real student information or the generated `students.db` file. The optional Ollama AI extension is intentionally not included because the assignment says it is not required; complete and test the core CRUD application first.
