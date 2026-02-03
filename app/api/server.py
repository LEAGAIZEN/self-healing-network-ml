
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
import os
import sys
import traceback

# PATH SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# IMPORTS
try:
    from src.drift.detect import check_data_drift
    from src.model.train import train_model
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("👉 HINT: Run 'pip install evidently' if you haven't yet.")
    sys.exit(1)

app = FastAPI(title="Self-Healing Firewall")

MODEL_PATH = os.path.join(project_root, "src", "model", "nsl_kdd_v1.pkl")
traffic_history = [] 

MODEL_COLUMNS = [
    "duration", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent", "hot", 
    "num_failed_logins", "logged_in", "num_compromised", "root_shell", "su_attempted", 
    "num_root", "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds", 
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate", 
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate", 
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", 
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate", 
    "dst_host_srv_rerror_rate"
]

class NetworkTraffic(BaseModel):
    features: List[float]

@app.on_event("startup")
def startup_event():
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ WARNING: Model not found at {MODEL_PATH}")
    else:
        print(f"✅ SYSTEM READY: Model loaded from {MODEL_PATH}")

@app.post("/predict")
def predict(data: NetworkTraffic, background_tasks: BackgroundTasks):
    try:
        if not os.path.exists(MODEL_PATH):
            return {"error": "Model not ready"}

        model = joblib.load(MODEL_PATH)
        # Filter raw features (41 -> 38)
        raw_input = [val for i, val in enumerate(data.features) if i not in [1, 2, 3]]
        
        # Create DataFrame
        input_df = pd.DataFrame([raw_input], columns=MODEL_COLUMNS)

        # Predict
        prediction = int(model.predict(input_df)[0])
        result = "Normal" if prediction == 0 else "Attack"
        
        traffic_history.append(input_df.iloc[0].to_dict())

        alert_msg = None
        if len(traffic_history) >= 20:
            print("🔍 DRIFT CHECK: Running...")
            df_history = pd.DataFrame(traffic_history)
            if check_data_drift(df_history):
                alert_msg = "Healing Triggered!"
                print("🚨 DRIFT DETECTED! Retraining...")
                background_tasks.add_task(train_model, df_history)
            traffic_history.clear()

        response = {"prediction": prediction, "status": result}
        if alert_msg:
            response["alert"] = alert_msg
        return response

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
