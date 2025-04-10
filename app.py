from flask import Flask, request, jsonify
import random
import re
import os  # Needed for setting the port dynamically

app = Flask(__name__)

# --- Static exercise data ---
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

# --- Utility functions ---
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
                    return {"error": "Calorie input exceeds safe limits (1,500)."}
            elif "minute" in words[i + 1] or "hour" in words[i + 1] or "hours" in words[i + 1]:
                duration = int(words[i])
                if duration > 120:
                    return {"error": "Duration exceeds safe limits (120 minutes)."}
        elif words[i] == "remove" and i + 1 < len(words):
            remove_exercise = words[i + 1].capitalize()
        elif words[i] == "replace" and i + 1 < len(words):
            replace_exercise = words[i + 1].capitalize()

    if muscle_gain and duration is not None:
        return {"duration": duration, "muscle_gain": True, "remove": remove_exercise, "replace": replace_exercise}

    if calories is None or duration is None:
        return {"error": "Please specify both calories and duration."}

    return {
        "calories": calories,
        "duration": duration,
        "muscle_gain": muscle_gain,
        "remove": remove_exercise,
        "replace": replace_exercise
    }

def generate_workout(calories, duration, calorie_ex, muscle_ex, muscle_goal=False):
    workout_plan = []
    time_per_exercise = duration // 6

    if muscle_goal:
        selected = random.sample(list(muscle_ex.keys()), 6)
        workout_plan = [f"{ex} — {time_per_exercise} minutes" for ex in selected]
    else:
        selected = random.sample(list(calorie_ex.items()), 6)
        workout_plan = [f"{ex} — {time_per_exercise} minutes (~{int(cal * time_per_exercise)} calories)" for ex, cal in selected]

    return workout_plan

def modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_ex, muscle_ex):
    modified = []
    for exercise in workout_plan:
        if remove_exercise and remove_exercise in exercise:
            new_ex = replace_exercise if replace_exercise else random.choice(list(calorie_ex.keys()))
            exercise = exercise.replace(remove_exercise, new_ex)
        modified.append(exercise)
    return modified

# --- API Endpoints ---
@app.route("/generate_workout", methods=["POST"])
def generate():
    data = request.get_json()
    parsed = parse_user_input(data.get("goal", ""))
    if "error" in parsed:
        return jsonify({"error": parsed["error"]}), 400

    workout = generate_workout(
        parsed.get("calories", 0),
        parsed["duration"],
        calorie_burn_exercises,
        muscle_gain_exercises,
        parsed.get("muscle_gain", False)
    )
    return jsonify({"workout_plan": workout})

@app.route("/modify_workout", methods=["POST"])
def modify():
    data = request.get_json()
    workout_plan = data.get("workout_plan", [])
    mod_request = data.get("modification", "")
    parsed = parse_user_input(mod_request)
    if not parsed.get("remove"):
        return jsonify({"error": "Please specify an exercise to remove."}), 400

    modified = modify_workout(
        workout_plan,
        parsed["remove"],
        parsed.get("replace"),
        calorie_burn_exercises,
        muscle_gain_exercises
    )
    return jsonify({"modified_workout_plan": modified})

# --- Required for Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # <- This line is critical
    app.run(host="0.0.0.0", port=port)        # <- So is this
