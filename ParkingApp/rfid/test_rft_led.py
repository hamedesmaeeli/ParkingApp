# rfid/test_rft_led.py
"""
تست RFT-23x با کنترل LED و بوق
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


def led_control(led1=0, led2=0, addr=ADDR):
    """
    کنترل LED (دستور 0x23)

    Args:
        led1 (int): 0 = خاموش, 1 = روشن
        led2 (int): 0 = خاموش, 1 = روشن
    """
    print(f"💡 تنظیم LED: LED1={led1}, LED2={led2}")
    response = send_command(0x23, [led1, led2], addr)
    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            print("   ✅ LED تنظیم شد.")
            return True
        else:
            print(f"   ❌ خطا: {status:02X}")
            return False
    return False


def led_red():
    """LED قرمز (LED1 روشن، LED2 خاموش)"""
    return led_control(1, 0)


def led_green():
    """LED سبز (LED1 خاموش، LED2 روشن)"""
    return led_control(0, 1)


def led_off():
    """LED خاموش"""
    return led_control(0, 0)


def led_yellow():
    """LED زرد (هر دو روشن)"""
    return led_control(1, 1)


def buzzer(beep_time=3, addr=ADDR):
    """کنترل بوق"""
    response = send_command(0x2C, [beep_time], addr)
    if response and len(response) >= 4:
        return response[3] == 0x00
    return False


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
        return response[3] == 0x00
    return False


def authenticate(block=0, snr=None, key_type=0x60):
    """احراز هویت"""
    if not snr:
        return False
    data = [key_type, block] + list(snr)
    response = send_command(0x37, data)
    if response and len(response) >= 4:
        return response[3] == 0x00
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
    print("🧪 تست RFT-23x با کنترل LED و بوق")
    print("=" * 60)

    # ۱. اطلاعات دستگاه
    info = get_info()
    print(f"📟 دستگاه: {info}")

    # ۲. تست LEDها
    print("\n💡 تست LED...")
    led_red()
    time.sleep(1)
    led_green()
    time.sleep(1)
    led_yellow()
    time.sleep(1)
    led_off()

    # ۳. درخواست کارت
    print("\n📇 لطفاً کارت را روی دستگاه قرار دهید...")

    # LED قرمز = در انتظار کارت
    led_red()

    card_type = request_card()
    if not card_type:
        print("❌ کارت تشخیص داده نشد!")
        led_off()
        return
    print(f"✅ نوع کارت: {card_type.hex().upper()}")

    # ===== کارت شناسایی شد =====
    # LED سبز + بوق
    led_green()
    buzzer(5)
    # ===========================

    # ۴. دریافت SNR
    snr = anticoll()
    if not snr:
        print("❌ SNR دریافت نشد!")
        led_red()
        return
    print(f"✅ SNR: {snr.hex().upper()}")

    # ۵. انتخاب کارت
    sak = select_card(snr)
    if sak is None:
        print("❌ کارت انتخاب نشد!")
        led_red()
        return
    print(f"✅ SAK: {sak:02X}")

    # ۶. بارگذاری کلید
    if not load_key():
        print("❌ بارگذاری کلید ناموفق!")
        led_red()
        return
    print("✅ کلید بارگذاری شد.")

    # ۷. احراز هویت
    if not authenticate(block=0, snr=snr):
        print("❌ احراز هویت ناموفق!")
        led_red()
        return
    print("✅ احراز هویت موفق!")

    # ۸. خواندن بلاک
    data = read_block(0, 1)
    if data:
        print(f"✅ داده‌های بلاک 0: {data.hex().upper()}")
        # LED سبز چشمک‌زن (موفقیت)
        for _ in range(3):
            led_green()
            time.sleep(0.2)
            led_off()
            time.sleep(0.2)
    else:
        print("❌ خواندن بلاک ناموفق!")
        led_red()

    # LED خاموش
    time.sleep(1)
    led_off()

    print("\n" + "=" * 60)
    print("🎉 تست کامل شد!")
    print("=" * 60)


if __name__ == "__main__":
    main()