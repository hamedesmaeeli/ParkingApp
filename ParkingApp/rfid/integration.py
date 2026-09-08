# rfid/integration.py
from PyQt5.QtCore import QObject, pyqtSignal
from .reader import RFIDReader


class RFIDIntegration(QObject):
    card_scanned = pyqtSignal(str)

    def __init__(self, port="COM6", baudrate=115200):
        super().__init__()
        self.reader = RFIDReader(port, baudrate)
        self.reader.card_detected.connect(self.on_card_detected)
        self.reader.error_occurred.connect(self.on_error)
        self.reader.status_changed.connect(self.on_status_changed)

        self.current_mode = "entry"  # 'entry' یا 'exit'
        self.last_card = None

    def set_mode(self, mode):
        """تنظیم حالت ورود یا خروج"""
        self.current_mode = mode
        print(f"🔄 حالت RFID: {mode}")

    def on_card_detected(self, uid):
        self.last_card = uid
        self.card_scanned.emit(uid)
        print(f"📇 کارت {uid} در حالت {self.current_mode} تشخیص داده شد")

    def on_error(self, error):
        print(f"❌ خطای RFID: {error}")

    def on_status_changed(self, status):
        print(f"📡 وضعیت RFID: {status}")

    def start(self):
        self.reader.start_reading()

    def stop(self):
        self.reader.stop_reading()