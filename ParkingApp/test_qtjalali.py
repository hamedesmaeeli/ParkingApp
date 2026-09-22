# test_qtjalali.py
"""
تست بررسی ماژول qtjalalicomponent
"""

import sys
import os

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🔍 بررسی ماژول qtjalalicomponent")
print("=" * 60)

try:
    import qtjalalicomponent

    print(f"\n✅ ماژول پیدا شد: {qtjalalicomponent.__file__}")

    print("\n📋 کلاس‌ها و توابع موجود:")
    for item in dir(qtjalalicomponent):
        if not item.startswith('_'):
            print(f"  - {item}")

    # ===== بررسی زیرماژول‌ها =====
    print("\n📋 زیرماژول‌ها:")
    import pkgutil

    package_path = os.path.dirname(qtjalalicomponent.__file__)
    for importer, modname, ispkg in pkgutil.iter_modules([package_path]):
        print(f"  - {modname} {'(پکیج)' if ispkg else '(ماژول)'}")

    # ===== بررسی کلاس JalaliDatePicker =====
    print("\n🔍 بررسی JalaliDatePicker:")
    if hasattr(qtjalalicomponent, 'JalaliDatePicker'):
        print("  ✅ کلاس JalaliDatePicker وجود دارد")
        picker_class = qtjalalicomponent.JalaliDatePicker
        print(f"  📋 متدهای موجود در JalaliDatePicker:")
        for method in dir(picker_class):
            if not method.startswith('_'):
                print(f"    - {method}")
    else:
        print("  ❌ کلاس JalaliDatePicker وجود ندارد")

        # ===== جستجوی کلاس‌های مشابه =====
        print("\n🔍 جستجوی کلاس‌های مشابه:")
        for item in dir(qtjalalicomponent):
            if 'date' in item.lower() or 'picker' in item.lower() or 'jalali' in item.lower():
                print(f"  - {item}")

except ImportError as e:
    print(f"❌ خطا در import: {e}")

    # ===== تلاش برای import مستقیم =====
    print("\n🔍 تلاش برای import مستقیم زیرماژول‌ها:")
    possible_modules = [
        "qtjalalicomponent.JalaliDatePicker",
        "qtjalalicomponent.datepicker",
        "qtjalalicomponent.widget",
        "qtjalalicomponent.picker",
    ]

    for module_name in possible_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} کار می‌کند")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")

print("\n" + "=" * 60)