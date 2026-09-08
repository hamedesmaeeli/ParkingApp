"""
ساده‌ترین خواننده RFID - فقط بوق + UID
"""

import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x00
PORT = "COM6"
BAUDRATE = 115200
#BAUDRATE = 9600
TIMEOUT = 2


def send_command(command, data=[], addr=ADDR):
    """ارسال دستور به دستگاه"""
    length = 1 + len(data)
    bcc = addr ^ length ^ command
    for b in data:
        bcc ^= b

    packet = bytes([STX, addr, length, command]) + bytes(data) + bytes([bcc])

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        ser.write(packet)
        time.sleep(0.2)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None


def buzzer(beep_time=3):
    """بوق (دستور 0x2C) - beep_time بر حسب 10ms"""
    response = send_command(0x2C, [beep_time])
    if response and len(response) >= 4:
        return response[3] == 0x00
    return False


def request_card():
    """درخواست کارت"""
    response = send_command(0x31, [0x52])
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) >= 6:
            return response[4:6]
    return None


def anticoll():
    """دریافت UID کارت (دستور 0x32)"""
    response = send_command(0x32, [0x93])
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) >= 8:
            return response[4:8]  # UID 4 بایت
    return None


def read_card_simple():
    """
    خواندن ساده کارت:
    1. درخواست کارت
    2. دریافت UID
    3. بوق
    """
    print("\n📇 لطفاً کارت را روی دستگاه قرار دهید...")

    # ۱. درخواست کارت
    card_type = request_card()
    if not card_type:
        print("❌ کارت تشخیص داده نشد!")
        return None

    print(f"✅ نوع کارت: {card_type.hex().upper()}")

    # ۲. دریافت UID
    uid = anticoll()
    if not uid:
        print("❌ UID دریافت نشد!")
        return None

    uid_hex = uid.hex().upper()
    print(f"✅ UID: {uid_hex}")

    # ۳. بوق
    buzzer(5)  # 50ms
    print("🔔 بوق!")

    return uid_hex


def main():
    print("=" * 50)
    print("🧪 خواننده ساده RFID")
    print("=" * 50)

    # اطلاعات دستگاه (اختیاری)
    response = send_command(0x21)
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) > 4:
            data = response[4:-1]
            print(f"📟 دستگاه: {data.decode('ascii', errors='ignore')}")

    # خواندن کارت
    uid = read_card_simple()

    if uid:
        print("\n" + "=" * 50)
        print(f"🎉 کارت خوانده شد! UID: {uid}")
        print("=" * 50)
    else:
        print("\n❌ خواندن کارت ناموفق بود.")
        print("   لطفاً کارت را روی دستگاه قرار دهید.")


if __name__ == "__main__":
    main()