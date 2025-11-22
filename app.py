"""
FloodAid AI - Super Simple Working Version
NO Urdu, NO Folium, NO Complex Code
ONLY Streamlit + Requests
"""

import streamlit as st
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(
    page_title="FloodAid AI",
    page_icon="🌊",
    layout="wide"
)

# RELIEF CENTERS DATA (Simple)
RELIEF_CENTERS = {
    "Peshawar": [
        {"name": "Peshawar Relief Camp A", "type": "Shelter", "contact": "0300-123-4567"},
        {"name": "Lady Reading Hospital", "type": "Medical", "contact": "091-9210-261"},
        {"name": "Food Distribution Center", "type": "Food/Water", "contact": "0300-456-7890"}
    ],
    "Lahore": [
        {"name": "Lahore Relief Camp", "type": "Shelter", "contact": "0300-111-2222"},
        {"name": "Mayo Hospital", "type": "Medical", "contact": "042-9230-5000"},
    ],
    "Karachi": [
        {"name": "Karachi Emergency Shelter", "type": "Shelter", "contact": "0300-555-6666"},
        {"name": "JPMC Hospital", "type": "Medical", "contact": "021-9926-1300"},
    ]
}

# AI RESPONSES
def get_response(question):
    q = question.lower()
    
    if "food" in q or "eat" in q or "hunger" in q:
        return "Food distribution is happening at relief centers. Visit the nearest center. Call NDMA: 1-800-NDMA-911"
    elif "medical" in q or "hospital" in q or "doctor" in q or "sick" in q:
        return "Medical facilities are available. Call 1122 for ambulance or go to nearest hospital."
    elif "shelter" in q or "stay" in q or "home" in q:
        return "Emergency shelters are open 24/7. Go to nearest relief camp. Check the map."
    elif "water" in q or "drink" in q:
        return "Safe water is being distributed at relief centers. Boil water before drinking if unavailable."
    elif "flood" in q or "danger" in q or "risk" in q:
        return "Check Alerts page to see current flood risk. Call 1122 for emergency."
    else:
        return "Contact NDMA: 1-800-NDMA-911 or Rescue: 1122 for immediate help."

# GET WEATHER (Simple version - no error handling complexity)
def get_weather(city):
    try:
        # Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return None
        
        lat = geo_data['results'][0]['latitude']
        lng = geo_data['results'][0]['longitude']
        
        # Get weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,precipitation"
        weather_response = requests.get(weather_url, timeout=5)
        weather_data = weather_response.json()
        current = weather_data['current']
        
        return {
            "temp": current['temperature_2m'],
            "humidity": current['relative_humidity_2m'],
            "rainfall": current['precipitation']
        }
    except:
        return None

# ASSESS FLOOD RISK
def get_risk_level(weather):
    if not weather:
        return "Unknown"
    
    humidity = weather['humidity']
    rainfall = weather['rainfall']
    
    if rainfall > 50 or humidity > 90:
        return "🔴 HIGH RISK - EVACUATE IMMEDIATELY"
    elif rainfall > 20 or humidity > 75:
        return "🟠 MEDIUM RISK - STAY ALERT"
    else:
        return "🟢 LOW RISK - SAFE"

# ============ SIDEBAR ============
st.sidebar.title("🌊 FloodAid AI")
st.sidebar.markdown("**Flood Relief Assistant**")
st.sidebar.markdown("For Pakistan")
st.sidebar.markdown("---")

# NAVIGATION
page = st.sidebar.radio(
    "Choose:",
    ["🏠 Home", "💬 Chat", "🗺️ Centers", "⚠️ Weather", "📊 Status"]
)

st.sidebar.markdown("---")
st.sidebar.error("🚨 EMERGENCY")
st.sidebar.write("📞 NDMA: 1-800-NDMA-911")
st.sidebar.write("📞 Rescue: 1122")
st.sidebar.write("📱 SMS: HELP to 8282")

# ============ PAGE 1: HOME ============
if page == "🏠 Home":
    st.title("🌊 FloodAid AI")
    st.write("Get help during floods in Pakistan")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Relief Centers", "10+")
    with col2:
        st.metric("Cities", "3")
    with col3:
        st.metric("Available", "24/7")
    
    st.markdown("---")
    st.subheader("What Can I Do?")
    st.write("✅ Chat - Ask questions")
    st.write("✅ Centers - Find relief camps")
    st.write("✅ Weather - Check flood warning")
    st.write("✅ Status - See all cities")
    
    st.markdown("---")
    st.success("🆘 Emergency? Call 1122 or NDMA: 1-800-NDMA-911")

# ============ PAGE 2: CHAT ============
elif page == "💬 Chat":
    st.title("💬 Ask for Help")
    
    city = st.selectbox("Your city:", list(RELIEF_CENTERS.keys()))
    question = st.text_input("Ask your question:", placeholder="e.g., Where can I get food?")
    
    if st.button("Get Answer"):
        if question:
            answer = get_response(question)
            st.success(answer)
            
            st.markdown("---")
            st.subheader("Relief Centers in " + city)
            
            for center in RELIEF_CENTERS[city]:
                st.write(f"**{center['name']}**")
                st.write(f"Type: {center['type']}")
                st.write(f"📞 {center['contact']}")
                st.write("---")
        else:
            st.warning("Please ask a question!")

# ============ PAGE 3: CENTERS ============
elif page == "🗺️ Centers":
    st.title("🗺️ Relief Centers")
    
    city = st.selectbox("Choose city:", list(RELIEF_CENTERS.keys()))
    
    st.subheader(f"Centers in {city}")
    
    for i, center in enumerate(RELIEF_CENTERS[city], 1):
        st.write(f"**{i}. {center['name']}**")
        st.write(f"   📍 Type: {center['type']}")
        st.write(f"   📞 Contact: {center['contact']}")
        st.write("")

# ============ PAGE 4: WEATHER ============
elif page == "⚠️ Weather":
    st.title("⚠️ Flood Warning")
    
    city = st.selectbox("Check city:", list(RELIEF_CENTERS.keys()))
    
    if st.button("Check Weather Now"):
        weather = get_weather(city)
        
        if weather:
            st.write(f"**Current Weather in {city}:**")
            st.write("")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("🌡️ Temperature")
                st.write(f"{weather['temp']}°C")
            with col2:
                st.write("💧 Humidity")
                st.write(f"{weather['humidity']}%")
            with col3:
                st.write("🌧️ Rainfall")
                st.write(f"{weather['rainfall']} mm")
            
            st.markdown("---")
            
            risk = get_risk_level(weather)
            
            if "HIGH" in risk:
                st.error(f"**{risk}**")
                st.warning("❌ EVACUATE IMMEDIATELY!")
                st.write("Call 1122 for emergency help")
            elif "MEDIUM" in risk:
                st.warning(f"**{risk}**")
                st.write("⚠️ Get ready to evacuate")
                st.write("Keep emergency items packed")
            else:
                st.success(f"**{risk}**")
                st.write("✅ Safe for now")
                st.write("Keep monitoring weather")
        else:
            st.error("Cannot get weather. Check internet connection.")

# ============ PAGE 5: STATUS ============
elif page == "📊 Status":
    st.title("📊 Status by City")
    
    st.write("**Real-time Status:**")
    st.write("")
    
    for city in RELIEF_CENTERS.keys():
        weather = get_weather(city)
        
        if weather:
            risk = get_risk_level(weather)
            centers = len(RELIEF_CENTERS[city])
            
            st.write(f"**{city}**")
            st.write(f"  Temp: {weather['temp']}°C | Risk: {risk} | Centers: {centers}")
        else:
            st.write(f"**{city}** - Cannot get weather")
        
        st.write("")

# ============ FOOTER ============
st.markdown("---")
st.markdown("<center>🌊 FloodAid AI - Flood Relief Assistant</center>", unsafe_allow_html=True)
st.markdown("<center>Emergency: Call 1122 | NDMA: 1-800-NDMA-911</center>", unsafe_allow_html=True)
