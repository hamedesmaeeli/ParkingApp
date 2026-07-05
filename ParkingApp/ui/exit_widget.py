"""
فرم خروج خودرو - نسخه اسکرول‌دار
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QGroupBox, QComboBox,
    QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_utils import IranianPlate


class ExitWidget(QWidget):
    car_exited = pyqtSignal(dict)

    def __init__(self, database, operator_name="admin"):
        super().__init__()
        self.db = database
        self.operator_name = operator_name
        self.current_plate = None
        self.init_ui()
        self.load_active_cars()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # عنوان
        title = QLabel("🚙 خروج خودرو و محاسبه هزینه")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # ============ جستجو ============
        search_group = QGroupBox("🔍 جستجوی خودرو")
        search_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title {
                left: 15px;
                padding: 8px 20px;
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
            }
        """)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 پلاک را جستجو کنید یا از لیست زیر انتخاب کنید...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
            }
        """)
        self.search_input.returnPressed.connect(self.search_plate)

        search_btn = QPushButton("🔍 جستجو")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 15px;
                min-height: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        search_btn.clicked.connect(self.search_plate)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # ============ اطلاعات خروج ============
        info_group = QGroupBox("📋 اطلاعات خروج")
        info_group.setStyleSheet("""
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

        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        # نمایش پلاک
        self.plate_display = QFrame()
        self.plate_display.setStyleSheet("""
            QFrame {
                background-color: #1a3a6b;
                border: 4px solid #f39c12;
                border-radius: 12px;
                padding: 15px;
                min-height: 60px;
            }
        """)
        plate_display_layout = QHBoxLayout(self.plate_display)
        plate_display_layout.setSpacing(8)

        plate_style = "color: white; font-size: 28px; font-weight: bold; background: transparent;"

        self.exit_part1 = QLabel("--")
        self.exit_part1.setStyleSheet(plate_style)
        self.exit_part1.setAlignment(Qt.AlignCenter)

        self.exit_letter = QLabel("-")
        self.exit_letter.setStyleSheet(plate_style)
        self.exit_letter.setAlignment(Qt.AlignCenter)

        self.exit_part2 = QLabel("---")
        self.exit_part2.setStyleSheet(plate_style)
        self.exit_part2.setAlignment(Qt.AlignCenter)

        iran_label = QLabel("ایران")
        iran_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background-color: #e74c3c; border-radius: 4px; padding: 8px;")
        iran_label.setAlignment(Qt.AlignCenter)

        self.exit_part3 = QLabel("--")
        self.exit_part3.setStyleSheet(plate_style)
        self.exit_part3.setAlignment(Qt.AlignCenter)

        plate_display_layout.addWidget(self.exit_part1)
        plate_display_layout.addWidget(self.exit_letter)
        plate_display_layout.addWidget(self.exit_part2)
        plate_display_layout.addStretch()
        plate_display_layout.addWidget(iran_label)
        plate_display_layout.addStretch()
        plate_display_layout.addWidget(self.exit_part3)

        info_layout.addWidget(self.plate_display)

        # جزئیات
        details_frame = QFrame()
        details_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 8px; padding: 15px; }")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(10)

        self.entry_time_label = QLabel("⏰ زمان ورود: ---")
        self.entry_time_label.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")

        self.duration_label = QLabel("⏱️ مدت توقف: ---")
        self.duration_label.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")

        self.cost_label = QLabel("💰 هزینه: ---")
        self.cost_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #e74c3c;
            padding: 15px;
            background-color: #fadbd8;
            border-radius: 8px;
        """)
        self.cost_label.setAlignment(Qt.AlignCenter)

        details_layout.addWidget(self.entry_time_label)
        details_layout.addWidget(self.duration_label)
        details_layout.addWidget(self.cost_label)

        info_layout.addWidget(details_frame)

        # روش پرداخت
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("💳 روش پرداخت:"))

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["نقدی 💵", "کارتخوان 💳", "اعتباری 🔄"])
        self.payment_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                min-width: 200px;
            }
        """)

        payment_layout.addWidget(self.payment_combo)
        payment_layout.addStretch()

        info_layout.addLayout(payment_layout)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # دکمه خروج
        self.exit_btn = QPushButton("✅ تأیید خروج و دریافت وجه")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 18px;
                padding: 20px;
                border-radius: 10px;
                min-height: 65px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.exit_btn.clicked.connect(self.confirm_exit)
        self.exit_btn.setEnabled(False)

        layout.addWidget(self.exit_btn)

        # ============ لیست خودروهای حاضر ============
        list_group = QGroupBox("📋 خودروهای حاضر در پارکینگ")
        list_group.setStyleSheet("""
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

        list_layout = QVBoxLayout()

        self.active_table = QTableWidget()
        self.active_table.setColumnCount(4)
        self.active_table.setHorizontalHeaderLabels(["پلاک", "نوع", "ورود", "مدت"])
        self.active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_table.setMaximumHeight(250)
        self.active_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        self.active_table.itemClicked.connect(self.on_table_click)

        list_layout.addWidget(self.active_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # فضای خالی
        spacer = QWidget()
        spacer.setMinimumHeight(50)
        layout.addWidget(spacer)

    def load_active_cars(self):
        """بارگذاری خودروهای حاضر"""
        try:
            cars = self.db.get_active_cars()
            self.active_table.setRowCount(0)

            for i, car in enumerate(cars):
                self.active_table.insertRow(i)
                plate = IranianPlate.from_full_plate(car['plate_number'])

                self.active_table.setItem(i, 0, QTableWidgetItem(plate.display_format))
                self.active_table.setItem(i, 1, QTableWidgetItem(plate.type_display))
                self.active_table.setItem(i, 2, QTableWidgetItem(
                    datetime.fromisoformat(car['entry_time']).strftime('%H:%M')
                ))
                self.active_table.setItem(i, 3, QTableWidgetItem(f"{car['duration_hours']:.1f} ساعت"))
        except Exception as e:
            print(f"Error: {e}")

    def search_plate(self):
        """جستجوی پلاک"""
        query = self.search_input.text().strip()
        if not query:
            return

        try:
            results = self.db.search_plate(query)
            if results['active']:
                car = results['active'][0]
                self.show_car_info(car)
            else:
                QMessageBox.information(self, "نتیجه", f"پلاک {query} در پارکینگ یافت نشد")
        except Exception as e:
            QMessageBox.warning(self, "خطا", str(e))

    def on_table_click(self, item):
        """کلیک روی جدول"""
        row = item.row()
        plate_text = self.active_table.item(row, 0).text()
        # استخراج پلاک از متن نمایشی
        parts = plate_text.split('|')
        if parts:
            self.search_input.setText(parts[0].strip())
            self.search_plate()

    def show_car_info(self, car):
        """نمایش اطلاعات خودرو"""
        plate = IranianPlate.from_full_plate(car['plate_number'])

        # نمایش پلاک
        self.exit_part1.setText(plate.part1)
        self.exit_letter.setText(plate.letter)
        self.exit_part2.setText(plate.part2)
        self.exit_part3.setText(plate.part3 if plate.part3 else "--")

        # زمان ورود
        entry_time = datetime.fromisoformat(car['entry_time'])
        self.entry_time_label.setText(f"⏰ زمان ورود: {entry_time.strftime('%H:%M:%S')}")

        # مدت توقف
        duration = datetime.now() - entry_time
        hours = duration.total_seconds() / 3600
        minutes = int(duration.total_seconds() / 60)

        if hours >= 1:
            self.duration_label.setText(f"⏱️ مدت توقف: {hours:.1f} ساعت ({minutes} دقیقه)")
        else:
            self.duration_label.setText(f"⏱️ مدت توقف: {minutes} دقیقه")

        # محاسبه هزینه
        free_minutes = int(self.db.get_setting('free_minutes', '15'))
        if minutes <= free_minutes:
            cost = 0
            cost_text = "🎉 رایگان (کمتر از ۱۵ دقیقه)"
        else:
            hourly_rate = float(self.db.get_setting('hourly_rate', '5000'))
            hours_charged = max(1, int(hours + 0.99))
            cost = hours_charged * hourly_rate
            cost_text = f"💰 هزینه قابل پرداخت: {cost:,.0f} تومان"

        self.cost_label.setText(cost_text)
        self.current_plate = plate
        self.exit_btn.setEnabled(True)

    def confirm_exit(self):
        """تأیید خروج"""
        if not self.current_plate:
            return

        reply = QMessageBox.question(
            self, "تأیید خروج",
            f"آیا از خروج خودرو {self.current_plate.full_plate} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                result = self.db.car_exit(self.current_plate.full_plate, {
                    'operator_name': self.operator_name,
                    'payment_method': 'cash'
                })

                QMessageBox.information(
                    self, "✅ خروج موفق",
                    f"خروج ثبت شد\n\n"
                    f"🚗 پلاک: {self.current_plate.display_format}\n"
                    f"⏱️ مدت: {result['duration_hours']:.1f} ساعت\n"
                    f"💰 هزینه: {result['final_cost']:,.0f} تومان"
                )

                self.car_exited.emit(result)
                self.clear_form()
                self.load_active_cars()

            except Exception as e:
                QMessageBox.critical(self, "خطا", str(e))

    def clear_form(self):
        """پاک کردن فرم"""
        self.search_input.clear()
        self.exit_part1.setText("--")
        self.exit_letter.setText("-")
        self.exit_part2.setText("---")
        self.exit_part3.setText("--")
        self.entry_time_label.setText("⏰ زمان ورود: ---")
        self.duration_label.setText("⏱️ مدت توقف: ---")
        self.cost_label.setText("💰 هزینه: ---")
        self.current_plate = None
        self.exit_btn.setEnabled(False)