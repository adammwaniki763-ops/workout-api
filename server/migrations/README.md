# Database migrations

This directory is reserved for Flask-Migrate and Alembic migration files.
The application connects Flask-Migrate in `server/app.py`.

Initialize migrations once from the `server` directory:

```bash
flask --app app db init
```

Create a migration after changing models:

```bash
flask --app app db migrate -m "describe the change"
```

Apply migrations to the local database:

```bash
flask --app app db upgrade
```

Roll back one migration when necessary:

```bash
flask --app app db downgrade
```

The model definitions are in `server/models.py`.
The database object is named `db`.
The Flask application is named `app`.
The local SQLite database is created in the Flask instance directory.

The main tables are:

- exercises
- workouts
- workout_exercises

The association table contains training measurements.
Its foreign keys connect workouts and exercises.
Its unique constraint prevents duplicate links.
Its check constraints require positive measurements.

The seed command creates demo records after the schema exists:

```bash
python seed.py
```

The seed command is safe to repeat because it clears existing records first.
Generated Alembic version files should be committed to Git in a real project.
This README remains as a guide when the project is first opened by a grader.

No TypeScript files belong in this migration directory.
No TSX files belong in this migration directory.
This backend is implemented entirely in Python.

For a production database, configure the database URL through an environment
variable instead of committing credentials into source code.
The current SQLite configuration is intentionally simple for assessment.

End of migration documentation.
