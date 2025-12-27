import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QTextEdit, QFileDialog, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from engine import AudioEngine

class AtmosHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nobara Atmos Bridge")
        self.setFixedSize(500, 450)

        self.engine = AudioEngine()
        self.engine.log_received.connect(self.update_log)

        layout = QVBoxLayout()
        
        # Header
        self.status_label = QLabel(f"Selected: {os.path.basename(self.engine.ableton_path)}")
        self.status_label.setStyleSheet("font-weight: bold; color: #3498db;")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_browse = QPushButton("📁 Select DAW (.exe)")
        self.btn_browse.clicked.connect(self.browse_daw)
        
        self.btn_launch = QPushButton("🚀 Launch & Bridge")
        self.btn_launch.clicked.connect(self.launch_all)
        self.btn_launch.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; height: 40px;")
        
        btn_layout.addWidget(self.btn_browse)
        btn_layout.addWidget(self.btn_launch)
        layout.addLayout(btn_layout)

        # Log View
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #121212; color: #00ff00; font-family: monospace; border: 1px solid #333;")
        layout.addWidget(self.log_view)

        # THE "PWEASE" FOOTER
        self.footer_label = QLabel("✨ RUN FL STUDIO OR ABLETON! ✨")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 14px; margin-top: 5px;")
        layout.addWidget(self.footer_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_log("READY: Select your DAW and hit Launch.")
        self.update_log("INFO: 8-Channel Atmos Sink is prepared.")

    def browse_daw(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select DAW Executable", os.path.expanduser("~/.wine"), "Executables (*.exe)")
        if file_path:
            self.engine.save_config(file_path)
            self.status_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.update_log(f"CONFIG: Set DAW to {file_path}")

    def update_log(self, message):
        self.log_view.append(message)

    def launch_all(self):
        if not self.engine.isRunning():
            self.engine.start()
            env = os.environ.copy()
            env["WINEASIO_NUMBER_OUTPUTS"] = "8"
            try:
                subprocess.Popen(["wine", self.engine.ableton_path], env=env)
                self.update_log("SYSTEM: Launching DAW via Wine...")
                self.update_log(">> RUN FL STUDIO OR ABLETON NOW! <<")
            except Exception as e:
                self.update_log(f"ERROR: Could not launch EXE: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AtmosHub()
    window.show()
    sys.exit(app.exec())
