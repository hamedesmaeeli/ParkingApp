# test_db_paths.py
from database import ParkingDatabase
from auth import UserManager
from ui.users_tab import UsersTab
from ui.main_window import MainWindow
import os

print("=" * 50)
print("🔍 بررسی مسیرهای دیتابیس")
print("=" * 50)

# ۱. دیتابیس
db = ParkingDatabase()
print(f"\n📁 Database: {os.path.abspath(db.db_path)}")

# ۲. UserManager
um = UserManager(db)
print(f"📁 UserManager: {os.path.abspath(um.db.db_path)}")

# ۳. بررسی یکسان بودن
print(f"\n✅ یکسان بودن Database و UserManager: {db.db_path == um.db.db_path}")

# ۴. بررسی کاربران
users = um.get_all_users()
print(f"\n📋 کاربران در دیتابیس اصلی:")
for user in users:
    print(f"  👤 {user['username']} | {user['role']}")