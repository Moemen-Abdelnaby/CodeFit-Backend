from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

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
                    return None, None, None, None, None
            elif "minute" in words[i + 1] or "hour" in words[i + 1] or "hours" in words[i + 1]:
                duration = int(words[i])
                if duration > 120:
                    return None, None, None, None, None
        elif words[i] == "remove" and i + 1 < len(words):
            remove_exercise = words[i + 1].capitalize()
        elif words[i] == "replace" and i + 1 < len(words):
            replace_exercise = words[i + 1].capitalize()

    if muscle_gain and duration is not None:
        return None, duration, muscle_gain, remove_exercise, replace_exercise

    if calories is None or duration is None:
        return None, None, None, None, None

    return calories, duration, muscle_gain, remove_exercise, replace_exercise

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

# --- API Endpoints ---

@app.route('/generate_workout', methods=['POST'])
def api_generate_workout():
    data = request.get_json()
    user_input = data.get('user_input', '')

    calories, duration, muscle_gain, remove_exercise, replace_exercise = parse_user_input(user_input)
    
    if (calories is None and not muscle_gain) or duration is None:
        return jsonify({"error": "Invalid input. Please provide a valid workout goal."}), 400

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

    workout_plan = generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain)

    return jsonify({"workout_plan": workout_plan}), 200

@app.route('/modify_workout', methods=['POST'])
def api_modify_workout():
    data = request.get_json()
    user_input = data.get('user_input', '')
    current_plan = data.get('current_plan', [])

    calories, duration, muscle_gain, remove_exercise, replace_exercise = parse_user_input(user_input)

    if not current_plan:
        return jsonify({"error": "Current plan is required to modify workout."}), 400

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

    modified_plan = modify_workout(current_plan, remove_exercise, replace_exercise, calorie_burn_exercises, muscle_gain_exercises)

    return jsonify({"modified_plan": modified_plan}), 200

@app.route('/', methods=['GET'])
def index():
    return "Workout Generator API is running ✅"

if __name__ == '__main__':
    app.run(debug=True)
