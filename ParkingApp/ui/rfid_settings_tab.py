"""
تب تنظیمات RFID - نسخه کامل با دکمه اعمال بدون ری‌استارت
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
import serial
import serial.tools.list_ports
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RFIDSettingsTab(QWidget):
    """تب تنظیمات RFID"""

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.init_ui()
        self.load_settings()
        self.refresh_ports()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # ===== عنوان =====
        title = QLabel("📡 تنظیمات RFID")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # ===== گروه تنظیمات اتصال =====
        connection_group = QGroupBox("🔌 تنظیمات اتصال")
        connection_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #e74c3c; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #e74c3c; color: white; border-radius: 5px; }
        """)
        connection_layout = QFormLayout()
        connection_layout.setSpacing(15)

        # ===== پورت COM =====
        port_layout = QHBoxLayout()

        self.rfid_port_combo = QComboBox()
        self.rfid_port_combo.setStyleSheet("""
            QComboBox {
                padding: 10px; border: 2px solid #ddd; border-radius: 5px;
                font-size: 14px; min-height: 40px;
            }
        """)
        self.rfid_port_combo.setEditable(True)
        port_layout.addWidget(self.rfid_port_combo)

        self.refresh_ports_btn = QPushButton("🔄")
        self.refresh_ports_btn.setFixedWidth(45)
        self.refresh_ports_btn.setToolTip("بروزرسانی لیست پورت‌ها")
        self.refresh_ports_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 10px; border-radius: 5px; border: none;
                font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.refresh_ports_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_ports_btn)

        connection_layout.addRow("پورت COM:", port_layout)

        # ===== Baud Rate =====
        self.rfid_baudrate_combo = QComboBox()
        self.rfid_baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.rfid_baudrate_combo.setStyleSheet("""
            QComboBox {
                padding: 10px; border: 2px solid #ddd; border-radius: 5px;
                font-size: 14px; min-height: 40px;
            }
        """)
        connection_layout.addRow("نرخ باود (Baud Rate):", self.rfid_baudrate_combo)

        # ===== آدرس دستگاه =====
        self.rfid_address_input = QLineEdit()
        self.rfid_address_input.setPlaceholderText("مثال: 0")
        self.rfid_address_input.setStyleSheet("padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        connection_layout.addRow("آدرس دستگاه:", self.rfid_address_input)

        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

        # ===== دکمه‌ها =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.test_btn = QPushButton("🔍 تست اتصال")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 15px 30px; border-radius: 8px;
                font-weight: bold; font-size: 15px; border: none;
                min-height: 50px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_btn)

        self.save_btn = QPushButton("💾 ذخیره تنظیمات")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 15px 30px; border-radius: 8px;
                font-weight: bold; font-size: 15px; border: none;
                min-height: 50px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)

        self.apply_btn = QPushButton("🔄 اعمال تنظیمات")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; color: white;
                padding: 15px 30px; border-radius: 8px;
                font-weight: bold; font-size: 15px; border: none;
                min-height: 50px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(self.apply_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ===== نتیجه تست =====
        self.test_result = QLabel("")
        self.test_result.setAlignment(Qt.AlignCenter)
        self.test_result.setStyleSheet("font-size: 13px; padding: 10px; border-radius: 5px;")
        self.test_result.setWordWrap(True)
        layout.addWidget(self.test_result)

        # ===== راهنما =====
        help_label = QLabel(
            "💡 راهنما:\n"
            "• پورت COM را از لیست انتخاب کنید یا دستی وارد کنید.\n"
            "• Baud Rate پیش‌فرض: 115200\n"
            "• اگر دستگاه شما کارت را نمی‌خواند، Baud Rate را به 9600 تغییر دهید.\n"
            "• دکمه 'اعمال تنظیمات' بدون ری‌استارت، RFID را دوباره راه‌اندازی می‌کند.\n"
            "• دکمه 'ذخیره تنظیمات' فقط ذخیره می‌کند (نیاز به ری‌استارت)."
        )
        help_label.setStyleSheet("""
            font-size: 13px; color: #7f8c8d; padding: 15px;
            background-color: #f8f9fa; border-radius: 8px;
            line-height: 1.6;
        """)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addStretch()

    def refresh_ports(self):
        """بروزرسانی لیست پورت‌های COM"""
        try:
            ports = serial.tools.list_ports.comports()

            current_text = self.rfid_port_combo.currentText()
            self.rfid_port_combo.clear()

            for port in ports:
                self.rfid_port_combo.addItem(port.device)

            if current_text:
                index = self.rfid_port_combo.findText(current_text)
                if index >= 0:
                    self.rfid_port_combo.setCurrentIndex(index)
                else:
                    self.rfid_port_combo.setEditText(current_text)

            print(f"✅ {len(ports)} پورت پیدا شد.")

        except Exception as e:
            print(f"❌ خطا در بروزرسانی پورت‌ها: {e}")

    def load_settings(self):
        """بارگذاری تنظیمات"""
        try:
            rfid_port = self.db.get_setting('rfid_port', 'COM6')
            index = self.rfid_port_combo.findText(rfid_port)
            if index >= 0:
                self.rfid_port_combo.setCurrentIndex(index)
            else:
                self.rfid_port_combo.setEditText(rfid_port)

            baudrate = self.db.get_setting('rfid_baudrate', '115200')
            index = self.rfid_baudrate_combo.findText(baudrate)
            if index >= 0:
                self.rfid_baudrate_combo.setCurrentIndex(index)

            self.rfid_address_input.setText(self.db.get_setting('rfid_address', '0'))

        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")

    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            self.db.set_setting('rfid_port', self.rfid_port_combo.currentText())
            self.db.set_setting('rfid_baudrate', self.rfid_baudrate_combo.currentText())
            self.db.set_setting('rfid_address', self.rfid_address_input.text())

            QMessageBox.information(
                self, "✅ موفق",
                "تنظیمات RFID ذخیره شد.\n"
                "برای اعمال تغییرات، برنامه را ری‌استارت کنید."
            )
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def apply_settings(self):
        """ذخیره و اعمال تنظیمات بدون ری‌استارت"""
        try:
            # ===== ۱. ذخیره تنظیمات =====
            self.db.set_setting('rfid_port', self.rfid_port_combo.currentText())
            self.db.set_setting('rfid_baudrate', self.rfid_baudrate_combo.currentText())
            self.db.set_setting('rfid_address', self.rfid_address_input.text())

            # ===== ۲. دریافت MainWindow =====
            main_window = self.window()

            if hasattr(main_window, 'rfid'):
                # ===== ۳. توقف RFID فعلی =====
                print("🔄 توقف RFID فعلی...")
                main_window.rfid.stop()

                # ===== ۴. ایجاد RFID جدید =====
                print("🔄 ایجاد RFID جدید با تنظیمات جدید...")
                from rfid import RFIDIntegration

                # ===== قطع اتصال سیگنال‌های قدیمی =====
                try:
                    main_window.rfid.card_scanned.disconnect()
                except:
                    pass

                # ===== ایجاد RFID جدید =====
                main_window.rfid = RFIDIntegration(db=main_window.db)
                main_window.rfid.start()

                # ===== به‌روزرسانی RFID در تب‌ها =====
                if hasattr(main_window, 'unified_widget'):
                    main_window.unified_widget.rfid = main_window.rfid
                    main_window.rfid.card_scanned.connect(main_window.unified_widget.on_card_scanned)

                if hasattr(main_window, 'cards_tab'):
                    main_window.cards_tab.rfid = main_window.rfid

                QMessageBox.information(
                    self, "✅ موفق",
                    "تنظیمات RFID ذخیره و اعمال شد.\n"
                    "بدون نیاز به ری‌استارت برنامه."
                )
            else:
                QMessageBox.warning(
                    self, "⚠️ توجه",
                    "تنظیمات ذخیره شد اما برای اعمال، برنامه را ری‌استارت کنید."
                )

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در اعمال تنظیمات:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def test_connection(self):
        """تست اتصال RFID"""
        try:
            port = self.rfid_port_combo.currentText()
            baudrate = int(self.rfid_baudrate_combo.currentText())

            if not port:
                self.test_result.setText("⚠️ پورت COM را انتخاب کنید!")
                self.test_result.setStyleSheet("font-size: 13px; color: #e74c3c; padding: 10px; background-color: #fadbd8; border-radius: 5px;")
                return

            ser = serial.Serial(port, baudrate, timeout=2)
            packet = bytes([0x02, 0x00, 0x01, 0x21, 0x20])
            ser.write(packet)
            time.sleep(0.3)
            response = ser.read(256)
            ser.close()

            if response:
                self.test_result.setText(f"✅ اتصال برقرار شد!\nپاسخ دستگاه: {response.hex().upper()}")
                self.test_result.setStyleSheet("font-size: 13px; color: #27ae60; padding: 10px; background-color: #d4edda; border-radius: 5px;")
            else:
                self.test_result.setText("⚠️ اتصال برقرار شد اما پاسخی دریافت نشد.\nلطفاً Baud Rate را تغییر دهید.")
                self.test_result.setStyleSheet("font-size: 13px; color: #f39c12; padding: 10px; background-color: #fdebd0; border-radius: 5px;")

        except Exception as e:
            self.test_result.setText(f"❌ اتصال برقرار نشد!\nخطا: {str(e)}")
            self.test_result.setStyleSheet("font-size: 13px; color: #e74c3c; padding: 10px; background-color: #fadbd8; border-radius: 5px;")