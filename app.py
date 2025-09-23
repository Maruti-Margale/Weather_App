import streamlit as st
import requests
from datetime import datetime
import pickle
import os

# -------------------------------
# 🔧 Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="☀️",
    layout="wide",
)

# -------------------------------
# 🔐 API Key (Warning: Keep Safe)
# -------------------------------
API_KEY = "abc7e74fada486e88d6b22f5ce803319"

# -------------------------------
# 📦 Load ML Model (Optional)
# -------------------------------
try:
    with open('weather_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
    model_status = "✅ ML model loaded successfully."
except FileNotFoundError:
    model_status = "⚠️ weather_model.pkl not found. ML prediction disabled."
    ml_model = None

# -------------------------------
# 🌤️ Get Current Weather
# -------------------------------
def get_weather_data(city):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()

        # Timezone correction
        timezone_offset = data.get("timezone", 0)
        sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset).strftime("%I:%M %p")
        sunset = datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset).strftime("%I:%M %p")
        day_length_seconds = data["sys"]["sunset"] - data["sys"]["sunrise"]
        hours = day_length_seconds // 3600
        minutes = (day_length_seconds % 3600) // 60

        # Get forecast
        forecast_data = get_5_day_forecast(city)

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

# -------------------------------
# 📅 Get 5-Day Forecast (one per day)
# -------------------------------
def get_5_day_forecast(city):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        data = response.json()

        daily_forecasts = []
        dates_seen = set()
        for forecast in data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).strftime('%a, %b %d')
            if forecast_date not in dates_seen and len(daily_forecasts) < 5:
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


# -------------------------------
# 🖥️ UI Components
# -------------------------------
st.sidebar.title("🌍 Weather Dashboard")
st.sidebar.markdown(model_status)

# 🌆 City input
city = st.sidebar.text_input("Enter city name", value="Mumbai")
search = st.sidebar.button("🔍 Get Weather")

# 📅 Optional ML prediction
st.sidebar.markdown("### 🔮 Temperature Predictor")
pred_date = st.sidebar.date_input("Pick a date for prediction")
if st.sidebar.button("Predict Temperature"):
    prediction_result = predict_temperature(str(pred_date))
    st.sidebar.success(prediction_result)

# ----------------------------------
# 📊 Main Section: Weather Display
# ----------------------------------
if search:
    weather = get_weather_data(city)
    if "error" in weather:
        st.error(weather["error"])
    else:
        # Current Weather Header
        st.header(f"🌤️ Current Weather in {weather['city']}")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🌡️ Temperature", f"{weather['temp']}°C")
            st.write(f"Feels like: {weather['feels_like']}°C")
            st.write(f"📄 {weather['description']}")

        with col2:
            st.metric("💧 Humidity", f"{weather['humidity']}%")
            st.metric("💨 Wind Speed", f"{weather['wind_speed']} m/s")

        with col3:
            st.metric("🌅 Sunrise", weather['sunrise'])
            st.metric("🌇 Sunset", weather['sunset'])
            st.metric("🕒 Day Length", weather['day_length'])

        st.write("---")

        # Forecast
        st.subheader("📅 5-Day Forecast")
        forecast_cols = st.columns(len(weather["forecast"]))
        for i, day in enumerate(weather["forecast"]):
            with forecast_cols[i]:
                st.markdown(f"**{day['date']}**")
                st.image(f"http://openweathermap.org/img/wn/{day['icon']}@2x.png", width=60)
                st.write(f"🔼 {day['temp_max']}°C")
                st.write(f"🔽 {day['temp_min']}°C")
                st.caption(day["description"])
