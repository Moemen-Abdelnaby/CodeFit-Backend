from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Calorie-burning exercises and muscle-gaining exercises
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

# Function to generate workout
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


@app.route('/generate_workout', methods=['POST'])
def workout():
    try:
        # Get JSON from the request
        data = request.get_json()

        user_input = data.get('message', '')

        # Parse the user input (You can adjust this as needed)
        calories = 300  # Example, you can parse this from the message
        duration = 30   # Example, you can parse this from the message
        muscle_gain = "muscle" in user_input.lower()

        # Generate the workout plan
        workout_plan = generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain)

        return jsonify({"workout_plan": workout_plan}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
