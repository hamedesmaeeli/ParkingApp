# rfid/test_rft_protocol.py
"""
تست کامل RFT-23x بر اساس مستندات رسمی
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


def send_command(command, data=[], addr=ADDR):
    """ارسال دستور طبق پروتکل مستندات"""
    length = 1 + len(data)  # 1 بایت برای CMD
    bcc = addr ^ length ^ command
    for b in data:
        bcc ^= b

    # ساخت بسته: STX + ADDR + LEN + CMD + DATA + BCC
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


def get_device_info():
    """دریافت اطلاعات دستگاه (دستور 0x21)"""
    print("\n🔍 دریافت اطلاعات دستگاه...")
    response = send_command(0x21)
    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        if len(response) >= 4:
            status = response[3]
            print(f"   وضعیت: {status:02X}")
            if status == 0x00 and len(response) > 4:
                data = response[4:-1]
                try:
                    print(f"   ✅ اطلاعات: {data.decode('ascii')}")
                except:
                    print(f"   ✅ داده: {binascii.b2a_hex(data).decode()}")
        return True
    return False


def request_card():
    """درخواست کارت (دستور 0x31 با پارامتر 0x52)"""
    print("\n🔍 درخواست کارت...")
    print("   لطفاً کارت را روی دستگاه قرار دهید...")
    time.sleep(0.5)
    response = send_command(0x31, [0x52])  # 0x52 = درخواست همه کارت‌ها

    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        if len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) >= 6:
                card_type = response[4:6]
                print(f"   ✅ نوع کارت: {binascii.b2a_hex(card_type).decode()}")
                return True
            else:
                print(f"   ❌ خطا: {status:02X} (تفسیر: {get_error_message(status)})")
                return False
    return False


def anticoll():
    """دریافت شماره سریال کارت (دستور 0x32 با پارامتر 0x93)"""
    print("\n🔍 دریافت شماره سریال کارت...")
    response = send_command(0x32, [0x93])  # 0x93 = Anticoll level 1

    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        if len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) >= 8:
                snr = response[4:8]
                print(f"   ✅ SNR: {binascii.b2a_hex(snr).decode()}")
                return snr
            else:
                print(f"   ❌ خطا: {status:02X} ({get_error_message(status)})")
                return None
    return None


def select_card(snr):
    """انتخاب کارت (دستور 0x33 با پارامتر 0x93 + SNR)"""
    print("\n🔍 انتخاب کارت...")
    response = send_command(0x33, [0x93] + list(snr))

    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        if len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) >= 5:
                sak = response[4]
                print(f"   ✅ SAK: {sak:02X}")
                return True
            else:
                print(f"   ❌ خطا: {status:02X}")
                return False
    return False


def read_card(block=0, count=1):
    """خواندن بلاک کارت (دستور 0x38)"""
    print(f"\n🔍 خواندن بلاک {block} (تعداد {count})...")
    response = send_command(0x38, [block, count])

    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        if len(response) >= 4:
            status = response[3]
            if status == 0x00 and len(response) > 4:
                data = response[4:-1]
                print(f"   ✅ داده: {binascii.b2a_hex(data).decode()}")
                return data
            else:
                print(f"   ❌ خطا: {status:02X} ({get_error_message(status)})")
                return None
    return None


def get_error_message(status):
    """ترجمه کدهای خطا از مستندات (بخش ۴.۳)"""
    errors = {
        0x00: "موفق",
        0x01: "کارت وجود ندارد (No Card)",
        0x02: "خطای Anticoll",
        0x03: "خطای بیت شمار",
        0x04: "خطای داده برگشتی",
        0x05: "خطای احراز هویت",
        0x0D: "خطای عملیات Value",
        0x0E: "خطای عملیات کارت",
        0x0F: "زمان عملیات کارت به پایان رسید",
        0x10: "خطای دستور یا پارامتر",
        0x11: "سایر خطاها"
    }
    return errors.get(status, f"خطای ناشناخته ({status:02X})")


def main():
    print("=" * 60)
    print("🧪 تست RFT-23x بر اساس مستندات رسمی")
    print("=" * 60)

    # ۱. اطلاعات دستگاه
    get_device_info()
    time.sleep(0.5)

    # ۲. درخواست کارت
    if not request_card():
        print("\n❌ کارت تشخیص داده نشد!")
        print("   لطفاً یک کارت MIFARE را روی دستگاه قرار دهید.")
        return

    time.sleep(0.5)

    # ۳. دریافت شماره سریال
    snr = anticoll()
    if not snr:
        print("\n❌ شماره سریال کارت دریافت نشد.")
        return

    time.sleep(0.5)

    # ۴. انتخاب کارت
    if not select_card(snr):
        print("\n❌ کارت انتخاب نشد.")
        return

    time.sleep(0.5)

    # ۵. خواندن بلاک 0 (Manufacturer Block)
    data = read_card(0, 1)
    if data:
        print(f"\n✅ داده‌های بلاک 0: {data.hex().upper()}")

    print("\n" + "=" * 60)
    print("🎉 تست کامل شد!")
    print("=" * 60)


if __name__ == "__main__":
    main()