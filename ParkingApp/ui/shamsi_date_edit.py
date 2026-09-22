"""
Shamsi Date Edit - تقویم شمسی کاملاً سفارشی
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QVBoxLayout, QDialog, QLabel, QFrame,
    QComboBox, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import jdatetime
from datetime import datetime

# ===== نام ماه‌های شمسی =====
SHAMSI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]


class ShamsiDateEdit(QWidget):
    """ویجت انتخاب تاریخ شمسی"""

    dateChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_shamsi = None
        self.init_ui()
        self.set_shamsi_date(datetime.now())

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== فیلد نمایش تاریخ =====
        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)
        self.date_input.setPlaceholderText("انتخاب تاریخ...")
        self.date_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
        """)
        layout.addWidget(self.date_input)

        # ===== دکمه باز کردن تقویم =====
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setFixedWidth(40)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.calendar_btn.clicked.connect(self.show_calendar)
        layout.addWidget(self.calendar_btn)

    def show_calendar(self):
        """نمایش دیالوگ تقویم شمسی"""
        dialog = ShamsiCalendarDialog(self, self.current_shamsi)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.get_selected_date()
            if selected_date:
                self.set_shamsi_date(selected_date)
                self.dateChanged.emit()

    def set_shamsi_date(self, date_obj):
        """تنظیم تاریخ شمسی از datetime میلادی"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj)
            except:
                return

        shamsi = jdatetime.date.fromgregorian(date=date_obj)
        self.current_shamsi = shamsi
        self.date_input.setText(shamsi.strftime('%Y/%m/%d'))

    def setDate(self, qdate):
        """تنظیم تاریخ از QDate میلادی"""
        if not isinstance(qdate, QDate):
            return

        gregorian = datetime(qdate.year(), qdate.month(), qdate.day())
        self.set_shamsi_date(gregorian)

    def get_shamsi_date(self):
        """دریافت تاریخ میلادی برای دیتابیس"""
        if self.current_shamsi:
            gregorian = self.current_shamsi.togregorian()
            return gregorian.strftime('%Y-%m-%d')
        return None

    def get_shamsi_string(self):
        """دریافت رشته تاریخ شمسی"""
        return self.date_input.text()


class ShamsiCalendarDialog(QDialog):
    """دیالوگ تقویم شمسی سفارشی"""

    def __init__(self, parent=None, current_shamsi=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب تاریخ")
        self.setModal(True)
        self.resize(450, 400)

        self.current_shamsi = current_shamsi or jdatetime.date.today()
        self.selected_shamsi = self.current_shamsi
        self.init_ui()
        self.build_calendar()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ===== نوار انتخاب ماه و سال (کشویی) =====
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        nav_layout = QHBoxLayout(nav_frame)

        # دکمه ماه قبلی
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: #3498db;
                border-radius: 15px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #ecf0f1; }
        """)
        self.prev_btn.clicked.connect(self.go_previous)

        # انتخاب ماه (کشویی)
        self.month_combo = QComboBox()
        self.month_combo.addItems(SHAMSI_MONTHS)
        self.month_combo.setCurrentIndex(self.current_shamsi.month - 1)
        self.month_combo.setStyleSheet("""
            QComboBox {
                background-color: white; color: #2c3e50;
                border-radius: 5px; padding: 5px; font-weight: bold;
                min-width: 100px;
            }
        """)
        self.month_combo.currentIndexChanged.connect(self.build_calendar)

        # انتخاب سال (کشویی)
        self.year_combo = QComboBox()
        current_year = self.current_shamsi.year
        for y in range(current_year - 10, current_year + 11):
            self.year_combo.addItem(str(y), y)
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: white; color: #2c3e50;
                border-radius: 5px; padding: 5px; font-weight: bold;
                min-width: 80px;
            }
        """)
        self.year_combo.currentIndexChanged.connect(self.build_calendar)

        # دکمه ماه بعدی
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: #3498db;
                border-radius: 15px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #ecf0f1; }
        """)
        self.next_btn.clicked.connect(self.go_next)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.month_combo, 1)
        nav_layout.addWidget(self.year_combo)
        nav_layout.addWidget(self.next_btn)

        layout.addWidget(nav_frame)

        # ===== روزهای هفته =====
        week_layout = QHBoxLayout()
        week_layout.setSpacing(0)
        week_days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        for day in week_days:
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
            week_layout.addWidget(lbl)
        layout.addLayout(week_layout)

        # ===== گرید روزها =====
        self.days_grid = QGridLayout()
        self.days_grid.setSpacing(2)
        layout.addLayout(self.days_grid)

        # ===== دکمه‌ها =====
        btn_layout = QHBoxLayout()

        ok_btn = QPushButton("✅ تأیید")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def build_calendar(self):
        """ساخت گرید روزها بر اساس ماه و سال انتخاب شده"""
        # پاک کردن گرید قبلی
        for i in reversed(range(self.days_grid.count())):
            widget = self.days_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # ===== دریافت ماه و سال انتخاب شده =====
        month = self.month_combo.currentIndex() + 1
        year = self.year_combo.currentData()

        # ===== محاسبه روز اول ماه =====
        first_day = jdatetime.date(year, month, 1)
        # شنبه = 0، یکشنبه = 1، ... جمعه = 6
        # jdatetime: شنبه = 0
        start_weekday = first_day.weekday()  # 0 = شنبه

        # ===== تعداد روزهای ماه =====
        if month <= 6:
            days_in_month = 31
        elif month <= 11:
            days_in_month = 30
        else:  # اسفند
            # بررسی سال کبیسه
            is_leap = jdatetime.date(year, 12, 30).isvalid() if hasattr(jdatetime.date, 'isvalid') else False
            days_in_month = 30 if jdatetime.date(year, 12, 30).isvalid() else 29

        # ===== ساخت دکمه‌های روز =====
        row = 0
        col = start_weekday

        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setFixedSize(50, 40)

            # ===== بررسی روز انتخاب شده =====
            is_selected = (day == self.selected_shamsi.day and
                          month == self.selected_shamsi.month and
                          year == self.selected_shamsi.year)

            if is_selected:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db; color: white;
                        border-radius: 5px; font-weight: bold;
                        border: none;
                    }
                """)
            elif col == 6:  # جمعه
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #fadbd8; color: #e74c3c;
                        border-radius: 5px; font-weight: bold;
                        border: none;
                    }
                    QPushButton:hover { background-color: #f5b7b1; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa; color: #2c3e50;
                        border-radius: 5px; border: none;
                    }
                    QPushButton:hover { background-color: #e9ecef; }
                """)

            # ===== اتصال کلیک =====
            btn.clicked.connect(lambda checked, d=day, m=month, y=year: self.select_day(d, m, y))

            self.days_grid.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_day(self, day, month, year):
        """انتخاب یک روز"""
        self.selected_shamsi = jdatetime.date(year, month, day)
        self.build_calendar()  # بازسازی برای به‌روزرسانی رنگ

    def go_previous(self):
        """رفتن به ماه قبلی"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_combo.currentData()

        if month == 1:
            self.month_combo.setCurrentIndex(11)
            self.year_combo.setCurrentText(str(year - 1))
        else:
            self.month_combo.setCurrentIndex(month - 2)

    def go_next(self):
        """رفتن به ماه بعدی"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_combo.currentData()

        if month == 12:
            self.month_combo.setCurrentIndex(0)
            self.year_combo.setCurrentText(str(year + 1))
        else:
            self.month_combo.setCurrentIndex(month)

    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده (datetime میلادی)"""
        if self.selected_shamsi:
            return self.selected_shamsi.togregorian()
        return None