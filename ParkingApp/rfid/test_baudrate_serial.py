# test_baudrate_serial.py
import serial
import time


def test_baudrates():
    port = "COM6"  # پورت خود را وارد کنید
    baudrates = [9600, 115200, 2400, 4800, 19200, 38400, 57600]

    for baud in baudrates:
        print(f"\n🔍 تست با Baud Rate: {baud}")
        try:
            ser = serial.Serial(port, baud, timeout=1)
            print(f"✅ متصل شد! در حال گوش دادن برای ۵ ثانیه...")
            time.sleep(5)
            ser.close()
        except Exception as e:
            print(f"❌ خطا: {e}")


if __name__ == "__main__":
    test_baudrates()