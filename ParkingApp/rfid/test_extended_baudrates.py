# test_extended_baudrates.py
import serial
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extended_baudrates(port="COM6"):
    """
    تست Baud Rate‌های گسترده‌تر برای یافتن نرخ صحیح
    """
    # Baud Rate‌های رایج و غیرمعمول
    baudrates = [
        1200, 1800, 2400, 3600, 4800, 7200,
        9600, 14400, 19200, 28800, 38400,
        57600, 76800, 115200, 128000, 153600,
        230400, 256000, 460800, 921600
    ]

    print(f"🔍 تست {len(baudrates)} Baud Rate مختلف روی پورت {port}")
    print("📇 لطفاً هنگام هر تست، یک کارت را جلوی دستگاه بگیرید.")
    print("=" * 60)

    working_rates = []

    for baud in baudrates:
        print(f"\n🔍 تست Baud Rate: {baud}")
        try:
            ser = serial.Serial(port, baud, timeout=1)
            print(f"✅ متصل شد! در حال گوش دادن برای ۳ ثانیه...")

            # گوش دادن برای داده
            start_time = time.time()
            data_received = False

            while time.time() - start_time < 3:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    if data:
                        print(f"📇 داده دریافت شد: {data}")
                        hex_str = ' '.join([f'{b:02X}' for b in data])
                        print(f"   HEX: {hex_str}")
                        data_received = True
                        working_rates.append(baud)
                time.sleep(0.1)

            ser.close()

            if not data_received:
                print(f"⚠️ هیچ داده‌ای دریافت نشد.")

        except Exception as e:
            print(f"❌ خطا: {e}")

    # گزارش نهایی
    print("\n" + "=" * 60)
    print("📊 گزارش نهایی:")
    if working_rates:
        print(f"✅ Baud Rate‌های کاری: {working_rates}")
    else:
        print("❌ هیچ Baud Rate کاری پیدا نشد.")
        print("   احتمالاً دستگاه داده‌ای ارسال نمی‌کند یا کارت‌ها سازگار نیستند.")


if __name__ == "__main__":
    test_extended_baudrates()