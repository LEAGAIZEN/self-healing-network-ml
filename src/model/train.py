import pandas as pd
import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# Define column names for NSL-KDD
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
    print("Loading data...")
    # Use absolute path or relative from root
    path = "data/raw/KDDTrain+.txt"
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Error: Could not find {path}. Run this from the project root!")
    df = pd.read_csv(path, header=None, names=COLUMNS)
    return df

def train_model():
    mlflow.set_experiment("Network_Intrusion_Baseline")
    
    with mlflow.start_run():
        df = load_data()
        
        # Simple Preprocessing
        for col in ["protocol_type", "service", "flag", "label"]:
            df[col] = df[col].astype('category').cat.codes
            
        X = df.drop(columns=["label", "difficulty"])
        y = df["label"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("🚀 Training Random Forest...")
        model = RandomForestClassifier(n_estimators=50, max_depth=10)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        
        print(f"✅ Model Accuracy: {acc:.4f}")
        mlflow.log_metric("accuracy", acc)
        
        # Save model
        os.makedirs("src/model", exist_ok=True)
        joblib.dump(model, "src/model/nsl_kdd_v1.pkl")
        print("💾 Model saved to src/model/nsl_kdd_v1.pkl")

if __name__ == "__main__":
    train_model()