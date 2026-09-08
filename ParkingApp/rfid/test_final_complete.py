# rfid/test_modes.py
import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x00
PORT = "COM6"
BAUDRATE = 9600


def send_command(command, data=[], addr=ADDR):
    length = 1 + len(data)
    bcc = addr ^ length ^ command
    for b in data:
        bcc ^= b

    if len(data):
        packet = struct.pack('BBBB{}BB'.format(len(data)), STX, addr, length, command, *(data + [bcc]))
    else:
        packet = struct.pack('BBBBB', STX, addr, length, command, bcc)

    print(f"📤 Sending: {binascii.b2a_hex(packet).decode()}")

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=2)
        ser.write(packet)
        time.sleep(0.3)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None


def test_modes():
    """تست تنظیم حالت با پارامترهای مختلف"""
    modes = [
        (0x00, "حالت عادی"),
        (0x01, "حالت تست"),
        (0x02, "حالت صرفه‌جویی"),
        (0x03, "حالت فعال"),
        (0x04, "حالت غیرفعال"),
    ]

    print("🔍 تست تنظیم حالت با پارامترهای مختلف")
    print("=" * 40)

    for mode, name in modes:
        print(f"\n🔄 تنظیم حالت: {name} (0x{mode:02X})")
        response = send_command(0x31, [mode])

        if response:
            print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
            if len(response) >= 4:
                status = response[3]
                if status == 0x00:
                    print("   ✅ موفق!")
                    return mode
                else:
                    print(f"   ⚠️ خطا: {status:02X}")
        else:
            print("   ❌ پاسخی دریافت نشد.")

        time.sleep(0.5)

    print("\n❌ هیچ حالتی کار نکرد.")
    return None


def read_card_without_mode():
    """خواندن کارت بدون تنظیم حالت"""
    print("\n📇 تلاش برای خواندن کارت بدون تنظیم حالت...")
    print("   لطفاً کارت را روی دستگاه قرار دهید...")
    time.sleep(1.5)

    response = send_command(0x38)

    if response and len(response) >= 4:
        status = response[3]
        if status == 0x00:
            uid = response[4:8]
            uid_str = binascii.b2a_hex(uid).decode().upper()
            print(f"   ✅ UID: {uid_str}")
            return uid
        else:
            print(f"   ❌ خطا: {status:02X}")
    return None


if __name__ == "__main__":
    # ۱. تنظیم آدرس
    print("🔍 تنظیم آدرس...")
    response = send_command(0x25, [0x00])
    if response:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")

    # ۲. تست حالت‌های مختلف
    mode = test_modes()

    # ۳. خواندن کارت
    if mode is not None:
        print("\n🔍 خواندن کارت با حالت تنظیم‌شده...")
        read_card_without_mode()
    else:
        print("\n🔍 خواندن کارت بدون تنظیم حالت...")
        read_card_without_mode()