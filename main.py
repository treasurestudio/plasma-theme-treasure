import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QStyle)

class AtmosBridge(QWidget):
    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".atmos_bridge_path"
        self.init_ui()
        self.auto_discover()

    def init_ui(self):
        self.setWindowTitle('Atmos Bridge v1.0')
        self.setMinimumSize(450, 200)

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Ready")
        self.path_label = QLabel("No path detected.")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("color: #777; font-size: 11px;")

        self.launch_btn = QPushButton(" Launch Ableton Bridge")
        self.launch_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.launch_btn.setMinimumHeight(50)
        self.launch_btn.clicked.connect(self.launch_app)

        self.browse_btn = QPushButton("Change Ableton Path")
        self.browse_btn.clicked.connect(self.manual_browse)

        layout.addWidget(QLabel("<b>Atmos Bridge Control</b>"))
        layout.addWidget(self.status_label)
        layout.addWidget(self.path_label)
        layout.addStretch()
        layout.addWidget(self.launch_btn)
        layout.addWidget(self.browse_btn)
        self.setLayout(layout)

    def auto_discover(self):
        """Logic to find the EXE without user input."""
        # Check saved config first
        if self.config_path.exists():
            saved = self.config_path.read_text().strip()
            if os.path.exists(saved):
                self.set_path(saved)
                return

        # Common Wine/Nobara install locations
        search_dirs = [
            Path.home() / ".wine/drive_c/Program Files",
            Path.home() / ".wine/drive_c/Program Files (x86)",
            Path.home() / ".wine/drive_c/Program Files/Common Files"
        ]

        for s_dir in search_dirs:
            if s_dir.exists():
                # Glob search for the actual binary
                matches = list(s_dir.rglob("Live.exe"))
                if matches:
                    self.set_path(str(matches[0]))
                    return

    def set_path(self, path):
        self.current_path = path
        self.path_label.setText(f"Target: {path}")
        self.status_label.setText("Status: Ableton Found")

    def manual_browse(self):
        file, _ = QFileDialog.getOpenFileName(self, "Find Live.exe", str(Path.home()), "Executables (*.exe)")
        if file:
            self.set_path(file)
            self.config_path.write_text(file)

    def launch_app(self):
        if hasattr(self, 'current_path') and os.path.exists(self.current_path):
            self.status_label.setText("Status: Launching Wine...")
            # Use proper subprocess handling
            subprocess.Popen(["wine", self.current_path],
                             env=os.environ.copy(),
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        else:
            self.status_label.setText("Status: Error - Path not set")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set a cleaner theme style
    app.setStyle('Fusion')
    gui = AtmosBridge()
    gui.show()
    sys.exit(app.exec())
