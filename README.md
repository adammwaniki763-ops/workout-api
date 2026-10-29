# Workout Tracking API

This is a Flask SQLAlchemy backend for the Moringa School summative lab.
The application tracks reusable exercises, workout sessions, and the details
of each exercise performed in a workout.

## Features

- Flask REST API
- SQLAlchemy database models
- SQLite local database
- Flask-Migrate configuration
- Marshmallow serialization and deserialization
- Model-level validation
- Schema-level validation
- Database table constraints
- Seed data for all three tables
- Cascade deletion of association records
- RESTful create, read, and delete endpoints
- Automated pytest endpoint tests
- No update endpoints, as required by the specification
- No TypeScript files
- No TSX files

## Data model

An Exercise is reusable and can belong to many Workouts. A Workout can contain
many Exercises. Because the relationship stores reps, sets, and duration, the
project uses a WorkoutExercise association object.

```text
Exercise 1 ---- many WorkoutExercise many ---- 1 Workout
```

The tables are:

- `exercises`: id, name, category, equipment_needed
- `workouts`: id, date, duration_minutes, notes
- `workout_exercises`: id, workout_id, exercise_id, reps, sets, duration_seconds

## Requirements

Use Python 3.10 or newer. The project is intentionally Python-only.

## Installation

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Database setup

Move into the server directory:

```bash
cd server
python seed.py
```

The seed script clears the existing records and creates exercises, workouts,
and association rows. It can be run again whenever a clean demo database is
needed.

For Flask-Migrate, set the Flask application:

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "create workout tables"
flask db upgrade
```

On Windows PowerShell use ` $env:FLASK_APP = "app.py" ` without the spaces.
The seed script also calls `db.create_all()` for a simple local setup.

## Run the server

From `server/` run:

```bash
python app.py
```

The API listens on `http://127.0.0.1:5555`.

## Required endpoints

| Method | URL | Purpose |
| --- | --- | --- |
| GET | `/workouts` | List workouts with exercises |
| GET | `/workouts/<id>` | Show one workout |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout |
| GET | `/exercises` | List exercises |
| GET | `/exercises/<id>` | Show an exercise and workouts |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Attach exercise |

## Example requests

Create an exercise:

```bash
curl -X POST http://127.0.0.1:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name":"Deadlift","category":"Strength","equipment_needed":true}'
```

Create a workout:

```bash
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-10-20","duration_minutes":45,"notes":"Lower body"}'
```

Attach an exercise:

```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps":12,"sets":3}'
```

## Validation included

Database constraints reject short names, short categories, non-positive workout
durations, future dates, non-positive reps, non-positive sets, and duplicate
workout-exercise pairs. Model validators reject invalid Python objects before
commit. Marshmallow validators reject blank strings, future dates, invalid
ranges, missing booleans, and links with no measurements.

## Testing

From the project root run:

```bash
pytest -q
```

The test suite uses a temporary SQLite database. It tests all required routes,
relationships, serialization, validation errors, cascade deletion, duplicate
links, and JSON error responses.

## Git workflow

Create a branch for each feature:

```bash
git checkout -b feature/models
 git add .
 git commit -m "feat: add workout models and relationships"
 git checkout main
 git merge feature/models
 git branch -d feature/models
```

Use clear commits for setup, models, relationships, validations, seed data,
endpoints, schemas, tests, and documentation.

## Folder structure

```text
workout-api/
├── README.md
├── requirements.txt
└── server/
    ├── app.py
    ├── models.py
    ├── schemas.py
    ├── seed.py
    ├── migrations/
    └── tests/
        └── test_api.py
```
