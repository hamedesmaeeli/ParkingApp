# test_commands.py
import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x01


def send_command(command, data=[], baudrate=115200):
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
        time.sleep(0.2)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_multiple_commands():
    commands = [
        (0x21, "اطلاعات دستگاه"),  # قبلاً کار کرده
        (0x31, "تنظیم حالت"),  # تنظیم حالت دستگاه
        (0x3A, "توقف"),  # توقف دستگاه
    ]

    for cmd, name in commands:
        print(f"\n🔍 تست دستور {name} (0x{cmd:02X})")
        response = send_command(cmd)
        if response:
            print(f"📥 Received: {binascii.b2a_hex(response).decode()}")
            if len(response) >= 5:
                status = response[4]
                if status == 0x00:
                    print("✅ موفق")
                else:
                    print(f"⚠️ وضعیت: {status:02X}")
        else:
            print("⏳ پاسخی دریافت نشد.")
        time.sleep(1)


if __name__ == "__main__":
    test_multiple_commands()