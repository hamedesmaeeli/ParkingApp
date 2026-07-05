"""
تب تنظیمات - نسخه ساده و اسکرول‌دار
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame, QGroupBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SettingsTab(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # عنوان
        title = QLabel("⚙️ تنظیمات سیستم")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # تنظیمات پایه
        basic_group = QGroupBox("تنظیمات پایه پارکینگ")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title {
                left: 15px;
                padding: 8px 20px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
            }
        """)

        basic_layout = QFormLayout()
        basic_layout.setSpacing(15)
        basic_layout.setLabelAlignment(Qt.AlignRight)

        field_style = "font-size: 14px; padding: 12px; border: 2px solid #ddd; border-radius: 6px; min-height: 25px;"

        self.parking_name = QLineEdit()
        self.parking_name.setStyleSheet(field_style)
        basic_layout.addRow("🏢 نام پارکینگ:", self.parking_name)

        self.hourly_rate = QDoubleSpinBox()
        self.hourly_rate.setRange(0, 1000000)
        self.hourly_rate.setPrefix("تومان ")
        self.hourly_rate.setStyleSheet(field_style)
        self.hourly_rate.setMinimumHeight(40)
        basic_layout.addRow("💰 نرخ هر ساعت:", self.hourly_rate)

        self.free_minutes = QSpinBox()
        self.free_minutes.setRange(0, 120)
        self.free_minutes.setSuffix(" دقیقه")
        self.free_minutes.setStyleSheet(field_style)
        self.free_minutes.setMinimumHeight(40)
        basic_layout.addRow("⏱️ دقایق رایگان:", self.free_minutes)

        self.max_daily = QDoubleSpinBox()
        self.max_daily.setRange(0, 10000000)
        self.max_daily.setPrefix("تومان ")
        self.max_daily.setStyleSheet(field_style)
        self.max_daily.setMinimumHeight(40)
        basic_layout.addRow("🔝 سقف روزانه:", self.max_daily)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # تنظیمات بکاپ
        backup_group = QGroupBox("تنظیمات پشتیبان‌گیری")
        backup_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title {
                left: 15px;
                padding: 8px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
            }
        """)

        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(10)

        self.backup_enabled = QCheckBox("💾 فعال‌سازی بکاپ خودکار")
        self.backup_enabled.setStyleSheet("font-size: 15px; font-weight: bold; padding: 10px;")

        backup_btn = QPushButton("💾 تهیه بکاپ الآن")
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        backup_btn.clicked.connect(self.backup_now)

        backup_layout.addWidget(self.backup_enabled)
        backup_layout.addWidget(backup_btn)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # دکمه‌های ذخیره
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        save_btn = QPushButton("💾 ذخیره تنظیمات")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 18px 35px;
                border-radius: 8px;
                font-size: 16px;
                border: none;
                min-height: 55px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        save_btn.clicked.connect(self.save_settings)

        reset_btn = QPushButton("🔄 بازنشانی پیش‌فرض")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 18px 35px;
                border-radius: 8px;
                font-size: 16px;
                border: none;
                min-height: 55px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        reset_btn.clicked.connect(self.reset_defaults)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)

        spacer = QWidget()
        spacer.setMinimumHeight(50)
        layout.addWidget(spacer)

    def load_settings(self):
        """بارگذاری تنظیمات"""
        settings = self.db.get_all_settings()

        self.parking_name.setText(settings.get('parking_name', 'پارکینگ اصلی'))
        self.hourly_rate.setValue(float(settings.get('hourly_rate', 5000)))
        self.free_minutes.setValue(int(settings.get('free_minutes', 15)))
        self.max_daily.setValue(float(settings.get('max_daily_cost', 50000)))
        self.backup_enabled.setChecked(settings.get('backup_enabled', 'true') == 'true')

    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            self.db.set_setting('parking_name', self.parking_name.text())
            self.db.set_setting('hourly_rate', str(self.hourly_rate.value()))
            self.db.set_setting('free_minutes', str(self.free_minutes.value()))
            self.db.set_setting('max_daily_cost', str(self.max_daily.value()))
            self.db.set_setting('backup_enabled', str(self.backup_enabled.isChecked()).lower())

            self.settings_changed.emit()
            QMessageBox.information(self, "موفق", "✅ تنظیمات ذخیره شد")

        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))

    def reset_defaults(self):
        """بازنشانی"""
        reply = QMessageBox.question(self, "تأیید", "بازنشانی به پیش‌فرض؟",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            defaults = {
                'parking_name': 'پارکینگ اصلی',
                'hourly_rate': '5000',
                'free_minutes': '15',
                'max_daily_cost': '50000',
                'backup_enabled': 'true'
            }
            for k, v in defaults.items():
                self.db.set_setting(k, v)
            self.load_settings()
            self.settings_changed.emit()
            QMessageBox.information(self, "موفق", "✅ تنظیمات بازنشانی شد")

    def backup_now(self):
        """بکاپ الآن"""
        try:
            path = self.db.backup_database()
            QMessageBox.information(self, "موفق", f"✅ بکاپ در:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))