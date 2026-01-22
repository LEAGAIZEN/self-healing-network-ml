from fastapi import FastAPI, BackgroundTasks
import pandas as pd
import joblib
import os
from contextlib import asynccontextmanager

# Import your modules (Note the dot notation)
from src.model.train import train_model
from src.drift.detect import run_drift_check

# Global variables to hold the model
model = None
MODEL_PATH = "src/model/nsl_kdd_v1.pkl"

# 1. Lifespan Manager: Loads model when app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    load_model()
    yield
    print("Shutting down...")

app = FastAPI(title="Self-Healing Network Shield", lifespan=lifespan)

def load_model():
    """Helper to reload the model from disk"""
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    else:
        print("⚠️ No model found. Please train first!")

@app.get("/")
def home():
    return {"status": "Running", "message": "System is active. Use /predict or /monitor"}

@app.post("/predict")
def predict(data: list):
    """
    Accepts a list of feature values (41 columns) and returns prediction.
    Example input: [[0, 1, 10, ... ]]
    """
    if not model:
        return {"error": "Model not loaded"}
    
    # Convert list to DataFrame (assuming order is correct)
    # In a real app, we would use Pydantic schemas to validate fields
    prediction = model.predict(data)
    return {"prediction": int(prediction[0]), "status": "Potential Attack" if prediction[0] == 1 else "Normal"}

@app.get("/monitor-drift")
def monitor(background_tasks: BackgroundTasks):
    """
    Triggers the Drift Detection Engine.
    If drift is detected (> 0.3), it kicks off a RETRAINING job in the background.
    """
    # Run the check we wrote earlier
    drift_detected = run_drift_check()
    
    if drift_detected:
        # THE MAGIC: Trigger retraining without stopping the API
        background_tasks.add_task(handle_retraining)
        return {"status": "Drift Detected", "action": "Retraining started in background"}
    
    return {"status": "Stable", "action": "No action needed"}

def handle_retraining():
    print("🔄 BACKGROUND TASK: Retraining model...")
    # 1. Run the training script
    train_model()
    # 2. Reload the new model into memory so the API uses the new version
    load_model()
    print("✅ RETRAINING COMPLETE: System updated.")