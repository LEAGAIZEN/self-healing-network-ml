import pandas as pd
import os
import sys

# --- 1. IMPORTS FOR EVIDENTLY ---
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
except ImportError:
    print("❌ Critical Error: 'evidently' is not installed. Run 'pip install evidently'")
    sys.exit(1)

# --- 2. PATH SETUP (BULLETPROOF VERSION) ---
# This grabs the folder where THIS file (detect.py) lives: .../self-healing-network-ml/src/drift
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up 2 levels to find the project root: .../self-healing-network-ml
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Define the data paths explicitly
# OLD:
# TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "KDDTrain+.txt")
# TEST_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "KDDTest+.txt")

# NEW (Add "raw"):
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTrain+.txt")
TEST_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTest+.txt")

# Define NSL-KDD Columns (The dataset has no headers, so we must provide them)
COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land", 
    "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", 
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations", 
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", 
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate", 
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", 
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", 
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", 
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate", 
    "dst_host_srv_rerror_rate", "label", "difficulty"
]

def check_data_drift():
    """
    Compares Training Data vs Test Data to detect distribution changes.
    Returns: True if drift is detected, False otherwise.
    """
    print(f"DEBUG: Looking for data at: {TRAIN_DATA_PATH}")
    
    # --- 3. LOAD DATA ---
    if not os.path.exists(TRAIN_DATA_PATH):
        print(f"❌ Error: Training file not found at {TRAIN_DATA_PATH}")
        return False
        
    if not os.path.exists(TEST_DATA_PATH):
        print(f"❌ Error: Test file not found at {TEST_DATA_PATH}")
        return False

    try:
        # Load datasets with the manual column names
        ref_data = pd.read_csv(TRAIN_DATA_PATH, names=COLUMNS)
        curr_data = pd.read_csv(TEST_DATA_PATH, names=COLUMNS)
        
        print(f"✅ Data Loaded. Reference: {ref_data.shape}, Current: {curr_data.shape}")

    except Exception as e:
        print(f"❌ Error reading CSV files: {e}")
        return False

    # --- 4. PREPARE FOR DRIFT CHECK ---
    # We only check numerical columns for the MVP (Skipping strings to avoid errors)
    num_cols = [c for c in COLUMNS if c not in ["protocol_type", "service", "flag", "label", "difficulty"]]
    
    # Sample the data to make the check fast (5000 rows is enough)
    ref_sample = ref_data[num_cols].sample(n=min(5000, len(ref_data)), random_state=42)
    curr_sample = curr_data[num_cols].sample(n=min(5000, len(curr_data)), random_state=42)

    # --- 5. RUN EVIDENTLY AI ---
    print("🔍 Calculating Drift metrics...")
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_sample, current_data=curr_sample)
    
    # Parse results
    result = report.as_dict()
    drift_share = result['metrics'][0]['result']['drift_share']
    
    print(f"📊 Drift Score: {drift_share:.4f} (Threshold: 0.3)")
    
    # --- 6. DECISION LOGIC ---
    # If more than 30% of features have drifted, trigger alert.
    # TIP: Change 0.3 to 0.0 if you want to force the alert for your demo.
    if drift_share > 0.3:
        print("🚨 CRITICAL DRIFT DETECTED!")
        return True
    else:
        print("✅ System Stable.")
        return False

# For testing this file directly (optional)
if __name__ == "__main__":
    check_data_drift()