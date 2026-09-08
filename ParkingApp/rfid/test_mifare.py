# rfid/test_mifare.py
import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x01


def send_command(command, data=[], baudrate=9600):
    length = 1 + len(data)
    bcc = ADDR ^ length ^ command
    for b in data:
        bcc ^= b

    if len(data):
        packet = struct.pack('BBBB{}BB'.format(len(data)), STX, ADDR, length, command, *(data + [bcc]))
    else:
        packet = struct.pack('BBBBB', STX, ADDR, length, command, bcc)

    print(f"📤 Sending: {binascii.b2a_hex(packet).decode()}")

    try:
        ser = serial.Serial('COM6', baudrate, timeout=2)
        ser.write(packet)
        time.sleep(0.3)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def reset_reader():
    """ریست دستگاه"""
    print("🔄 ریست دستگاه...")
    response = send_command(0x3B)  # دستور ریست
    if response:
        print(f"📥 Response: {binascii.b2a_hex(response).decode()}")
        return response
    return None


def read_card_with_prep():
    """آماده‌سازی و خواندن کارت"""
    # ۱. ریست دستگاه
    reset_reader()
    time.sleep(1)

    # ۲. تنظیم حالت
    send_command(0x31, [0x00])
    time.sleep(0.5)

    # ۳. خواندن کارت
    print("📇 لطفاً کارت را روی دستگاه قرار دهید...")
    time.sleep(2)
    return send_command(0x38)


if __name__ == "__main__":
    print("🔍 تست کامل RFID Reader")
    print("=" * 40)

    # تست اصلی
    response = read_card_with_prep()

    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")

        # بررسی پاسخ
        if response[0] == STX and len(response) >= 5:
            status = response[4]
            if status == 0x00:
                uid = response[5:9]
                print(f"✅ UID: {binascii.b2a_hex(uid).decode()}")
            else:
                print(f"❌ Status Error: {status:02X}")
                if status == 0x0F:
                    print("   → کارت روی دستگاه قرار ندارد.")
                elif status == 0x10:
                    print("   → خطای ارتباط با کارت.")
                elif status == 0x11:
                    print("   → کارت نامعتبر.")
    else:
        print("❌ پاسخی دریافت نشد.")