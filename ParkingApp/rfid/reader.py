# rfid/reader.py
"""
RFID Reader - کلاس اصلی برای ارتباط با دستگاه RFT-23x
"""

import serial
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class RFIDReader(QObject):
    """
    کلاس مدیریت دستگاه RFID Reader
    """

    card_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, port="COM6", baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = 2
        self.is_running = False
        self.reader_thread = None

        self.STX = 0x02
        self.ADDR = 0x00

        # ===== تست اتصال (اختیاری - حذف شد) =====
        # دیگر اتصال را در __init__ بررسی نمی‌کنیم
        print(f"🔌 RFIDReader آماده: {port}@{baudrate}")

    def send_command(self, command, data=[]):
        """ارسال دستور به دستگاه"""
        length = 1 + len(data)
        bcc = self.ADDR ^ length ^ command
        for b in data:
            bcc ^= b

        packet = bytes([self.STX, self.ADDR, length, command]) + bytes(data) + bytes([bcc])

        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            ser.write(packet)
            time.sleep(0.2)
            resp = ser.read(256)
            ser.close()
            return resp
        except Exception as e:
            self.error_occurred.emit(f"خطا در ارسال: {str(e)}")
            return None

    def buzzer(self, beep_time=5):
        """بوق زدن"""
        try:
            response = self.send_command(0x2C, [beep_time])
            return response and len(response) >= 4 and response[3] == 0x00
        except:
            return False

    def request_card(self):
        """درخواست کارت"""
        response = self.send_command(0x31, [0x52])
        if response and len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) >= 6:
                return response[4:6]
        return None

    def anticoll(self):
        """دریافت UID کارت"""
        response = self.send_command(0x32, [0x93])
        if response and len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) >= 8:
                return response[4:8]
        return None

    def read_card(self):
        """خواندن کامل کارت: درخواست + UID + بوق"""
        card_type = self.request_card()
        if not card_type:
            return None

        uid = self.anticoll()
        if not uid:
            return None

        uid_hex = uid.hex().upper()
        print(f"   ✅ UID: {uid_hex}")

        self.buzzer(5)

        return uid_hex

    def read_loop(self):
        """حلقه خواندن مداوم کارت"""
        print("🔄 read_loop started")
        while self.is_running:
            try:
                uid = self.read_card()
                if uid:
                    self.card_detected.emit(uid)
                    self.status_changed.emit(f"✅ کارت: {uid}")
                    time.sleep(1)
                else:
                    time.sleep(0.3)
            except Exception as e:
                self.error_occurred.emit(str(e))
                time.sleep(0.5)

    def start_reading(self):
        """شروع خواندن مداوم کارت"""
        if self.is_running:
            return

        self.is_running = True
        self.reader_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.reader_thread.start()
        self.status_changed.emit("🔄 در حال خواندن کارت...")

    def stop_reading(self):
        """توقف خواندن مداوم کارت"""
        self.is_running = False
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=1)
        self.status_changed.emit("⏹️ متوقف شد")