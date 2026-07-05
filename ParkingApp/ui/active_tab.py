"""
تب خودروهای حاضر - نسخه ساده و اسکرول‌دار
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QGroupBox,
    QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_utils import IranianPlate


class ActiveTab(QWidget):
    car_selected = pyqtSignal(dict)

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)

        # عنوان
        title = QLabel("🅿️ خودروهای حاضر در پارکینگ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
        """)
        layout.addWidget(title)

        # کارت‌های آمار
        stats_frame = QFrame()
        stats_frame.setStyleSheet("QFrame { background: transparent; }")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)

        # کارت‌ها
        self.total_card = self.create_stat_card("🚗 کل خودروها", "0", "#3498db")
        self.personal_card = self.create_stat_card("👤 شخصی", "0", "#27ae60")
        self.taxi_card = self.create_stat_card("🚕 تاکسی", "0", "#f39c12")
        self.other_card = self.create_stat_card("🏛️ سایر", "0", "#9b59b6")

        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.personal_card)
        stats_layout.addWidget(self.taxi_card)
        stats_layout.addWidget(self.other_card)

        layout.addWidget(stats_frame)

        # جدول
        table_group = QGroupBox("📋 لیست خودروها")
        table_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
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

        table_layout = QVBoxLayout()

        # نوار اطلاعات
        info_layout = QHBoxLayout()

        self.count_label = QLabel("تعداد: ۰ خودرو")
        self.count_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")

        self.last_update_label = QLabel("آخرین بروزرسانی: --:--:--")
        self.last_update_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")

        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        refresh_btn.clicked.connect(self.refresh_data)

        info_layout.addWidget(self.count_label)
        info_layout.addStretch()
        info_layout.addWidget(self.last_update_label)
        info_layout.addWidget(refresh_btn)

        table_layout.addLayout(info_layout)

        # جدول
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "نوع", "استان",
            "زمان ورود", "مدت حضور", "هزینه تقریبی", "وضعیت"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        self.table.setSortingEnabled(True)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # فضای خالی
        spacer = QWidget()
        spacer.setMinimumHeight(30)
        layout.addWidget(spacer)

        # بارگذاری اولیه
        self.refresh_data()

    def create_stat_card(self, title, value, color):
        """ایجاد کارت آمار"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {color}10;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold; background: transparent;")

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #2c3e50; font-size: 28px; font-weight: bold; background: transparent;")
        value_label.setObjectName("value")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        return card

    def refresh_data(self):
        """بروزرسانی داده‌ها"""
        try:
            cars = self.db.get_active_cars()

            # بروزرسانی کارت‌ها
            total = len(cars)
            personal = sum(1 for c in cars if c.get('plate_type') == 'personal')
            taxi = sum(1 for c in cars if c.get('plate_type') == 'taxi')
            other = total - personal - taxi

            # پیدا کردن labelهای value
            for card in [self.total_card, self.personal_card, self.taxi_card, self.other_card]:
                for child in card.children():
                    if hasattr(child, 'objectName') and child.objectName() == "value":
                        if card == self.total_card:
                            child.setText(str(total))
                        elif card == self.personal_card:
                            child.setText(str(personal))
                        elif card == self.taxi_card:
                            child.setText(str(taxi))
                        elif card == self.other_card:
                            child.setText(str(other))

            self.count_label.setText(f"تعداد: {total} خودرو")
            self.last_update_label.setText(f"آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}")

            # پر کردن جدول
            self.table.setRowCount(0)

            for i, car in enumerate(cars):
                self.table.insertRow(i)

                plate = IranianPlate.from_full_plate(car['plate_number'])
                entry_time = datetime.fromisoformat(car['entry_time'])
                duration = datetime.now() - entry_time
                hours = duration.total_seconds() / 3600
                minutes = int(duration.total_seconds() / 60)

                # ردیف
                self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

                # پلاک
                plate_item = QTableWidgetItem(plate.display_format)
                plate_item.setFont(QFont("Tahoma", 11, QFont.Bold))
                self.table.setItem(i, 1, plate_item)

                # نوع
                self.table.setItem(i, 2, QTableWidgetItem(plate.type_display))

                # استان
                self.table.setItem(i, 3, QTableWidgetItem(plate.province))

                # زمان ورود
                self.table.setItem(i, 4, QTableWidgetItem(entry_time.strftime('%H:%M:%S')))

                # مدت حضور
                if hours >= 1:
                    dur_text = f"{hours:.1f} ساعت"
                else:
                    dur_text = f"{minutes} دقیقه"
                self.table.setItem(i, 5, QTableWidgetItem(dur_text))

                # هزینه تقریبی
                if car['estimated_cost'] > 0:
                    cost_text = f"{car['estimated_cost']:,.0f} تومان"
                else:
                    cost_text = "رایگان"
                cost_item = QTableWidgetItem(cost_text)
                if car['estimated_cost'] > 0:
                    cost_item.setForeground(QColor("#e74c3c"))
                else:
                    cost_item.setForeground(QColor("#27ae60"))
                self.table.setItem(i, 6, cost_item)

                # وضعیت
                if hours > 5:
                    status = "⚠️ طولانی"
                    status_color = QColor("#e74c3c")
                elif hours > 3:
                    status = "⏳ متوسط"
                    status_color = QColor("#f39c12")
                else:
                    status = "✅ عادی"
                    status_color = QColor("#27ae60")

                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                self.table.setItem(i, 7, status_item)

                # رنگ‌آمیزی سطر
                if hours > 5:
                    for col in range(8):
                        self.table.item(i, col).setBackground(QColor("#fadbd8"))
                elif hours > 3:
                    for col in range(8):
                        self.table.item(i, col).setBackground(QColor("#fef9e7"))

        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری:\n{str(e)}")

    def setup_timer(self):
        """تایمر بروزرسانی خودکار"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # هر ۳۰ ثانیه