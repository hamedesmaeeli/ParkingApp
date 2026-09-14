#!/usr/bin/env python3
"""
سیستم مدیریت پارکینگ - نسخه نهایی
"""

import sys
import os
from datetime import datetime

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import ParkingDatabase
from ui.main_window import MainWindow
from auth import UserManager
from auth.login_widget import LoginWidget

# ===== نگهداری reference به پنجره‌ها =====
main_window = None
login_widget = None


def main():
    global main_window, login_widget

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 10))
    app.setLayoutDirection(Qt.RightToLeft)
    app.setApplicationName("سیستم مدیریت پارکینگ")

    try:
        # راه‌اندازی پایگاه داده
        db = ParkingDatabase()
        db.backup_database()

        # راه‌اندازی مدیریت کاربران
        user_manager = UserManager(db)
        user_manager.create_default_users()

        # ===== نمایش صفحه ورود =====
        login_widget = LoginWidget(user_manager)

        # main.py

        def on_login(user):
            """وقتی کاربر وارد شد"""
            global main_window
            print("\n" + "=" * 50)
            print("✅ on_login called")
            print(f"   user: {user['username']} | role: {user['role']}")

            # ===== بررسی current_user =====
            current = user_manager.get_current_user()
            print(f"   current_user: {current}")
            if current:
                print(f"   current_user.username: {current['username']}")
                print(f"   current_user.role: {current['role']}")
            # =================================

            login_widget.close()
            print("   login_widget closed")

            main_window = MainWindow(db, user_manager)
            print("   MainWindow created")

            main_window.show()
            print("   MainWindow shown")
            print("=" * 50 + "\n")

        login_widget.login_success.connect(on_login)
        login_widget.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()