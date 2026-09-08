# rfid/test_read_card_improved.py
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
        time.sleep(0.2)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def read_card_retry():
    """تلاش برای خواندن کارت با تأخیر و تکرار"""
    for attempt in range(3):
        print(f"\n🔄 تلاش {attempt + 1} از 3")
        print("📇 لطفاً یک کارت را روی دستگاه قرار دهید...")

        # تأخیر برای قرار دادن کارت
        time.sleep(1.5)

        response = send_command(0x38)

        if response and len(response) > 0:
            print(f"📥 Received: {binascii.b2a_hex(response).decode()}")

            if response[0] == STX and len(response) >= 5:
                status = response[4]
                if status == 0x00:
                    # خواندن UID
                    uid = response[5:9]  # ۴ بایت UID
                    print(f"✅ Card UID: {binascii.b2a_hex(uid).decode()}")
                    print(f"   UID (decimal): {int.from_bytes(uid, byteorder='big')}")
                    return uid
                else:
                    print(f"⚠️ خطا در خواندن کارت (Status: {status:02X})")
                    if status == 0x0F:
                        print("   → کارت روی دستگاه قرار ندارد.")
            else:
                print("⚠️ پاسخ نامعتبر.")
        else:
            print("⏳ پاسخی دریافت نشد.")

        time.sleep(1)

    print("\n❌ خواندن کارت پس از ۳ تلاش ناموفق بود.")
    return None


if __name__ == "__main__":
    read_card_retry()