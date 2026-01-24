# app/api/main.py
from fastapi import FastAPI, BackgroundTasks
import joblib
import pandas as pd
import os
import sys

# --- PATH FINDER (Keep this!) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import Partner B's logic (The Brains)
try:
    from src.model.train import train_model
    from src.drift.detector import check_drift
except ImportError:
    # Fallback if files are missing (prevents crash)
    def check_drift(df): return False
    def train_model(df): print("Simulating training...")

app = FastAPI(title="Self-Healing Firewall API")

MODEL_PATH = os.path.join(project_root, "src", "model", "model.pkl")
traffic_history = [] # The memory buffer

@app.get("/")
def home():
    return {"status": "System Online", "model_loaded": os.path.exists(MODEL_PATH)}

@app.post("/predict")
def predict(data: dict, background_tasks: BackgroundTasks):
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model not found."}

    # 1. PREDICT
    try:
        model = joblib.load(MODEL_PATH)
        df = pd.DataFrame([data])
        prediction = model.predict(df)[0]
        # Map 1/11 to "Attack", 0 to "Normal"
        result = "Normal Traffic" if prediction == 0 else "Attack Detected"
    except Exception as e:
        return {"error": str(e)}

    # 2. MONITOR (The Self-Healing Loop)
    traffic_history.append(data)
    
    # Every 20 packets, check for hackers changing tactics
    if len(traffic_history) >= 20:
        df_history = pd.DataFrame(traffic_history)
        
        # Check for Drift (Partner B's code)
        if check_drift(df_history):
            print("🚨 DRIFT DETECTED: Attacks are changing! Retraining model...")
            background_tasks.add_task(train_model, df_history)
            traffic_history.clear()
            return {"prediction": result, "alert": "Healing Triggered!"}
        
        traffic_history.clear()

    return {"prediction": result, "intrusion_flag": int(prediction)}