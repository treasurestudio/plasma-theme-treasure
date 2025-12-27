import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QTextEdit, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from engine import AudioEngine

class NobaraAudioHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = AudioEngine()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NOBARA HUB | Studio Control")
        self.setFixedSize(450, 680)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #a0a0a0; font-family: 'Segoe UI', sans-serif; font-size: 12px; }
            QPushButton {
                background-color: #333333; color: #eeeeee; border: 1px solid #111111;
                padding: 12px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #444444; }
            QPushButton#launch { background-color: #d79921; color: #1e1e1e; font-size: 14px; }
            QPushButton#path_btn { background-color: #262626; color: #777; font-size: 10px; padding: 5px; }
            QTextEdit { background-color: #000000; color: #b8bb26; border: 1px solid #333; font-family: 'Monospace'; font-size: 11px; }
        """)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Dynamic Hardware Status
        self.status_led = QLabel("● SCANNING FOR HARDWARE...")
        self.status_led.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_led)

        # Main Controls
        self.launch_btn = QPushButton("LAUNCH DAW ENGINE")
        self.launch_btn.setObjectName("launch")
        self.launch_btn.clicked.connect(self.engine.start)
        layout.addWidget(self.launch_btn)

        self.rescue_btn = QPushButton("FORCE RE-PATCH AUDIO")
        self.rescue_btn.clicked.connect(self.engine.rescue_bluetooth)
        layout.addWidget(self.rescue_btn)

        # Console Output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        # Configuration Section
        layout.addWidget(QLabel("TARGET EXECUTABLE:"))
        self.path_label = QLabel(self.engine.ableton_path)
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("color: #504945; font-style: italic;")
        layout.addWidget(self.path_label)

        self.path_btn = QPushButton("SELECT NEW DAW EXE")
        self.path_btn.setObjectName("path_btn")
        self.path_btn.clicked.connect(self.browse_path)
        layout.addWidget(self.path_btn)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Wiring Logic
        self.engine.log_received.connect(self.console.append)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(3000)

    def browse_path(self):
        file_filter = "Executable (*.exe);;All Files (*)"
        initial_dir = os.path.dirname(self.engine.ableton_path)
        filename, _ = QFileDialog.getOpenFileName(self, "Select DAW EXE", initial_dir, file_filter)
        if filename:
            if self.engine.save_config(filename):
                self.path_label.setText(filename)
                self.console.append(f"SYSTEM: Target DAW updated to {filename}")

    def update_status(self):
        """Polls for hardware (Heavys/Headset) and updates the UI."""
        if self.engine.check_bluetooth():
            self.status_led.setText("● HARDWARE: READY")
            self.status_led.setStyleSheet("color: #b8bb26; font-weight: bold; font-size: 14px;")
        else:
            self.status_led.setText("○ HARDWARE: NOT DETECTED")
            self.status_led.setStyleSheet("color: #fb4934; font-weight: bold; font-size: 14px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NobaraAudioHub()
    window.show()
    sys.exit(app.exec())
