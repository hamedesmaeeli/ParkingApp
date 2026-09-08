# rfid/test_rft_authenticate.py
"""
تست کامل RFT-23x با احراز هویت
"""

import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x00
PORT = "COM6"
BAUDRATE = 9600
TIMEOUT = 2

# کلید پیش‌فرض MIFARE (معمولاً 6 بایت 0xFF)
DEFAULT_KEY = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])


def send_command(command, data=[], addr=ADDR):
    length = 1 + len(data)
    bcc = addr ^ length ^ command
    for b in data:
        bcc ^= b

    packet = bytes([STX, addr, length, command]) + bytes(data) + bytes([bcc])
    print(f"📤 Sending: {binascii.b2a_hex(packet).decode()}")

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


def load_key(key=DEFAULT_KEY):
    """بارگذاری کلید در خواننده (دستور 0x35)"""
    print("\n🔑 بارگذاری کلید...")
    response = send_command(0x35, list(key))
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            print("   ✅ کلید بارگذاری شد.")
            return True
        else:
            print(f"   ❌ خطا: {status:02X}")
            return False
    return False


def authenticate(block=0, snr=None, key_type=0x60):
    """
    احراز هویت (دستور 0x37)
    key_type: 0x60 = KeyA, 0x61 = KeyB
    """
    print(f"\n🔐 احراز هویت برای بلاک {block}...")
    if not snr:
        print("   ❌ SNR موجود نیست!")
        return False

    # پارامترها: key_type + block + snr (4 بایت)
    data = [key_type, block] + list(snr)
    response = send_command(0x37, data)

    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            print("   ✅ احراز هویت موفق!")
            return True
        else:
            print(f"   ❌ خطا: {status:02X}")
            return False
    return False


def read_block(block=0, count=1):
    """خواندن بلاک (دستور 0x38)"""
    print(f"\n📖 خواندن بلاک {block}...")
    response = send_command(0x38, [block, count])

    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) > 4:
            data = response[4:-1]
            print(f"   ✅ داده: {data.hex().upper()}")
            return data
        else:
            print(f"   ❌ خطا: {status:02X}")
            return None
    return None


def get_info():
    """اطلاعات دستگاه"""
    response = send_command(0x21)
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) > 4:
            data = response[4:-1]
            return data.decode('ascii', errors='ignore')
    return "Unknown"


def request_card():
    """درخواست کارت"""
    response = send_command(0x31, [0x52])
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) >= 6:
            return response[4:6]
    return None


def anticoll():
    """دریافت SNR"""
    response = send_command(0x32, [0x93])
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) >= 8:
            return response[4:8]
    return None


def select_card(snr):
    """انتخاب کارت"""
    response = send_command(0x33, [0x93] + list(snr))
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) >= 5:
            return response[4]
    return None


def main():
    print("=" * 60)
    print("🧪 تست کامل RFT-23x با احراز هویت")
    print("=" * 60)

    # ۱. اطلاعات دستگاه
    info = get_info()
    print(f"📟 دستگاه: {info}")

    # ۲. درخواست کارت
    print("\n📇 لطفاً کارت را روی دستگاه قرار دهید...")
    time.sleep(1)

    card_type = request_card()
    if not card_type:
        print("❌ کارت تشخیص داده نشد!")
        return
    print(f"✅ نوع کارت: {card_type.hex().upper()}")

    # ۳. دریافت SNR
    snr = anticoll()
    if not snr:
        print("❌ SNR دریافت نشد!")
        return
    print(f"✅ SNR: {snr.hex().upper()}")

    # ۴. انتخاب کارت
    sak = select_card(snr)
    if sak is None:
        print("❌ کارت انتخاب نشد!")
        return
    print(f"✅ SAK: {sak:02X}")

    # ۵. بارگذاری کلید
    if not load_key():
        print("❌ بارگذاری کلید ناموفق!")
        return

    # ۶. احراز هویت برای بلاک 0
    if not authenticate(block=0, snr=snr):
        print("❌ احراز هویت ناموفق!")
        return

    # ۷. خواندن بلاک 0
    data = read_block(0, 1)
    if data:
        print(f"\n📋 داده‌های بلاک 0: {data.hex().upper()}")

    print("\n" + "=" * 60)
    print("🎉 تست کامل شد!")
    print("=" * 60)


if __name__ == "__main__":
    main()