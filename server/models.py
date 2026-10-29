"""Database models for the workout tracking application.

The application contains three entities: Exercise, Workout, and
WorkoutExercise. WorkoutExercise is an association object because the
relationship itself stores reps, sets, and duration information.
"""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates


db = SQLAlchemy()


class Exercise(db.Model):
    """A reusable exercise that can appear in many workouts."""

    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("length(trim(name)) >= 2", name="exercise_name_length"),
        CheckConstraint("length(trim(category)) >= 2", name="exercise_category_length"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    @validates("name")
    def validate_name(self, key, value):
        """Reject blank or very short exercise names before database insert."""
        if not isinstance(value, str) or len(value.strip()) < 2:
            raise ValueError("Exercise name must contain at least 2 characters.")
        return value.strip().title()

    @validates("category")
    def validate_category(self, key, value):
        """Reject blank categories and normalize their presentation."""
        if not isinstance(value, str) or len(value.strip()) < 2:
            raise ValueError("Exercise category must contain at least 2 characters.")
        return value.strip().title()

    @validates("equipment_needed")
    def validate_equipment(self, key, value):
        """Require the equipment flag to be a genuine boolean."""
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be true or false.")
        return value

    def to_dict(self, include_workouts=False):
        """Serialize an exercise without exposing SQLAlchemy internals."""
        result = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "equipment_needed": self.equipment_needed,
        }
        if include_workouts:
            result["workouts"] = [
                {
                    "id": link.workout.id,
                    "date": link.workout.date.isoformat(),
                    "duration_minutes": link.workout.duration_minutes,
                    "notes": link.workout.notes,
                }
                for link in self.workout_exercises
            ]
        return result


class Workout(db.Model):
    """A trainer's workout session."""

    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="workout_duration_positive"),
        CheckConstraint("date <= CURRENT_DATE", name="workout_date_not_future"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        """Ensure a workout lasts a positive whole number of minutes."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    @validates("date")
    def validate_date(self, key, value):
        """Prevent workouts from being scheduled in the future."""
        if not isinstance(value, date):
            raise ValueError("date must be a valid date.")
        if value > date.today():
            raise ValueError("Workout date cannot be in the future.")
        return value

    def to_dict(self, include_exercises=True):
        """Serialize a workout and optionally its association details."""
        result = {
            "id": self.id,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
        }
        if include_exercises:
            result["exercises"] = [link.to_dict() for link in self.workout_exercises]
        return result


class WorkoutExercise(db.Model):
    """Association object connecting one workout and one exercise."""

    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="unique_workout_exercise"),
        CheckConstraint("reps IS NULL OR reps > 0", name="reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="sets_positive"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds > 0", name="seconds_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_measurement(self, key, value):
        """Require optional training measurements to be positive integers."""
        if value is None:
            return value
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{key} must be a positive integer when provided.")
        return value

    def to_dict(self):
        """Serialize the exercise and the training measurements."""
        return {
            "id": self.exercise.id,
            "name": self.exercise.name,
            "category": self.exercise.category,
            "equipment_needed": self.exercise.equipment_needed,
            "workout_exercise_id": self.id,
            "reps": self.reps,
            "sets": self.sets,
            "duration_seconds": self.duration_seconds,
        }
