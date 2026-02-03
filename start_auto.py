import pandas as pd
import os
import sys

# ==============================
# 1. SAFE EVIDENTLY IMPORTS
# ==============================
EVIDENTLY_AVAILABLE = False
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
    EVIDENTLY_AVAILABLE = True
    print("✅ Evidently AI Library Loaded Successfully.")
except ImportError as e:
    print(f"⚠️ DRIFT MODULE WARNING: Could not import evidently ({e}).")
    print("   -> Drift detection will be SKIPPED, but the server will run.")
    EVIDENTLY_AVAILABLE = False

# ==============================
# 2. PATH SETUP
# ==============================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "KDDTrain+.txt")

# ==============================
# 3. COLUMN DEFINITIONS
# ==============================
COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
    "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate",
    "label", "difficulty"
]

# ==============================
# 4. DRIFT DETECTION FUNCTION
# ==============================
def check_data_drift(df_current: pd.DataFrame) -> bool:
    """
    Detects data drift using Evidently.
    Returns True if drift is detected, else False.
    """
    # --- SAFETY CHECK ---
    if not EVIDENTLY_AVAILABLE:
        print("⚠️ SKIPPING DRIFT CHECK: Evidently library is missing or broken.")
        return False

    print("🔍 DRIFT CHECK STARTED")

    # Load reference data
    if not os.path.exists(TRAIN_DATA_PATH):
        print(f"❌ Training data not found: {TRAIN_DATA_PATH}")
        return False

    try:
        ref_data = pd.read_csv(TRAIN_DATA_PATH, names=COLUMNS)

        # Select numerical columns only
        exclude_cols = ["protocol_type", "service", "flag", "label", "difficulty"]
        available_cols = [c for c in COLUMNS if c in df_current.columns]
        num_cols = [c for c in available_cols if c not in exclude_cols]

        if not num_cols:
            print("⚠️ No numerical columns found for drift check.")
            return False

        # Take a sample for speed
        ref_sample = ref_data[num_cols].sample(n=min(5000, len(ref_data)), random_state=42)
        curr_sample = df_current[num_cols]

        # Run Report
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=ref_sample, current_data=curr_sample)
        
        # Parse Result
        result = report.as_dict()
        drift_share = result["metrics"][0]["result"]["drift_share"]
        
        print(f"📊 Drift Share: {drift_share:.4f}")

        if drift_share > 0.3:
            print("🚨 DRIFT DETECTED — HEALING REQUIRED")
            return True

        print("✅ No Significant Drift")
        return False

    except Exception as e:
        print(f"❌ DRIFT CHECK FAILED: {e}")
        return False