"""Reset and seed the workout database with useful demonstration records."""

from datetime import date, timedelta

from app import app
from models import Exercise, Workout, WorkoutExercise, db


EXERCISE_SEED = [
    {"name": "Push Up", "category": "Strength", "equipment_needed": False},
    {"name": "Barbell Squat", "category": "Strength", "equipment_needed": True},
    {"name": "Jumping Jacks", "category": "Cardio", "equipment_needed": False},
    {"name": "Plank", "category": "Core", "equipment_needed": False},
    {"name": "Dumbbell Row", "category": "Strength", "equipment_needed": True},
]


def clear_database():
    """Remove all records so the script can safely be rerun."""
    db.session.query(WorkoutExercise).delete()
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()
    db.session.commit()


def create_exercises():
    """Insert reusable exercises and return them in insertion order."""
    exercises = [Exercise(**attributes) for attributes in EXERCISE_SEED]
    db.session.add_all(exercises)
    db.session.commit()
    return exercises


def create_workouts():
    """Insert recent workouts that satisfy the date validation."""
    today = date.today()
    workouts = [
        Workout(
            date=today,
            duration_minutes=45,
            notes="Full body beginner session.",
        ),
        Workout(
            date=today - timedelta(days=1),
            duration_minutes=60,
            notes="Strength and conditioning session.",
        ),
        Workout(
            date=today - timedelta(days=3),
            duration_minutes=30,
            notes="Short core and mobility session.",
        ),
    ]
    db.session.add_all(workouts)
    db.session.commit()
    return workouts


def attach_exercises(exercises, workouts):
    """Create association records with different measurement styles."""
    links = [
        WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[0].id, reps=12, sets=3),
        WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[2].id, duration_seconds=60, sets=3),
        WorkoutExercise(workout_id=workouts[1].id, exercise_id=exercises[1].id, reps=8, sets=4),
        WorkoutExercise(workout_id=workouts[1].id, exercise_id=exercises[4].id, reps=10, sets=3),
        WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[3].id, duration_seconds=45, sets=4),
    ]
    db.session.add_all(links)
    db.session.commit()
    return links


def seed_database():
    """Reset the database and populate every table."""
    clear_database()
    exercises = create_exercises()
    workouts = create_workouts()
    links = attach_exercises(exercises, workouts)
    print(f"Seeded {len(exercises)} exercises.")
    print(f"Seeded {len(workouts)} workouts.")
    print(f"Seeded {len(links)} workout-exercise links.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database()
        print("Database seeding complete.")
