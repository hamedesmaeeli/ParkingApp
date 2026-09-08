# test_all_baudrates.py
import serial
import time


def test_all_baudrates(port="COM6"):
    baudrates = [9600, 115200, 19200, 57600, 2400, 4800, 38400]

    for baud in baudrates:
        print(f"\n🔍 تست Baud Rate: {baud}")
        try:
            ser = serial.Serial(port, baud, timeout=2)
            print(f"✅ متصل شد! در حال گوش دادن برای ۳ ثانیه...")
            time.sleep(3)
            ser.close()
        except Exception as e:
            print(f"❌ خطا: {e}")


if __name__ == "__main__":
    test_all_baudrates()