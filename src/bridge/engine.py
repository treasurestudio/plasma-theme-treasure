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
        self.load_config()

    def load_config(self):
        """Loads the saved EXE path or defaults to a standard Ableton path."""
        default_path = os.path.expanduser("~/.wine/drive_c/ProgramData/Ableton/Live 12 Lite/Program/Ableton Live 12 Lite.exe")
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
        """Saves the user-selected EXE path for the next session."""
        with open(self.config_file, 'w') as f:
            json.dump({"path": path}, f)
        self.ableton_path = path
        return True

    def check_bluetooth(self):
        """Checks if a Bluetooth (bluez) device is currently recognized by the system."""
        try:
            out = subprocess.check_output("pactl list short sinks", shell=True, text=True)
            return "bluez" in out.lower() or "headset" in out.lower()
        except:
            return False

    def setup_audio_bridge(self):
        """Creates the virtual Atmos_Bridge sink if it's missing."""
        check = os.popen("pactl list short sinks | grep Atmos_Bridge").read()
        if not check:
            self.log_received.emit("SYSTEM: Building Virtual Atmos Bridge...")
            subprocess.run(["pactl", "load-module", "module-null-sink", "sink_name=Atmos_Bridge", "sink_properties=device.description=Atmos_Bridge"])

    def rescue_bluetooth(self):
        """Force-restarts the audio bridge and re-scans for hardware."""
        self.log_received.emit("RESCUE: Tearing down and rebuilding bridge...")
        subprocess.run(["pactl", "unload-module", "module-null-sink"], capture_output=True)
        time.sleep(1)
        self.setup_audio_bridge()
        self.fix_window_and_patch()

    def fix_window_and_patch(self):
        """The 'Magic' Function: Fixes UI geometry and routes audio wires."""
        time.sleep(12) # Wait for Wine to initialize the window
        self.log_received.emit("SYSTEM: Calibrating DAW Geometry...")
        try:
            # 1. WINDOW FIX: Force size and focus using xdotool/wmctrl
            active_win = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            subprocess.run(["wmctrl", "-i", "-r", active_win, "-e", "0,100,100,1600,900"])
            subprocess.run(["wmctrl", "-i", "-r", active_win, "-b", "add,maximized_vert,maximized_horz"])

            # 2. SMART AUDIO PATCHING: Find the real hardware (Heavys, Headset, etc.)
            sinks = subprocess.check_output("pactl list short sinks", shell=True, text=True)
            target_hw = None

            for line in sinks.splitlines():
                sink_name = line.split()[1]
                # Filter out our own bridge and find the physical hardware
                if "Atmos_Bridge" not in sink_name:
                    # Priority order: Bluetooth > USB > Internal PCI
                    if "bluez" in sink_name.lower() or "usb" in sink_name.lower() or "headset" in sink_name.lower():
                        target_hw = sink_name
                        break
                    target_hw = sink_name # Last resort: take any available sink

            if target_hw:
                # Use Pipewire Link to connect the virtual bridge to your physical device
                subprocess.run(["pw-link", "Atmos_Bridge:monitor_FL", f"{target_hw}:playback_FL"], capture_output=True)
                subprocess.run(["pw-link", "Atmos_Bridge:monitor_FR", f"{target_hw}:playback_FR"], capture_output=True)
                self.log_received.emit(f"SUCCESS: Routed Atmos to {target_hw}")
            else:
                self.log_received.emit("WARNING: No physical hardware detected for routing.")

        except Exception as e:
            self.log_received.emit(f"WINDOW/ROUTING ERROR: {str(e)}")

    def run(self):
        """Launches the DAW within the optimized Wine environment."""
        self.setup_audio_bridge()

        # Optimize Wine for Pro Audio
        env = os.environ.copy()
        env.update({
            "WINEPREFIX": os.path.expanduser("~/.wine"),
            "PIPEWIRE_LATENCY": "1024/48000", # Balances stability and speed
            "WINEDEBUG": "-all",            # Keeps logs clean
            "WINE_RT_PRIO": "1"              # Requests realtime priority
        })

        try:
            self.log_received.emit(f"LAUNCHING: {os.path.basename(self.ableton_path)}")
            # Start the DAW
            subprocess.Popen(["wine", self.ableton_path], env=env)
            # Run the window fixer and audio patcher in the background
            self.fix_window_and_patch()
        except Exception as e:
            self.log_received.emit(f"LAUNCH ERROR: {str(e)}")
