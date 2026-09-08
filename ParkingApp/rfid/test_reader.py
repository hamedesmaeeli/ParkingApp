"""
تست RFID Reader
"""

import sys
import os

# ===== اضافه کردن مسیر پروژه =====
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox
from PyQt5.QtCore import Qt
from rfid.reader import RFIDReader  # ← import مطلق


class RFIDTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.reader = RFIDReader()
        self.init_ui()
        self.setup_connections()
        self.load_ports()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # عنوان
        title = QLabel("🧪 تست RFID Reader")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # انتخاب پورت
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("پورت:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        port_layout.addWidget(self.port_combo)
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(40)
        self.refresh_btn.clicked.connect(self.load_ports)
        port_layout.addWidget(self.refresh_btn)
        layout.addLayout(port_layout)

        # وضعیت
        self.status_label = QLabel("⏳ در حال جستجوی دستگاه...")
        self.status_label.setStyleSheet("font-size: 14px; padding: 8px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)

        # دکمه‌های کنترل
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("🔗 اتصال")
        self.connect_btn.clicked.connect(self.connect_reader)
        self.start_btn = QPushButton("▶️ شروع")
        self.start_btn.clicked.connect(self.start_reader)
        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.clicked.connect(self.stop_reader)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # ورود دستی
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("کارت دستی:"))
        self.card_input = QPushButton("📇 شبیه‌سازی")
        self.card_input.clicked.connect(self.manual_card)
        manual_layout.addWidget(self.card_input)
        layout.addLayout(manual_layout)

        # لاگ
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: monospace; font-size: 12px; min-height: 200px;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.setWindowTitle("تست RFID Reader")
        self.resize(500, 450)

    def load_ports(self):
        self.port_combo.clear()
        ports = self.reader.get_available_ports()
        for port in ports:
            self.port_combo.addItem(f"{port['port']} - {port['description']}", port['port'])
        if ports:
            self.log(f"📋 {len(ports)} پورت پیدا شد")
        else:
            self.log("⚠️ هیچ پورتی پیدا نشد")

    def setup_connections(self):
        self.reader.card_read.connect(self.on_card_read)
        self.reader.error_occurred.connect(self.on_error)
        self.reader.status_changed.connect(self.on_status_change)

    def connect_reader(self):
        port = self.port_combo.currentData()
        if self.reader.connect(port):
            self.connect_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.log(f"✅ متصل به {port}")
        else:
            self.log(f"❌ خطا در اتصال به {port}")

    def start_reader(self):
        self.reader.start_reading()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log("▶️ شروع خواندن کارت...")

    def stop_reader(self):
        self.reader.stop_reading()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("⏹️ توقف خواندن کارت")

    def manual_card(self):
        import random
        card = f"{random.randint(10000000, 99999999)}"
        self.reader.manual_read(card)

    def log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")

    def on_card_read(self, card_number):
        self.log(f"📇 کارت: {card_number}")

    def on_error(self, error):
        self.log(f"❌ {error}")

    def on_status_change(self, status):
        self.status_label.setText(status)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTestWindow()
    window.show()
    sys.exit(app.exec_())