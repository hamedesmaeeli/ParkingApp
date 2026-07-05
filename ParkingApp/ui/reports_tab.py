"""
تب گزارش‌گیری و آمار
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QDateEdit, QComboBox, QFrame, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
import os

from ui.styles import ParkingStyles


class ReportsTab(QWidget):
    """تب گزارش‌ها و آمار"""

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # عنوان
        title = QLabel("📈 گزارش‌ها و آمار")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # انتخاب بازه زمانی
        date_group = QGroupBox("📅 بازه زمانی گزارش")
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)

        # گزارش‌های آماده
        quick_reports = QComboBox()
        quick_reports.addItems([
            "انتخاب بازه زمانی...",
            "امروز",
            "دیروز",
            "این هفته",
            "این ماه",
            "ماه گذشته",
            "سه ماه اخیر",
            "امسال"
        ])
        quick_reports.setMinimumHeight(45)
        quick_reports.currentIndexChanged.connect(self.on_quick_report)

        date_layout.addWidget(QLabel("گزارش سریع:"))
        date_layout.addWidget(quick_reports)

        date_layout.addWidget(QLabel("از:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        self.date_from.setMinimumHeight(45)
        date_layout.addWidget(self.date_from)

        date_layout.addWidget(QLabel("تا:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setMinimumHeight(45)
        date_layout.addWidget(self.date_to)

        generate_btn = QPushButton("📊 تولید گزارش")
        generate_btn.setObjectName("goldenBtn")
        generate_btn.clicked.connect(self.generate_report)
        generate_btn.setMinimumHeight(45)
        date_layout.addWidget(generate_btn)

        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # کارت‌های آمار خلاصه
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        self.income_card = self.create_summary_card("💰 درآمد کل", "۰ تومان", ParkingStyles.SUCCESS)
        self.count_card = self.create_summary_card("🚗 تعداد خودرو", "۰", ParkingStyles.INFO)
        self.avg_card = self.create_summary_card("⏱️ میانگین توقف", "۰ ساعت", ParkingStyles.WARNING)
        self.max_card = self.create_summary_card("📈 بیشترین درآمد", "۰ تومان", ParkingStyles.GOLD)

        summary_layout.addWidget(self.income_card)
        summary_layout.addWidget(self.count_card)
        summary_layout.addWidget(self.avg_card)
        summary_layout.addWidget(self.max_card)

        layout.addLayout(summary_layout)

        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(7)
        self.report_table.setHorizontalHeaderLabels([
            "تاریخ", "تعداد", "درآمد کل", "میانگین توقف",
            "شخصی", "تاکسی", "سایر"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.setAlternatingRowColors(True)

        layout.addWidget(self.report_table)

        # دکمه‌های خروجی
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)

        export_excel_btn = QPushButton("📥 Excel")
        export_excel_btn.setObjectName("successBtn")
        export_excel_btn.clicked.connect(self.export_excel)
        export_excel_btn.setMinimumHeight(45)

        export_pdf_btn = QPushButton("📄 PDF")
        export_pdf_btn.setObjectName("goldenBtn")
        export_pdf_btn.clicked.connect(self.export_pdf)
        export_pdf_btn.setMinimumHeight(45)

        print_btn = QPushButton("🖨️ چاپ")
        print_btn.clicked.connect(self.print_report)
        print_btn.setMinimumHeight(45)

        export_layout.addWidget(export_excel_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addWidget(print_btn)
        export_layout.addStretch()

        layout.addLayout(export_layout)

    def create_summary_card(self, title, value, color):
        """ایجاد کارت خلاصه"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 white, stop: 1 #f8f9fa);
                border: 2px solid {color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; background: transparent;")

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(
            f"color: {ParkingStyles.PRIMARY_DARK}; font-size: 18px; font-weight: bold; background: transparent;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        # ذخیره reference
        card.value_label = value_label

        return card

    def on_quick_report(self, index):
        """انتخاب گزارش سریع"""
        today = QDate.currentDate()

        if index == 1:  # امروز
            self.date_from.setDate(today)
            self.date_to.setDate(today)
        elif index == 2:  # دیروز
            yesterday = today.addDays(-1)
            self.date_from.setDate(yesterday)
            self.date_to.setDate(yesterday)
        elif index == 3:  # این هفته
            self.date_from.setDate(today.addDays(-today.dayOfWeek() + 1))
            self.date_to.setDate(today)
        elif index == 4:  # این ماه
            self.date_from.setDate(QDate(today.year(), today.month(), 1))
            self.date_to.setDate(today)
        elif index == 5:  # ماه گذشته
            last_month = today.addMonths(-1)
            self.date_from.setDate(QDate(last_month.year(), last_month.month(), 1))
            self.date_to.setDate(QDate(last_month.year(), last_month.month(), last_month.daysInMonth()))
        elif index == 6:  # سه ماه اخیر
            self.date_from.setDate(today.addMonths(-3))
            self.date_to.setDate(today)
        elif index == 7:  # امسال
            self.date_from.setDate(QDate(today.year(), 1, 1))
            self.date_to.setDate(today)

    def generate_report(self):
        """تولید گزارش"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")

            # دریافت آمار کلی
            stats = self.db.get_statistics(date_to)

            # بروزرسانی کارت‌ها
            self.income_card.value_label.setText(f"{stats['daily']['income']:,.0f} تومان")
            self.count_card.value_label.setText(str(stats['daily']['count']))
            self.avg_card.value_label.setText(f"{stats['daily']['avg_duration']:.1f} ساعت")

            # محاسبه بیشترین درآمد
            max_income = max([item['income'] for item in stats['by_plate_type']]) if stats['by_plate_type'] else 0
            self.max_card.value_label.setText(f"{max_income:,.0f} تومان")

            # پر کردن جدول روزانه
            from datetime import datetime, timedelta

            start = datetime.strptime(date_from, "%Y-%m-%d")
            end = datetime.strptime(date_to, "%Y-%m-%d")

            self.report_table.setRowCount(0)
            row = 0

            current = start
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                daily_stats = self.db.get_statistics(date_str)

                self.report_table.insertRow(row)

                self.report_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.report_table.setItem(row, 1, QTableWidgetItem(str(daily_stats['daily']['count'])))
                self.report_table.setItem(row, 2, QTableWidgetItem(f"{daily_stats['daily']['income']:,.0f}"))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{daily_stats['daily']['avg_duration']:.1f}"))

                # تفکیک انواع
                by_type = {item['plate_type']: item['count'] for item in daily_stats['by_plate_type']}
                self.report_table.setItem(row, 4, QTableWidgetItem(str(by_type.get('personal', 0))))
                self.report_table.setItem(row, 5, QTableWidgetItem(str(by_type.get('taxi', 0))))
                self.report_table.setItem(row, 6, QTableWidgetItem(str(
                    by_type.get('governmental', 0) + by_type.get('military', 0) + by_type.get('diplomatic', 0)
                )))

                # رنگ‌آمیزی درآمد
                if daily_stats['daily']['income'] > 1000000:
                    for col in range(7):
                        self.report_table.item(row, col).setBackground(QColor("#d5f5e3"))

                row += 1
                current += timedelta(days=1)

            QMessageBox.information(self, "موفق", "گزارش با موفقیت تولید شد")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش:\n{str(e)}")

    def export_excel(self):
        """خروجی Excel"""
        QMessageBox.information(self, "خروجی", "قابلیت خروجی Excel در منوی تاریخچه موجود است")

    def export_pdf(self):
        """خروجی PDF"""
        QMessageBox.information(self, "PDF", "قابلیت خروجی PDF در نسخه‌های بعدی اضافه خواهد شد")

    def print_report(self):
        """چاپ گزارش"""
        QMessageBox.information(self, "چاپ", "گزارش آماده چاپ است")