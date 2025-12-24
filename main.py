import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap

class AtmosBridgeUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATMOS BRIDGE")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Comprehensive search for the logo
        search_paths = [
            os.path.join(self.script_dir, "logo.png"),
            os.path.join(self.script_dir, "assets", "logo.png"),
            os.path.expanduser("~/Desktop/nobara-atmos-bridge/logo.png")
        ]
        
        self.logo_path = next((p for p in search_paths if os.path.exists(p)), None)
        self.ableton_exe = "/home/john/.wine/drive_c/Program Files/Common Files/Live 12 Lite/Program/Live.exe"
        
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel()
        if self.logo_path:
            pixmap = QPixmap(self.logo_path)
            self.logo_label.setPixmap(pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.setWindowIcon(QIcon(self.logo_path))
        else:
            self.logo_label.setText("⚠️ LOGO.PNG NOT FOUND\nPlace it in: ~/Desktop/nobara-atmos-bridge/")
            self.logo_label.setStyleSheet("color: yellow; font-size: 25px; border: 2px dashed yellow; padding: 30px;")
        
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("○ READY")
        self.status_label.setStyleSheet("font-size: 50px; font-weight: bold; color: #4CAF50; margin: 30px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.run_btn = QPushButton("🚀 LAUNCH ABLETON")
        self.run_btn.setFixedSize(500, 120)
        self.run_btn.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; font-size: 30px; border-radius: 20px;")
        self.run_btn.clicked.connect(self.launch_ableton)
        layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #000000;") 
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

    def update_status(self):
        try:
            output = subprocess.check_output("ps -aux | grep -iE 'Live|Ableton'", shell=True)
            is_running = len([line for line in output.splitlines() if b"grep" not in line]) > 0
        except: is_running = False
        
        if is_running:
            self.status_label.setText("● ATMOS LINK ACTIVE")
            self.status_label.setStyleSheet("font-size: 50px; font-weight: bold; color: #e0b0ff; background-color: #2a0a4d; padding: 30px; border-radius: 20px; border: 3px solid #8a2be2;")
            self.run_btn.hide()
        else:
            self.status_label.setText("○ READY")
            self.status_label.setStyleSheet("font-size: 50px; font-weight: bold; color: #4CAF50;")
            self.run_btn.show()

    def launch_ableton(self):
        wdir = os.path.dirname(self.ableton_exe)
        subprocess.Popen(["wine", self.ableton_exe], cwd=wdir)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AtmosBridgeUI()
    window.show()
    sys.exit(app.exec())
