# test_rfid_integration.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt
from rfid.integration import RFIDIntegration


class RFIDTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.rfid = RFIDIntegration()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("⏳ در حال آماده‌سازی...")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶️ شروع")
        self.start_btn.clicked.connect(self.start_rfid)
        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.clicked.connect(self.stop_rfid)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: monospace; font-size: 12px; min-height: 300px;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.setWindowTitle("RFID Integration Test")
        self.resize(500, 400)

    def setup_connections(self):
        self.rfid.card_scanned.connect(self.on_card_scanned)
        self.rfid.reader.status_changed.connect(self.on_status)
        self.rfid.reader.error_occurred.connect(self.on_error)

    def start_rfid(self):
        self.rfid.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log("▶️ شروع خواندن کارت...")

    def stop_rfid(self):
        self.rfid.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("⏹️ توقف خواندن کارت")

    def on_card_scanned(self, uid):
        self.log(f"📇 کارت شناسایی شد: {uid}")
        self.status_label.setText(f"✅ کارت: {uid}")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #d4edda;")

    def on_status(self, status):
        self.status_label.setText(status)
        self.log(f"📡 {status}")

    def on_error(self, error):
        self.log(f"❌ {error}")

    def log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTestWindow()
    window.show()
    sys.exit(app.exec_())