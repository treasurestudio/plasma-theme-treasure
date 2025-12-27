import subprocess
import os
import signal
import sys

class AtmosEngine:
    def __init__(self):
        self.process = None
        # The 7.1 Channel Map for Nobara/PipeWire
        self.channels = "[FL,FR,FC,LFE,RL,RR,SL,SR]"
        self.sink_name = "Atmos_Bridge"
        self.description = "Atmos Bridge (7.1 Surround)"

    def start(self):
        print(f"🚀 Starting {self.description}...")

        # Direct PipeWire command to create the virtual 7.1 device
        cmd = [
            "pw-loopback",
            "--name", self.sink_name,
            "--capture-props", f"node.description='{self.description}' media.class=Audio/Sink audio.position={self.channels}",
            "--playback-props", "node.passive=true"
        ]

        try:
            # Launch as a background process
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Bridge is LIVE. Select 'Atmos Bridge' in your Sound Settings.")
        except Exception as e:
            print(f"❌ Failed to start: {e}")

    def stop(self):
        if self.process:
            print("🛑 Stopping Bridge...")
            os.kill(self.process.pid, signal.SIGTERM)
            self.process = None
        else:
            print("Bridge is not running.")

if __name__ == "__main__":
    engine = AtmosEngine()
    engine.start()
    try:
        print("\nKEEP THIS TERMINAL OPEN TO KEEP THE BRIDGE ACTIVE")
        print("Press Ctrl+C to close the bridge and exit.")
        # Keeps the script running so the bridge doesn't disappear
        while True:
            pass
    except KeyboardInterrupt:
        engine.stop()
        sys.exit(0)
