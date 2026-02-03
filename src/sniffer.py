import time
import requests
import random
from scapy.all import sniff, IP, TCP

# Configuration
API_URL = "http://127.0.0.1:8000/predict"
INTERFACE = "en0"  # 'en0' is standard for Mac Wi-Fi. Use 'eth0' or 'wlan0' for Linux/Windows.

print(f"🕵️‍♂️ STARTING PACKET SNIFFER on {INTERFACE}...")
print("Browse the web (Google, YouTube) to generate traffic!")

def process_packet(packet):
    """
    This function runs for EVERY single packet your Wi-Fi card receives.
    """
    if IP in packet and TCP in packet:
        # 1. Extract REAL data from the packet
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_len = len(packet)
        
        # 2. Extract the features we can (Simplification for Demo)
        # Real extraction of all 41 features requires complex flow calculation.
        # For this demo, we use the REAL packet size and pad the rest.
        
        # We simulate the 41 features, but insert the REAL length at index 4 (src_bytes)
        features = [0] * 41
        features[4] = packet_len  # Real packet size
        features[5] = random.randint(0, 500) # Simulating dst_bytes
        
        # 3. Send to your AI Brain
        try:
            payload = {"features": features}
            response = requests.post(API_URL, json=payload)
            result = response.json()
            
            # 4. Print the verdict
            status_icon = "✅" if result['prediction'] == 0 else "🚨"
            print(f"{status_icon} Packet: {src_ip} -> {dst_ip} | Size: {packet_len} bytes | Verdict: {result['status']}")
            
        except Exception as e:
            print(f"❌ API Error: {e}")

# Start Sniffing (Capture 100 packets then stop, or remove count to run forever)
sniff(iface=INTERFACE, filter="tcp", prn=process_packet, store=False)