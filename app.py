import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

st.set_page_config(page_title="Radar System - Muhammad Hamza", layout="wide")

st.title("🛰️ Networked Radar System for Stealth Detection")
st.markdown("**Inventor:** Muhammad Hamza")
st.markdown("**Technology:** Signal Loss Detection + TDOA")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Settings")
num_radars = st.sidebar.slider("Number of Radars", 3, 8, 5)
area_size = st.sidebar.slider("Area Size (km)", 20, 100, 50)
jet_speed = st.sidebar.slider("Jet Speed (m/s)", 100, 1000, 300)
steps = st.sidebar.slider("Simulation Steps", 20, 100, 50)

# Radars ki position
radars = np.array([
    [0, 0],
    [area_size/2, 0],
    [area_size, area_size/2],
    [0, area_size/2],
    [area_size, 0]
])

radar_names = ["Skyblue", "Red", "Green", "Yellow", "Orange"]
radar_colors = ["cyan", "red", "green", "yellow", "orange"]

# Jet ka path
jet_x = np.linspace(0, area_size, steps)
jet_y = np.sin(jet_x / 10) * 15 + area_size/2

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📍 Radar Network Visualization")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Radars
    for i, (r, name, color) in enumerate(zip(radars, radar_names, radar_colors)):
        if i < num_radars:
            ax.scatter(r[0], r[1], c=color, s=300, marker='^', 
                      label=f'Radar {i+1} ({name})', edgecolors='black', linewidth=2)
            ax.annotate(name, (r[0], r[1]), textcoords="offset points", 
                       xytext=(0,15), ha='center', fontweight='bold')
    
    # Jet path
    ax.plot(jet_x, jet_y, 'b--', linewidth=2, label='Jet Path')
    ax.scatter(jet_x[0], jet_y[0], c='blue', s=150, marker='>', label='Jet Start')
    ax.scatter(jet_x[-1], jet_y[-1], c='blue', s=150, marker='<', label='Jet End')
    
    # Signal lines
    for i, r in enumerate(radars):
        if i < num_radars:
            for j in range(0, steps, 5):
                ax.plot([r[0], jet_x[j]], [r[1], jet_y[j]], 
                       color=radar_colors[i], alpha=0.15, linewidth=0.5)
    
    ax.set_xlabel("X Position (km)", fontsize=12)
    ax.set_ylabel("Y Position (km)", fontsize=12)
    ax.set_title("Networked Radar System - Muhammad Hamza", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-5, area_size + 5)
    ax.set_ylim(-5, area_size + 5)
    
    st.pyplot(fig)

with col2:
    st.header("🚨 Alert System")
    
    alerts = []
    for i, r in enumerate(radars):
        if i < num_radars:
            for j in range(steps):
                dist = np.sqrt((jet_x[j] - r[0])**2 + (jet_y[j] - r[1])**2)
                if dist < 10:
                    alerts.append({
                        "Radar": radar_names[i],
                        "Step": j,
                        "Distance (km)": round(dist, 2)
                    })
    
    if alerts:
        st.error(f"⚠️ {len(alerts)} Alerts Generated!")
        df = pd.DataFrame(alerts)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("✅ No Alerts - Area Clear")

# TDOA Calculation
st.markdown("---")
st.header("📊 TDOA Calculation (Speed Detection)")

if len(alerts) >= 2:
    t1 = alerts[0]["Step"]
    t2 = alerts[1]["Step"]
    delta_t = abs(t2 - t1) * 0.01  # seconds
    c = 3e8  # speed of light
    distance = c * delta_t
    
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Alert 1 Time", f"{t1} steps")
    with col4:
        st.metric("Alert 2 Time", f"{t2} steps")
    with col5:
        st.metric("Time Difference", f"{delta_t:.4f} s")
    
    st.info(f"📐 Calculated Distance: {distance:.2f} meters")
    st.info(f"✈️ Jet Speed: {jet_speed} m/s (user defined)")

# Info
st.markdown("---")
st.markdown("""
### 📖 How It Works
1. **5 Radars** border par lagayi gayi hain
2. Har radar **apna signal** bhejta hai
3. Har radar **doosre radars ka signal** bhi observe karta hai
4. Jab **stealth jet** signal ko absorb karti hai
5. **Signal loss** detect hota hai
6. **Alert** generate hota hai
7. **TDOA** se speed calculate hoti hai

**Inventor:** Muhammad Hamza  
**Technology:** Signal Loss Detection + TDOA
""")
