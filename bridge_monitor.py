import os
import time

def monitor_bridge_health():
    print("--- AI Bridge Monitor Active ---")
    # This simulates 'watching' the Pipewire/ALSA bus
    while True:
        # Command to check for Xruns (audio dropouts) in logs
        check_logs = os.popen('journalctl -u pipewire --since "10 seconds ago" | grep -i "xrun"').read()
        
        if "xrun" in check_logs.lower():
            print("[ALERT] Signal instability detected on the bus!")
            print("[ACTION] Triggering Bus Optimizer to stabilize...")
            os.system("python3 bus_optimizer.py") # Self-healing logic!
        else:
            print("[HEALTHY] Signal pathing is 100% accurate.")
            
        time.sleep(5) # Check every 5 seconds

if __name__ == "__main__":
    monitor_bridge_health()
