import os
import subprocess
import time
import sys
import shutil
import json

# --- PATHS & ENVIRONMENT ---
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(CURRENT_DIR, "config.json")
ATMOS_ENGINE = os.path.join(CURRENT_DIR, "engine.py")
WINE_CMD = shutil.which("wine") or "/usr/bin/wine"
DEFAULT_DLL_PATH = "/usr/lib/wine/x86_64-windows/wineasio.dll"

def setup_environment():
    """Sets the specific environment variables for 7.1 Atmos Routing."""
    env = os.environ.copy()
    env["PYTHONPATH"] = CURRENT_DIR
    env["WINEASIO_NUMBER_OUTPUTS"] = "8"
    env["WINEASIO_NUMBER_INPUTS"] = "0"
    env["WINEASIO_AUTOSTART_SERVER"] = "on"
    env["PIPEWIRE_LATENCY"] = "256/48000"
    return env

def load_apps():
    """Loads apps. If config is missing, it creates a high-quality default."""
    defaults = {
        "apps": [
            {"name": "FL Studio 20", "exec": os.path.join(HOME, ".wine/drive_c/Program Files/Image-Line/FL Studio 20/FL64.exe"), "type": "wine"},
            {"name": "Bitwig Studio", "exec": "bitwig-studio", "type": "native"},
            {"name": "Ableton Live 11", "exec": os.path.join(HOME, ".wine/drive_c/Program Files/Ableton/Live 11 Suite/Program/Ableton Live 11 Suite.exe"), "type": "wine"},
            {"name": "Spotify (Atmos Test)", "exec": "spotify", "type": "native"}
        ]
    }

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(defaults, f, indent=4)
        return defaults["apps"]

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("apps", defaults["apps"])
    except:
        return defaults["apps"]

def get_visual_selection(apps):
    """Creates a professional GTK dropdown list."""
    list_items = []
    for i, app in enumerate(apps, 1):
        # Check if the app actually exists so the user knows what will work
        exists = "READY" if app["type"] == "native" or os.path.exists(app["exec"]) else "NOT FOUND"
        list_items.extend([str(i), app['name'], app['type'].upper(), exists])

    # Zenity command for a clean, professional table
    cmd = [
        "zenity", "--list", "--title=ATMOS MUSIC HUB v1.0",
        "--column=ID", "--column=Software", "--column=Engine", "--column=Status",
        "--text=Select Audio Host for 7.1 Atmos Bridging:",
        "--height=400", "--width=500", "--hide-column=1"
    ] + list_items

    try:
        selection = subprocess.check_output(cmd).decode().strip()
        return int(selection) - 1
    except:
        return None

def launch_hub():
    # 1. Clear any old ghost processes first
    os.system("killall -9 python3 engine.py 2>/dev/null")

    apps = load_apps()
    env = setup_environment()

    # 2. Register WineASIO (Crucial for the 8-channel output)
    if os.path.exists(DEFAULT_DLL_PATH):
        subprocess.run([WINE_CMD, "regsvr32", "/s", DEFAULT_DLL_PATH], env=env)

    # 3. Start the Atmos Engine
    if not os.path.exists(ATMOS_ENGINE):
        print(f"Error: {ATMOS_ENGINE} not found.")
        return

    print("🚀 Initializing Atmos Routing Engine...")
    bridge_proc = subprocess.Popen([sys.executable, ATMOS_ENGINE], env=env)

    # 4. Show the Dropdown
    idx = get_visual_selection(apps)

    if idx is not None:
        selected = apps[idx]
        print(f"🌌 Bridging {selected['name']}...")

        try:
            if selected["type"] == "wine":
                # Ensure we use the full path for Wine apps
                subprocess.Popen([WINE_CMD, selected["exec"]], env=env).wait()
            else:
                subprocess.Popen([selected["exec"]], env=env).wait()
        except Exception as e:
            os.system(f"zenity --error --text='Failed to launch {selected['name']}: {str(e)}'")

    # 5. Full Cleanup on Exit
    print("🛑 Closing Atmos Bridge...")
    bridge_proc.terminate()
    os.system("killall -9 wine-preloader FL64.exe 2>/dev/null")
    print("✅ Session Ended.")

if __name__ == "__main__":
    launch_hub()
