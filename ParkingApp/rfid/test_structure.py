# rfid/test_structure.py
import serial
import binascii
import struct

STX = 0x02
ADDR = 0x00
PORT = "COM6"
BAUDRATE = 9600

def send_command(command, data=[]):
    length = 1 + len(data)
    bcc = ADDR ^ length ^ command
    for b in data:
        bcc ^= b

    if len(data):
        packet = struct.pack('BBBB{}BB'.format(len(data)), STX, ADDR, length, command, *(data + [bcc]))
    else:
        packet = struct.pack('BBBBB', STX, ADDR, length, command, bcc)

    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    ser.write(packet)
    import time
    time.sleep(0.3)
    resp = ser.read(256)
    ser.close()
    return resp

print("🔍 تست ساختار پاسخ...")
response = send_command(0x21)

if response:
    print(f"📥 Received (HEX): {binascii.b2a_hex(response).decode()}")
    print(f"📥 Length: {len(response)} bytes")
    print("\n📊 تحلیل بایت‌ها:")
    for i, b in enumerate(response):
        print(f"   بایت {i}: {b:02X} (index {i})")