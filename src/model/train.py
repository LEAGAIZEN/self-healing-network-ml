import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

# --- PATH SETUP ---
# Grabs the folder where THIS file lives
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Define Paths
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTrain+.txt")
MODEL_PATH = os.path.join(PROJECT_ROOT, "src", "model", "nsl_kdd_v1.pkl")

# NSL-KDD Column Names
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

def train_model(new_data=None):
    print(f"🚀 TRAINING: Loading baseline data from {TRAIN_DATA_PATH}...")
    
    if not os.path.exists(TRAIN_DATA_PATH):
        print(f"❌ Error: Training data not found at {TRAIN_DATA_PATH}")
        return

    # 1. Load Original Data
    df = pd.read_csv(TRAIN_DATA_PATH, names=COLUMNS)
    
    # 2. Integrate New Knowledge (Self-Healing)
    if new_data is not None and not new_data.empty:
        print(f"🧠 LEARNING: Integrating {len(new_data)} new attack packets into the brain...")
        # Assume these new packets are attacks (label them as 'neptune' or similar)
        new_data['label'] = "neptune" 
        df = pd.concat([df, new_data], ignore_index=True)

    # 3. Preprocessing
    # Drop non-numerical columns
    X = df.drop(["protocol_type", "service", "flag", "label", "difficulty"], axis=1, errors='ignore')
    # Convert Labels: Normal=0, Everything else=1
    y = df["label"].apply(lambda x: 0 if x == "normal" else 1)
    
    # 4. Train
    print("🏋️ TRAINING: Fitting Random Forest...")
    clf = RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42)
    clf.fit(X, y)
    
    # 5. Save
    joblib.dump(clf, MODEL_PATH)
    print(f"✅ COMPLETE: New model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()