"""Automated tests for the workout API endpoints."""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app as flask_app
from models import Exercise, Workout, WorkoutExercise, db


@pytest.fixture()
def client(tmp_path):
    """Use a temporary SQLite file so tests never touch a real database."""
    database_path = tmp_path / "test.db"
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
    )
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        exercise = Exercise(name="Push Up", category="Strength", equipment_needed=False)
        workout = Workout(date=date.today(), duration_minutes=30, notes="Test session")
        db.session.add_all([exercise, workout])
        db.session.commit()
    with flask_app.test_client() as test_client:
        yield test_client
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_list_workouts(client):
    response = client.get("/workouts")
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]["exercises"] == []


def test_get_workout(client):
    response = client.get("/workouts/1")
    assert response.status_code == 200
    assert response.get_json()["duration_minutes"] == 30


def test_create_workout(client):
    response = client.post("/workouts", json={
        "date": date.today().isoformat(),
        "duration_minutes": 45,
        "notes": "New session",
    })
    assert response.status_code == 201
    assert response.get_json()["duration_minutes"] == 45


def test_future_workout_is_rejected_by_schema(client):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.post("/workouts", json={"date": tomorrow, "duration_minutes": 30})
    assert response.status_code == 400
    assert "date" in str(response.get_json())


def test_invalid_workout_duration_is_rejected(client):
    response = client.post("/workouts", json={"date": date.today().isoformat(), "duration_minutes": 0})
    assert response.status_code == 400


def test_delete_workout(client):
    response = client.delete("/workouts/1")
    assert response.status_code == 200
    assert client.get("/workouts/1").status_code == 404


def test_list_exercises(client):
    response = client.get("/exercises")
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Push Up"


def test_get_exercise(client):
    response = client.get("/exercises/1")
    assert response.status_code == 200
    assert response.get_json()["category"] == "Strength"
    assert response.get_json()["workouts"] == []


def test_create_exercise(client):
    response = client.post("/exercises", json={
        "name": "Running",
        "category": "Cardio",
        "equipment_needed": False,
    })
    assert response.status_code == 201
    assert response.get_json()["name"] == "Running"


def test_blank_exercise_name_is_rejected(client):
    response = client.post("/exercises", json={
        "name": "  ",
        "category": "Core",
        "equipment_needed": False,
    })
    assert response.status_code == 400


def test_missing_equipment_boolean_is_rejected(client):
    response = client.post("/exercises", json={"name": "Lunge", "category": "Legs"})
    assert response.status_code == 400


def test_add_exercise_to_workout(client):
    response = client.post("/workouts/1/exercises/1/workout_exercises", json={"reps": 12, "sets": 3})
    assert response.status_code == 201
    assert response.get_json()["reps"] == 12
    assert response.get_json()["sets"] == 3
    detail = client.get("/workouts/1").get_json()
    assert len(detail["exercises"]) == 1


def test_link_requires_measurement(client):
    response = client.post("/workouts/1/exercises/1/workout_exercises", json={})
    assert response.status_code == 400


def test_duplicate_link_is_rejected(client):
    client.post("/workouts/1/exercises/1/workout_exercises", json={"duration_seconds": 30})
    response = client.post("/workouts/1/exercises/1/workout_exercises", json={"reps": 10})
    assert response.status_code == 409


def test_delete_exercise_cascades_link(client):
    client.post("/workouts/1/exercises/1/workout_exercises", json={"reps": 10})
    response = client.delete("/exercises/1")
    assert response.status_code == 200
    with flask_app.app_context():
        assert WorkoutExercise.query.count() == 0


def test_missing_record_returns_404(client):
    assert client.get("/workouts/999").status_code == 404
    assert client.get("/exercises/999").status_code == 404
    assert client.delete("/workouts/999").status_code == 404
    assert client.delete("/exercises/999").status_code == 404


def test_unknown_route_returns_json(client):
    response = client.get("/unknown")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Route not found."
