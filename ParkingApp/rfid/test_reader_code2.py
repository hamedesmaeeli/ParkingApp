# rfid/test_read_card.py
import serial
import time
import binascii
import struct

STX = 0x02
ADDR = 0x01  # آدرس دستگاه که در پاسخ قبلی دریافت شد


def send_command(command, data=[], baudrate=9600):
    """ارسال دستور به دستگاه و دریافت پاسخ"""
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


def read_card():
    """تلاش برای خواندن کارت"""
    print("📇 لطفاً یک کارت را روی دستگاه قرار دهید...")
    time.sleep(1)  # فرصت برای قرار دادن کارت

    # دستور 0x38 برای خواندن کارت
    response = send_command(0x38)

    if response and len(response) > 0:
        print(f"📥 Received: {binascii.b2a_hex(response).decode()}")

        # تجزیه پاسخ
        if response[0] == STX:
            status = response[4]  # بایت پنجم (وضعیت)
            if status == 0x00:
                # موفقیت - استخراج UID کارت
                uid = response[5:9]  # ۴ بایت UID
                print(f"✅ Card UID: {binascii.b2a_hex(uid).decode()}")
                print(f"   UID (decimal): {int.from_bytes(uid, byteorder='big')}")
                return uid
            else:
                print(f"❌ خطا در خواندن کارت (Status: {status:02X})")
                return None
    else:
        print("⏳ پاسخی از دستگاه دریافت نشد.")
        return None


if __name__ == "__main__":
    read_card()