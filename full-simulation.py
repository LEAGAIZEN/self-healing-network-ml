import requests
import time
import json

# API URL
API_URL = "http://127.0.0.1:8000/predict"

# --- REAL DATA (Crucial for Accuracy) ---
# A real "Normal" packet from the NSL-KDD dataset
normal_packet = {
    "features": [0, 1, 20, 2, 215, 45076, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
}

# A real "Attack" packet (Neptune DoS)
attack_packet = {
    "features": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 250, 250, 1.0, 1.0, 0.0, 0.0, 0.05, 0.07, 0.0, 255, 10, 0.04, 0.06, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
}

def check_accuracy(packet, expected_label, phase_name):
    print(f"\n📊 {phase_name}...")
    correct = 0
    total = 5
    
    for i in range(total):
        try:
            res = requests.post(API_URL, json=packet)
            
            # --- DEBUGGING BLOCK ---
            if res.status_code != 200:
                print(f"   ❌ API ERROR (Packet {i}): Status {res.status_code}")
                print(f"   Response: {res.text}")
                continue
                
            data = res.json()
            if "error" in data:
                print(f"   ❌ LOGIC ERROR: {data['error']}")
                continue
            # -----------------------

            pred = data.get("prediction")
            if pred == expected_label:
                correct += 1
            else:
                # Print why it failed (False Positive/Negative)
                print(f"   ⚠️ MISMATCH: Expected {expected_label}, got {pred}")

        except Exception as e:
            print(f"   ❌ CONNECTION ERROR: {e}")
            print("   (Is the server running? Did you run 'uvicorn app.api.main:app --reload'?)")
            return

    score = (correct/total)*100
    print(f"   >> Accuracy: {score}%")

# --- START SIMULATION ---
print("--- 🛡️ SELF-HEALING NETWORK DIAGNOSTIC ---")

# PHASE 1: Baseline
# If this fails, your API is broken or model file is missing
check_accuracy(normal_packet, 0, "PHASE 1: Baseline (Normal Traffic)")

# PHASE 2: Attack
check_accuracy(attack_packet, 1, "PHASE 2: Attack (Before Learning)")

# PHASE 3: Trigger Healing
print("\n[PHASE 3] Flooding system to trigger Retraining...")
triggered = False
for i in range(25):
    try:
        res = requests.post(API_URL, json=attack_packet)
        if res.status_code == 200 and "alert" in res.json():
            print(f"   🚨 ALERT RECEIVED: {res.json()['alert']}")
            triggered = True
            break
    except:
        pass
    time.sleep(0.05)

if triggered:
    print("   ⏳ Waiting 15 seconds for training to finish...")
    time.sleep(15)
    
    # PHASE 4: Verify Fix
    check_accuracy(attack_packet, 1, "PHASE 4: Attack (Post-Healing)")
    print("\n✅ DIAGNOSTIC COMPLETE.")
else:
    print("\n❌ FAILED: Retraining was never triggered.")
    print("   Check your API terminal for 'Drift Detected' messages.")