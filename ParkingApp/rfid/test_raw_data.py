# test_raw_data.py
import serial
import time


def read_raw(port="COM6", baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ متصل به {port} با سرعت {baudrate}")
        print("🔄 در حال نمایش داده‌های خام... (برای ۱۰ ثانیه)")
        print("📇 لطفاً یک کارت را جلوی دستگاه بگیرید.")

        start = time.time()
        while time.time() - start < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                hex_str = ' '.join([f'{b:02X}' for b in data])
                print(f"📇 HEX: {hex_str}")
                try:
                    ascii_str = data.decode('utf-8', errors='replace')
                    print(f"📇 ASCII: {ascii_str}")
                except:
                    pass
            time.sleep(0.05)

        ser.close()
        print("✅ تست کامل شد.")

    except Exception as e:
        print(f"❌ خطا: {e}")


if __name__ == "__main__":
    read_raw()