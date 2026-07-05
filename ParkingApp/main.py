#!/usr/bin/env python3
"""
سیستم مدیریت پارکینگ - نسخه نهایی ساده و جادار
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import ParkingDatabase
from ui.main_window import MainWindow


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 10))
    app.setLayoutDirection(Qt.RightToLeft)
    app.setApplicationName("سیستم مدیریت پارکینگ")

    try:
        # راه‌اندازی پایگاه داده
        db = ParkingDatabase()
        db.backup_database()

        # ایجاد و نمایش پنجره اصلی
        window = MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()