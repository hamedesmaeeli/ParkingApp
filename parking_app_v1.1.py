import sys
import json
import os
import re
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QGroupBox, QFormLayout, QHeaderView,
    QSpinBox, QDoubleSpinBox, QStatusBar, QFrame, QSplitter,
    QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QRegExpValidator
from PyQt5.QtCore import QRegExp

class IranianPlateValidator:
    """اعتبارسنجی پلاک‌های ایرانی"""
    
    # الگوهای معتبر پلاک ایران
    PLATE_PATTERNS = {
        'personal': r'^\d{2}[الف-ی]\d{3}-\d{2}$',  # 12A345-67
        'taxi': r'^\d{2}ت\d{3}-\d{2}$',           # 12T345-67
        'governmental': r'^\d{2}[الف-ی]\d{3}-\d{1}$',  # 12A345-6
        'military': r'^\d{3}[الف-ی]\d{2}-\d{2}$', # 123A45-67
        'diplomatic': r'^\d{2}د\d{3}-\d{2}$',     # 12D345-67
    }
    
    # حروف مجاز در پلاک‌های شخصی
    VALID_LETTERS = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د',
        'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ',
        'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و',
        'ه', 'ی'
    ]
    
    # کدهای استان
    PROVINCE_CODES = {
        '01': 'تهران مرکزی', '02': 'تهران شرق', '03': 'تهران غرب',
        '11': 'اصفهان', '12': 'خراسان رضوی', '13': 'فارس',
        '14': 'آذربایجان شرقی', '15': 'آذربایجان غربی', '16': 'خوزستان',
        '17': 'مازندران', '18': 'کرمان', '19': 'گیلان',
        '21': 'سیستان و بلوچستان', '22': 'همدان', '23': 'زنجان',
        '24': 'لرستان', '25': 'گلستان', '26': 'کردستان',
        '27': 'هرمزگان', '28': 'مرکزی', '29': 'بوشهر',
        '31': 'چهارمحال و بختیاری', '32': 'کهگیلویه و بویراحمد',
        '33': 'ایلام', '34': 'کرمانشاه', '35': 'یزد',
        '36': 'سمنان', '37': 'قزوین', '38': 'البرز',
        '41': 'خراسان شمالی', '42': 'خراسان جنوبی', '43': 'اردبیل',
        '51': 'قشم', '52': 'کیش'
    }
    
    @classmethod
    def validate_plate(cls, plate_number):
        """
        اعتبارسنجی پلاک ایرانی
        برمی‌گرداند: (is_valid, plate_type, formatted_plate, message)
        """
        # حذف فاصله‌ها و تبدیل به فرمت استاندارد
        plate = plate_number.strip().replace(' ', '')
        
        if not plate:
            return False, None, None, "پلاک نمی‌تواند خالی باشد"
        
        # بررسی طول پلاک
        if len(plate) < 7 or len(plate) > 9:
            return False, None, None, "طول پلاک نامعتبر است"
        
        # اضافه کردن خط تیره اگر وجود نداشته باشد
        if '-' not in plate:
            # سعی در تشخیص محل خط تیره
            if len(plate) == 8:  # فرمت معمول: 12A34567
                plate = plate[:5] + '-' + plate[5:]
            elif len(plate) == 7:  # فرمت دولتی: 12A3456
                plate = plate[:5] + '-' + plate[5:]
            elif len(plate) == 9:  # فرمت نظامی: 123A4567
                plate = plate[:6] + '-' + plate[6:]
        
        # بررسی الگوهای مختلف
        for plate_type, pattern in cls.PLATE_PATTERNS.items():
            if re.match(pattern, plate):
                return True, plate_type, plate, "پلاک معتبر است"
        
        # بررسی دستی برای حروف فارسی
        if cls._manual_validation(plate):
            return True, 'personal', plate, "پلاک معتبر است"
        
        return False, None, None, "فرمت پلاک نامعتبر است"
    
    @classmethod
    def _manual_validation(cls, plate):
        """بررسی دستی پلاک برای حروف فارسی"""
        try:
            parts = plate.split('-')
            if len(parts) != 2:
                return False
            
            first_part = parts[0]
            second_part = parts[1]
            
            # بررسی بخش اول (مثلاً 12A345)
            if len(first_part) == 5:
                if not first_part[:2].isdigit():
                    return False
                if not first_part[3:].isdigit():
                    return False
                # حرف میانی باید فارسی باشد
                middle_char = first_part[2]
                if middle_char not in cls.VALID_LETTERS:
                    return False
            
            # بررسی بخش دوم (کد استان)
            if len(second_part) in [1, 2]:
                if not second_part.isdigit():
                    return False
            else:
                return False
            
            return True
        except:
            return False
    
    @classmethod
    def get_province_name(cls, plate):
        """دریافت نام استان از روی کد پلاک"""
        try:
            if '-' in plate:
                code = plate.split('-')[1]
                if len(code) == 2 and code in cls.PROVINCE_CODES:
                    return cls.PROVINCE_CODES[code]
                elif len(code) == 1:
                    return "پلاک دولتی"
        except:
            pass
        return "نامشخص"
    
    @classmethod
    def format_plate_display(cls, plate):
        """فرمت‌بندی پلاک برای نمایش زیبا"""
        if '-' in plate:
            parts = plate.split('-')
            return f"{parts[0]} - {parts[1]}"
        return plate


class ParkingSystem:
    """سیستم اصلی مدیریت پارکینگ"""
    def __init__(self, hourly_rate=5000, data_file="parking_data.json"):
        self.hourly_rate = hourly_rate
        self.data_file = data_file
        self.active_cars = {}  # plate: {entry_time, plate_type, province}
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
        """ثبت ورود خودرو با اعتبارسنجی پلاک ایرانی"""
        # اعتبارسنجی پلاک
        is_valid, plate_type, formatted_plate, message = IranianPlateValidator.validate_plate(plate_number)
        
        if not is_valid:
            return False, message
        
        # بررسی تکراری نبودن
        if formatted_plate in self.active_cars:
            return False, f"خودرو با پلاک {formatted_plate} قبلاً وارد شده است!"
        
        entry_time = datetime.now()
        province = IranianPlateValidator.get_province_name(formatted_plate)
        
        self.active_cars[formatted_plate] = {
            'entry_time': entry_time.isoformat(),
            'plate_type': plate_type,
            'province': province
        }
        self.save_data()
        
        type_names = {
            'personal': 'شخصی',
            'taxi': 'تاکسی',
            'governmental': 'دولتی',
            'military': 'نظامی',
            'diplomatic': 'سیاسی'
        }
        
        return True, f"ورود خودرو {type_names.get(plate_type, '')} با پلاک {formatted_plate} - استان: {province}"
    
    def car_exit(self, plate_number):
        """ثبت خروج خودرو و محاسبه هزینه"""
        # فرمت‌بندی پلاک
        plate = plate_number.strip().replace(' ', '')
        if '-' not in plate and len(plate) >= 7:
            if len(plate) == 8:
                plate = plate[:5] + '-' + plate[5:]
            elif len(plate) == 7:
                plate = plate[:5] + '-' + plate[5:]
        
        if plate not in self.active_cars:
            return None, "خودرو در پارکینگ نیست!"
        
        car_info = self.active_cars[plate]
        entry_time = datetime.fromisoformat(car_info['entry_time'])
        exit_time = datetime.now()
        duration = exit_time - entry_time
        total_hours = duration.total_seconds() / 3600
        
        # محاسبه هزینه
        if total_hours <= 0.25:  # کمتر از 15 دقیقه رایگان
            cost = 0
            discount_msg = " (کمتر از 15 دقیقه - رایگان)"
        else:
            hours_charged = max(1, int(total_hours + 0.99))
            
            # تخفیف برای تاکسی‌ها و خودروهای عمومی
            if car_info['plate_type'] in ['taxi', 'governmental']:
                cost = hours_charged * self.hourly_rate * 0.7  # 30% تخفیف
                discount_msg = " (با 30% تخفیف)"
            else:
                cost = hours_charged * self.hourly_rate
                discount_msg = ""
        
        record = {
            'plate': plate,
            'entry_time': entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'duration_hours': round(total_hours, 2),
            'cost': cost,
            'plate_type': car_info['plate_type'],
            'province': car_info['province'],
            'discount': discount_msg
        }
        self.parking_history.append(record)
        del self.active_cars[plate]
        self.save_data()
        
        return record, f"خروج موفق - هزینه: {cost:,.0f} تومان{discount_msg}"


class ParkingManagementApp(QMainWindow):
    """رابط کاربری گرافیکی با PyQt5"""
    
    def __init__(self):
        super().__init__()
        self.parking_system = ParkingSystem()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🏢 سیستم مدیریت پارکینگ - پلاک ایرانی")
        self.setGeometry(100, 100, 1300, 750)
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
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                font-size: 14px;
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
    
    def create_plate_input_widget(self, placeholder="مثال: 12A345-67"):
        """ایجاد ویجت ورود پلاک با فرمت ایرانی"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # فیلد ورود پلاک
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFont(QFont("Tahoma", 14))
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setMinimumHeight(40)
        
        # راهنمای فرمت
        help_label = QLabel("فرمت: 12A345-67")
        help_label.setFont(QFont("Tahoma", 9))
        help_label.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(line_edit)
        layout.addWidget(help_label)
        
        return widget, line_edit
    
    def create_entry_exit_tab(self):
        """تب ورود و خروج خودرو"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # گروه ورود
        entry_group = QGroupBox("ورود خودرو")
        entry_layout = QFormLayout()
        
        self.entry_plate_widget, self.entry_plate_input = self.create_plate_input_widget()
        self.entry_plate_input.returnPressed.connect(self.car_entry)
        
        entry_btn = QPushButton("ثبت ورود 🚗")
        entry_btn.clicked.connect(self.car_entry)
        entry_btn.setMinimumHeight(50)
        
        entry_layout.addRow("پلاک خودرو:", self.entry_plate_widget)
        entry_layout.addRow("", entry_btn)
        entry_group.setLayout(entry_layout)
        layout.addWidget(entry_group)
        
        # نمونه پلاک‌های معتبر
        examples_group = QGroupBox("نمونه پلاک‌های معتبر")
        examples_layout = QGridLayout()
        
        examples = [
            ("شخصی:", "12A345-67"),
            ("تاکسی:", "12ت345-67"),
            ("دولتی:", "12A345-6"),
            ("نظامی:", "123A45-67"),
            ("سیاسی:", "12د345-67")
        ]
        
        for i, (label, example) in enumerate(examples):
            examples_layout.addWidget(QLabel(f"<b>{label}</b> {example}"), i // 2, i % 2)
        
        examples_group.setLayout(examples_layout)
        layout.addWidget(examples_group)
        
        # گروه خروج
        exit_group = QGroupBox("خروج خودرو")
        exit_layout = QFormLayout()
        
        self.exit_plate_widget, self.exit_plate_input = self.create_plate_input_widget()
        self.exit_plate_input.returnPressed.connect(self.car_exit)
        
        exit_btn = QPushButton("ثبت خروج و محاسبه هزینه 💰")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self.car_exit)
        exit_btn.setMinimumHeight(50)
        
        exit_layout.addRow("پلاک خودرو:", self.exit_plate_widget)
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
        self.active_table.setColumnCount(6)
        self.active_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "نوع پلاک", "استان", "زمان ورود", "مدت حضور"
        ])
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
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "نوع", "استان", "زمان ورود", "زمان خروج", 
            "مدت (ساعت)", "هزینه (تومان)"
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
        
        # تخفیف‌ها
        discount_group = QGroupBox("تخفیف‌های خودکار")
        discount_layout = QVBoxLayout()
        
        discount_info = QLabel("""
        🚕 تاکسی‌ها: 30% تخفیف
        🏛️ خودروهای دولتی: 30% تخفیف
        ⏱️ توقف کمتر از 15 دقیقه: رایگان
        
        توجه: تخفیف‌ها به صورت خودکار اعمال می‌شوند
        """)
        discount_info.setFont(QFont("Tahoma", 10))
        discount_layout.addWidget(discount_info)
        discount_group.setLayout(discount_layout)
        layout.addWidget(discount_group)
        
        # اطلاعات برنامه
        info_group = QGroupBox("اطلاعات برنامه")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
        🏢 سیستم مدیریت پارکینگ
        📅 نسخه 2.0 - پشتیبانی از پلاک ایرانی
        
        ویژگی‌ها:
        • اعتبارسنجی پلاک‌های ایرانی
        • تشخیص خودکار نوع پلاک و استان
        • تخفیف خودکار برای تاکسی و خودروهای دولتی
        • محاسبه دقیق هزینه پارکینگ
        • گزارش‌گیری کامل با جزئیات پلاک
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
            type_names = {
                'personal': 'شخصی',
                'taxi': 'تاکسی',
                'governmental': 'دولتی',
                'military': 'نظامی',
                'diplomatic': 'سیاسی'
            }
            
            info_text = f"""
            🚗 پلاک: {record['plate']}
            📋 نوع: {type_names.get(record['plate_type'], 'نامشخص')}
            📍 استان: {record['province']}
            ⏰ ورود: {datetime.fromisoformat(record['entry_time']).strftime('%H:%M:%S')}
            ⏰ خروج: {datetime.fromisoformat(record['exit_time']).strftime('%H:%M:%S')}
            ⏱️ مدت توقف: {record['duration_hours']:.2f} ساعت
            💰 هزینه: {record['cost']:,.0f} تومان{record.get('discount', '')}
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
        
        type_names = {
            'personal': 'شخصی',
            'taxi': 'تاکسی',
            'governmental': 'دولتی',
            'military': 'نظامی',
            'diplomatic': 'سیاسی'
        }
        
        for i, (plate, car_info) in enumerate(active_cars.items()):
            entry_time = datetime.fromisoformat(car_info['entry_time'])
            duration = datetime.now() - entry_time
            hours = duration.total_seconds() / 3600
            
            self.active_table.insertRow(i)
            self.active_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            # نمایش پلاک با فرمت زیبا
            plate_display = IranianPlateValidator.format_plate_display(plate)
            self.active_table.setItem(i, 1, QTableWidgetItem(plate_display))
            
            self.active_table.setItem(i, 2, QTableWidgetItem(type_names.get(car_info['plate_type'], 'نامشخص')))
            self.active_table.setItem(i, 3, QTableWidgetItem(car_info.get('province', 'نامشخص')))
            self.active_table.setItem(i, 4, QTableWidgetItem(entry_time.strftime('%H:%M:%S')))
            self.active_table.setItem(i, 5, QTableWidgetItem(f"{hours:.1f} ساعت"))
            
            # رنگ‌آمیزی بر اساس مدت زمان
            if hours > 5:
                for col in range(6):
                    self.active_table.item(i, col).setBackground(QColor("#ffeaa7"))
            elif hours > 3:
                for col in range(6):
                    self.active_table.item(i, col).setBackground(QColor("#dfe6e9"))
    
    def refresh_history(self):
        """بروزرسانی جدول تاریخچه"""
        self.history_table.setRowCount(0)
        history = self.parking_system.parking_history[-50:]
        
        type_names = {
            'personal': 'شخصی',
            'taxi': 'تاکسی',
            'governmental': 'دولتی',
            'military': 'نظامی',
            'diplomatic': 'سیاسی'
        }
        
        total_income = 0
        for i, record in enumerate(reversed(history)):
            entry_time = datetime.fromisoformat(record['entry_time'])
            exit_time = datetime.fromisoformat(record['exit_time'])
            
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            plate_display = IranianPlateValidator.format_plate_display(record['plate'])
            self.history_table.setItem(i, 1, QTableWidgetItem(plate_display))
            
            self.history_table.setItem(i, 2, QTableWidgetItem(type_names.get(record.get('plate_type', 'personal'), 'شخصی')))
            self.history_table.setItem(i, 3, QTableWidgetItem(record.get('province', 'نامشخص')))
            self.history_table.setItem(i, 4, QTableWidgetItem(entry_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 5, QTableWidgetItem(exit_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 6, QTableWidgetItem(f"{record['duration_hours']:.1f}"))
            
            # نمایش هزینه با فرمت
            cost_text = f"{record['cost']:,.0f}"
            if record.get('discount'):
                cost_text += " ⭐"
            self.history_table.setItem(i, 7, QTableWidgetItem(cost_text))
            
            total_income += record['cost']
        
        # بروزرسانی آمار
        today = datetime.now().strftime('%Y-%m-%d')
        today_income = sum(r['cost'] for r in history if r['entry_time'].startswith(today))
        today_count = sum(1 for r in history if r['entry_time'].startswith(today))
        
        # تفکیک انواع پلاک
        plate_types_count = {}
        for r in history:
            if r['entry_time'].startswith(today):
                ptype = r.get('plate_type', 'personal')
                plate_types_count[ptype] = plate_types_count.get(ptype, 0) + 1
        
        types_str = " | ".join([f"{type_names.get(k, k)}: {v}" for k, v in plate_types_count.items()])
        
        self.stats_label.setText(
            f"📊 آمار امروز: {today_count} خودرو | {types_str} | "
            f"درآمد امروز: {today_income:,.0f} تومان | "
            f"کل درآمد: {total_income:,.0f} تومان"
        )
    
    def save_rate(self):
        """ذخیره نرخ جدید"""
        new_rate = self.rate_input.value()
        self.parking_system.hourly_rate = new_rate
        QMessageBox.information(self, "موفق", f"نرخ ساعتی به {new_rate:,.0f} تومان تغییر کرد")
    
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
        
        # محاسبه تعداد هر نوع پلاک
        type_count = {}
        for car_info in self.parking_system.active_cars.values():
            ptype = car_info['plate_type']
            type_count[ptype] = type_count.get(ptype, 0) + 1
        
        status = f"🚗 خودروهای حاضر: {active_count}"
        if type_count:
            types = []
            for ptype, count in type_count.items():
                type_names = {'personal': 'شخصی', 'taxi': 'تاکسی', 'governmental': 'دولتی'}
                types.append(f"{type_names.get(ptype, ptype)}: {count}")
            status += f" ({' | '.join(types)})"
        
        status += f" | 📊 کل ثبت‌ها: {total_history} | 💰 نرخ: {self.parking_system.hourly_rate:,} تومان/ساعت"
        self.status_bar.showMessage(status)
    
    def setup_timer(self):
        """تنظیم تایمر برای بروزرسانی خودکار"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(60000)  # هر 60 ثانیه
    
    def auto_refresh(self):
        """بروزرسانی خودکار"""
        if self.tab_widget.currentIndex() == 1:
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