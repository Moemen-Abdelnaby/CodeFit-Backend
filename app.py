from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import re
import uuid

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

GOAL_WORKOUTS = {
    "lose weight": [
        "Jump rope - 10 minutes",
        "HIIT circuit - 20 minutes",
        "Running - 30 minutes",
        "Mountain climbers - 3 sets of 20"
    ],
    "build muscle": [
        "Bench press - 4 sets of 8",
        "Squats - 4 sets of 10",
        "Deadlift - 3 sets of 6",
        "Pull-ups - 3 sets of 8"
    ],
    "gain weight": [
        "Pushups - 4 sets of 15",
        "Dumbbell rows - 3 sets of 10",
        "Barbell squats - 4 sets of 8",
        "Overhead press - 3 sets of 10"
    ],
    "calorie burn": [
        "Cycling - 30 minutes",
        "Jump rope - 15 minutes",
        "Burpees - 3 sets of 15",
        "Rowing - 20 minutes"
    ]
}

def normalize_goal(raw_goal):
    raw_goal = raw_goal.lower()
    if re.search(r'\bcalori(e|es)?\b', raw_goal):
        return "calorie burn"
    elif "muscle" in raw_goal:
        return "build muscle"
    elif "lose" in raw_goal and "weight" in raw_goal:
        return "lose weight"
    elif "gain" in raw_goal and "weight" in raw_goal:
        return "gain weight"
    return raw_goal.strip()

@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    request_id = str(uuid.uuid4())
    data = request.get_json()

    logging.info(f"[{request_id}] Received /generate_workout: {data}")

    if not data or 'goal' not in data:
        error_msg = "Missing 'goal' in request"
        logging.error(f"[{request_id}] {error_msg}")
        return jsonify({"error": error_msg, "request_id": request_id}), 400

    goal = normalize_goal(data['goal'])

    if goal not in GOAL_WORKOUTS:
        error_msg = f"Unknown goal: {goal}"
        logging.warning(f"[{request_id}] {error_msg}")
        return jsonify({"error": error_msg, "request_id": request_id}), 400

    logging.info(f"[{request_id}] Generating plan for: {goal}")
    return jsonify({"workout_plan": GOAL_WORKOUTS[goal], "request_id": request_id})


@app.route('/modify_workout', methods=['POST'])
def modify_workout():
    request_id = str(uuid.uuid4())
    data = request.get_json()
    logging.info(f"[{request_id}] Received /modify_workout: {data}")

    if not data or 'modification' not in data or 'current_plan' not in data:
        error_msg = "Missing 'modification' or 'current_plan'"
        logging.error(f"[{request_id}] {error_msg}")
        return jsonify({"error": error_msg, "request_id": request_id}), 400

    mod = data['modification'].strip().lower()
    current_plan = data['current_plan']

    if not isinstance(current_plan, list) or not all(isinstance(item, str) for item in current_plan):
        error_msg = "Invalid 'current_plan' format. Must be a list of strings."
        logging.error(f"[{request_id}] {error_msg}")
        return jsonify({"error": error_msg, "request_id": request_id}), 400

    # Apply basic modifications
    if "add" in mod and "cardio" in mod:
        current_plan.append("Cardio blast - 20 minutes")
    elif "replace" in mod and "squats" in mod:
        current_plan = [item.replace("Squats", "Lunges") for item in current_plan]
    elif "remove" in mod and "deadlift" in mod:
        current_plan = [item for item in current_plan if "Deadlift" not in item]

    logging.info(f"[{request_id}] Modified plan: {current_plan}")
    return jsonify({"modified_plan": current_plan, "request_id": request_id})


@app.route('/', methods=['GET'])
def index():
    return "CodeFit Backend is running ✅"

if __name__ == '__main__':
    app.run(debug=True)
