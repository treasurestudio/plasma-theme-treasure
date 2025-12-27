import subprocess
import os
import time
import json
from PyQt6.QtCore import QThread, pyqtSignal

class AudioEngine(QThread):
    log_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config_file = os.path.expanduser("~/.audio_hub_config")
        self.ableton_path = ""
        self.load_config()

    def load_config(self):
        # Default search path for common DAWs
        default_path = os.path.expanduser("~/.wine/drive_c/Program Files/Image-Line/FL Studio 21/FL64.exe")
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.ableton_path = data.get("path", default_path)
            except:
                self.ableton_path = default_path
        else:
            self.ableton_path = default_path

    def save_config(self, path):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"path": path}, f)
            self.ableton_path = path
            return True
        except Exception as e:
            self.log_received.emit(f"ERROR: {e}")
            return False

    def setup_audio_bridge(self):
        check = os.popen("pactl list short sinks | grep Atmos_Bridge").read()
        if not check:
            self.log_received.emit("SYSTEM: Building 8-Channel Atmos Bridge...")
            subprocess.run([
                "pactl", "load-module", "module-null-sink", 
                "sink_name=Atmos_Bridge", 
                "sink_properties=device.description=Atmos_Bridge channel_map=front-left,front-right,rear-left,rear-right,front-center,lfe,side-left,side-right"
            ])
        subprocess.run(["pw-metadata", "-n", "settings", "0", "clock.force-rate", "48000"])

    def fix_window_and_patch(self):
        self.log_received.emit("SYSTEM: Monitoring for DAW...")
        target_hw = None
        try:
            sinks = subprocess.check_output("pactl list short sinks", shell=True, text=True)
            for line in sinks.splitlines():
                sink_name = line.split()[1]
                if "Atmos_Bridge" not in sink_name and any(x in sink_name.lower() for x in ["h1h", "bluez", "usb", "pci", "analog"]):
                    target_hw = sink_name
                    break
        except:
            pass

        for i in range(30):
            try:
                win_list = subprocess.check_output(["wmctrl", "-l"], text=True)
                if any(daw in win_list for daw in ["Live", "FL Studio", "Wine"]):
                    if target_hw:
                        subprocess.run(["pw-link", "Atmos_Bridge:monitor_FL", f"{target_hw}:playback_FL"], capture_output=True)
                        subprocess.run(["pw-link", "Atmos_Bridge:monitor_FR", f"{target_hw}:playback_FR"], capture_output=True)
                        self.log_received.emit(f"SUCCESS: Connected to {target_hw}")
                    break
            except:
                pass
            time.sleep(1)

    def run(self):
        try:
            self.setup_audio_bridge()
            self.fix_window_and_patch()
        except Exception as e:
            self.log_received.emit(f"CRITICAL: {e}")
