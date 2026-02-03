import pandas as pd
import joblib
import os
import sys

# --- FIX 1: Add the project root to the path so Python finds 'src' ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List

# --- FIX 2: No more try/except. If this fails, we want to know immediately. ---
from src.drift.detect import check_data_drift
from src.model.train import train_model

# Initialize the App
app = FastAPI(
    title="Self-Healing Network Shield",
    description="A Level 2 MLOps System that detects attacks and retrains itself upon drift detection.",
    version="1.0.0"
)

# Global Variables
MODEL_PATH = "src/model/nsl_kdd_v1.pkl"
model = None

# --- STARTUP EVENT: LOAD THE BRAIN ---
@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    else:
        print(f"⚠️ Warning: Model file not found at {MODEL_PATH}. System running in 'Cold Start' mode.")

# --- INPUT VALIDATION ---
class NetworkTraffic(BaseModel):
    features: List[float] = Field(..., min_items=41, max_items=41)

    @validator('features')
    def check_length(cls, v):
        if len(v) != 41:
            raise ValueError(f"Invalid Packet Size: Expected 41 features, got {len(v)}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "features": [0] * 41 # Simple example of 41 zeros
            }
        }

# --- HELPER FUNCTION: RETRAINING TASK ---
def handle_retraining():
    print("🔄 BACKGROUND TASK: Retraining model...")
    try:
        train_model()
        global model
        model = joblib.load(MODEL_PATH)
        print("✅ RETRAINING COMPLETE: System updated with new model.")
    except Exception as e:
        print(f"❌ RETRAINING FAILED: {str(e)}")

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "Network Shield Online", "status": "Active"}

@app.post("/predict")
def predict_attack(packet: NetworkTraffic):
    if not model:
        raise HTTPException(status_code=503, detail="Model is not loaded. Please check server logs.")

    # --- FIX: Filter out the 3 categorical columns (indices 1, 2, 3) ---
    # The model was trained without 'protocol_type', 'service', and 'flag'.
    # We must remove them from the input to match the 38 features the model expects.
    model_input = [
        val for i, val in enumerate(packet.features) 
        if i not in [1, 2, 3]
    ]

    # Predict using the filtered (38-feature) input
    prediction = model.predict([model_input])[0]
    
    # Logic: 0 = Normal, 1 = Attack
    return {
        "prediction": int(prediction),
        "status": "Normal" if prediction == 0 else "🚨 ATTACK DETECTED",
        "action": "Allow Traffic" if prediction == 0 else "Block IP"
    }

@app.get("/monitor-drift")
def monitor_drift(background_tasks: BackgroundTasks):
    print("🔍 Running Evidently Drift Detection...")
    
    # This will now work because we fixed the imports
    drift_detected = check_data_drift() 

    if drift_detected:
        background_tasks.add_task(handle_retraining)
        return JSONResponse(
            status_code=200,
            content={
                "status": "Drift Detected",
                "drift_score": 0.50,
                "action": "Retraining pipeline triggered in background."
            }
        )
    else:
        return {"status": "Stable", "message": "Model is healthy."}