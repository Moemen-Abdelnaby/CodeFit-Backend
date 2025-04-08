
# Workout AI API

This is a simple Python-based API for generating custom workout plans based on user input, such as calorie goals, duration, and workout type (muscle gain or fat burn). It's designed to be used with a Flutter frontend.

## Features

- Generate calorie-burning workouts based on time and calorie targets
- Generate muscle gain workouts based on duration
- Modify workouts by removing or replacing exercises

## Setup

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run the API locally:

```
python app.py
```

3. The API will be available at `http://localhost:5000`.

## Deployment

To deploy this API on [Render](https://render.com):

1. Push this folder to a GitHub repository
2. Create a new Web Service on Render
3. Set the build and start command as:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. Choose Python environment and connect the repo

## API Endpoint

### `POST /generate_workout`

**Request JSON:**
```
{
  "message": "I want to burn 300 calories in 30 minutes"
}
```

**Response JSON:**
```
{
  "workout_plan": [
    "10 min of Jump Rope (~100 cal)",
    "10 min of Burpees (~100 cal)",
    "10 min of Mountain Climbers (~100 cal)"
  ]
}
```

## License

This project is open-source and free to use.
