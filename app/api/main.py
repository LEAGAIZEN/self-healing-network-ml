# app/api/main.py
from fastapi import FastAPI
import pickle
import pandas as pd
import os

app = FastAPI(title="Self-Healing Firewall API")

# This is where Partner B's model will eventually live
MODEL_PATH = "src/model/saved_models/model.pkl"

@app.get("/")
def home():
    # Check if the model exists yet
    if os.path.exists(MODEL_PATH):
        return {"status": "System Online", "model_loaded": True}
    else:
        return {"status": "Waiting for Partner B...", "model_loaded": False}

@app.post("/predict")
def predict(data: dict):
    # Security check: Don't crash if model isn't ready
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model not found. The AI is not trained yet."}
    
    # Load the model (This runs every time a request comes in)
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    
    # Convert incoming JSON data to a pandas DataFrame
    df = pd.DataFrame([data])
    
    # Make a prediction (0 = Normal, 1 = Attack)
    prediction = model.predict(df)
    result = "Attack Detected" if prediction[0] == 1 else "Normal Traffic"
    
    return {"prediction": result, "intrusion_flag": int(prediction[0])}