from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import random
import re
import uuid

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# Define exercises for calorie burn and muscle gain
calorie_burn_exercises = {
    "Jump Rope": 12,
    "Burpees": 10,
    "Jumping Jacks": 8,
    "Mountain Climbers": 11,
    "High Knees": 10,
    "Running in Place": 9,
    "Cycling (Stationary)": 10,
    "Rowing Machine": 9,
    "Box Jumps": 12,
    "Shadow Boxing": 8
}

muscle_gain_exercises = {
    "Squats": "Legs",
    "Push-ups": "Chest & Arms",
    "Lunges": "Legs & Glutes",
    "Plank": "Core",
    "Deadlifts": "Back & Legs",
    "Bench Press": "Chest & Arms",
    "Pull-ups": "Back & Biceps",
    "Dips": "Triceps & Shoulders",
    "Russian Twists": "Core",
    "Leg Raises": "Core"
}

# --- Spell Correction ---
def correct_spelling(input_str):
    corrections = {
        "calori": "calorie",
        "minut": "minute",
        "hour": "hour",
        "hours": "hours"
    }
    for wrong, correct in corrections.items():
        input_str = re.sub(rf'\b{wrong}\b', correct, input_str, flags=re.IGNORECASE)
    return input_str

# --- Parse User Input ---
def parse_user_input(user_input):
    user_input = correct_spelling(user_input.lower())
    words = user_input.split()
    calories = None
    duration = None
    muscle_gain = "muscle" in words
    remove_exercise = None
    replace_exercise = None

    for i in range(len(words) - 1):
        if words[i].isdigit():
            if "calorie" in words[i + 1]:
                calories = int(words[i])
                if calories > 1500:
                    return None, None, None, None, None, "Warning: Calorie input exceeds safe limits (1,500 calories). Please adjust your request."
            elif "minute" in words[i + 1] or "hour" in words[i + 1] or "hours" in words[i + 1]:
                duration = int(words[i])
                if duration > 120:
                    return None, None, None, None, None, "Warning: Duration exceeds safe limits (120 minutes). Please adjust your request."
        elif words[i] == "remove" and i + 1 < len(words):
            remove_exercise = words[i + 1].capitalize()
        elif words[i] == "replace" and i + 1 < len(words):
            replace_exercise = words[i + 1].capitalize()

    if muscle_gain and duration is not None:
        return None, duration, muscle_gain, remove_exercise, replace_exercise, None

    if calories is None or duration is None:
        return None, None, None, None, None, "Missing required information (calories, duration)."

    return calories, duration, muscle_gain, remove_exercise, replace_exercise, None

# --- Generate Workout ---
def generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain):
    workout_plan = []
    total_calories = 0
    total_time = 0

    if muscle_gain:
        for exercise, muscle_group in muscle_gain_exercises.items():
            workout_plan.append(f"{exercise} - Focus on {muscle_group}, 3 sets of 10 reps")
    else:
        while total_time < duration:
            exercise, burn_rate = random.choice(list(calorie_burn_exercises.items()))
            time_for_exercise = min(duration - total_time, random.randint(5, 15))
            calories_burned = (calories / duration) * time_for_exercise
            workout_plan.append(f"{time_for_exercise} min of {exercise} (~{int(calories_burned)} cal)")
            total_calories += calories_burned
            total_time += time_for_exercise

        if total_time < duration:
            last_entry = workout_plan.pop()
            updated_time = time_for_exercise + (duration - total_time)
            updated_calories = (calories / duration) * updated_time
            updated_entry = last_entry.replace(f"{time_for_exercise} min", f"{updated_time} min").replace(
                f"~{int(calories_burned)} cal", f"~{int(updated_calories)} cal")
            workout_plan.append(updated_entry)

    return workout_plan

# --- Modify Workout ---
def modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises):
    modified_plan = []
    for exercise in workout_plan:
        if remove_exercise and remove_exercise in exercise:
            if replace_exercise:
                new_exercise = replace_exercise
            else:
                new_exercise, _ = random.choice(list(calorie_burn_exercises.items()))
            exercise = exercise.replace(remove_exercise, new_exercise)
        modified_plan.append(exercise)
    return modified_plan

@app.route('/generate_workout', methods=['POST'])
def generate_workout_api():
    request_id = str(uuid.uuid4())
    data = request.get_json()

    logging.info(f"[{request_id}] Received /generate_workout: {data}")

    if not data or 'goal' not in data or 'calories' not in data or 'duration' not in data:
        error_msg = "Missing 'goal', 'calories', or 'duration' in request"
        logging.error(f"[{request_id}] {error_msg}")
        return jsonify({"error": error_msg, "request_id": request_id}), 400

    goal = data.get("goal", "").strip().lower()
    calories = data['calories']
    duration = data['duration']

    muscle_gain = "muscle" in goal
    remove_exercise = data.get("remove_exercise")
    replace_exercise = data.get("replace_exercise")

    # Parse input and validate
    calories, duration, muscle_gain, remove_exercise, replace_exercise, validation_error = parse_user_input(f"goal {goal} calories {calories} duration {duration}")
    
    if validation_error:
        return jsonify({"error": validation_error, "request_id": request_id}), 400

    # Generate the workout plan
    workout_plan = generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain)

    # If modification is required
    if remove_exercise or replace_exercise:
        workout_plan = modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises)

    logging.info(f"[{request_id}] Generated workout plan: {workout_plan}")
    return jsonify({"workout_plan": workout_plan, "request_id": request_id})


@app.route('/', methods=['GET'])
def index():
    return "CodeFit Backend is running ✅"


if __name__ == '__main__':
    app.run(debug=True)
