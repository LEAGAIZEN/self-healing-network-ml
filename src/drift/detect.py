import pandas as pd
import os
import json
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# Define column names (Same as training)
COLUMNS = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty"]

def load_data():
    print("Loading data for drift check...")
    # Reference = What the model learned from
    ref_path = "data/raw/KDDTrain+.txt"
    # Current = New traffic (The Test set)
    curr_path = "data/raw/KDDTest+.txt"
    
    if not os.path.exists(ref_path) or not os.path.exists(curr_path):
        raise FileNotFoundError("❌ Data files not found inside data/raw/")
        
    ref = pd.read_csv(ref_path, header=None, names=COLUMNS)
    curr = pd.read_csv(curr_path, header=None, names=COLUMNS)
    
    # We only care about the features, not the label for input drift
    return ref.drop(columns=['label', 'difficulty']), curr.drop(columns=['label', 'difficulty'])

def run_drift_check():
    reference_data, current_data = load_data()
    
    # Take a sample to speed it up (Drift detection on 100k rows can be slow on laptops)
    # We take 5000 random rows from each
    reference_sample = reference_data.sample(5000, random_state=42)
    current_sample = current_data.sample(5000, random_state=42)
    
    print("🔍 Running Evidently Drift Detection...")
    
    # 1. Initialize the Report
    report = Report(metrics=[DataDriftPreset()])
    
    # 2. Run the calculation
    report.run(reference_data=reference_sample, current_data=current_sample)
    
    # 3. Get the results
    result = report.as_dict()
    drift_share = result['metrics'][0]['result']['drift_share']
    number_of_drifted_features = result['metrics'][0]['result']['number_of_drifted_columns']
    
    print("\n" + "="*30)
    print(f"📊 DRIFT REPORT")
    print("="*30)
    print(f"Drifted Features: {number_of_drifted_features} out of {len(reference_sample.columns)}")
    print(f"Drift Score: {drift_share:.2f}")
    
    # Threshold: If more than 30% of features drift, we panic.
    if drift_share > 0.3:
        print("\n🚨 CRITICAL DRIFT DETECTED! 🚨")
        print("The traffic patterns have changed significantly.")
        print("Action: Triggering Retraining Pipeline...")
        # In the future, this return value will trigger the API
        return True
    else:
        print("\n✅ System Stable. No retraining needed.")
        return False

if __name__ == "__main__":
    run_drift_check()