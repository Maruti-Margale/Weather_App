import streamlit as st
import requests
from datetime import datetime
import pickle
import os

# Set up the Streamlit page
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="☀️",
    layout="wide",
)

# Replace with your actual API key
# Warning: Do not use this key in a production environment, as it's publicly visible.
API_KEY = "abc7e74fada486e88d6b22f5ce803319"

# Load the trained ML model if it exists
try:
    with open('weather_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
    model_status = "Model loaded successfully."
except FileNotFoundError:
    model_status = "Warning: weather_model.pkl not found. Prediction features will not work."
    ml_model = None

# A helper function to fetch weather data
def get_weather_data(city):
    """
    Fetches current weather data for a given city from the OpenWeatherMap API.
    """
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        forecast_data = get_daily_forecast(lat, lon)

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
            "pressure": data["main"]["pressure"],
            "forecast": forecast_data
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to weather service: {e}"}
    except KeyError:
        return {"error": "City not found!"}

# A helper function to get forecast data
def get_daily_forecast(lat, lon):
    forecast_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&exclude=minutely,hourly,alerts"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        data = response.json()
        forecasts = data['daily'][:10]
        daily_forecasts = []
        for day in forecasts:
            daily_forecasts.append({
                "date": datetime.fromtimestamp(day['dt']).strftime('%a, %b %d'),
                "temp_max": round(day['temp']['max']),
                "temp_min": round(day['temp']['min']),
                "icon": day['weather'][0]['icon'],
                "description": day['weather'][0]['description'].title()
            })
        return daily_forecasts
    except (requests.exceptions.RequestException, KeyError) as e:
        st.error(f"Error fetching forecast data: {e}")
        return []

# --- UI Components and Logic ---

st.sidebar.title("Weather Dashboard")
st.sidebar.markdown(model_status)

# User input for city
city = st.sidebar.text_input("Enter a city", "Kathmandu")
search_button = st.sidebar.button("Get Weather")

# --- Display current weather ---
if search_button:
    weather = get_weather_data(city)
    
    if "error" in weather:
        st.error(weather["error"])
    else:
        st.header(f"Weather for {weather['city']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temperature", f"{weather['temp']}°C")
            st.write(f"Feels like: {weather['feels_like']}°C")
            st.write(f"Description: {weather['description']}")
        
        with col2:
            st.metric("Humidity", f"{weather['humidity']}%")
            st.metric("Wind Speed", f"{weather['wind_speed']} m/s")
        
        with col3:
            st.metric("Sunrise", weather['sunrise'])
            st.metric("Sunset", weather['sunset'])
            
        st.write("---")
        
        # --- Display forecast ---
        st.subheader("10-Day Forecast")
        forecast_cols = st.columns(10)
        for i, day in enumerate(weather["forecast"]):
            with forecast_cols[i]:
                st.write(day['date'])
                st.image(f"http://openweathermap.org/img/wn/{day['icon']}@2x.png", width=50)
                st.write(f"High: {day['temp_max']}°C")
                st.write(f"Low: {day['temp_min']}°C")
        
        # --- Display ML Prediction ---
        st.write("---")
        st.subheader("Predict Future Temperature")
        if ml_model:
            prediction_date_str = st.date_input("Select a date for prediction")
            predict_button = st.button("Predict")
            
            if predict_button:
                prediction_date = prediction_date_str
                features = [[prediction_date.month, prediction_date.timetuple().tm_yday]]
                predicted_temp = round(ml_model.predict(features)[0])
                st.success(f"Predicted Temperature for {prediction_date}: {predicted_temp}°C")
        else:
            st.warning(model_status)
