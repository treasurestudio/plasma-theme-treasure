import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QComboBox, QTextEdit, QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import json
import subprocess

# Import the engine
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from src.engine import AtmosEngine

class BridgeWorker(QThread):
    """Runs the audio bridge in a separate thread"""
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.engine = AtmosEngine()
        self.running = False

    def run(self):
        self.running = True
        self.status_update.emit("🚀 Starting audio bridge...")
        self.engine.start()
        self.status_update.emit("✅ Bridge is LIVE and routing audio")

        # Keep thread alive while bridge is running
        while self.running:
            self.msleep(100)

    def stop(self):
        self.running = False
        self.engine.stop()
        self.status_update.emit("🛑 Bridge stopped")

class AtmosBridgeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bridge_worker = None
        self.config_file = os.path.join(BASE_DIR, "configs", "bridge_config.json")
        self.config = self.load_config()

        self.init_ui()
        self.load_saved_settings()

    def init_ui(self):
        self.setWindowTitle("Atmos Bridge Hub - Nobara Linux")
        self.setGeometry(100, 100, 700, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Title
        title = QLabel("🎵 Atmos Bridge Hub")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # DAW Selection Group
        daw_group = QGroupBox("DAW Configuration")
        daw_layout = QVBoxLayout()

        daw_label = QLabel("Select your DAW executable:")
        daw_layout.addWidget(daw_label)

        daw_path_layout = QHBoxLayout()
        self.daw_path_input = QLineEdit()
        self.daw_path_input.setPlaceholderText("Path to Ableton.exe or FL Studio.exe")
        self.daw_path_input.setReadOnly(True)
        daw_path_layout.addWidget(self.daw_path_input)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_daw)
        daw_path_layout.addWidget(self.browse_btn)

        daw_layout.addLayout(daw_path_layout)
        daw_group.setLayout(daw_layout)
        layout.addWidget(daw_group)

        # Audio Device Selection Group
        audio_group = QGroupBox("Audio Output Device")
        audio_layout = QVBoxLayout()

        audio_label = QLabel("Select output device:")
        audio_layout.addWidget(audio_label)

        self.audio_device_combo = QComboBox()
        audio_layout.addWidget(self.audio_device_combo)

        refresh_audio_btn = QPushButton("Refresh Devices")
        refresh_audio_btn.clicked.connect(self.refresh_audio_devices)
        audio_layout.addWidget(refresh_audio_btn)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # Bridge Control
        control_layout = QHBoxLayout()

        self.start_bridge_btn = QPushButton("Start Bridge")
        self.start_bridge_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;")
        self.start_bridge_btn.clicked.connect(self.start_bridge)
        control_layout.addWidget(self.start_bridge_btn)

        self.stop_bridge_btn = QPushButton("Stop Bridge")
        self.stop_bridge_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 10px;")
        self.stop_bridge_btn.clicked.connect(self.stop_bridge)
        self.stop_bridge_btn.setEnabled(False)
        control_layout.addWidget(self.stop_bridge_btn)

        self.launch_daw_btn = QPushButton("Launch DAW")
        self.launch_daw_btn.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px; padding: 10px;")
        self.launch_daw_btn.clicked.connect(self.launch_daw)
        control_layout.addWidget(self.launch_daw_btn)

        layout.addLayout(control_layout)

        # Status Display
        status_group = QGroupBox("Status Log")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setStyleSheet(
            "background-color: #1a1a1a; "
            "color: #ffffff; "
            "border: 1px solid #333; "
            "padding: 5px; "
            "font-family: 'Courier New', monospace;"
        )
        status_layout.addWidget(self.status_text)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Instructions
        instructions = QLabel(
            "📖 Instructions:\n"
            "1. Browse and select your DAW executable (Ableton/FL Studio)\n"
            "2. Choose your audio output device\n"
            "3. Click 'Start Bridge' to create the audio connection\n"
            "4. Click 'Launch DAW' to start your music production software\n"
            "5. In your DAW, set output to 'Atmos_Bridge'"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)

        # Initial status
        self.log_status("✅ Bridge initialized and ready")
        self.log_status(f"📁 Configuration directory: {BASE_DIR}")

        # Now refresh audio devices after UI is fully initialized
        self.refresh_audio_devices()

    def browse_daw(self):
        """Open file browser to select DAW executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select DAW Executable",
            os.path.expanduser("~/.wine/drive_c/"),
            "Executable Files (*.exe);;All Files (*)"
        )

        if file_path:
            self.daw_path_input.setText(file_path)
            self.config['daw_path'] = file_path
            self.save_config()
            self.log_status(f"✅ DAW selected: {os.path.basename(file_path)}")

    def refresh_audio_devices(self):
        """Refresh list of available audio output devices"""
        self.audio_device_combo.clear()

        try:
            # Get PipeWire sinks
            result = subprocess.run(
                ['pactl', 'list', 'short', 'sinks'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                devices = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append(parts[1])

                self.audio_device_combo.addItems(devices)
                self.log_status(f"🔊 Found {len(devices)} audio devices")
            else:
                self.audio_device_combo.addItem("Default")
                self.log_status("⚠️ Could not detect audio devices, using default")

        except Exception as e:
            self.audio_device_combo.addItem("Default")
            self.log_status(f"⚠️ Error detecting devices: {str(e)}")

    def start_bridge(self):
        """Start the audio bridge"""
        if self.bridge_worker and self.bridge_worker.isRunning():
            self.log_status("⚠️ Bridge is already running")
            return

        self.bridge_worker = BridgeWorker()
        self.bridge_worker.status_update.connect(self.log_status)
        self.bridge_worker.start()

        self.start_bridge_btn.setEnabled(False)
        self.stop_bridge_btn.setEnabled(True)

    def stop_bridge(self):
        """Stop the audio bridge"""
        if self.bridge_worker and self.bridge_worker.isRunning():
            self.bridge_worker.stop()
            self.bridge_worker.wait()

        self.start_bridge_btn.setEnabled(True)
        self.stop_bridge_btn.setEnabled(False)

    def launch_daw(self):
        """Launch the selected DAW"""
        daw_path = self.daw_path_input.text()

        if not daw_path:
            self.log_status("❌ No DAW selected. Please browse and select your DAW first.")
            return

        if not os.path.exists(daw_path):
            self.log_status(f"❌ DAW not found at: {daw_path}")
            return

        try:
            self.log_status(f"🚀 Launching DAW: {os.path.basename(daw_path)}")
            subprocess.Popen(['wine', daw_path])
            self.log_status("✅ DAW launched successfully")
        except Exception as e:
            self.log_status(f"❌ Error launching DAW: {str(e)}")

    def log_status(self, message):
        """Add message to status log"""
        self.status_text.append(message)

    def load_config(self):
        """Load saved configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        """Save configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_saved_settings(self):
        """Load previously saved settings"""
        if 'daw_path' in self.config:
            self.daw_path_input.setText(self.config['daw_path'])
            self.log_status(f"📂 Loaded saved DAW path: {os.path.basename(self.config['daw_path'])}")

    def closeEvent(self, event):
        """Handle window close"""
        if self.bridge_worker and self.bridge_worker.isRunning():
            self.stop_bridge()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AtmosBridgeGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
