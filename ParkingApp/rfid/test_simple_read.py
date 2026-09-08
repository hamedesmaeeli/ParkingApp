# test_simple_read.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rfid.reader import RFIDReader
import time

print("🔍 تست ساده RFID Reader...")
reader = RFIDReader(port="COM6")

# تست اتصال
print("📡 تست اتصال...")
response = reader.send_command(0x21)
if response:
    print(f"✅ دستگاه پاسخ داد: {response.hex()}")
else:
    print("❌ دستگاه پاسخ نداد! پورت COM6 را بررسی کنید.")
    exit()

# شروع خواندن
def on_card(uid):
    print(f"📇 کارت: {uid}")

reader.card_detected.connect(on_card)
reader.start_reading()

print("📇 لطفاً کارت را روی دستگاه قرار دهید...")
time.sleep(10)  # ۱۰ ثانیه فرصت
reader.stop_reading()