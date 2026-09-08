# ui/cards_tab.py
"""
تب مدیریت کارت‌های پارکینگ با قابلیت ثبت از طریق RFID
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QMessageBox, QHeaderView,
    QGroupBox, QGridLayout, QApplication, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush
from rfid import RFIDIntegration


class CardsTab(QWidget):
    """تب مدیریت کارت‌های پارکینگ"""

    card_changed = pyqtSignal()  # سیگنال تغییر کارت‌ها

    def __init__(self, database, rfid):
        super().__init__()
        self.db = database
        self.rfid = None
        self.is_reading = False
        self.init_ui()
        self.load_cards()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ===== عنوان =====
        title = QLabel("🎫 مدیریت کارت‌های پارکینگ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # ===== بخش جستجو و فیلتر =====
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        filter_layout.addWidget(QLabel("جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره کارت یا پلاک...")
        self.search_input.textChanged.connect(self.filter_cards)
        self.search_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("وضعیت:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "فعال", "در حال استفاده", "غیرفعال"])
        self.status_filter.currentTextChanged.connect(self.filter_cards)
        self.status_filter.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        filter_layout.addWidget(self.status_filter)

        filter_layout.addStretch()

        # ===== دکمه ثبت کارت با RFID =====
        self.rfid_btn = QPushButton("📡 ثبت با کارت‌خوان")
        self.rfid_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad; color: white;
                padding: 8px 20px; border-radius: 6px; font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #9b59b6; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.rfid_btn.clicked.connect(self.start_rfid_registration)
        filter_layout.addWidget(self.rfid_btn)

        # دکمه ثبت کارت جدید
        self.add_btn = QPushButton("➕ ثبت کارت جدید")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 8px 20px; border-radius: 6px; font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.add_btn.clicked.connect(self.add_new_card)
        filter_layout.addWidget(self.add_btn)

        layout.addLayout(filter_layout)

        # ===== نوار وضعیت RFID =====
        rfid_status_layout = QHBoxLayout()
        self.rfid_status_label = QLabel("📡 وضعیت: آماده")
        self.rfid_status_label.setStyleSheet("padding: 5px; color: #7f8c8d;")
        rfid_status_layout.addWidget(self.rfid_status_label)

        self.rfid_progress = QProgressBar()
        self.rfid_progress.setVisible(False)
        self.rfid_progress.setMaximumHeight(15)
        self.rfid_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3498db; border-radius: 3px;
                text-align: center; font-size: 10px;
            }
            QProgressBar::chunk { background-color: #27ae60; border-radius: 2px; }
        """)
        rfid_status_layout.addWidget(self.rfid_progress)
        layout.addLayout(rfid_status_layout)

        # ===== جدول کارت‌ها =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "شماره کارت", "UID", "وضعیت", "پلاک اختصاصی", "زمان اختصاص", "عملیات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # ===== دکمه‌های پایین =====
        bottom_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 بروزرسانی")
        self.refresh_btn.clicked.connect(self.load_cards)
        self.refresh_btn.setStyleSheet("padding: 8px 20px; border: 2px solid #3498db; border-radius: 5px;")
        bottom_layout.addWidget(self.refresh_btn)

        self.delete_all_btn = QPushButton("🗑️ حذف همه کارت‌ها")
        self.delete_all_btn.clicked.connect(self.delete_all_cards)
        self.delete_all_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px; border: 2px solid #e74c3c; 
                border-radius: 5px; color: #e74c3c;
            }
            QPushButton:hover { background-color: #e74c3c; color: white; }
        """)
        bottom_layout.addWidget(self.delete_all_btn)

        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def load_cards(self):
        """بارگذاری لیست کارت‌ها از دیتابیس"""
        try:
            cards = self.db.get_all_cards()
            self.table.setRowCount(len(cards))

            for i, card in enumerate(cards):
                # شماره کارت
                item = QTableWidgetItem(card['card_number'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 0, item)

                # UID
                uid = card.get('uid', '')
                item = QTableWidgetItem(uid if uid else '—')
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 1, item)

                # وضعیت
                status = card['status']
                status_text = {
                    'active': '✅ فعال',
                    'in_use': '🔄 در حال استفاده',
                    'expired': '❌ غیرفعال'
                }.get(status, status)

                status_item = QTableWidgetItem(status_text)
                status_item.setTextAlignment(Qt.AlignCenter)

                # رنگ وضعیت
                if status == 'active':
                    status_item.setForeground(QBrush(QColor('#27ae60')))
                elif status == 'in_use':
                    status_item.setForeground(QBrush(QColor('#f39c12')))
                else:
                    status_item.setForeground(QBrush(QColor('#e74c3c')))

                self.table.setItem(i, 2, status_item)

                # پلاک اختصاصی
                assigned = card.get('assigned_to', '')
                item = QTableWidgetItem(assigned if assigned else '—')
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 3, item)

                # زمان اختصاص
                assigned_at = card.get('assigned_at', '')
                item = QTableWidgetItem(assigned_at if assigned_at else '—')
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 4, item)

                # عملیات (دکمه‌های ویرایش و حذف)
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(5)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.setToolTip("ویرایش کارت")
                edit_btn.clicked.connect(lambda checked, c=card: self.edit_card(c))
                edit_btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #3498db; color: white; 
                        border: none; border-radius: 5px;
                    }
                    QPushButton:hover { background-color: #2980b9; }
                """)
                btn_layout.addWidget(edit_btn)

                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setToolTip("حذف کارت")
                delete_btn.clicked.connect(lambda checked, c=card: self.delete_card(c))
                delete_btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #e74c3c; color: white; 
                        border: none; border-radius: 5px;
                    }
                    QPushButton:hover { background-color: #c0392b; }
                """)
                btn_layout.addWidget(delete_btn)

                self.table.setCellWidget(i, 5, btn_widget)

            self.apply_filter()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در بارگذاری کارت‌ها:\n{str(e)}")

    def apply_filter(self):
        """اعمال فیلتر روی جدول"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()

        for row in range(self.table.rowCount()):
            show = True

            # فیلتر جستجو
            if search_text:
                card_number = self.table.item(row, 0).text().lower()
                assigned = self.table.item(row, 3).text().lower()
                if search_text not in card_number and search_text not in assigned:
                    show = False

            # فیلتر وضعیت
            if show and status_filter != "همه":
                status_item = self.table.item(row, 2)
                if status_item:
                    status_text = status_item.text()
                    if status_filter == "فعال" and "✅" not in status_text:
                        show = False
                    elif status_filter == "در حال استفاده" and "🔄" not in status_text:
                        show = False
                    elif status_filter == "غیرفعال" and "❌" not in status_text:
                        show = False

            self.table.setRowHidden(row, not show)

    def filter_cards(self):
        """فیلتر کردن کارت‌ها"""
        self.apply_filter()

    def start_rfid_registration(self):
        """شروع فرآیند ثبت کارت با RFID"""
        if self.is_reading:
            return

        # بررسی اتصال RFID
        try:
            self.rfid = RFIDIntegration()
            self.rfid.card_scanned.connect(self.on_rfid_card_scanned)
            self.rfid.reader.error_occurred.connect(self.on_rfid_error)
            self.rfid.reader.status_changed.connect(self.on_rfid_status)

            self.is_reading = True
            self.rfid_btn.setEnabled(False)
            self.rfid_btn.setText("⏳ در حال خواندن...")
            self.rfid_progress.setVisible(True)
            self.rfid_progress.setRange(0, 0)  # حالت نامحدود
            self.rfid_status_label.setText("📡 لطفاً کارت را روی دستگاه قرار دهید...")
            self.rfid_status_label.setStyleSheet("padding: 5px; color: #f39c12; font-weight: bold;")

            self.rfid.start()

            # تایم‌اوت ۲۰ ثانیه
            QTimer.singleShot(20000, self.stop_rfid_registration)

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در اتصال به RFID:\n{str(e)}")
            self.stop_rfid_registration()

    def on_rfid_card_scanned(self, uid):
        """وقتی کارت RFID اسکن شد"""
        self.stop_rfid_registration()

        # بررسی اینکه آیا این UID قبلاً ثبت شده است
        existing = self.db.get_card_by_uid(uid)
        if existing:
            QMessageBox.information(
                self, "ℹ️ تکراری",
                f"این کارت (UID: {uid}) قبلاً ثبت شده است.\n"
                f"شماره کارت: {existing['card_number']}"
            )
            return

        # باز کردن دیالوگ ثبت کارت با UID پر شده
        dialog = CardDialog(self.db, self, uid=uid)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cards()
            self.card_changed.emit()

    def on_rfid_error(self, error):
        self.rfid_status_label.setText(f"❌ {error}")
        self.rfid_status_label.setStyleSheet("padding: 5px; color: #e74c3c; font-weight: bold;")

    def on_rfid_status(self, status):
        self.rfid_status_label.setText(f"📡 {status}")

    def stop_rfid_registration(self):
        """توقف فرآیند ثبت RFID"""
        self.is_reading = False
        if self.rfid:
            self.rfid.stop()
            self.rfid = None

        self.rfid_btn.setEnabled(True)
        self.rfid_btn.setText("📡 ثبت با کارت‌خوان")
        self.rfid_progress.setVisible(False)
        self.rfid_progress.setRange(0, 100)

        if "کارت" not in self.rfid_status_label.text():
            self.rfid_status_label.setText("📡 وضعیت: آماده")
            self.rfid_status_label.setStyleSheet("padding: 5px; color: #7f8c8d;")

    def add_new_card(self):
        """افزودن کارت جدید"""
        dialog = CardDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cards()
            self.card_changed.emit()

    def edit_card(self, card):
        """ویرایش کارت"""
        dialog = CardDialog(self.db, self, card_data=card)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cards()
            self.card_changed.emit()

    def delete_card(self, card):
        """حذف کارت"""
        reply = QMessageBox.question(
            self, "تأیید حذف",
            f"آیا از حذف کارت {card['card_number']} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_card(card['card_number'])
                QMessageBox.information(self, "✅ موفق", f"کارت {card['card_number']} حذف شد.")
                self.load_cards()
                self.card_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", str(e))

    def delete_all_cards(self):
        """حذف همه کارت‌ها"""
        reply = QMessageBox.question(
            self, "تأیید حذف همه",
            "آیا از حذف همه کارت‌ها اطمینان دارید؟\nاین عمل غیرقابل بازگشت است!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_all_cards()
                QMessageBox.information(self, "✅ موفق", "همه کارت‌ها حذف شدند.")
                self.load_cards()
                self.card_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", str(e))


class CardDialog(QDialog):
    """دیالوگ ثبت/ویرایش کارت با پشتیبانی UID"""

    def __init__(self, database, parent=None, card_data=None, uid=None):
        super().__init__(parent)
        self.db = database
        self.card_data = card_data
        self.uid = uid
        self.setWindowTitle("ثبت کارت جدید" if not card_data else "ویرایش کارت")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

        if card_data:
            self.load_data()
        elif uid:
            self.uid_input.setText(uid)
            self.uid_input.setReadOnly(True)
            self.uid_input.setStyleSheet(
                "padding: 8px; border: 2px solid #27ae60; border-radius: 5px; background-color: #eafaf1;")

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # شماره کارت
        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("مثال: 00001")
        self.card_number_input.setMaxLength(5)
        self.card_number_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("شماره کارت:", self.card_number_input)

        # UID کارت RFID
        self.uid_input = QLineEdit()
        self.uid_input.setPlaceholderText("مثال: 3231CD40")
        self.uid_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("UID کارت:", self.uid_input)

        # وضعیت
        self.status_combo = QComboBox()
        self.status_combo.addItems(["فعال", "در حال استفاده", "غیرفعال"])
        self.status_combo.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("وضعیت:", self.status_combo)

        # پلاک اختصاصی
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("مثال: 12الف345-67")
        self.plate_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("پلاک اختصاصی:", self.plate_input)

        layout.addLayout(form_layout)

        # دکمه‌ها
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("""
            QPushButton { padding: 8px 20px; border-radius: 5px; }
            QPushButton[text="OK"] { background-color: #27ae60; color: white; }
            QPushButton[text="Cancel"] { background-color: #e74c3c; color: white; }
        """)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_data(self):
        """بارگذاری داده‌های کارت برای ویرایش"""
        self.card_number_input.setText(self.card_data['card_number'])
        self.card_number_input.setReadOnly(True)

        if self.card_data.get('uid'):
            self.uid_input.setText(self.card_data['uid'])

        status_map = {
            'active': 'فعال',
            'in_use': 'در حال استفاده',
            'expired': 'غیرفعال'
        }
        self.status_combo.setCurrentText(status_map.get(self.card_data['status'], 'فعال'))

        if self.card_data.get('assigned_to'):
            self.plate_input.setText(self.card_data['assigned_to'])

    def accept(self):
        """ذخیره کارت"""
        card_number = self.card_number_input.text().strip()
        uid = self.uid_input.text().strip()
        status_text = self.status_combo.currentText()
        assigned_to = self.plate_input.text().strip()

        if not card_number:
            QMessageBox.warning(self, "⚠️ خطا", "شماره کارت الزامی است!")
            return

        status_map = {
            'فعال': 'active',
            'در حال استفاده': 'in_use',
            'غیرفعال': 'expired'
        }
        status = status_map.get(status_text, 'active')

        try:
            if self.card_data:
                self.db.update_card(
                    card_number,
                    uid=uid if uid else None,
                    status=status,
                    assigned_to=assigned_to if assigned_to else None
                )
            else:
                self.db.add_card(
                    card_number,
                    uid=uid if uid else None,
                    status=status,
                    assigned_to=assigned_to if assigned_to else None
                )

            QMessageBox.information(self, "✅ موفق", "کارت با موفقیت ذخیره شد.")
            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))