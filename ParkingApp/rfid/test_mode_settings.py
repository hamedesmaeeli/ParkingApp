# test_mode_settings.py
def set_mode_with_param(mode_param=0x00):
    """تنظیم حالت دستگاه با پارامترهای مختلف"""
    print(f"🔄 تنظیم حالت با پارامتر {mode_param:02X}...")
    response = send_command(0x31, [mode_param])
    if response and len(response) >= 5:
        status = response[4]
        if status == 0x00:
            print("✅ حالت دستگاه تنظیم شد.")
            return True
        else:
            print(f"⚠️ خطا در تنظیم حالت (Status: {status:02X})")
    return False

# تست پارامترهای مختلف
for param in [0x00, 0x01, 0x02]:
    set_mode_with_param(param)
    time.sleep(1)