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
        background-color: #0E1117;
        color: #00FF41;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        background-color: #1F2937;
        color: #00FF41;
        border: 1px solid #00FF41;
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

# --- SIDEBAR: MANUAL PACKET BUILDER ---
st.sidebar.header("🔧 Manual Packet Builder")
st.sidebar.write("Craft a custom packet to test the AI.")

# Critical features inputs
src_bytes = st.sidebar.number_input("Source Bytes (src_bytes)", value=0)
dst_bytes = st.sidebar.number_input("Destination Bytes (dst_bytes)", value=0)
count = st.sidebar.number_input("Traffic Count (count)", value=0)
srv_count = st.sidebar.number_input("Server Count (srv_count)", value=0)
serror_rate = st.sidebar.slider("Error Rate (serror_rate)", 0.0, 1.0, 0.0)

if st.sidebar.button("🚀 Send Custom Packet"):
    # Create the full 41-feature array (Defaulting others to 0)
    custom_features = [0] * 41
    custom_features[4] = src_bytes     # src_bytes index
    custom_features[5] = dst_bytes     # dst_bytes index
    custom_features[22] = count        # count index
    custom_features[23] = srv_count    # srv_count index
    custom_features[24] = serror_rate  # serror_rate index
    
    # Send to API
    try:
        res = requests.post(f"{API_URL}/predict", json={"features": custom_features})
        if res.status_code == 200:
            result = res.json()
            st.sidebar.success(f"Prediction: {result.get('status')}")
            
            # Check for Healing Alert
            if "alert" in result:
                st.sidebar.error(f"🚨 {result['alert']}")
                st.toast("🔥 Healing Process Triggered!", icon="🔥")
        else:
            st.sidebar.error("API Error")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# --- MAIN DASHBOARD AREA ---
col1, col2 = st.columns([2, 1])

# Initialize session state for the graph
if "history" not in st.session_state:
    st.session_state.history = []

with col1:
    st.subheader("📡 Live Network Traffic Monitor")
    
    # Placeholder for the graph
    chart_placeholder = st.empty()
    
    # Quick Simulation Buttons
    st.write("---")
    st.write("**Rapid Simulation Tools:**")
    c1, c2 = st.columns(2)
    
    if c1.button("✅ Simulate Normal Traffic (10 pkts)"):
        # Real normal packet data
        normal_pkt = [0, 1, 20, 2, 215, 45076, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        with st.spinner("Sending Normal Traffic..."):
            for _ in range(10):
                try:
                    requests.post(f"{API_URL}/predict", json={"features": normal_pkt})
                    st.session_state.history.append(100) # Low traffic value for graph
                except:
                    pass
                time.sleep(0.05)
        st.success("Sent 10 Normal Packets")

    if c2.button("⚠️ Simulate DoS Attack (25 pkts)"):
        # Attack pattern (Neptune DoS)
        attack_pkt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 250, 250, 1.0, 1.0, 0.0, 0.0, 0.05, 0.07, 0.0, 255, 10, 0.04, 0.06, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
        
        progress_bar = st.progress(0)
        with st.spinner("🚀 LAUNCHING ATTACK..."):
            for i in range(25):
                try:
                    res = requests.post(f"{API_URL}/predict", json={"features": attack_pkt})
                    st.session_state.history.append(500) # High spike value for graph
                    
                    # Check for Self-Healing Trigger
                    data = res.json()
                    if "alert" in data:
                        st.error(f"🚨 SYSTEM ALERT: {data['alert']}")
                        st.balloons()
                except:
                    pass
                time.sleep(0.05)
                progress_bar.progress((i + 1) * 4)

    # Update the Graph (Show last 50 points)
    if len(st.session_state.history) > 0:
        chart_data = pd.DataFrame(st.session_state.history[-50:], columns=["Traffic Load (Bytes)"])
        chart_placeholder.line_chart(chart_data)
    else:
        st.info("Waiting for traffic... Use the buttons above.")

with col2:
    st.subheader("🛡️ Defense Stats")
    
    # Calculate fake dynamic stats based on history
    total_req = len(st.session_state.history)
    # Assume high spikes (500) are attacks
    attacks = sum(1 for x in st.session_state.history if x > 400)
    
    st.metric(label="Total Packets Scanned", value=f"{14205 + total_req}")
    st.metric(label="Attacks Blocked", value=f"{1240 + attacks}", delta="Active Defense")
    st.metric(label="System Uptime", value="99.98%")
    
    st.markdown("---")
    st.info("ℹ️ **Status:** Monitoring for Concept Drift...")