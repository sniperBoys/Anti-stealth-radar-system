import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Radar Simulation - Muhammad Hamza", layout="wide")

st.title("🛰️ Professional Radar Simulation")
st.markdown("**Inventor:** Muhammad Hamza | **Technology:** Signal Loss + TDOA")

# ==================== SESSION STATE ====================
if 'jet' not in st.session_state:
    st.session_state.jet = {
        'x': 50.0, 'y': 50.0,
        'vx': 0.0, 'vy': 0.0,
        'heading': 0.0,
        'speed': 0.0,
        'throttle': 0.5,
        'turn_rate': 0.0
    }
    st.session_state.time = 0.0
    st.session_state.dt = 0.1
    st.session_state.trail = []
    st.session_state.alerts = []
    st.session_state.radar_data = []
    st.session_state.signal_loss = {}
    st.session_state.running = False

# ==================== SIDEBAR CONTROLS ====================
st.sidebar.header("✈️ Aircraft Controls")
throttle = st.sidebar.slider("Throttle (%)", 0, 100, 50)
turn_input = st.sidebar.slider("Turn Rate (deg/s)", -30, 30, 0)
max_speed = st.sidebar.slider("Max Speed (m/s)", 200, 1000, 400)

st.sidebar.header("🛰️ Radar Settings")
num_radars = st.sidebar.slider("Number of Radars", 3, 8, 5)
detection_range = st.sidebar.slider("Detection Range (km)", 5, 40, 20)
area_size = st.sidebar.slider("Area Size (km)", 50, 200, 100)

st.sidebar.header("⚙️ Simulation")
sim_speed = st.sidebar.slider("Simulation Speed", 1, 10, 1)

# ==================== PHYSICS ENGINE ====================
def update_physics(jet, dt, throttle, turn_input, max_speed):
    """Aerodynamic physics update"""
    # Throttle se target speed
    target_speed = (throttle / 100.0) * max_speed
    
    # Acceleration (throttle - drag)
    drag = 0.001 * jet['speed']**2
    acceleration = (target_speed - jet['speed']) * 0.5 - drag
    
    # Speed update
    jet['speed'] = max(0, jet['speed'] + acceleration * dt)
    
    # Heading update (turn rate)
    jet['heading'] += turn_input * dt
    jet['heading'] = jet['heading'] % 360
    
    # Velocity components
    heading_rad = np.radians(jet['heading'])
    jet['vx'] = jet['speed'] * np.cos(heading_rad)
    jet['vy'] = jet['speed'] * np.sin(heading_rad)
    
    # Position update (convert m/s to km)
    jet['x'] += (jet['vx'] / 1000.0) * dt
    jet['y'] += (jet['vy'] / 1000.0) * dt
    
    # Boundary check
    jet['x'] = np.clip(jet['x'], 0, area_size)
    jet['y'] = np.clip(jet['y'], 0, area_size)
    
    return jet

# ==================== RADAR NETWORK ====================
radars = [
    {"name": "Skyblue", "x": 0, "y": 0, "color": "#00CED1"},
    {"name": "Red", "x": area_size/2, "y": 0, "color": "#FF4444"},
    {"name": "Green", "x": area_size, "y": area_size/2, "color": "#44FF44"},
    {"name": "Yellow", "x": 0, "y": area_size/2, "color": "#FFD700"},
    {"name": "Orange", "x": area_size, "y": 0, "color": "#FF8C00"}
][:num_radars]

# ==================== SIGNAL LOSS DETECTION ====================
def detect_signal_loss(jet, radars, detection_range, time):
    """Check which radars lost signal"""
    alerts = []
    for r in radars:
        dist = np.sqrt((jet['x'] - r['x'])**2 + (jet['y'] - r['y'])**2)
        if dist < detection_range:
            alerts.append({
                'time': round(time, 2),
                'radar': r['name'],
                'distance': round(dist, 2),
                'jet_x': round(jet['x'], 2),
                'jet_y': round(jet['y'], 2),
                'speed': round(jet['speed'], 2),
                'heading': round(jet['heading'], 1)
            })
    return alerts

# ==================== TDOA CALCULATION ====================
def calculate_tdoa(alerts):
    """Calculate TDOA between alerts"""
    if len(alerts) < 2:
        return None
    
    a1 = alerts[-2]
    a2 = alerts[-1]
    
    delta_t = a2['time'] - a1['time']
    delta_x = a2['jet_x'] - a1['jet_x']
    delta_y = a2['jet_y'] - a1['jet_y']
    distance = np.sqrt(delta_x**2 + delta_y**2)
    
    if delta_t > 0:
        calculated_speed = (distance * 1000) / delta_t
    else:
        calculated_speed = 0
    
    return {
        'delta_t': round(delta_t, 3),
        'distance': round(distance, 3),
        'calculated_speed': round(calculated_speed, 2),
        'actual_speed': a2['speed']
    }

# ==================== UPDATE LOOP ====================
if st.session_state.running:
    for _ in range(sim_speed):
        st.session_state.jet = update_physics(
            st.session_state.jet, st.session_state.dt,
            throttle, turn_input, max_speed
        )
        st.session_state.time += st.session_state.dt
        
        # Trail
        st.session_state.trail.append({
            'x': st.session_state.jet['x'],
            'y': st.session_state.jet['y']
        })
        
        # Alerts
        new_alerts = detect_signal_loss(
            st.session_state.jet, radars, detection_range,
            st.session_state.time
        )
        for a in new_alerts:
            if not any(al['radar'] == a['radar'] and 
                      abs(al['time'] - a['time']) < 0.5 
                      for al in st.session_state.alerts):
                st.session_state.alerts.append(a)

# ==================== LAYOUT ====================
col_main, col_data = st.columns([3, 1])

with col_main:
    # ===== MAIN RADAR SCREEN =====
    fig = go.Figure()
    
    # Radar detection circles
    for r in radars:
        theta = np.linspace(0, 2*np.pi, 100)
        fig.add_trace(go.Scatter(
            x=r['x'] + detection_range * np.cos(theta),
            y=r['y'] + detection_range * np.sin(theta),
            mode='lines',
            line=dict(color=r['color'], width=1, dash='dot'),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Radars
    for r in radars:
        fig.add_trace(go.Scatter(
            x=[r['x']], y=[r['y']],
            mode='markers+text',
            marker=dict(size=25, color=r['color'], symbol='triangle-up',
                       line=dict(width=2, color='white')),
            text=[r['name']],
            textposition="top center",
            textfont=dict(color='white', size=12),
            name=r['name'],
            showlegend=True
        ))
    
    # Radar waves (signal lines to jet)
    for r in radars:
        dist = np.sqrt((st.session_state.jet['x'] - r['x'])**2 + 
                      (st.session_state.jet['y'] - r['y'])**2)
        if dist < detection_range:
            # Signal loss - dashed line
            fig.add_trace(go.Scatter(
                x=[r['x'], st.session_state.jet['x']],
                y=[r['y'], st.session_state.jet['y']],
                mode='lines',
                line=dict(color=r['color'], width=2, dash='dot'),
                opacity=0.5,
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Jet trail
    if len(st.session_state.trail) > 1:
        trail_x = [t['x'] for t in st.session_state.trail]
        trail_y = [t['y'] for t in st.session_state.trail]
        fig.add_trace(go.Scatter(
            x=trail_x, y=trail_y,
            mode='lines',
            line=dict(color='cyan', width=2),
            name='Trail',
            opacity=0.6
        ))
    
    # Jet
    heading_rad = np.radians(st.session_state.jet['heading'])
    fig.add_trace(go.Scatter(
        x=[st.session_state.jet['x']],
        y=[st.session_state.jet['y']],
        mode='markers+text',
        marker=dict(size=20, color='white', symbol='arrow',
                   angle=st.session_state.jet['heading'],
                   line=dict(width=2, color='cyan')),
        text=["✈️"],
        textposition="top center",
        name='Jet',
        showlegend=True
    ))
    
    # Layout
    fig.update_layout(
        xaxis=dict(range=[-5, area_size+5], title="X (km)",
                  showgrid=True, gridcolor='#333', color='white'),
        yaxis=dict(range=[-5, area_size+5], title="Y (km)",
                  showgrid=True, gridcolor='#333', color='white'),
        height=650,
        plot_bgcolor='#0a0a1a',
        paper_bgcolor='#1a1a2e',
        font=dict(color='white'),
        hovermode='closest',
        dragmode='pan'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Control buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶️ START" if not st.session_state.running else "⏸️ PAUSE"):
            st.session_state.running = not st.session_state.running
            st.rerun()
    with c2:
        if st.button("🔄 RESET"):
            st.session_state.jet = {
                'x': 50.0, 'y': 50.0, 'vx': 0.0, 'vy': 0.0,
                'heading': 0.0, 'speed': 0.0, 'throttle': 0.5, 'turn_rate': 0.0
            }
            st.session_state.time = 0.0
            st.session_state.trail = []
            st.session_state.alerts = []
            st.session_state.running = False
            st.rerun()
    with c3:
        st.metric("Time", f"{st.session_state.time:.1f} s")

with col_data:
    # ===== LIVE DATA PANEL =====
    st.header("📊 Live Data")
    
    jet = st.session_state.jet
    st.metric("Position X", f"{jet['x']:.2f} km")
    st.metric("Position Y", f"{jet['y']:.2f} km")
    st.metric("Speed", f"{jet['speed']:.1f} m/s")
    st.metric("Heading", f"{jet['heading']:.1f}°")
    
    st.markdown("---")
    st.header("🚨 Alerts")
    st.metric("Total Alerts", len(st.session_state.alerts))
    
    if st.session_state.alerts:
        latest = st.session_state.alerts[-1]
        st.error(f"⚠️ {latest['radar']} Radar\n"
                f"Dist: {latest['distance']} km\n"
                f"Time: {latest['time']} s")

# ==================== TDOA PANEL ====================
st.markdown("---")
st.header("📐 TDOA Calculation (Doosre Radar Se)")

tdoa = calculate_tdoa(st.session_state.alerts)

if tdoa:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Time Diff (Δt)", f"{tdoa['delta_t']} s")
    with c2:
        st.metric("Distance", f"{tdoa['distance']} km")
    with c3:
        st.metric("Calculated Speed", f"{tdoa['calculated_speed']} m/s")
    with c4:
        st.metric("Actual Speed", f"{tdoa['actual_speed']} m/s")
else:
    st.info("⏳ Waiting for 2+ alerts to calculate TDOA...")

# ==================== DATA COLLECTION ====================
st.markdown("---")
st.header("📁 Data Collection")

if st.session_state.alerts:
    df = pd.DataFrame(st.session_state.alerts)
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data (CSV)",
        data=csv,
        file_name=f"radar_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("No alerts yet. Start simulation!")

# ==================== AUTO REFRESH ====================
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()
