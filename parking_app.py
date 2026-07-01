import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QGroupBox, QFormLayout, QHeaderView,
    QSpinBox, QDoubleSpinBox, QStatusBar, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

class ParkingSystem:
    """سیستم اصلی مدیریت پارکینگ"""
    def __init__(self, hourly_rate=5000, data_file="parking_data.json"):
        self.hourly_rate = hourly_rate
        self.data_file = data_file
        self.active_cars = {}
        self.parking_history = []
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_cars = data.get('active_cars', {})
                    self.parking_history = data.get('parking_history', [])
            except:
                pass
    
    def save_data(self):
        data = {
            'active_cars': self.active_cars,
            'parking_history': self.parking_history
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def car_entry(self, plate_number):
        plate_number = plate_number.upper().replace(' ', '')
        if plate_number in self.active_cars:
            return False, "خودرو قبلاً وارد شده است!"
        
        entry_time = datetime.now()
        self.active_cars[plate_number] = entry_time.isoformat()
        self.save_data()
        return True, f"ورود خودرو با پلاک {plate_number} ثبت شد"
    
    def car_exit(self, plate_number):
        plate_number = plate_number.upper().replace(' ', '')
        if plate_number not in self.active_cars:
            return None, "خودرو در پارکینگ نیست!"
        
        entry_time = datetime.fromisoformat(self.active_cars[plate_number])
        exit_time = datetime.now()
        duration = exit_time - entry_time
        total_hours = duration.total_seconds() / 3600
        
        if total_hours <= 0.25:
            cost = 0
        else:
            hours_charged = max(1, int(total_hours + 0.99))
            cost = hours_charged * self.hourly_rate
        
        record = {
            'plate': plate_number,
            'entry_time': entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'duration_hours': round(total_hours, 2),
            'cost': cost
        }
        self.parking_history.append(record)
        del self.active_cars[plate_number]
        self.save_data()
        
        return record, f"خروج موفق - هزینه: {cost:,} تومان"


class ParkingManagementApp(QMainWindow):
    """رابط کاربری گرافیکی با PyQt5"""
    
    def __init__(self):
        super().__init__()
        self.parking_system = ParkingSystem()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🏢 سیستم مدیریت پارکینگ")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # هدر
        header = QLabel("سیستم مدیریت هوشمند پارکینگ")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Tahoma", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        main_layout.addWidget(header)
        
        # تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Tahoma", 10))
        
        # تب ورود/خروج
        self.entry_exit_tab = self.create_entry_exit_tab()
        self.tab_widget.addTab(self.entry_exit_tab, "🚗 ورود/خروج")
        
        # تب پارکینگ فعلی
        self.active_tab = self.create_active_tab()
        self.tab_widget.addTab(self.active_tab, "🅿️ پارکینگ فعلی")
        
        # تب تاریخچه
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📊 تاریخچه")
        
        # تب تنظیمات
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ تنظیمات")
        
        main_layout.addWidget(self.tab_widget)
        
        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
    def get_stylesheet(self):
        """استایل‌دهی برنامه"""
        return """
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2ecc71;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#exit_btn {
                background-color: #e74c3c;
            }
            QPushButton#exit_btn:hover {
                background-color: #c0392b;
            }
            QPushButton#refresh_btn {
                background-color: #2ecc71;
            }
            QPushButton#refresh_btn:hover {
                background-color: #27ae60;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
            }
        """
    
    def create_entry_exit_tab(self):
        """تب ورود و خروج خودرو"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # گروه ورود
        entry_group = QGroupBox("ورود خودرو")
        entry_layout = QFormLayout()
        
        self.entry_plate_input = QLineEdit()
        self.entry_plate_input.setPlaceholderText("مثال: 12A345-67")
        self.entry_plate_input.setFont(QFont("Tahoma", 14))
        self.entry_plate_input.returnPressed.connect(self.car_entry)
        
        entry_btn = QPushButton("ثبت ورود 🚗")
        entry_btn.clicked.connect(self.car_entry)
        
        entry_layout.addRow("پلاک خودرو:", self.entry_plate_input)
        entry_layout.addRow("", entry_btn)
        entry_group.setLayout(entry_layout)
        layout.addWidget(entry_group)
        
        # گروه خروج
        exit_group = QGroupBox("خروج خودرو")
        exit_layout = QFormLayout()
        
        self.exit_plate_input = QLineEdit()
        self.exit_plate_input.setPlaceholderText("مثال: 12A345-67")
        self.exit_plate_input.setFont(QFont("Tahoma", 14))
        self.exit_plate_input.returnPressed.connect(self.car_exit)
        
        exit_btn = QPushButton("ثبت خروج و محاسبه هزینه 💰")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self.car_exit)
        
        exit_layout.addRow("پلاک خودرو:", self.exit_plate_input)
        exit_layout.addRow("", exit_btn)
        exit_group.setLayout(exit_layout)
        layout.addWidget(exit_group)
        
        # نمایش اطلاعات خروج
        self.exit_info_label = QLabel("")
        self.exit_info_label.setFont(QFont("Tahoma", 12))
        self.exit_info_label.setAlignment(Qt.AlignCenter)
        self.exit_info_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(self.exit_info_label)
        
        layout.addStretch()
        return widget
    
    def create_active_tab(self):
        """تب نمایش خودروهای حاضر"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_active_cars)
        
        lbl = QLabel(f"نرخ ساعتی: {self.parking_system.hourly_rate:,} تومان")
        lbl.setFont(QFont("Tahoma", 10))
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(lbl)
        layout.addLayout(btn_layout)
        
        # جدول خودروهای حاضر
        self.active_table = QTableWidget()
        self.active_table.setColumnCount(4)
        self.active_table.setHorizontalHeaderLabels(["ردیف", "پلاک", "زمان ورود", "مدت حضور"])
        self.active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.active_table)
        
        self.refresh_active_cars()
        return widget
    
    def create_history_tab(self):
        """تب تاریخچه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_history)
        
        clear_btn = QPushButton("🗑️ پاک کردن تاریخچه")
        clear_btn.setObjectName("exit_btn")
        clear_btn.clicked.connect(self.clear_history)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        # جدول تاریخچه
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "زمان ورود", "زمان خروج", "مدت (ساعت)", "هزینه (تومان)"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.history_table)
        
        # آمار
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Tahoma", 11))
        self.stats_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(self.stats_label)
        
        self.refresh_history()
        return widget
    
    def create_settings_tab(self):
        """تب تنظیمات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # تنظیمات نرخ
        rate_group = QGroupBox("تنظیمات نرخ پارکینگ")
        rate_layout = QFormLayout()
        
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(1000, 1000000)
        self.rate_input.setValue(self.parking_system.hourly_rate)
        self.rate_input.setPrefix("تومان ")
        self.rate_input.setFont(QFont("Tahoma", 12))
        
        save_rate_btn = QPushButton("💾 ذخیره نرخ جدید")
        save_rate_btn.clicked.connect(self.save_rate)
        
        rate_layout.addRow("نرخ هر ساعت:", self.rate_input)
        rate_layout.addRow("", save_rate_btn)
        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)
        
        # اطلاعات برنامه
        info_group = QGroupBox("اطلاعات برنامه")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
        🏢 سیستم مدیریت پارکینگ
        📅 نسخه 1.0
        
        ویژگی‌ها:
        • ثبت ورود و خروج خودروها
        • محاسبه خودکار هزینه بر اساس زمان توقف
        • ذخیره‌سازی دائمی اطلاعات
        • گزارش‌گیری و مشاهده تاریخچه
        • توقف کمتر از 15 دقیقه رایگان
        """)
        info_text.setFont(QFont("Tahoma", 10))
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def car_entry(self):
        """ثبت ورود خودرو"""
        plate = self.entry_plate_input.text().strip()
        if not plate:
            QMessageBox.warning(self, "خطا", "لطفاً پلاک خودرو را وارد کنید!")
            return
        
        success, message = self.parking_system.car_entry(plate)
        if success:
            QMessageBox.information(self, "موفق", message)
            self.entry_plate_input.clear()
            self.refresh_active_cars()
            self.update_status()
        else:
            QMessageBox.warning(self, "خطا", message)
    
    def car_exit(self):
        """ثبت خروج خودرو و محاسبه هزینه"""
        plate = self.exit_plate_input.text().strip()
        if not plate:
            QMessageBox.warning(self, "خطا", "لطفاً پلاک خودرو را وارد کنید!")
            return
        
        record, message = self.parking_system.car_exit(plate)
        if record:
            # نمایش اطلاعات کامل خروج
            info_text = f"""
            🚗 پلاک: {record['plate']}
            ⏰ ورود: {datetime.fromisoformat(record['entry_time']).strftime('%H:%M:%S')}
            ⏰ خروج: {datetime.fromisoformat(record['exit_time']).strftime('%H:%M:%S')}
            ⏱️ مدت توقف: {record['duration_hours']:.2f} ساعت
            💰 هزینه: {record['cost']:,} تومان
            """
            self.exit_info_label.setText(info_text)
            self.exit_plate_input.clear()
            self.refresh_active_cars()
            self.refresh_history()
            self.update_status()
            QMessageBox.information(self, "خروج موفق", message)
        else:
            QMessageBox.warning(self, "خطا", message)
    
    def refresh_active_cars(self):
        """بروزرسانی جدول خودروهای حاضر"""
        self.active_table.setRowCount(0)
        active_cars = self.parking_system.active_cars
        
        for i, (plate, entry_time_str) in enumerate(active_cars.items()):
            entry_time = datetime.fromisoformat(entry_time_str)
            duration = datetime.now() - entry_time
            hours = duration.total_seconds() / 3600
            
            self.active_table.insertRow(i)
            self.active_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.active_table.setItem(i, 1, QTableWidgetItem(plate))
            self.active_table.setItem(i, 2, QTableWidgetItem(entry_time.strftime('%H:%M:%S')))
            self.active_table.setItem(i, 3, QTableWidgetItem(f"{hours:.1f} ساعت"))
            
            # رنگ‌آمیزی بر اساس مدت زمان
            if hours > 5:
                for col in range(4):
                    self.active_table.item(i, col).setBackground(QColor("#ffeaa7"))
    
    def refresh_history(self):
        """بروزرسانی جدول تاریخچه"""
        self.history_table.setRowCount(0)
        history = self.parking_system.parking_history[-50:]  # نمایش 50 مورد آخر
        
        total_income = 0
        for i, record in enumerate(reversed(history)):
            entry_time = datetime.fromisoformat(record['entry_time'])
            exit_time = datetime.fromisoformat(record['exit_time'])
            
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.history_table.setItem(i, 1, QTableWidgetItem(record['plate']))
            self.history_table.setItem(i, 2, QTableWidgetItem(entry_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 3, QTableWidgetItem(exit_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{record['duration_hours']:.1f}"))
            self.history_table.setItem(i, 5, QTableWidgetItem(f"{record['cost']:,}"))
            
            total_income += record['cost']
        
        # بروزرسانی آمار
        today = datetime.now().strftime('%Y-%m-%d')
        today_income = sum(r['cost'] for r in history if r['entry_time'].startswith(today))
        today_count = sum(1 for r in history if r['entry_time'].startswith(today))
        
        self.stats_label.setText(
            f"📊 آمار امروز: {today_count} خودرو | درآمد امروز: {today_income:,} تومان | "
            f"کل درآمد نمایش داده شده: {total_income:,} تومان"
        )
    
    def save_rate(self):
        """ذخیره نرخ جدید"""
        new_rate = self.rate_input.value()
        self.parking_system.hourly_rate = new_rate
        QMessageBox.information(self, "موفق", f"نرخ ساعتی به {new_rate:,} تومان تغییر کرد")
    
    def clear_history(self):
        """پاک کردن تاریخچه"""
        reply = QMessageBox.question(
            self, "تأیید", "آیا از پاک کردن تمام تاریخچه اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.parking_system.parking_history.clear()
            self.parking_system.save_data()
            self.refresh_history()
            QMessageBox.information(self, "موفق", "تاریخچه پاک شد")
    
    def update_status(self):
        """بروزرسانی نوار وضعیت"""
        active_count = len(self.parking_system.active_cars)
        total_history = len(self.parking_system.parking_history)
        self.status_bar.showMessage(
            f"🚗 خودروهای حاضر: {active_count} | 📊 کل ثبت‌ها: {total_history} | 💰 نرخ: {self.parking_system.hourly_rate:,} تومان/ساعت"
        )
    
    def setup_timer(self):
        """تنظیم تایمر برای بروزرسانی خودکار"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(60000)  # هر 60 ثانیه
    
    def auto_refresh(self):
        """بروزرسانی خودکار"""
        if self.tab_widget.currentIndex() == 1:  # تب پارکینگ فعلی
            self.refresh_active_cars()
        self.update_status()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 9))
    
    # تنظیم جهت راست به چپ
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = ParkingManagementApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()