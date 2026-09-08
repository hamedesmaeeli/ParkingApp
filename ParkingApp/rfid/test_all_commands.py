# rfid/test_all_commands.py
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

    packet = struct.pack('BBBB{}BB'.format(len(data)), STX, ADDR, length, command, *(data + [bcc]))

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


def test_all_commands():
    commands = [
        (0x21, "اطلاعات دستگاه"),
        (0x22, "اطلاعات نسخه"),
        (0x25, "تنظیم آدرس"),
        (0x31, "تنظیم حالت"),
        (0x32, "گرفتن وضعیت"),
        (0x38, "خواندن کارت"),
        (0x39, "خواب"),
        (0x3A, "بیدار"),
        (0x3B, "ریست"),
        (0x40, "نوشتن کارت"),
        (0x41, "حذف کارت"),
    ]

    for cmd, name in commands:
        print(f"\n🔍 تست {name} (0x{cmd:02X})")
        response = send_command(cmd)
        if response:
            print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
        else:
            print("⏳ بدون پاسخ")


if __name__ == "__main__":
    test_all_commands()