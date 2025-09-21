import streamlit as st
import requests
from datetime import datetime
import pickle
import os
import streamlit as st
import requests
import pickle
import pandas as pd
from datetime import datetime

# Inject custom CSS for styling the app
st.markdown("""
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f0f2f5;
        color: #333;
        margin: 0;
    }
    .main-header {
        background-color: #4CAF50;
        color: white;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .input-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .results-section {
        background-color: #e9f5e9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .weather-info {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-top: 20px;
    }
    .weather-info img {
        width: 100px;
        height: 100px;
    }
    .forecast-table {
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stMarkdown h1 {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
    }
    .stMarkdown h2 {
        font-size: 2rem;
        color: #4CAF50;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# Load the machine learning model
try:
    with open('weather_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
except FileNotFoundError:
    st.error("Error: The weather prediction model file 'weather_model.pkl' was not found.")
    st.stop()
except ModuleNotFoundError:
    st.error("Error: The weather prediction model could not be loaded due to missing libraries. Please ensure 'scikit-learn' is installed.")
    st.stop()


# Streamlit app layout
st.title("Weather Prediction App")

st.header("Get Live Weather Data and Forecasts")

city = st.text_input("Enter a city name:", "New York")

if st.button("Get Weather"):
    # API URL and key (using a placeholder for security)
    api_key = "d1b58957827827d00465c4004733391b"
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    try:
        # Fetch current weather data
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        # Check for city not found error
        if weather_data.get("cod") == "404":
            st.error("City not found. Please check the spelling.")
        else:
            # Display current weather
            st.markdown(f"## Current Weather in {weather_data['name']}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Temperature: {weather_data['main']['temp']}°C")
                st.write(f"Feels Like: {weather_data['main']['feels_like']}°C")
                st.write(f"Humidity: {weather_data['main']['humidity']}%")
                st.write(f"Wind Speed: {weather_data['wind']['speed']} m/s")
            with col2:
                weather_icon = weather_data['weather'][0]['icon']
                icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
                st.image(icon_url, caption=weather_data['weather'][0]['description'].title())
                st.write(f"Condition: {weather_data['weather'][0]['description'].title()}")

            # Fetch and display 5-day weather forecast
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()

            if forecast_data.get("cod") == "200":
                st.markdown("---")
                st.markdown("## 5-Day Forecast (3-Hour Intervals)")

                # Create a list to hold the forecast data
                forecast_list = []

                # Use a set to track dates and only display one entry per day
                displayed_dates = set()

                for forecast in forecast_data['list']:
                    timestamp = forecast['dt']
                    forecast_datetime = datetime.fromtimestamp(timestamp)
                    date_str = forecast_datetime.strftime('%Y-%m-%d')
                    
                    # Only process one forecast per day to keep the table clean
                    if date_str not in displayed_dates:
                        displayed_dates.add(date_str)
                        forecast_list.append({
                            'Date': forecast_datetime.strftime('%A, %B %d'),
                            'Time': forecast_datetime.strftime('%I:%M %p'),
                            'Temperature (°C)': forecast['main']['temp'],
                            'Humidity (%)': forecast['main']['humidity'],
                            'Description': forecast['weather'][0]['description'].title(),
                        })

                # Create a DataFrame from the forecast list
                forecast_df = pd.DataFrame(forecast_list)
                st.table(forecast_df)
            else:
                st.warning("Could not retrieve forecast data.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")

# This will need to be in the same file as the above code.
# The user will need to add the model file to the app's directory.
# The `requirements.txt` file also needs to be in the app's directory to install dependencies.

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
        # Call the new function to get the 5-day forecast
        forecast_data = get_5_day_forecast(city)

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

# A helper function to get forecast data using the 2.5 API
def get_5_day_forecast(city):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        data = response.json()
        
        daily_forecasts = []
        # The API returns data in 3-hour intervals, so we'll grab one entry per day
        # We can identify daily entries by checking the time (e.g., around noon)
        dates_seen = set()
        for forecast in data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).strftime('%a, %b %d')
            if forecast_date not in dates_seen:
                daily_forecasts.append({
                    "date": forecast_date,
                    "temp_max": round(forecast['main']['temp_max']),
                    "temp_min": round(forecast['main']['temp_min']),
                    "icon": forecast['weather'][0]['icon'],
                    "description": forecast['weather'][0]['description'].title()
                })
                dates_seen.add(forecast_date)
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
        st.subheader("5-Day Forecast")
        forecast_cols = st.columns(len(weather["forecast"]))
        for i, day in enumerate(weather["forecast"]):
            with forecast_cols[i]:
                st.write(day['date'])
                st.image(f"http://openweathermap.org/img/wn/{day['icon']}@2x.png", width=50)
                st.write(f"High: {day['temp_max']}°C")
                st.write(f"Low: {day['temp_min']}°C")
        
