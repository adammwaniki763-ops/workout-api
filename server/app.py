"""Flask API for the workout tracking application."""

from datetime import datetime

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False

db.init_app(app)
migrate = Migrate(app, db)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
link_schema = WorkoutExerciseSchema()


def error_response(message, status=400, messages=None):
    """Return one consistent JSON error shape."""
    payload = {"error": message}
    if messages:
        payload["messages"] = messages
    return jsonify(payload), status


def parse_json():
    """Read a JSON object and reject missing or non-object payloads."""
    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError("Request body must be valid JSON.")
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    return payload


@app.get("/health")
def health():
    """Confirm that the API process is running."""
    return jsonify({"status": "ok", "service": "workout-api"}), 200


@app.get("/workouts")
def list_workouts():
    """List every workout and its associated exercise measurements."""
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    """Return one workout or a 404 JSON response."""
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return error_response("Workout not found.", 404)
    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    """Deserialize, validate, and persist a new workout."""
    try:
        payload = parse_json()
        data = workout_schema.load(payload)
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValidationError as error:
        db.session.rollback()
        return error_response("Validation failed.", 400, error.messages)
    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)
    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    """Delete a workout and cascade its association rows."""
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return error_response("Workout not found.", 404)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted."}), 200


@app.get("/exercises")
def list_exercises():
    """List all reusable exercises."""
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    """Return one exercise with its associated workouts."""
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return error_response("Exercise not found.", 404)
    result = exercise.to_dict(include_workouts=True)
    return jsonify(result), 200


@app.post("/exercises")
def create_exercise():
    """Deserialize, validate, and persist a reusable exercise."""
    try:
        payload = parse_json()
        data = exercise_schema.load(payload)
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValidationError as error:
        db.session.rollback()
        return error_response("Validation failed.", 400, error.messages)
    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)
    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    """Delete an exercise and cascade its association rows."""
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return error_response("Exercise not found.", 404)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise deleted."}), 200


@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    """Create an association with reps, sets, or duration details."""
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if workout is None:
        return error_response("Workout not found.", 404)
    if exercise is None:
        return error_response("Exercise not found.", 404)
    if WorkoutExercise.query.filter_by(workout_id=workout_id, exercise_id=exercise_id).first():
        return error_response("Exercise is already attached to this workout.", 409)
    try:
        payload = parse_json()
        data = link_schema.load({**payload, "exercise_id": exercise_id})
        link = WorkoutExercise(workout_id=workout_id, **data)
        db.session.add(link)
        db.session.commit()
    except ValidationError as error:
        db.session.rollback()
        return error_response("Validation failed.", 400, error.messages)
    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)
    return jsonify(link.to_dict()), 201


@app.errorhandler(404)
def route_not_found(error):
    """Return JSON for unknown URLs."""
    return error_response("Route not found.", 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Return JSON for unsupported HTTP methods."""
    return error_response("Method not allowed.", 405)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
