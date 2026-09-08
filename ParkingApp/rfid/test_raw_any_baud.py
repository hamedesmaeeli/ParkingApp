# test_raw_any_baud.py
import serial
import time


def test_raw_any_baud(port="COM6"):
    """
    تست دریافت داده بدون توجه به Baud Rate
    """
    baudrates = [9600, 115200, 19200, 57600]

    for baud in baudrates:
        print(f"\n🔍 تست با Baud Rate: {baud}")
        try:
            ser = serial.Serial(port, baud, timeout=1)
            print(f"✅ متصل شد!")

            # پاک کردن بافر
            ser.reset_input_buffer()

            print("📇 لطفاً کارت را جلوی دستگاه بگیرید...")
            start_time = time.time()

            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    # خواندن همه داده‌ها
                    data = ser.read(ser.in_waiting)
                    if data:
                        print(f"📇 داده: {data}")
                        # نمایش به صورت HEX
                        print(f"   HEX: {' '.join([f'{b:02X}' for b in data])}")
                        # تلاش برای decode
                        try:
                            print(f"   ASCII: {data.decode('utf-8', errors='replace')}")
                        except:
                            pass
                time.sleep(0.1)

            ser.close()

        except Exception as e:
            print(f"❌ خطا: {e}")


if __name__ == "__main__":
    test_raw_any_baud()