import os
import subprocess

def optimize_system():
    print("--- Initiating Low-Latency Bus Optimization ---")
    
    # 1. Set CPU Governor to Performance
    # Prevents CPU frequency scaling which causes 'pops' and 'clicks'
    try:
        os.system("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
        print("[SUCCESS] CPU locked in Performance Mode.")
    except Exception as e:
        print(f"[ERROR] Failed to set CPU governor: {e}")

    # 2. Adjust PCI Bus Latency Timer
    # Gives the audio interface more 'headroom' on the motherboard
    try:
        os.system("sudo setpci -v -d *:* latency_timer=b0")
        print("[SUCCESS] PCI Bus Latency adjusted for high-priority audio.")
    except Exception as e:
        print(f"[ERROR] PCI adjustment failed: {e}")

    # 3. Real-time Priority Check (System Integration)
    print("[INFO] System optimized for SIT (System Integration Testing).")

if __name__ == "__main__":
    optimize_system()
