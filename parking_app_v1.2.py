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
    QComboBox, QGridLayout, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QRegExpValidator, QFontDatabase
from PyQt5.QtCore import QRegExp

class IranianPlateValidator:
    """اعتبارسنجی پلاک‌های ایرانی"""
    
    PLATE_PATTERNS = {
        'personal': r'^\d{2}[الف-ی]\d{3}-\d{2}$',
        'taxi': r'^\d{2}ت\d{3}-\d{2}$',
        'governmental': r'^\d{2}[الف-ی]\d{3}-\d{1}$',
        'military': r'^\d{3}[الف-ی]\d{2}-\d{2}$',
        'diplomatic': r'^\d{2}د\d{3}-\d{2}$',
    }
    
    VALID_LETTERS = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د',
        'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ',
        'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و',
        'ه', 'ی'
    ]
    
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
    def validate_plate_parts(cls, part1, letter, part2, part3):
        """اعتبارسنجی بخش‌های مختلف پلاک"""
        # ترکیب بخش‌ها
        if letter and part3:
            plate = f"{part1}{letter}{part2}-{part3}"
        else:
            return False, None, None, "همه بخش‌ها باید پر شوند"
        
        return cls.validate_plate(plate)
    
    @classmethod
    def validate_plate(cls, plate_number):
        plate = plate_number.strip().replace(' ', '')
        
        if not plate:
            return False, None, None, "پلاک نمی‌تواند خالی باشد"
        
        if len(plate) < 7 or len(plate) > 9:
            return False, None, None, "طول پلاک نامعتبر است"
        
        if '-' not in plate:
            if len(plate) == 8:
                plate = plate[:5] + '-' + plate[5:]
            elif len(plate) == 7:
                plate = plate[:5] + '-' + plate[5:]
            elif len(plate) == 9:
                plate = plate[:6] + '-' + plate[6:]
        
        for plate_type, pattern in cls.PLATE_PATTERNS.items():
            if re.match(pattern, plate):
                return True, plate_type, plate, "پلاک معتبر است"
        
        if cls._manual_validation(plate):
            return True, 'personal', plate, "پلاک معتبر است"
        
        return False, None, None, "فرمت پلاک نامعتبر است"
    
    @classmethod
    def _manual_validation(cls, plate):
        try:
            parts = plate.split('-')
            if len(parts) != 2:
                return False
            
            first_part = parts[0]
            second_part = parts[1]
            
            if len(first_part) == 5:
                if not first_part[:2].isdigit():
                    return False
                if not first_part[3:].isdigit():
                    return False
                middle_char = first_part[2]
                if middle_char not in cls.VALID_LETTERS:
                    return False
            
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
        """فرمت‌بندی پلاک برای نمایش زیبا به سبک ایرانی"""
        if '-' in plate:
            parts = plate.split('-')
            # بخش اول: دو رقم اول + حرف + سه رقم
            first = parts[0]
            if len(first) == 5:
                formatted_first = f"{first[:2]} {first[2]} {first[3:]}"
            elif len(first) == 6:
                formatted_first = f"{first[:3]} {first[3]} {first[4:]}"
            else:
                formatted_first = first
            
            # بخش دوم: کد استان
            second = parts[1]
            
            return f"{formatted_first} {second}"
        return plate


class IranianPlateWidget(QWidget):
    """ویجت سفارشی ورود پلاک ایرانی به صورت چند بخشی"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # استایل مشترک برای همه فیلدها
        field_style = """
            QLineEdit {
                font-size: 18px;
                font-weight: bold;
                font-family: 'Tahoma', 'B Nazanin';
                text-align: center;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ebf5fb;
            }
        """
        
        # بخش اول: دو رقم اول
        self.part1_input = QLineEdit()
        self.part1_input.setPlaceholderText("۱۲")
        self.part1_input.setMaxLength(2)
        self.part1_input.setFixedWidth(60)
        self.part1_input.setAlignment(Qt.AlignCenter)
        self.part1_input.setStyleSheet(field_style)
        self.part1_input.textChanged.connect(self.on_part1_changed)
        
        # جداکننده
        separator1 = QLabel("|")
        separator1.setStyleSheet("font-size: 20px; color: #7f8c8d; font-weight: bold;")
        separator1.setFixedWidth(10)
        separator1.setAlignment(Qt.AlignCenter)
        
        # بخش دوم: حرف پلاک
        self.letter_input = QLineEdit()
        self.letter_input.setPlaceholderText("الف")
        self.letter_input.setMaxLength(1)
        self.letter_input.setFixedWidth(60)
        self.letter_input.setAlignment(Qt.AlignCenter)
        self.letter_input.setStyleSheet(field_style)
        
        # جداکننده
        separator2 = QLabel("|")
        separator2.setStyleSheet("font-size: 20px; color: #7f8c8d; font-weight: bold;")
        separator2.setFixedWidth(10)
        separator2.setAlignment(Qt.AlignCenter)
        
        # بخش سوم: سه رقم
        self.part2_input = QLineEdit()
        self.part2_input.setPlaceholderText("۳۴۵")
        self.part2_input.setMaxLength(3)
        self.part2_input.setFixedWidth(80)
        self.part2_input.setAlignment(Qt.AlignCenter)
        self.part2_input.setStyleSheet(field_style)
        
        # خط تیره ایران
        iran_separator = QLabel("ایران")
        iran_separator.setStyleSheet("""
            font-size: 11px; 
            color: #e74c3c; 
            font-weight: bold;
            background-color: #fadbd8;
            border: 1px solid #e74c3c;
            border-radius: 5px;
            padding: 8px 5px;
        """)
        iran_separator.setFixedWidth(45)
        iran_separator.setAlignment(Qt.AlignCenter)
        
        # بخش چهارم: کد استان
        self.part3_input = QLineEdit()
        self.part3_input.setPlaceholderText("۱۱")
        self.part3_input.setMaxLength(2)
        self.part3_input.setFixedWidth(60)
        self.part3_input.setAlignment(Qt.AlignCenter)
        self.part3_input.setStyleSheet(field_style)
        
        # راهنما
        help_label = QLabel("۱۲ الف ۳۴۵ ایران ۱۱")
        help_label.setStyleSheet("font-size: 10px; color: #95a5a6; font-style: italic;")
        help_label.setFixedWidth(120)
        
        layout.addWidget(self.part1_input)
        layout.addWidget(separator1)
        layout.addWidget(self.letter_input)
        layout.addWidget(separator2)
        layout.addWidget(self.part2_input)
        layout.addWidget(iran_separator)
        layout.addWidget(self.part3_input)
        layout.addWidget(help_label)
        layout.addStretch()
    
    def on_part1_changed(self, text):
        """وقتی بخش اول تغییر کرد، فوکوس به بخش بعدی"""
        if len(text) == 2:
            self.letter_input.setFocus()
    
    def get_plate(self):
        """دریافت پلاک کامل"""
        part1 = self.part1_input.text().strip()
        letter = self.letter_input.text().strip()
        part2 = self.part2_input.text().strip()
        part3 = self.part3_input.text().strip()
        
        if part1 and letter and part2 and part3:
            return f"{part1}{letter}{part2}-{part3}"
        return ""
    
    def clear(self):
        """پاک کردن همه فیلدها"""
        self.part1_input.clear()
        self.letter_input.clear()
        self.part2_input.clear()
        self.part3_input.clear()
        self.part1_input.setFocus()
    
    def set_plate(self, plate):
        """تنظیم پلاک در فیلدها"""
        if '-' in plate:
            parts = plate.split('-')
            first = parts[0]
            second = parts[1]
            
            if len(first) == 5:
                self.part1_input.setText(first[:2])
                self.letter_input.setText(first[2])
                self.part2_input.setText(first[3:])
            elif len(first) == 6:
                self.part1_input.setText(first[:3])
                self.letter_input.setText(first[3])
                self.part2_input.setText(first[4:])
            
            self.part3_input.setText(second)


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
        is_valid, plate_type, formatted_plate, message = IranianPlateValidator.validate_plate(plate_number)
        
        if not is_valid:
            return False, message
        
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
        
        if total_hours <= 0.25:
            cost = 0
            discount_msg = " (کمتر از 15 دقیقه - رایگان)"
        else:
            hours_charged = max(1, int(total_hours + 0.99))
            
            if car_info['plate_type'] in ['taxi', 'governmental']:
                cost = hours_charged * self.hourly_rate * 0.7
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
    """رابط کاربری گرافیکی با PyQt5 - تم ایرانی"""
    
    def __init__(self):
        super().__init__()
        self.parking_system = ParkingSystem()
        self.init_ui()
        self.setup_timer()
        self.apply_persian_theme()
        
    def apply_persian_theme(self):
        """اعمال تم ایرانی-اسلامی"""
        self.setStyleSheet("""
            /* ========== استایل اصلی برنامه ========== */
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0c1929, stop: 0.5 #1a2a40, stop: 1 #0c1929);
            }
            
            QWidget {
                font-family: 'Tahoma', 'B Nazanin', 'Iranian Sans';
            }
            
            /* ========== تب‌ها ========== */
            QTabWidget::pane {
                border: 2px solid #c8a45c;
                border-radius: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fef9e7, stop: 1 #fdebd0);
                padding: 5px;
                margin-top: -1px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
                color: #c8a45c;
                padding: 12px 25px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #c8a45c;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 0.5 #d4af6a, stop: 1 #b8944a);
                color: #1a252f;
                font-weight: bold;
                border: 2px solid #8b6914;
                border-bottom: none;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                color: #f4d03f;
            }
            
            /* ========== دکمه‌ها ========== */
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2980b9, stop: 1 #1a5276);
                color: white;
                border: 2px solid #1a5276;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 12px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border: 2px solid #3498db;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1a5276, stop: 1 #154360);
                padding-top: 14px;
                padding-bottom: 10px;
            }
            
            QPushButton#exit_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #922b21);
                border: 2px solid #922b21;
                color: white;
            }
            
            QPushButton#exit_btn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            
            QPushButton#refresh_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #1e8449);
                border: 2px solid #1e8449;
                color: white;
            }
            
            QPushButton#refresh_btn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71, stop: 1 #27ae60);
            }
            
            QPushButton#golden_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 0.5 #d4af6a, stop: 1 #b8944a);
                border: 2px solid #8b6914;
                color: #1a252f;
                font-weight: bold;
            }
            
            QPushButton#golden_btn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d4af6a, stop: 0.5 #deb974, stop: 1 #c8a45c);
            }
            
            /* ========== گروه‌ها ========== */
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #c8a45c;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                background: rgba(255, 255, 255, 0.9);
                color: #2c3e50;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 1 #b8944a);
                color: #1a252f;
                border-radius: 8px;
                font-size: 12px;
            }
            
            /* ========== فیلدهای ورودی ========== */
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
            }
            
            QLineEdit:focus {
                border: 2px solid #c8a45c;
                background-color: #fef9e7;
            }
            
            QSpinBox, QDoubleSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #c8a45c;
                background-color: #fef9e7;
            }
            
            /* ========== جداول ========== */
            QTableWidget {
                border: 2px solid #c8a45c;
                border-radius: 10px;
                gridline-color: #e8d5b7;
                background-color: white;
                alternate-background-color: #fef9e7;
                selection-background-color: #c8a45c;
                selection-color: #1a252f;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
                color: #c8a45c;
                padding: 10px;
                border: 1px solid #8b6914;
                font-weight: bold;
                font-size: 11px;
            }
            
            /* ========== لیبل‌ها ========== */
            QLabel {
                color: #2c3e50;
            }
            
            /* ========== نوار وضعیت ========== */
            QStatusBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
                color: #c8a45c;
                border-top: 2px solid #c8a45c;
                font-weight: bold;
                padding: 5px;
            }
            
            /* ========== اسکرول بار ========== */
            QScrollBar:vertical {
                border: none;
                background: #fef9e7;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #c8a45c;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #b8944a;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* ========== کامبوباکس ========== */
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            
            QComboBox:focus {
                border: 2px solid #c8a45c;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #c8a45c;
                margin-right: 5px;
            }
        """)
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🏢 سیستم مدیریت پارکینگ - پلاک ایرانی")
        self.setGeometry(100, 100, 1400, 800)
        
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # هدر با طراحی ایرانی
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a252f, stop: 0.3 #c8a45c, stop: 0.5 #d4af6a, 
                    stop: 0.7 #c8a45c, stop: 1 #1a252f);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        # لوگو یا آیکون
        logo_label = QLabel("🅿️")
        logo_label.setStyleSheet("font-size: 40px; background: transparent;")
        
        # عنوان
        title_label = QLabel("سیستم مدیریت هوشمند پارکینگ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #1a252f;
            background: transparent;
            font-family: 'Tahoma', 'B Nazanin';
        """)
        
        # تاریخ و ساعت
        self.datetime_label = QLabel(datetime.now().strftime("%Y/%m/%d - %H:%M:%S"))
        self.datetime_label.setStyleSheet("""
            font-size: 14px;
            color: #1a252f;
            background: transparent;
            font-weight: bold;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.datetime_label)
        
        main_layout.addWidget(header_widget)
        
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
        
        # تایمر برای بروزرسانی زمان
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_datetime)
        self.clock_timer.start(1000)
    
    def update_datetime(self):
        """بروزرسانی تاریخ و ساعت"""
        self.datetime_label.setText(datetime.now().strftime("%Y/%m/%d - %H:%M:%S"))
    
    def create_entry_exit_tab(self):
        """تب ورود و خروج خودرو با فیلدهای چند بخشی پلاک"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # گروه ورود
        entry_group = QGroupBox("ثبت ورود خودرو")
        entry_layout = QVBoxLayout()
        
        # ویجت پلاک ایرانی
        plate_label = QLabel("پلاک خودرو:")
        plate_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.entry_plate_widget = IranianPlateWidget()
        
        # دکمه ورود
        entry_btn = QPushButton("🚗 ثبت ورود خودرو")
        entry_btn.setObjectName("golden_btn")
        entry_btn.clicked.connect(self.car_entry)
        entry_btn.setMinimumHeight(50)
        
        entry_layout.addWidget(plate_label)
        entry_layout.addWidget(self.entry_plate_widget)
        entry_layout.addWidget(entry_btn)
        entry_group.setLayout(entry_layout)
        layout.addWidget(entry_group)
        
        # نمونه پلاک‌های معتبر
        examples_group = QGroupBox("نمونه پلاک‌های معتبر ایران")
        examples_layout = QGridLayout()
        examples_layout.setSpacing(10)
        
        examples = [
            ("شخصی:", "۱۲ الف ۳۴۵ ایران ۱۱", "#3498db"),
            ("تاکسی:", "۱۲ ت ۳۴۵ ایران ۱۱", "#e67e22"),
            ("دولتی:", "۱۲ الف ۳۴۵ ایران ۱", "#27ae60"),
            ("نظامی:", "۱۲۳ الف ۴۵ ایران ۱۱", "#e74c3c"),
            ("سیاسی:", "۱۲ د ۳۴۵ ایران ۱۱", "#8e44ad")
        ]
        
        for i, (label, example, color) in enumerate(examples):
            example_widget = QFrame()
            example_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}15;
                    border: 1px solid {color};
                    border-radius: 8px;
                    padding: 5px;
                }}
            """)
            example_layout = QHBoxLayout(example_widget)
            
            type_label = QLabel(f"<b style='color: {color}'>{label}</b>")
            type_label.setStyleSheet("font-size: 11px;")
            
            plate_example = QLabel(example)
            plate_example.setStyleSheet(f"""
                font-size: 12px; 
                font-weight: bold; 
                color: {color};
                font-family: 'Tahoma', 'B Nazanin';
            """)
            
            example_layout.addWidget(type_label)
            example_layout.addWidget(plate_example)
            example_layout.addStretch()
            
            examples_layout.addWidget(example_widget, i // 2, i % 2)
        
        examples_group.setLayout(examples_layout)
        layout.addWidget(examples_group)
        
        # گروه خروج
        exit_group = QGroupBox("ثبت خروج خودرو و محاسبه هزینه")
        exit_layout = QVBoxLayout()
        
        exit_plate_label = QLabel("پلاک خودرو:")
        exit_plate_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.exit_plate_widget = IranianPlateWidget()
        
        exit_btn = QPushButton("💰 محاسبه هزینه و ثبت خروج")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self.car_exit)
        exit_btn.setMinimumHeight(50)
        
        exit_layout.addWidget(exit_plate_label)
        exit_layout.addWidget(self.exit_plate_widget)
        exit_layout.addWidget(exit_btn)
        exit_group.setLayout(exit_layout)
        layout.addWidget(exit_group)
        
        # نمایش اطلاعات خروج
        self.exit_info_frame = QFrame()
        self.exit_info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #fef9e7, stop: 1 #fdebd0);
                border: 2px solid #c8a45c;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        exit_info_layout = QVBoxLayout(self.exit_info_frame)
        
        self.exit_info_label = QLabel("اطلاعات خروج خودرو در اینجا نمایش داده می‌شود")
        self.exit_info_label.setFont(QFont("Tahoma", 12))
        self.exit_info_label.setAlignment(Qt.AlignCenter)
        self.exit_info_label.setStyleSheet("color: #2c3e50; background: transparent;")
        self.exit_info_label.setWordWrap(True)
        
        exit_info_layout.addWidget(self.exit_info_label)
        layout.addWidget(self.exit_info_frame)
        
        return widget
    
    def create_active_tab(self):
        """تب نمایش خودروهای حاضر"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی لیست")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_active_cars)
        
        count_label = QLabel("تعداد خودروهای حاضر: ۰")
        count_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        self.active_count_label = count_label
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(count_label)
        layout.addLayout(btn_layout)
        
        # جدول خودروهای حاضر
        self.active_table = QTableWidget()
        self.active_table.setColumnCount(7)
        self.active_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک کامل", "نوع پلاک", "استان", "زمان ورود", "مدت حضور", "هزینه تقریبی"
        ])
        self.active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.active_table.setAlternatingRowColors(True)
        layout.addWidget(self.active_table)
        
        self.refresh_active_cars()
        return widget
    
    def create_history_tab(self):
        """تب تاریخچه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی تاریخچه")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_history)
        
        clear_btn = QPushButton("🗑️ پاک کردن تاریخچه")
        clear_btn.setObjectName("exit_btn")
        clear_btn.clicked.connect(self.clear_history)
        
        export_btn = QPushButton("📥 خروجی اکسل")
        export_btn.setObjectName("golden_btn")
        export_btn.clicked.connect(self.export_to_excel)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        # جدول تاریخچه
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "نوع", "استان", "زمان ورود", "زمان خروج", 
            "مدت (ساعت)", "هزینه (تومان)", "تخفیف"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        # آمار
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_frame)
        
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Tahoma", 11))
        self.stats_label.setStyleSheet("color: #c8a45c; background: transparent;")
        self.stats_label.setWordWrap(True)
        
        stats_layout.addWidget(self.stats_label)
        layout.addWidget(self.stats_frame)
        
        self.refresh_history()
        return widget
    
    def create_settings_tab(self):
        """تب تنظیمات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # تنظیمات نرخ
        rate_group = QGroupBox("⚙️ تنظیمات نرخ پارکینگ")
        rate_layout = QFormLayout()
        rate_layout.setSpacing(10)
        
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(1000, 1000000)
        self.rate_input.setValue(self.parking_system.hourly_rate)
        self.rate_input.setPrefix("تومان ")
        self.rate_input.setFont(QFont("Tahoma", 12))
        self.rate_input.setMinimumHeight(40)
        
        save_rate_btn = QPushButton("💾 ذخیره نرخ جدید")
        save_rate_btn.setObjectName("golden_btn")
        save_rate_btn.clicked.connect(self.save_rate)
        save_rate_btn.setMinimumHeight(45)
        
        rate_layout.addRow("نرخ هر ساعت:", self.rate_input)
        rate_layout.addRow("", save_rate_btn)
        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)
        
        # تخفیف‌ها
        discount_group = QGroupBox("🎁 تخفیف‌های ویژه")
        discount_layout = QVBoxLayout()
        
        discounts = [
            ("🚕 تاکسی‌ها", "۳۰٪ تخفیف خودکار", "#e67e22"),
            ("🏛️ خودروهای دولتی", "۳۰٪ تخفیف خودکار", "#27ae60"),
            ("⏱️ توقف زیر ۱۵ دقیقه", "رایگان", "#3498db"),
        ]
        
        for icon_text, desc, color in discounts:
            discount_frame = QFrame()
            discount_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}15;
                    border: 1px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            discount_item_layout = QHBoxLayout(discount_frame)
            
            icon_label = QLabel(icon_text)
            icon_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color}; background: transparent;")
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"font-size: 12px; color: {color}; background: transparent;")
            
            discount_item_layout.addWidget(icon_label)
            discount_item_layout.addWidget(desc_label)
            discount_item_layout.addStretch()
            
            discount_layout.addWidget(discount_frame)
        
        discount_group.setLayout(discount_layout)
        layout.addWidget(discount_group)
        
        # درباره برنامه
        about_group = QGroupBox("📋 درباره نرم‌افزار")
        about_layout = QVBoxLayout()
        
        about_text = QLabel("""
        <div style='text-align: center; line-height: 1.8;'>
        <h3 style='color: #c8a45c;'>🏢 سیستم مدیریت پارکینگ</h3>
        <p style='color: #2c3e50;'>
        <b>نسخه ۲.۰</b> - پشتیبانی کامل از پلاک‌های ایرانی<br>
        طراحی شده با استانداردهای روز و رابط کاربری فارسی<br>
        <br>
        ✨ <b>ویژگی‌ها:</b><br>
        • اعتبارسنجی پیشرفته پلاک‌های ایرانی<br>
        • ورود پلاک به صورت بخش‌بندی شده<br>
        • تشخیص خودکار نوع پلاک و استان<br>
        • تخفیف هوشمند برای خودروهای عمومی<br>
        • گزارش‌گیری کامل با قابلیت خروجی<br>
        • رابط کاربری زیبا و کاربرپسند
        </p>
        </div>
        """)
        about_text.setStyleSheet("background: transparent;")
        about_text.setWordWrap(True)
        
        about_layout.addWidget(about_text)
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        return widget
    
    def car_entry(self):
        """ثبت ورود خودرو"""
        plate = self.entry_plate_widget.get_plate()
        if not plate:
            QMessageBox.warning(self, "خطا", "لطفاً تمام بخش‌های پلاک را وارد کنید!")
            return
        
        success, message = self.parking_system.car_entry(plate)
        if success:
            QMessageBox.information(self, "موفق", message)
            self.entry_plate_widget.clear()
            self.refresh_active_cars()
            self.update_status()
        else:
            QMessageBox.warning(self, "خطا", message)
    
    def car_exit(self):
        """ثبت خروج خودرو و محاسبه هزینه"""
        plate = self.exit_plate_widget.get_plate()
        if not plate:
            QMessageBox.warning(self, "خطا", "لطفاً تمام بخش‌های پلاک را وارد کنید!")
            return
        
        record, message = self.parking_system.car_exit(plate)
        if record:
            type_names = {
                'personal': 'شخصی',
                'taxi': 'تاکسی',
                'governmental': 'دولتی',
                'military': 'نظامی',
                'diplomatic': 'سیاسی'
            }
            
            info_text = f"""
            <div style='text-align: center; line-height: 2;'>
            <span style='font-size: 16px; font-weight: bold; color: #c8a45c;'>
            🚗 اطلاعات خروج خودرو
            </span><br>
            <b>پلاک:</b> {IranianPlateValidator.format_plate_display(record['plate'])}<br>
            <b>نوع:</b> {type_names.get(record['plate_type'], 'نامشخص')}<br>
            <b>استان:</b> {record['province']}<br>
            <b>زمان ورود:</b> {datetime.fromisoformat(record['entry_time']).strftime('%H:%M:%S')}<br>
            <b>زمان خروج:</b> {datetime.fromisoformat(record['exit_time']).strftime('%H:%M:%S')}<br>
            <b>مدت توقف:</b> {record['duration_hours']:.2f} ساعت<br>
            <span style='font-size: 16px; font-weight: bold; color: #e74c3c;'>
            💰 هزینه قابل پرداخت: {record['cost']:,.0f} تومان{record.get('discount', '')}
            </span>
            </div>
            """
            self.exit_info_label.setText(info_text)
            self.exit_plate_widget.clear()
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
        
        self.active_count_label.setText(f"تعداد خودروهای حاضر: {len(active_cars)}")
        
        for i, (plate, car_info) in enumerate(active_cars.items()):
            entry_time = datetime.fromisoformat(car_info['entry_time'])
            duration = datetime.now() - entry_time
            hours = duration.total_seconds() / 3600
            
            # محاسبه هزینه تقریبی
            if hours > 0.25:
                est_cost = max(1, int(hours + 0.99)) * self.parking_system.hourly_rate
                if car_info['plate_type'] in ['taxi', 'governmental']:
                    est_cost *= 0.7
            else:
                est_cost = 0
            
            self.active_table.insertRow(i)
            self.active_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            # نمایش پلاک با فرمت زیبا
            plate_display = IranianPlateValidator.format_plate_display(plate)
            plate_item = QTableWidgetItem(plate_display)
            plate_item.setFont(QFont("Tahoma", 10, QFont.Bold))
            self.active_table.setItem(i, 1, plate_item)
            
            self.active_table.setItem(i, 2, QTableWidgetItem(type_names.get(car_info['plate_type'], 'نامشخص')))
            self.active_table.setItem(i, 3, QTableWidgetItem(car_info.get('province', 'نامشخص')))
            self.active_table.setItem(i, 4, QTableWidgetItem(entry_time.strftime('%H:%M:%S')))
            self.active_table.setItem(i, 5, QTableWidgetItem(f"{hours:.1f} ساعت"))
            self.active_table.setItem(i, 6, QTableWidgetItem(f"{est_cost:,.0f}" if est_cost > 0 else "رایگان"))
            
            # رنگ‌آمیزی بر اساس مدت زمان
            if hours > 5:
                color = QColor("#fadbd8")  # قرمز کم‌رنگ
            elif hours > 3:
                color = QColor("#fef9e7")  # طلایی کم‌رنگ
            else:
                color = QColor("#e8f8f5")  # سبز کم‌رنگ
            
            for col in range(7):
                self.active_table.item(i, col).setBackground(color)
    
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
        today = datetime.now().strftime('%Y-%m-%d')
        today_income = 0
        today_count = 0
        
        for i, record in enumerate(reversed(history)):
            entry_time = datetime.fromisoformat(record['entry_time'])
            exit_time = datetime.fromisoformat(record['exit_time'])
            
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            plate_display = IranianPlateValidator.format_plate_display(record['plate'])
            plate_item = QTableWidgetItem(plate_display)
            plate_item.setFont(QFont("Tahoma", 10, QFont.Bold))
            self.history_table.setItem(i, 1, plate_item)
            
            self.history_table.setItem(i, 2, QTableWidgetItem(type_names.get(record.get('plate_type', 'personal'), 'شخصی')))
            self.history_table.setItem(i, 3, QTableWidgetItem(record.get('province', 'نامشخص')))
            self.history_table.setItem(i, 4, QTableWidgetItem(entry_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 5, QTableWidgetItem(exit_time.strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 6, QTableWidgetItem(f"{record['duration_hours']:.1f}"))
            
            cost_text = f"{record['cost']:,.0f}"
            self.history_table.setItem(i, 7, QTableWidgetItem(cost_text))
            
            discount_text = "⭐ دارد" if record.get('discount') else "—"
            self.history_table.setItem(i, 8, QTableWidgetItem(discount_text))
            
            total_income += record['cost']
            
            if record['entry_time'].startswith(today):
                today_income += record['cost']
                today_count += 1
        
        # آمار
        plate_types_count = {}
        for r in history:
            if r['entry_time'].startswith(today):
                ptype = r.get('plate_type', 'personal')
                plate_types_count[ptype] = plate_types_count.get(ptype, 0) + 1
        
        types_str = " | ".join([f"{type_names.get(k, k)}: {v}" for k, v in plate_types_count.items()])
        
        stats_html = f"""
        <div style='text-align: center;'>
        <b style='font-size: 14px;'>📊 آمار امروز ({today})</b><br>
        🚗 تعداد خودرو: <b>{today_count}</b> | {types_str}<br>
        💰 درآمد امروز: <b style='color: #2ecc71;'>{today_income:,.0f} تومان</b> | 
        💰 کل درآمد: <b style='color: #c8a45c;'>{total_income:,.0f} تومان</b>
        </div>
        """
        self.stats_label.setText(stats_html)
    
    def save_rate(self):
        """ذخیره نرخ جدید"""
        new_rate = self.rate_input.value()
        self.parking_system.hourly_rate = new_rate
        QMessageBox.information(self, "موفق", f"نرخ ساعتی به {new_rate:,.0f} تومان تغییر کرد")
    
    def clear_history(self):
        """پاک کردن تاریخچه"""
        reply = QMessageBox.question(
            self, "تأیید", 
            "آیا از پاک کردن تمام تاریخچه اطمینان دارید؟\nاین عمل قابل بازگشت نیست!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.parking_system.parking_history.clear()
            self.parking_system.save_data()
            self.refresh_history()
            QMessageBox.information(self, "موفق", "تاریخچه با موفقیت پاک شد")
    
    def export_to_excel(self):
        """خروجی اکسل (نمونه)"""
        QMessageBox.information(self, "خروجی", "قابلیت خروجی اکسل در نسخه‌های بعدی اضافه خواهد شد")
    
    def update_status(self):
        """بروزرسانی نوار وضعیت"""
        active_count = len(self.parking_system.active_cars)
        total_history = len(self.parking_system.parking_history)
        
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
        self.timer.start(60000)
    
    def auto_refresh(self):
        """بروزرسانی خودکار"""
        if self.tab_widget.currentIndex() == 1:
            self.refresh_active_cars()
        self.update_status()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 9))
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = ParkingManagementApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()