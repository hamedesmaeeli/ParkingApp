"""
اسکریپت نصب و راه‌اندازی سیستم مدیریت پارکینگ
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """نمایش بنر نصب"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║          🏢 سیستم مدیریت هوشمند پارکینگ 🏢              ║
    ║                    نسخه ۳.۰                               ║
    ║              نصب و راه‌اندازی خودکار                      ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """بررسی نسخه Python"""
    if sys.version_info < (3, 7):
        print("❌ نیاز به Python 3.7 یا بالاتر")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def create_directories():
    """ایجاد پوشه‌های مورد نیاز"""
    directories = [
        'data',
        'backups',
        'exports',
        'captured_plates',
        'logs',
        'ui'
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 پوشه {directory} ایجاد شد")

    # ایجاد فایل‌های __init__.py
    for init_file in ['ui/__init__.py']:
        if not os.path.exists(init_file):
            Path(init_file).touch()
            print(f"📄 فایل {init_file} ایجاد شد")


def install_requirements():
    """نصب کتابخانه‌های مورد نیاز"""
    print("\n📦 در حال نصب کتابخانه‌های مورد نیاز...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ کتابخانه‌ها با موفقیت نصب شدند")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در نصب کتابخانه‌ها: {e}")
        print("لطفاً دستی نصب کنید: pip install -r requirements.txt")


def create_shortcut():
    """ایجاد میانبر در دسکتاپ (ویندوز)"""
    if os.name == 'nt':
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            path = os.path.join(desktop, "سیستم مدیریت پارکینگ.lnk")

            target = sys.executable
            wDir = os.path.dirname(os.path.abspath(__file__))
            icon = os.path.join(wDir, "icon.ico")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.Arguments = f'"{os.path.join(wDir, "main.py")}"'
            if os.path.exists(icon):
                shortcut.IconLocation = icon
            shortcut.save()

            print("✅ میانبر دسکتاپ ایجاد شد")
        except ImportError:
            print("⚠️ کتابخانه winshell نصب نیست، میانبر ایجاد نشد")
        except Exception as e:
            print(f"⚠️ خطا در ایجاد میانبر: {e}")


def initialize_database():
    """راه‌اندازی اولیه پایگاه داده"""
    print("\n🗄️ در حال راه‌اندازی پایگاه داده...")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from database import ParkingDatabase

        db = ParkingDatabase()
        print("✅ پایگاه داده با موفقیت راه‌اندازی شد")

        # نمایش اطلاعات
        settings = db.get_all_settings()
        print(f"   📊 تنظیمات: {len(settings)} مورد")
        print(f"   💰 نرخ ساعتی: {settings.get('hourly_rate', '5000')} تومان")

    except Exception as e:
        print(f"❌ خطا در راه‌اندازی پایگاه داده: {e}")


def create_run_script():
    """ایجاد اسکریپت اجرای سریع"""
    if os.name == 'nt':
        # Windows batch file
        with open("run.bat", "w", encoding="utf-8") as f:
            f.write(f"""@echo off
chcp 65001 > nul
echo راه‌اندازی سیستم مدیریت پارکینگ...
"{sys.executable}" "{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')}"
pause
""")
        print("✅ فایل run.bat ایجاد شد")
    else:
        # Linux/Mac shell script
        with open("run.sh", "w") as f:
            f.write(f"""#!/bin/bash
echo "راه‌اندازی سیستم مدیریت پارکینگ..."
python3 "{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')}"
""")
        os.chmod("run.sh", 0o755)
        print("✅ فایل run.sh ایجاد شد")


def main():
    """تابع اصلی نصب"""
    print_banner()

    print("\n🔍 بررسی پیش‌نیازها...")
    check_python_version()

    print("\n📁 ایجاد ساختار پوشه‌ها...")
    create_directories()

    print("\n📦 نصب کتابخانه‌ها...")
    install_requirements()

    print("\n🗄️ راه‌اندازی پایگاه داده...")
    initialize_database()

    print("\n🔧 ایجاد فایل‌های کمکی...")
    create_run_script()
    create_shortcut()

    print("\n" + "=" * 60)
    print("✅ نصب با موفقیت به پایان رسید!")
    print("=" * 60)
    print("\n🚀 برای اجرای برنامه:")

    if os.name == 'nt':
        print("   • فایل run.bat را اجرا کنید")
        print("   • یا از میانبر دسکتاپ استفاده کنید")
        print(f"   • یا دستور زیر را اجرا کنید:")
        print(f"     python main.py")
    else:
        print("   • ./run.sh را اجرا کنید")
        print(f"   • یا دستور زیر را اجرا کنید:")
        print(f"     python3 main.py")

    print("\n👤 اطلاعات ورود پیش‌فرض:")
    print("   نام کاربری: admin")
    print("   رمز عبور: admin123")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()