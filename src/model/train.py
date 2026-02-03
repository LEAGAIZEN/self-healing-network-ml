import pandas as pd
import joblib
import os
import sys
from sklearn.ensemble import RandomForestClassifier

# --- 1. PATH SETUP (BULLETPROOF VERSION) ---
# Grabs the folder where THIS file lives: .../src/model
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels to project root: .../self-healing-network-ml
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Updated Paths to point to 'data/raw'
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTrain+.txt")
TEST_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTest+.txt")
MODEL_PATH = os.path.join(PROJECT_ROOT, "src", "model", "nsl_kdd_v1.pkl")

# Define Columns
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

def train_model():
    print(f"🚀 Starting Retraining Pipeline...")
    print(f"DEBUG: Loading training data from {TRAIN_DATA_PATH}")

    # 1. Load Data
    if not os.path.exists(TRAIN_DATA_PATH):
        raise FileNotFoundError(f"Training data not found at {TRAIN_DATA_PATH}")

    df_train = pd.read_csv(TRAIN_DATA_PATH, names=COLUMNS)
    df_test = pd.read_csv(TEST_DATA_PATH, names=COLUMNS)
    
    # Combine them (Simulating "Learning from new data")
    # In a real system, you would append only the *new* drifted data.
    full_df = pd.concat([df_train, df_test.sample(2000)]) 
    
    # 2. Preprocessing
    # Drop categorical columns for MVP simplicity
    X = full_df.drop(["protocol_type", "service", "flag", "label", "difficulty"], axis=1)
    
    # Convert labels: Normal=0, Attack=1
    y = full_df["label"].apply(lambda x: 0 if x == "normal" else 1)
    
    # 3. Train
    print("🧠 Training Random Forest Model...")
    clf = RandomForestClassifier(n_estimators=10, max_depth=5)
    clf.fit(X, y)
    
    # 4. Save
    joblib.dump(clf, MODEL_PATH)
    print(f"💾 Model successfully saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()