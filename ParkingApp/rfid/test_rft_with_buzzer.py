# rfid/test_rft_with_buzzer.py
"""
تست کامل RFT-23x با احراز هویت و بوق
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

# کلید پیش‌فرض MIFARE
DEFAULT_KEY = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])


def send_command(command, data=[], addr=ADDR):
    """ارسال دستور طبق پروتکل"""
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


def buzzer(beep_time=3, addr=ADDR):
    """
    کنترل بوق (دستور 0x2C)

    Args:
        beep_time (int): زمان بوق به واحد 10ms (پیش‌فرض 3 = 30ms)
        addr (int): آدرس دستگاه
    """
    print(f"🔔 بوق به مدت {beep_time * 10}ms...")
    response = send_command(0x2C, [beep_time], addr)
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            print("   ✅ بوق با موفقیت پخش شد.")
            return True
        else:
            print(f"   ❌ خطا در پخش بوق: {status:02X}")
            return False
    return False


def buzzer_success():
    """بوق موفقیت (۳ بوق کوتاه)"""
    for _ in range(3):
        buzzer(2)
        time.sleep(0.1)


def buzzer_error():
    """بوق خطا (۱ بوق بلند)"""
    buzzer(10)


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


def load_key(key=DEFAULT_KEY):
    """بارگذاری کلید"""
    response = send_command(0x35, list(key))
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            return True
    return False


def authenticate(block=0, snr=None, key_type=0x60):
    """احراز هویت"""
    if not snr:
        return False
    data = [key_type, block] + list(snr)
    response = send_command(0x37, data)
    if response and len(response) >= 4:
        status = response[3]
        return status == 0x00
    return False


def read_block(block=0, count=1):
    """خواندن بلاک"""
    response = send_command(0x38, [block, count])
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00 and len(response) > 4:
            return response[4:-1]
    return None


def main():
    print("=" * 60)
    print("🧪 تست کامل RFT-23x با بوق")
    print("=" * 60)

    # ۱. اطلاعات دستگاه
    info = get_info()
    print(f"📟 دستگاه: {info}")

    # ۲. بوق تست
    print("\n🔔 تست بوق...")
    buzzer(5)
    time.sleep(0.5)

    # ۳. درخواست کارت
    print("\n📇 لطفاً کارت را روی دستگاه قرار دهید...")
    time.sleep(1)

    card_type = request_card()
    if not card_type:
        print("❌ کارت تشخیص داده نشد!")
        buzzer_error()
        return
    print(f"✅ نوع کارت: {card_type.hex().upper()}")

    # ۴. دریافت SNR
    snr = anticoll()
    if not snr:
        print("❌ SNR دریافت نشد!")
        buzzer_error()
        return
    print(f"✅ SNR: {snr.hex().upper()}")

    # ۵. انتخاب کارت
    sak = select_card(snr)
    if sak is None:
        print("❌ کارت انتخاب نشد!")
        buzzer_error()
        return
    print(f"✅ SAK: {sak:02X}")

    # ۶. بارگذاری کلید
    if not load_key():
        print("❌ بارگذاری کلید ناموفق!")
        buzzer_error()
        return
    print("✅ کلید بارگذاری شد.")

    # ۷. احراز هویت
    if not authenticate(block=0, snr=snr):
        print("❌ احراز هویت ناموفق!")
        buzzer_error()
        return
    print("✅ احراز هویت موفق!")

    # ۸. خواندن بلاک
    data = read_block(0, 1)
    if data:
        print(f"✅ داده‌های بلاک 0: {data.hex().upper()}")
        # ===== بوق موفقیت =====
        buzzer_success()
    else:
        print("❌ خواندن بلاک ناموفق!")
        buzzer_error()

    print("\n" + "=" * 60)
    print("🎉 تست کامل شد!")
    print("=" * 60)


if __name__ == "__main__":
    main()