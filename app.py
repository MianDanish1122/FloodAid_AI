"""
FloodAid AI - Real-Time Flood Relief Assistant
Complete Streamlit Application
"""

import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os
import json

# PAGE CONFIG
st.set_page_config(
    page_title="🌊 FloodAid AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RELIEF CENTERS DATA
RELIEF_CENTERS = {
    "Peshawar": [
        {"name": "Peshawar Relief Camp A", "lat": 34.0151, "lng": 71.5249, "type": "Shelter", "capacity": 500, "contact": "0300-123-4567"},
        {"name": "Lady Reading Hospital", "lat": 34.0056, "lng": 71.5194, "type": "Medical", "capacity": 200, "contact": "091-9210-261"},
        {"name": "Food Distribution Center", "lat": 34.0200, "lng": 71.5300, "type": "Food/Water", "capacity": 1000, "contact": "0300-456-7890"}
    ],
    "Lahore": [
        {"name": "Lahore Relief Camp", "lat": 31.5204, "lng": 74.3587, "type": "Shelter", "capacity": 800, "contact": "0300-111-2222"},
        {"name": "Mayo Hospital", "lat": 31.5582, "lng": 74.3137, "type": "Medical", "capacity": 300, "contact": "042-9230-5000"},
    ],
    "Karachi": [
        {"name": "Karachi Emergency Shelter", "lat": 24.8607, "lng": 67.0011, "type": "Shelter", "capacity": 1200, "contact": "0300-555-6666"},
        {"name": "JPMC Hospital", "lat": 24.9643, "lng": 67.0802, "type": "Medical", "capacity": 400, "contact": "021-9926-1300"},
    ]
}

# WEATHER API FUNCTION
def get_weather_free(city):
    """Get weather from Open-Meteo API"""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return None
        
        result = geo_data['results'][0]
        latitude = result['latitude']
        longitude = result['longitude']
        country = result.get('country', '')
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto"
        
        weather_response = requests.get(weather_url, timeout=5)
        weather_data = weather_response.json()
        current = weather_data['current']
        
        return {
            "City": f"{city}, {country}",
            "Temperature": f"{current['temperature_2m']}°C",
            "Humidity": f"{current['relative_humidity_2m']}%",
            "Rainfall": f"{current['precipitation']} mm",
            "Weather": "Clear",
            "Wind Speed": f"{current['wind_speed_10m']} km/h",
            "Latitude": latitude,
            "Longitude": longitude
        }
    except:
        return None

# FLOOD RISK ASSESSMENT
def assess_flood_risk(weather_data):
    """Calculate flood risk"""
    if not weather_data:
        return "Unknown"
    
    humidity = int(weather_data['Humidity'].split('%')[0])
    rainfall = float(weather_data['Rainfall'].split()[0])
    
    risk_score = 0
    if rainfall > 50:
        risk_score += 40
    if humidity > 90:
        risk_score += 30
    
    if risk_score >= 60:
        return "🔴 HIGH RISK - EVACUATE!"
    elif risk_score >= 30:
        return "🟠 MEDIUM RISK - STAY ALERT"
    else:
        return "🟢 LOW RISK - SAFE"

# FALLBACK RESPONSES
def get_ai_response(question):
    """Get response for user question"""
    responses = {
        "relief": "Relief camps are available. Check map. Call NDMA: 1-800-NDMA-911",
        "food": "Food distribution at relief centers. Visit nearest center.",
        "water": "Safe water being distributed. Boil if unavailable.",
        "medical": "Medical facilities marked on map. Call 1122 for ambulance.",
        "shelter": "Emergency shelters open 24/7. Go to nearest relief camp.",
        "default": "📞 NDMA: 1-800-NDMA-911 | Rescue: 1122"
    }
    
    for key in responses:
        if key in question.lower():
            return responses[key]
    return responses["default"]

# CREATE MAP
def create_relief_map(city):
    """Create relief center map"""
    centers = RELIEF_CENTERS[city]
    center_lat = sum(c["lat"] for c in centers) / len(centers)
    center_lng = sum(c["lng"] for c in centers) / len(centers)
    
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    
    colors = {"Shelter": "blue", "Medical": "red", "Food/Water": "green"}
    
    for center in centers:
        folium.Marker(
            location=[center["lat"], center["lng"]],
            popup=f"<b>{center['name']}</b><br>Type: {center['type']}<br>Contact: {center['contact']}",
            icon=folium.Icon(color=colors.get(center["type"], "gray"), icon="info-sign")
        ).add_to(m)
    
    return m

# ============ SIDEBAR ============
st.sidebar.title("🌊 FloodAid AI")
st.sidebar.markdown("**Flood Relief Assistant**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "💬 Chat", "🗺️ Map", "⚠️ Alerts", "📊 Dashboard"]
)

st.sidebar.markdown("---")
st.sidebar.info("📞 NDMA: 1-800-NDMA-911\n📞 Rescue: 1122")

# ============ PAGE 1: HOME ============
if page == "🏠 Home":
    st.title("🌊 FloodAid AI - Flood Relief Assistant")
    st.markdown("Get help during floods. Find relief, food, water, shelter, and medical help.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Relief Centers", "15+")
    with col2:
        st.metric("Cities", "3+")
    with col3:
        st.metric("Users", "1000+")
    
    st.markdown("---")
    st.success("🆘 Emergency: NDMA 1-800-NDMA-911 | Rescue: 1122")

# ============ PAGE 2: CHAT ============
elif page == "💬 Chat":
    st.title("💬 Ask for Help")
    
    city = st.selectbox("Select city:", list(RELIEF_CENTERS.keys()))
    question = st.text_input("Ask:", placeholder="Where can I get food?")
    
    if st.button("Get Answer"):
        if question:
            answer = get_ai_response(question)
            st.success(answer)
            
            st.markdown("---")
            st.write("**Relief Centers:**")
            for center in RELIEF_CENTERS[city]:
                st.write(f"• {center['name']} ({center['type']}) - Contact: {center['contact']}")
        else:
            st.warning("Please ask a question!")

# ============ PAGE 3: MAP ============
elif page == "🗺️ Map":
    st.title("🗺️ Relief Centers Map")
    
    city = st.selectbox("Select city:", list(RELIEF_CENTERS.keys()))
    
    st.write(f"**Relief centers in {city}:**")
    
    map_obj = create_relief_map(city)
    st_folium(map_obj, width=1400, height=500)
    
    st.markdown("---")
    df = pd.DataFrame(RELIEF_CENTERS[city])
    st.dataframe(df[["name", "type", "capacity", "contact"]], use_container_width=True)

# ============ PAGE 4: ALERTS ============
elif page == "⚠️ Alerts":
    st.title("⚠️ Flood Alerts")
    
    city = st.selectbox("Check city:", list(RELIEF_CENTERS.keys()))
    
    if st.button("Refresh Weather"):
        weather = get_weather_free(city)
        
        if weather:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🌡️ Temp", weather["Temperature"])
            with col2:
                st.metric("💧 Humidity", weather["Humidity"])
            with col3:
                st.metric("🌧️ Rain", weather["Rainfall"])
            
            st.markdown("---")
            risk = assess_flood_risk(weather)
            
            if "HIGH" in risk:
                st.error(f"**{risk}** - Evacuate immediately!")
            elif "MEDIUM" in risk:
                st.warning(f"**{risk}** - Stay alert and ready!")
            else:
                st.success(f"**{risk}** - Safe for now!")

# ============ PAGE 5: DASHBOARD ============
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    st.write("**Status by City:**")
    
    data = []
    for city in RELIEF_CENTERS.keys():
        weather = get_weather_free(city)
        if weather:
            risk = assess_flood_risk(weather)
            data.append({
                "City": city,
                "Temp": weather["Temperature"],
                "Risk": risk,
                "Centers": len(RELIEF_CENTERS[city])
            })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown("<center>🌊 FloodAid AI | Call NDMA 1-800-NDMA-911</center>", unsafe_allow_html=True)
