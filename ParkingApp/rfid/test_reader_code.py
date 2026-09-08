import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x00

def communicate(command, data=[]):
    # محاسبه LEN و BCC
    length = 1 + len(data)  # 1 بایت برای CMD
    bcc = ADDR ^ length ^ command
    for b in data:
        bcc ^= b

    # ساخت بسته
    if len(data):
        packet = struct.pack('BBBB{}BB'.format(len(data)), STX, ADDR, length, command, *(data + [bcc]))
    else:
        packet = struct.pack('BBBBB', STX, ADDR, length, command, bcc)

    # نمایش بسته ارسالی برای دیباگ
    print(f"📤 Sending: {binascii.b2a_hex(packet).decode()}")

    ser = serial.Serial('COM6', 9600, timeout=1)
    ser.write(packet)
    time.sleep(0.1)
    resp = ser.read(256)  # خواندن پاسخ
    ser.close()

    # نمایش پاسخ دریافتی
    if resp:
        print(f"📥 Received: {binascii.b2a_hex(resp).decode()}")
    else:
        print("⏳ No response received.")

# تست دریافت شماره نسخه (دستور 0x21)
communicate(0x21)