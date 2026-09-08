# rfid/test_final.py
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


def test_final():
    print("🔍 تست نهایی RFID Reader")
    print("=" * 40)

    # ۱. تنظیم حالت با پارامترهای مختلف
    for param in [0x00, 0x01]:
        print(f"\n🔄 تنظیم حالت با پارامتر {param:02X}")
        response = send_command(0x31, [param])
        if response:
            print(f"📥 Response: {binascii.b2a_hex(response).decode()}")

        # ۲. خواندن کارت
        print("📇 لطفاً کارت را روی دستگاه قرار دهید...")
        time.sleep(2)
        response = send_command(0x38)
        if response:
            print(f"📥 Response: {binascii.b2a_hex(response).decode()}")
            if len(response) >= 5:
                status = response[4]
                if status == 0x00:
                    uid = response[5:9]
                    print(f"✅ UID: {binascii.b2a_hex(uid).decode()}")
                    return True
                elif status == 0x0F:
                    print("   → کارت روی دستگاه قرار ندارد.")
        time.sleep(1)

    print("\n❌ تست ناموفق بود.")
    return False


if __name__ == "__main__":
    test_final()