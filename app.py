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

    for i in range(len(words)):
        if words[i].isdigit():
            if i + 1 < len(words) and "calorie" in words[i + 1]:
                calories = int(words[i])
                if calories > 1500:
                    return None, None, None, None, None, "Warning: Calorie input exceeds safe limits (1,500 calories)."
            elif i + 1 < len(words) and any(k in words[i + 1] for k in ["minute", "hour", "hours"]):
                duration = int(words[i])
                if duration > 120:
                    return None, None, None, None, None, "Warning: Duration exceeds safe limits (120 minutes)."

        elif words[i] == "remove":
            remove_words = []
            for j in range(i + 1, len(words)):
                if words[j] in ["replace", "with", "and"]:
                    break
                remove_words.append(words[j])
            if remove_words:
                remove_exercise = " ".join(remove_words).title()

        elif words[i] == "replace":
            replace_words = []
            for j in range(i + 1, len(words)):
                if words[j] in ["with", "remove", "and"]:
                    break
                replace_words.append(words[j])
            if replace_words:
                remove_exercise = " ".join(replace_words).title()

            # Check for replacement word
            if "with" in words[i:]:
                with_index = words.index("with", i)
                replacement = []
                for k in range(with_index + 1, len(words)):
                    if words[k] in ["remove", "replace", "and"]:
                        break
                    replacement.append(words[k])
                if replacement:
                    replace_exercise = " ".join(replacement).title()

    # Allow modifications even without calories/duration
    if not muscle_gain and (calories is None or duration is None) and not (remove_exercise or replace_exercise):
        return None, None, None, None, None, "Missing required information (calories, duration) or modification intent."

    return calories, duration, muscle_gain, remove_exercise, replace_exercise, None

def build_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain, exclude=None):
    workout_plan = []
    total_calories = 0
    total_time = 0

    if muscle_gain:
        for exercise, muscle_group in muscle_gain_exercises.items():
            if exclude and exclude.lower() in exercise.lower():
                continue
            workout_plan.append(f"{exercise} - Focus on {muscle_group}, 3 sets of 10 reps")
    else:
        available_exercises = {
            name: rate for name, rate in calorie_burn_exercises.items()
            if not exclude or exclude.lower() not in name.lower()
        }

        if not available_exercises:
            return ["No available exercises after filtering out unwanted ones."]

        exercise_list = list(available_exercises.items())
        random.shuffle(exercise_list)

        index = 0
        while total_time < duration and index < len(exercise_list):
            exercise, burn_rate = exercise_list[index]
            time_for_exercise = min(duration - total_time, random.randint(5, 15))
            calories_burned = (calories / duration) * time_for_exercise
            workout_plan.append(f"{time_for_exercise} min of {exercise} (~{int(calories_burned)} cal)")
            total_calories += calories_burned
            total_time += time_for_exercise
            index += 1

        if total_time < duration:
            workout_plan.append(f"(Time left: {duration - total_time} min — no more unique exercises available)")

    return workout_plan

def modify_existing_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises):
    modified_plan = []
    all_exercises = list(calorie_burn_exercises.keys()) + list(muscle_gain_exercises.keys())

    for entry in workout_plan:
        match = re.search(r'of (.+?) \(', entry)
        if match:
            current_exercise = match.group(1).strip()
        else:
            current_exercise = entry.split(" - ")[0].strip()

        if remove_exercise and current_exercise.lower() == remove_exercise.lower():
            if not replace_exercise:
                replacement_choices = [e for e in all_exercises if e.lower() != remove_exercise.lower()]
                replace_exercise = random.choice(replacement_choices)
            entry = re.sub(re.escape(current_exercise), replace_exercise, entry, flags=re.IGNORECASE)
        
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

    workout_plan = build_workout(
        calories,
        duration,
        calorie_burn_exercises,
        muscle_gain_exercises,
        muscle_gain,
        exclude=remove_exercise
    )

    if remove_exercise or replace_exercise:
        workout_plan = modify_existing_workout(
            workout_plan,
            remove_exercise,
            replace_exercise,
            calorie_burn_exercises,
            muscle_gain_exercises
        )

    return jsonify({"workout_plan": workout_plan, "request_id": request_id})

@app.route('/modify_workout', methods=['POST'])
def modify_workout_api():
    data = request.get_json()
    workout_plan = data.get("current_plan", [])
    user_input = data.get("modification", "")

    calories, duration, muscle_gain, remove_exercise, replace_exercise, error = parse_user_input(user_input)
    if error:
        return jsonify({"error": error}), 400

    modified_plan = modify_existing_workout(
        workout_plan,
        remove_exercise,
        replace_exercise,
        calorie_burn_exercises,
        muscle_gain_exercises
    )

    return jsonify({"modified_plan": modified_plan})

@app.route('/', methods=['GET'])
def index():
    return "CodeFit Backend is running ✅"

if __name__ == '__main__':
    app.run(debug=True)
