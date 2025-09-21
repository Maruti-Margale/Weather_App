from flask import Flask, render_template, request
import requests
from datetime import datetime
import pickle
import os

app = Flask(__name__)

# Replace with your actual API key
# Warning: Do not use this key in a production environment, as it's publicly visible.
API_KEY = "abc7e74fada486e88d6b22f5ce803319"

# Load the trained ML model if it exists
try:
    with open('weather_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
    print("Machine learning model loaded successfully.")
except FileNotFoundError:
    print("Warning: weather_model.pkl not found. Prediction features will not work.")
    ml_model = None

def get_weather_data(city):
    """
    Fetches current weather data for a given city from the OpenWeatherMap API.
    """
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()

        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%I:%M %p")
        day_length_seconds = data["sys"]["sunset"] - data["sys"]["sunrise"]
        hours = day_length_seconds // 3600
        minutes = (day_length_seconds % 3600) // 60

        return {
            "city": data["name"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "sunrise": sunrise,
            "sunset": sunset,
            "day_length": f"{hours}h {minutes}m",
            "wind_speed": data["wind"]["speed"],
            "temp_max": round(data["main"]["temp_max"]),
            "temp_min": round(data["main"]["temp_min"]),
            "pressure": data["main"]["pressure"] # Added pressure for potential ML features
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to weather service: {e}"}
    except KeyError:
        return {"error": "City not found!"}

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders the main page and handles city search.
    """
    city = request.form.get("city") or "Kathmandu"
    weather = get_weather_data(city)
    return render_template("index.html", weather=weather)

# Example route for future ML prediction (requires a trained model and a form)
@app.route("/predict", methods=["POST"])
def predict():
    if ml_model is None:
        return {"error": "Prediction model not available."}, 503

    try:
        # Example of getting data from a form
        input_date_str = request.form.get("prediction_date")
        input_date = datetime.strptime(input_date_str, "%Y-%m-%d")
        
        # You would need to get all features your model was trained on
        # This is a placeholder; in a real app, you would need more data
        features = [[input_date.month, input_date.day]] 
        
        predicted_temp = round(ml_model.predict(features)[0])
        return {"predicted_temp": predicted_temp}
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}, 400

if __name__ == "__main__":
    app.run(debug=True)