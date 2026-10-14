import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Radar Game - Muhammad Hamza", layout="wide")

st.title("🎮 Radar Game - Muhammad Hamza")
st.markdown("**Apni finger se jet ko move karein aur radar aapko track karega!**")
st.markdown("---")

# Session state initialize
if 'jet_x' not in st.session_state:
    st.session_state.jet_x = 50
    st.session_state.jet_y = 50
    st.session_state.prev_x = 50
    st.session_state.prev_y = 50
    st.session_state.speed_history = []
    st.session_state.alert_history = []
    st.session_state.start_time = time.time()

# Sidebar
st.sidebar.header("⚙️ Radar Settings")
area_size = st.sidebar.slider("Area Size (km)", 20, 100, 100)
detection_range = st.sidebar.slider("Radar Detection Range (km)", 5, 30, 15)

# 5 Radars ki position (border par)
radars = [
    {"name": "Skyblue", "x": 0, "y": 0, "color": "cyan"},
    {"name": "Red", "x": area_size/2, "y": 0, "color": "red"},
    {"name": "Green", "x": area_size, "y": area_size/2, "color": "green"},
    {"name": "Yellow", "x": 0, "y": area_size/2, "color": "yellow"},
    {"name": "Orange", "x": area_size, "y": 0, "color": "orange"}
]

# Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.header("📍 Radar Screen - Touch to Move Jet")
    
    # Plotly figure
    fig = go.Figure()
    
    # Radars plot
    for r in radars:
        fig.add_trace(go.Scatter(
            x=[r["x"]], y=[r["y"]],
            mode='markers+text',
            marker=dict(size=25, color=r["color"], symbol='triangle-up', 
                       line=dict(width=2, color='black')),
            text=[r["name"]],
            textposition="top center",
            name=f'Radar {r["name"]}',
            showlegend=True
        ))
    
    # Radar detection circles
    for r in radars:
        theta = np.linspace(0, 2*np.pi, 100)
        x_circle = r["x"] + detection_range * np.cos(theta)
        y_circle = r["y"] + detection_range * np.sin(theta)
        fig.add_trace(go.Scatter(
            x=x_circle, y=y_circle,
            mode='lines',
            line=dict(color=r["color"], width=1, dash='dot'),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Jet position
    fig.add_trace(go.Scatter(
        x=[st.session_state.jet_x], y=[st.session_state.jet_y],
        mode='markers+text',
        marker=dict(size=30, color='blue', symbol='x',
                   line=dict(width=3, color='darkblue')),
        text=["✈️ JET"],
        textposition="top center",
        name='Jet',
        showlegend=True
    ))
    
    # Jet trail (speed history)
    if len(st.session_state.speed_history) > 0:
        trail_x = [h['x'] for h in st.session_state.speed_history]
        trail_y = [h['y'] for h in st.session_state.speed_history]
        fig.add_trace(go.Scatter(
            x=trail_x, y=trail_y,
            mode='lines',
            line=dict(color='blue', width=2, dash='dash'),
            name='Jet Trail',
            opacity=0.5
        ))
    
    # Layout
    fig.update_layout(
        xaxis=dict(range=[-10, area_size+10], title="X (km)", 
                  showgrid=True, gridcolor='lightgray'),
        yaxis=dict(range=[-10, area_size+10], title="Y (km)", 
                  showgrid=True, gridcolor='lightgray'),
        height=600,
        plot_bgcolor='#0a0a1a',
        paper_bgcolor='#1a1a2e',
        font=dict(color='white'),
        hovermode='closest',
        dragmode='pan'
    )
    
    # Click event
    clicked = plotly_events(fig, click_event=True, key="radar_click")
    
    if clicked:
        new_x = clicked[0]['x']
        new_y = clicked[0]['y']
        
        # Distance calculate
        dist = np.sqrt((new_x - st.session_state.jet_x)**2 + 
                      (new_y - st.session_state.jet_y)**2)
        
        # Time calculate
        current_time = time.time()
        time_diff = current_time - st.session_state.start_time
        
        # Speed calculate (km/s)
        if time_diff > 0:
            speed = dist / time_diff if time_diff > 0 else 0
        else:
            speed = 0
        
        # Update jet position
        st.session_state.prev_x = st.session_state.jet_x
        st.session_state.prev_y = st.session_state.jet_y
        st.session_state.jet_x = new_x
        st.session_state.jet_y = new_y
        st.session_state.start_time = current_time
        
        # Speed history
        st.session_state.speed_history.append({
            'x': new_x, 'y': new_y, 'speed': speed, 'time': current_time
        })
        
        # Radar detection check
        for r in radars:
            radar_dist = np.sqrt((new_x - r["x"])**2 + (new_y - r["y"])**2)
            if radar_dist < detection_range:
                alert = {
                    'radar': r["name"],
                    'distance': round(radar_dist, 2),
                    'jet_x': round(new_x, 2),
                    'jet_y': round(new_y, 2),
                    'time': round(current_time, 2)
                }
                if alert not in st.session_state.alert_history:
                    st.session_state.alert_history.append(alert)
        
        st.rerun()

with col2:
    st.header("📊 Live Tracking")
    
    # Current position
    st.metric("Jet X", f"{st.session_state.jet_x:.1f} km")
    st.metric("Jet Y", f"{st.session_state.jet_y:.1f} km")
    
    # Current speed
    if len(st.session_state.speed_history) > 0:
        current_speed = st.session_state.speed_history[-1]['speed']
        st.metric("Jet Speed", f"{current_speed:.2f} km/s")
    else:
        st.metric("Jet Speed", "0.00 km/s")
    
    st.markdown("---")
    
    # Alert System
    st.header("🚨 Radar Alerts")
    if st.session_state.alert_history:
        for alert in st.session_state.alert_history[-5:]:
            st.error(f"⚠️ {alert['radar']} Radar detected Jet!\n"
                    f"Distance: {alert['distance']} km")
    else:
        st.success("✅ No Alerts - Jet Not Detected")
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset Game"):
        st.session_state.jet_x = 50
        st.session_state.jet_y = 50
        st.session_state.speed_history = []
        st.session_state.alert_history = []
        st.session_state.start_time = time.time()
        st.rerun()

# Statistics
st.markdown("---")
st.header("📈 Statistics")

col3, col4, col5 = st.columns(3)

with col3:
    total_distance = 0
    for i in range(1, len(st.session_state.speed_history)):
        prev = st.session_state.speed_history[i-1]
        curr = st.session_state.speed_history[i]
        total_distance += np.sqrt((curr['x']-prev['x'])**2 + (curr['y']-prev['y'])**2)
    st.metric("Total Distance", f"{total_distance:.2f} km")

with col4:
    st.metric("Total Alerts", len(st.session_state.alert_history))

with col5:
    if len(st.session_state.speed_history) > 0:
        avg_speed = np.mean([h['speed'] for h in st.session_state.speed_history])
        st.metric("Average Speed", f"{avg_speed:.2f} km/s")
    else:
        st.metric("Average Speed", "0.00 km/s")

# Instructions
st.markdown("---")
st.markdown("""
### 🎮 How to Play
1. **Tap anywhere on the radar screen** to move the jet
2. Radar will **automatically track** your jet
3. **Speed, distance, alerts** will be calculated live
4. **5 Radars** will detect your jet if you get close
5. Try to **avoid radar detection**!

**Inventor:** Muhammad Hamza  
**Technology:** Signal Loss Detection + TDOA
""")
