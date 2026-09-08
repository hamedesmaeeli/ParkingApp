# test_rfid_baudrate.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rfid.reader import RFIDReader
import time


def test_baudrates():
    port = "COM6"
    baudrates = [9600, 115200, 2400, 4800, 19200, 38400, 57600]

    for baud in baudrates:
        print(f"\n🔍 تست با Baud Rate: {baud}")
        reader = RFIDReader(port=port, baudrate=baud)

        if reader.connect():
            print(f"✅ متصل شد! در حال گوش دادن برای ۳ ثانیه...")
            reader.start_reading()
            time.sleep(3)
            reader.stop_reading()
            reader.serial_connection.close()
        else:
            print(f"❌ اتصال با {baud} ممکن نیست")


if __name__ == "__main__":
    test_baudrates()