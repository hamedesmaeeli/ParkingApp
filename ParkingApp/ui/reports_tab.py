"""
تب گزارش‌گیری - نسخه کامل با تقویم شمسی
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox,
    QMessageBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import os
import sys
import subprocess
import platform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reports import ReportGenerator
from ui.shamsi_date_edit import ShamsiDateEdit  # ← اضافه شد


class ReportsTab(QWidget):
    """تب گزارش‌گیری با تقویم شمسی"""

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.generator = ReportGenerator(database)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # ===== عنوان =====
        title = QLabel("📊 گزارش‌گیری")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # ===== گزارش سریع =====
        quick_group = QGroupBox("⚡ گزارش سریع")
        quick_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #3498db; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #3498db; color: white; border-radius: 5px; }
        """)
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(15)

        # گزارش روزانه
        daily_btn = QPushButton("📅 گزارش روزانه")
        daily_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 15px; border-radius: 8px; font-weight: bold;
                font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        daily_btn.clicked.connect(self.daily_report)
        quick_layout.addWidget(daily_btn)

        # گزارش ماهانه
        monthly_btn = QPushButton("📆 گزارش ماهانه")
        monthly_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; color: white;
                padding: 15px; border-radius: 8px; font-weight: bold;
                font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        monthly_btn.clicked.connect(self.monthly_report)
        quick_layout.addWidget(monthly_btn)

        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        # ===== گزارش سفارشی =====
        custom_group = QGroupBox("🔧 گزارش سفارشی")
        custom_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #27ae60; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #27ae60; color: white; border-radius: 5px; }
        """)
        custom_layout = QGridLayout()
        custom_layout.setSpacing(15)

        # ===== تاریخ شروع (شمسی) =====
        custom_layout.addWidget(QLabel("از تاریخ:"), 0, 0)
        self.date_from = ShamsiDateEdit()  # ← ShamsiDateEdit
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        custom_layout.addWidget(self.date_from, 0, 1)

        # ===== تاریخ پایان (شمسی) =====
        custom_layout.addWidget(QLabel("تا تاریخ:"), 0, 2)
        self.date_to = ShamsiDateEdit()  # ← ShamsiDateEdit
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        custom_layout.addWidget(self.date_to, 0, 3)

        # دکمه‌های خروجی
        excel_btn = QPushButton("📊 خروجی Excel")
        excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 12px; border-radius: 8px; font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        excel_btn.clicked.connect(self.custom_excel)
        custom_layout.addWidget(excel_btn, 1, 0, 1, 4)


        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        # ===== دکمه باز کردن پوشه =====
        folder_layout = QHBoxLayout()
        folder_layout.addStretch()

        open_folder_btn = QPushButton("📂 باز کردن پوشه خروجی‌ها")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white;
                padding: 12px 30px; border-radius: 8px;
                font-weight: bold; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        open_folder_btn.clicked.connect(self.open_exports_folder)
        folder_layout.addWidget(open_folder_btn)
        folder_layout.addStretch()

        layout.addLayout(folder_layout)

        # ===== راهنما =====
        help_label = QLabel(
            "💡 راهنما:\n"
            "• گزارش روزانه: آمار امروز (خروجی Excel)\n"
            "• گزارش ماهانه: آمار ماه جاری (خروجی Excel و PDF)\n"
            "• گزارش سفارشی: انتخاب بازه زمانی دلخواه\n"
            "• فایل‌های خروجی در پوشه exports ذخیره می‌شوند.\n"
            "• پس از تولید، امکان باز کردن فایل وجود دارد."
        )
        help_label.setStyleSheet("""
            font-size: 13px; color: #7f8c8d; padding: 15px;
            background-color: #f8f9fa; border-radius: 8px;
            line-height: 1.6;
        """)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addStretch()

    # ======================== گزارش‌ها ========================

    def daily_report(self):
        """گزارش روزانه"""
        try:
            result = self.generator.daily_report()

            reply = QMessageBox.question(
                self, "✅ گزارش روزانه",
                f"گزارش روزانه با موفقیت ایجاد شد.\n\n"
                f"📁 فایل: {result['excel']}\n"
                f"📊 تعداد خودرو: {result['stats']['daily']['count']}\n"
                f"💰 درآمد: {result['stats']['daily']['income']:,.0f} تومان\n\n"
                f"آیا می‌خواهید فایل را باز کنید؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.open_file(result['excel'])

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def monthly_report(self):
        """گزارش ماهانه (فقط Excel)"""
        try:
            result = self.generator.monthly_report()

            reply = QMessageBox.question(
                self, "✅ گزارش ماهانه",
                f"گزارش ماهانه با موفقیت ایجاد شد.\n\n"
                f"📁 Excel: {result['excel']}\n\n"
                f"آیا می‌خواهید فایل را باز کنید؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.open_file(result['excel'])

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def custom_excel(self):
        """خروجی Excel سفارشی با تقویم شمسی"""
        try:
            # ===== دریافت تاریخ میلادی از ویجت شمسی =====
            date_from = self.date_from.get_shamsi_date()
            date_to = self.date_to.get_shamsi_date()
            # ============================================

            filepath = self.generator.excel.export_history(date_from, date_to)

            reply = QMessageBox.question(
                self, "✅ خروجی Excel",
                f"فایل Excel با موفقیت ایجاد شد.\n\n📁 {filepath}\n\n"
                f"آیا می‌خواهید فایل را باز کنید؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.open_file(filepath)

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))
            import traceback
            traceback.print_exc()

        # ======================== عملیات فایل ========================

    def open_file(self, filepath):
        """باز کردن فایل با برنامه پیش‌فرض سیستم"""
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "⚠️ خطا", f"فایل پیدا نشد:\n{filepath}")
            return

        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', filepath])
            else:
                subprocess.call(['xdg-open', filepath])
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در باز کردن فایل:\n{str(e)}")

    def open_exports_folder(self):
        """باز کردن پوشه exports"""
        export_dir = os.path.abspath("exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)

        try:
            if platform.system() == 'Windows':
                os.startfile(export_dir)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', export_dir])
            else:
                subprocess.call(['xdg-open', export_dir])
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در باز کردن پوشه:\n{str(e)}")