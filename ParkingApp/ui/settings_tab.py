"""
تب تنظیمات - نسخه کامل با نرخ ساعت اول و دوم و پشتیبان‌گیری خودکار
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QMessageBox, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backup import BackupManager, AutoBackup


class SettingsTab(QWidget):
    """تب تنظیمات پارکینگ با پشتیبان‌گیری"""

    settings_changed = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.backup_manager = BackupManager(database)
        self.auto_backup = AutoBackup(self.backup_manager)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # ===== عنوان =====
        title = QLabel("⚙️ تنظیمات پارکینگ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # ===== گروه نرخ‌ها =====
        rate_group = QGroupBox("💰 نرخ‌های پارکینگ")
        rate_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #27ae60; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #27ae60; color: white; border-radius: 5px; }
        """)
        rate_layout = QFormLayout()
        rate_layout.setSpacing(15)

        # نرخ ساعت اول
        self.first_hour_input = QLineEdit()
        self.first_hour_input.setPlaceholderText("مثال: 10000")
        self.first_hour_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        rate_layout.addRow("💵 نرخ ساعت اول (تومان):", self.first_hour_input)

        # نرخ ساعت دوم به بعد
        self.next_hours_input = QLineEdit()
        self.next_hours_input.setPlaceholderText("مثال: 5000")
        self.next_hours_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        rate_layout.addRow("💵 نرخ ساعت دوم به بعد (تومان):", self.next_hours_input)

        # دقیقه رایگان
        self.free_minutes_input = QLineEdit()
        self.free_minutes_input.setPlaceholderText("مثال: 15")
        self.free_minutes_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        rate_layout.addRow("⏱️ دقیقه رایگان:", self.free_minutes_input)

        # سقف هزینه روزانه
        self.max_daily_input = QLineEdit()
        self.max_daily_input.setPlaceholderText("مثال: 50000")
        self.max_daily_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        rate_layout.addRow("📊 سقف هزینه روزانه (تومان):", self.max_daily_input)

        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)

        # ===== گروه اطلاعات پارکینگ =====
        info_group = QGroupBox("🏢 اطلاعات پارکینگ")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #3498db; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #3498db; color: white; border-radius: 5px; }
        """)
        info_layout = QFormLayout()
        info_layout.setSpacing(15)

        self.parking_name_input = QLineEdit()
        self.parking_name_input.setPlaceholderText("مثال: پارکینگ اصلی")
        self.parking_name_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        info_layout.addRow("نام پارکینگ:", self.parking_name_input)

        self.max_capacity_input = QLineEdit()
        self.max_capacity_input.setPlaceholderText("مثال: 100")
        self.max_capacity_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        info_layout.addRow("ظرفیت پارکینگ:", self.max_capacity_input)

        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("مثال: شرکت مدیریت پارکینگ")
        self.company_name_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        info_layout.addRow("نام شرکت:", self.company_name_input)

        self.company_phone_input = QLineEdit()
        self.company_phone_input.setPlaceholderText("مثال: 021-12345678")
        self.company_phone_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        info_layout.addRow("تلفن شرکت:", self.company_phone_input)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # ===== گروه پشتیبان‌گیری خودکار =====
        backup_group = QGroupBox("💾 پشتیبان‌گیری خودکار")
        backup_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #9b59b6; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #9b59b6; color: white; border-radius: 5px; }
        """)
        backup_layout = QFormLayout()
        backup_layout.setSpacing(15)

        # فعال بودن بکاپ خودکار
        self.backup_enabled_cb = QCheckBox("فعال بودن بکاپ خودکار")
        self.backup_enabled_cb.setStyleSheet("font-size: 14px;")
        self.backup_enabled_cb.stateChanged.connect(self.toggle_auto_backup)
        backup_layout.addRow("", self.backup_enabled_cb)

        # فاصله بکاپ
        self.backup_interval_input = QLineEdit()
        self.backup_interval_input.setPlaceholderText("مثال: 24")
        self.backup_interval_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        backup_layout.addRow("⏱️ فاصله بکاپ (ساعت):", self.backup_interval_input)

        # وضعیت بکاپ خودکار
        self.auto_backup_status = QLabel("⏹️ غیرفعال")
        self.auto_backup_status.setStyleSheet("font-size: 13px; color: #7f8c8d; padding: 5px;")
        backup_layout.addRow("", self.auto_backup_status)

        # دکمه بکاپ دستی
        self.manual_backup_btn = QPushButton("📦 ایجاد بکاپ دستی")
        self.manual_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.manual_backup_btn.clicked.connect(self.create_manual_backup)
        backup_layout.addRow("", self.manual_backup_btn)

        # دکمه بازیابی
        self.restore_backup_btn = QPushButton("📂 بازیابی از فایل")
        self.restore_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.restore_backup_btn.clicked.connect(self.restore_backup)
        backup_layout.addRow("", self.restore_backup_btn)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # ===== دکمه‌های ذخیره و بازنشانی =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        save_btn = QPushButton("💾 ذخیره تنظیمات")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 15px 40px; border-radius: 8px;
                font-weight: bold; font-size: 15px; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        save_btn.clicked.connect(self.save_settings)

        reset_btn = QPushButton("🔄 بازنشانی")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white;
                padding: 15px 40px; border-radius: 8px;
                font-weight: bold; font-size: 15px; border: none;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        reset_btn.clicked.connect(self.load_settings)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== راهنما =====
        help_label = QLabel(
            "💡 راهنما:\n"
            "• نرخ ساعت اول: هزینه ساعت اول پارک\n"
            "• نرخ ساعت دوم به بعد: هزینه هر ساعت اضافه\n"
            "• دقیقه رایگان: مدت زمان رایگان اولیه\n"
            "• سقف هزینه روزانه: حداکثر هزینه در یک روز\n"
            "• پشتیبان‌گیری: ایجاد نسخه پشتیبان از دیتابیس"
        )
        help_label.setStyleSheet("""
            font-size: 13px; color: #7f8c8d; padding: 15px;
            background-color: #f8f9fa; border-radius: 8px;
            line-height: 1.6;
        """)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addStretch()

    # ======================== تنظیمات ========================

    def load_settings(self):
        """بارگذاری تنظیمات از دیتابیس"""
        try:
            self.first_hour_input.setText(self.db.get_setting('first_hour_rate', '10000'))
            self.next_hours_input.setText(self.db.get_setting('next_hours_rate', '5000'))
            self.free_minutes_input.setText(self.db.get_setting('free_minutes', '15'))
            self.max_daily_input.setText(self.db.get_setting('max_daily_cost', '50000'))
            self.parking_name_input.setText(self.db.get_setting('parking_name', 'پارکینگ اصلی'))
            self.max_capacity_input.setText(self.db.get_setting('max_capacity', '100'))
            self.company_name_input.setText(self.db.get_setting('company_name', 'شرکت مدیریت پارکینگ'))
            self.company_phone_input.setText(self.db.get_setting('company_phone', ''))

            # پشتیبان‌گیری
            backup_enabled = self.db.get_setting('backup_enabled', 'true')
            self.backup_enabled_cb.setChecked(backup_enabled.lower() == 'true')
            self.backup_interval_input.setText(self.db.get_setting('backup_interval_hours', '24'))

        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")

    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            # اعتبارسنجی
            try:
                float(self.first_hour_input.text())
                float(self.next_hours_input.text())
                int(self.free_minutes_input.text())
                float(self.max_daily_input.text())
            except ValueError:
                QMessageBox.warning(self, "⚠️ خطا", "لطفاً مقادیر عددی معتبر وارد کنید!")
                return

            self.db.set_setting('first_hour_rate', self.first_hour_input.text())
            self.db.set_setting('next_hours_rate', self.next_hours_input.text())
            self.db.set_setting('free_minutes', self.free_minutes_input.text())
            self.db.set_setting('max_daily_cost', self.max_daily_input.text())
            self.db.set_setting('parking_name', self.parking_name_input.text())
            self.db.set_setting('max_capacity', self.max_capacity_input.text())
            self.db.set_setting('company_name', self.company_name_input.text())
            self.db.set_setting('company_phone', self.company_phone_input.text())
            self.db.set_setting('backup_enabled', 'true' if self.backup_enabled_cb.isChecked() else 'false')
            self.db.set_setting('backup_interval_hours', self.backup_interval_input.text())

            QMessageBox.information(self, "✅ موفق", "تنظیمات با موفقیت ذخیره شد.")
            self.settings_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    # ======================== پشتیبان‌گیری ========================

    def toggle_auto_backup(self, state):
        """فعال/غیرفعال کردن بکاپ خودکار"""
        if state == Qt.Checked:
            try:
                interval = int(self.backup_interval_input.text() or "24")
                self.auto_backup.set_interval(interval)
                self.auto_backup.start()
                self.auto_backup_status.setText(f"✅ فعال (هر {interval} ساعت)")
                self.auto_backup_status.setStyleSheet("font-size: 13px; color: #27ae60; padding: 5px;")
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", str(e))
                self.backup_enabled_cb.setChecked(False)
        else:
            self.auto_backup.stop()
            self.auto_backup_status.setText("⏹️ غیرفعال")
            self.auto_backup_status.setStyleSheet("font-size: 13px; color: #7f8c8d; padding: 5px;")

    def create_manual_backup(self):
        """ایجاد بکاپ دستی"""
        try:
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(
                self, "✅ بکاپ ایجاد شد",
                f"فایل بکاپ با موفقیت ایجاد شد.\n\n📁 {backup_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def restore_backup(self):
        """بازیابی از فایل"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل بکاپ", "backups", "Database Files (*.db)"
        )
        if not filepath:
            return

        reply = QMessageBox.question(
            self, "تأیید بازیابی",
            f"آیا از بازیابی دیتابیس اطمینان دارید؟\n\n"
            f"📁 {filepath}\n\n"
            f"⚠️ دیتابیس فعلی جایگزین خواهد شد!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.backup_manager.restore_backup(filepath)
                QMessageBox.information(
                    self, "✅ بازیابی موفق",
                    "دیتابیس با موفقیت بازیابی شد.\nلطفاً برنامه را ری‌استارت کنید."
                )
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", str(e))