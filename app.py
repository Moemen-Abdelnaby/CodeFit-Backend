import random
from flask import Flask, request, jsonify

app = Flask(__name__)

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


def generate_workout(calories, duration, muscle_gain):
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

        if total_time < duration and workout_plan:
            last_entry = workout_plan.pop()
            updated_time = time_for_exercise + (duration - total_time)
            updated_calories = (calories / duration) * updated_time
            updated_entry = last_entry.replace(f"{time_for_exercise} min", f"{updated_time} min").replace(
                f"~{int(calories_burned)} cal", f"~{int(updated_calories)} cal")
            workout_plan.append(updated_entry)

    return workout_plan


def modify_workout(plan, remove_exercise, replace_exercise, muscle_gain):
    modified = []
    for item in plan:
        if remove_exercise and remove_exercise in item:
            if replace_exercise:
                new_exercise = replace_exercise
            else:
                new_exercise = random.choice(
                    list(muscle_gain_exercises if muscle_gain else calorie_burn_exercises))
            item = item.replace(remove_exercise, new_exercise)
        modified.append(item)
    return modified


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    calories = data.get("calories")
    duration = data.get("duration")
    muscle_gain = data.get("muscle_gain", False)
    remove_exercise = data.get("remove_exercise")
    replace_exercise = data.get("replace_exercise")

    if not duration or (not muscle_gain and not calories):
        return jsonify({"error": "Please provide duration and either calories or muscle_gain flag."}), 400

    workout = generate_workout(calories, duration, muscle_gain)

    if remove_exercise:
        workout = modify_workout(
            workout, remove_exercise, replace_exercise, muscle_gain
        )

    return jsonify({
        "workout_plan": workout
    })


@app.route("/", methods=["GET"])
def home():
    return "Workout AI API is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
