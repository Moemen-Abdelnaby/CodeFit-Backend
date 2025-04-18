from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import random
import re
import uuid

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Exercise data
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

# --- Utilities ---
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

def is_muscle_gain_intent(text):
    keywords = ["muscle", "strength", "bulk", "gain", "build"]
    return any(kw in text for kw in keywords)

def parse_user_input(user_input):
    user_input = correct_spelling(user_input.lower())
    words = user_input.split()
    calories = None
    duration = None
    muscle_gain = is_muscle_gain_intent(user_input)
    remove_exercise = None
    replace_exercise = None

    for i in range(len(words) - 1):
        if words[i].isdigit():
            if "calorie" in words[i + 1]:
                calories = int(words[i])
                if calories > 1500:
                    return None, None, None, None, None, "Warning: Calorie input exceeds safe limits (1,500 calories)."
            elif "minute" in words[i + 1] or "hour" in words[i + 1] or "hours" in words[i + 1]:
                duration = int(words[i])
                if duration > 120:
                    return None, None, None, None, None, "Warning: Duration exceeds safe limits (120 minutes)."
        elif words[i] == "remove" and i + 1 < len(words):
            remove_exercise = words[i + 1].capitalize()
        elif words[i] == "replace" and i + 1 < len(words):
            replace_exercise = words[i + 1].capitalize()

    if not muscle_gain and (calories is None or duration is None):
        return None, None, None, None, None, "Missing required information (calories, duration)."

    return calories, duration, muscle_gain, remove_exercise, replace_exercise, None

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

    return workout_plan

def modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises):
    modified_plan = []
    for entry in workout_plan:
        if remove_exercise and remove_exercise in entry:
            if replace_exercise:
                new_exercise = replace_exercise
                entry = entry.replace(remove_exercise, new_exercise)
                modified_plan.append(entry)
            # If no replacement, remove the exercise (skip this entry)
        else:
            modified_plan.append(entry)
    return modified_plan

@app.route('/generate_workout', methods=['POST'])
def generate_workout_api():
    request_id = str(uuid.uuid4())
    data = request.get_json()
    logger.debug(f"[{request_id}] Received /generate_workout: {data}")

    goal = data.get("goal", "")
    if not goal:
        return jsonify({"error": "Missing 'goal'", "request_id": request_id}), 400

    calories, duration, muscle_gain, remove_exercise, replace_exercise, error = parse_user_input(goal)
    if error:
        return jsonify({"error": error, "request_id": request_id}), 400

    workout_plan = generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain)
    if remove_exercise or replace_exercise:
        workout_plan = modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises)

    return jsonify({"workout_plan": workout_plan, "request_id": request_id})

@app.route('/modify_workout', methods=['POST'])
def modify_workout_api():
    request_id = str(uuid.uuid4())
    data = request.get_json()
    logger.debug(f"[{request_id}] Received /modify_workout: {data}")

    modification = data.get("modification", "")
    current_plan = data.get("current_plan", [])

    if not modification or not current_plan:
        return jsonify({
            "error": "Missing 'modification' or 'current_plan'",
            "request_id": request_id
        }), 400

    _, _, _, remove_exercise, replace_exercise, _ = parse_user_input(modification)
    modified_plan = modify_workout(current_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises)

    return jsonify({"modified_plan": modified_plan, "request_id": request_id})

@app.route('/', methods=['GET'])
def index():
    return "CodeFit Backend is running ✅"

if __name__ == '__main__':
    app.run(debug=True)
