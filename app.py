import random
import re

# Utility function to check for common spelling errors
def correct_spelling(input_str):
    # Common spelling mistakes
    corrections = {
        "calori": "calorie",
        "minut": "minute",
        "hour": "hour",
        "hours": "hours"
    }

    # Replace possible common misspellings with the correct ones
    for wrong, correct in corrections.items():
        input_str = re.sub(rf'\b{wrong}\b', correct, input_str, flags=re.IGNORECASE)

    return input_str

def parse_user_input(user_input):
    user_input = correct_spelling(user_input.lower())  # Correct common spelling mistakes
    words = user_input.split()
    calories = None
    duration = None
    muscle_gain = "muscle" in words
    remove_exercise = None
    replace_exercise = None

    # Safety check: If time > 120 minutes or calories > 1500, show a warning
    for i in range(len(words) - 1):
        if words[i].isdigit():
            if "calorie" in words[i + 1]:
                calories = int(words[i])
                if calories > 1500:
                    print("Warning: Calorie input exceeds safe limits (1,500 calories). Please adjust your request.")
                    return None, None, None, None, None
            elif "minute" in words[i + 1] or "hour" in words[i + 1] or "hours" in words[i + 1]:
                duration = int(words[i])
                if duration > 120:
                    print("Warning: Duration exceeds safe limits (120 minutes). Please adjust your request.")
                    return None, None, None, None, None
        elif words[i] == "remove" and i + 1 < len(words):
            remove_exercise = words[i + 1].capitalize()
        elif words[i] == "replace" and i + 1 < len(words):
            replace_exercise = words[i + 1].capitalize()

    # If the input is valid, return the parsed values
    if muscle_gain and duration is not None:
        return None, duration, muscle_gain, remove_exercise, replace_exercise

    # If calories or duration are too high or not specified, return None
    if calories is None or duration is None:
        return None, None, None, None, None

    return calories, duration, muscle_gain, remove_exercise, replace_exercise

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


if __name__ == "__main__":
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

    while True:
        # Ask user for input
        user_request = input("Describe your workout goal: ")

        # Process input
        calories, duration, muscle_gain, remove_exercise, replace_exercise = parse_user_input(user_request)

        # If the input is invalid (either due to excessive calories or time), display an error message and ask again
        if calories is None or duration is None:
            continue  # Continue asking for valid input

        # Generate workout plan
        workout_plan = generate_workout(calories, duration, calorie_burn_exercises, muscle_gain_exercises, muscle_gain)

        # Display the workout plan
        print("\nGenerated Workout Plan:")
        print("\n".join(workout_plan))

        while True:
            modify = input("Do you want to modify the workout? (yes/no): ").strip().lower()
            if modify != "yes":
                break

            mod_request = input(
                "Describe your modification (e.g., 'remove Jump Rope' or 'replace Burpees with Push-ups'): ")
            _, _, _, remove_exercise, replace_exercise = parse_user_input(mod_request)

            if not remove_exercise:
                print("Please specify an exercise to remove.")
                continue

            # Modify workout plan
            workout_plan = modify_workout(workout_plan, remove_exercise, replace_exercise, calorie_burn_exercises,
                                          muscle_gain_exercises)

            # Display the updated workout plan
            print("\nUpdated Workout Plan:")
            print("\n".join(workout_plan))
