"""Marshmallow schemas for serialization and input validation."""

from datetime import date

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class ExerciseSchema(Schema):
    """Validate and serialize Exercise payloads."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    category = fields.Str(required=True, validate=validate.Length(min=2, max=80))
    equipment_needed = fields.Bool(required=True)
    workouts = fields.List(fields.Dict(), dump_only=True)

    @validates_schema
    def validate_text_values(self, data, **kwargs):
        """Reject whitespace-only values that pass length checks."""
        for field_name in ("name", "category"):
            value = data.get(field_name)
            if value is not None and not value.strip():
                raise ValidationError({field_name: ["Value cannot be blank."]})


class WorkoutExerciseSchema(Schema):
    """Validate measurements used when linking an exercise to a workout."""

    id = fields.Int(dump_only=True)
    exercise_id = fields.Int(required=True, validate=validate.Range(min=1))
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))
    name = fields.Str(dump_only=True)
    category = fields.Str(dump_only=True)
    equipment_needed = fields.Bool(dump_only=True)
    workout_exercise_id = fields.Int(dump_only=True)

    @validates_schema
    def require_measurement(self, data, **kwargs):
        """Require at least one useful training measurement."""
        measurements = (data.get("reps"), data.get("sets"), data.get("duration_seconds"))
        if all(value is None for value in measurements):
            raise ValidationError("Provide reps, sets, or duration_seconds.")


class WorkoutSchema(Schema):
    """Validate and serialize Workout payloads."""

    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema),
        dump_only=True,
        attribute="workout_exercises",
    )

    @validates_schema
    def validate_date_not_future(self, data, **kwargs):
        """Reject a workout date later than today."""
        workout_date = data.get("date")
        if workout_date and workout_date > date.today():
            raise ValidationError({"date": ["Workout date cannot be in the future."]})

    @validates_schema
    def validate_notes(self, data, **kwargs):
        """Reject notes that contain only whitespace."""
        notes = data.get("notes")
        if notes is not None and notes.strip() == "":
            raise ValidationError({"notes": ["Notes cannot be blank when supplied."]})


class ErrorSchema(Schema):
    """Document the JSON error format used by the API."""

    error = fields.String(required=True)
    messages = fields.Dict(required=False)
