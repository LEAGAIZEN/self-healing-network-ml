import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="🛡️ Self-Healing Network Shield", 
    layout="wide", 
    page_icon="🛡️"
)

# --- CUSTOM CSS FOR "HACKER" AESTHETIC ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #00ff41;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/919/919825.png", width=80)
with col_title:
    st.title("Self-Healing Network Defense System")
    st.markdown("### Level 2 MLOps: Automated Drift Detection & Retraining")

st.divider()

# --- SIDEBAR: SIMULATION CONTROLS ---
st.sidebar.header("🕹️ Control Panel")

# 1. System Connectivity Check
if st.sidebar.button("📡 Check System Status"):
    try:
        res = requests.get(f"{API_URL}/")
        if res.status_code == 200:
            st.sidebar.success("✅ SYSTEM ONLINE")
        else:
            st.sidebar.error("❌ SYSTEM OFFLINE")
    except:
        st.sidebar.error("❌ CONNECTION FAILED")

st.sidebar.markdown("---")

# 2. DRIFT SIMULATION TRIGGER
st.sidebar.subheader("⚠ Threat Simulation")
st.sidebar.info("Click below to analyze recent traffic for concept drift.")

if st.sidebar.button("🔍 RUN DRIFT DIAGNOSTIC"):
    with st.spinner("🔄 Analyzing Traffic Patterns..."):
        try:
            # Call the API we built
            response = requests.get(f"{API_URL}/monitor-drift")
            data = response.json()
            
            # Scenario A: Drift Detected
            if data.get('status') == "Drift Detected":
                st.error("🚨 CRITICAL ALERT: CONCEPT DRIFT DETECTED")
                
                # Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.metric("Drift Score", "0.50", "CRITICAL", delta_color="inverse")
                m2.metric("Model Status", "Compromised", "Obsolete")
                m3.metric("Automated Action", "Retraining", "Triggered")
                
                # Visualizing the Healing Process
                with st.expander("Show Repair Logs", expanded=True):
                    st.write("🔄 System reacting to new attack vector...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "📥 Loading new attack signatures...",
                        "🧠 Retraining Random Forest Model...",
                        "💾 Saving new model weights...",
                        "✅ Deploying v2.0 Model..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        time.sleep(1.5) # Fake delay for demo effect
                        progress_bar.progress((i + 1) * 25)
                    
                st.success("✨ SELF-HEALING COMPLETE: System has adapted to the new attack.")
                st.balloons()
                
            # Scenario B: Stable
            else:
                st.success("✅ SYSTEM STABLE: No anomalies detected in data distribution.")
                st.json(data)

        except Exception as e:
            st.error(f"Failed to connect to Brain: {e}")

# --- MAIN DASHBOARD: LIVE TRAFFIC ---
st.subheader("📡 Live Network Traffic Monitor")

# Create two columns for charts
c1, c2 = st.columns([2, 1])

with c1:
    # Fake live data simulation for visual appeal
    live_data = pd.DataFrame({
        'Packet Sequence': range(20),
        'Packet Size (Bytes)': [120, 130, 125, 140, 450, 500, 520, 510, 130, 120, 125, 140, 120, 135, 122, 130, 145, 132, 128, 135]
    })
    st.line_chart(live_data.set_index('Packet Sequence'))
    st.caption("⚠️ Spikes (Lines 4-8) indicate potential DDoS or heavy payload attacks.")

with c2:
    st.subheader("🛡️ Defense Stats")
    st.info("Total Requests: **14,205**")
    st.warning("Attacks Blocked: **1,240**")
    st.success("System Uptime: **99.98%**")

# --- MANUAL PACKET INSPECTOR ---
st.divider()
st.subheader("🧪 Manual Packet Inspector")
st.write("Test the model with a raw network packet vector.")

# Default "Attack" Vector (example)
default_input = "0,1,0,45,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,0,255,255,1,0,0,0,0,0,0,0"
input_data = st.text_input("Enter 41 Features (Comma Separated):", default_input)

if st.button("🛡️ ANALYZE PACKET"):
    try:
        # Parse input
        features = [float(x) for x in input_data.split(",")]
        
        # Send to API
        payload = {"features": features}
        res = requests.post(f"{API_URL}/predict", json=payload)
        
        if res.status_code == 200:
            result = res.json()
            
            if result['prediction'] != 0:
                st.error(f"🚨 {result['status']} | Action: {result['action']}")
            else:
                st.success(f"✅ {result['status']} | Action: {result['action']}")
        else:
            st.error("Error: API rejected the data.")
            
    except Exception as e:
        st.error(f"Invalid Format: {e}")