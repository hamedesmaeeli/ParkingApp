import sys
import json
import os
import re
import cv2
import pytesseract
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QGroupBox, QFormLayout, QHeaderView,
    QSpinBox, QDoubleSpinBox, QStatusBar, QFrame, QGridLayout,
    QSplitter, QComboBox, QDialog, QDialogButtonBox, QSlider,
    QCheckBox, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QSize, QRect, QDateTime
)
from PyQt5.QtGui import (
    QFont, QIcon, QColor, QPalette, QImage, QPixmap, QPainter,
    QPen, QBrush, QFontDatabase
)

# تنظیم مسیر Tesseract (در ویندوز)
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class IranianPlateValidator:
    """اعتبارسنجی پلاک‌های ایرانی"""
    
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
    def validate_plate_parts(cls, part1, letter, part2, part3=""):
        if not part1 or not letter or not part2:
            return False, "همه بخش‌ها باید پر شوند"
        
        if not part1.isdigit() or len(part1) != 2:
            return False, "بخش اول باید ۲ رقم باشد"
        
        if not part2.isdigit() or len(part2) != 3:
            return False, "بخش سوم باید ۳ رقم باشد"
        
        if letter not in cls.VALID_LETTERS:
            return False, "حرف پلاک نامعتبر است"
        
        if part3 and not part3.isdigit():
            return False, "کد استان باید عددی باشد"
        
        return True, ""
    
    @classmethod
    def create_full_plate(cls, part1, letter, part2, part3=""):
        if part3:
            return f"{part1}{letter}{part2}-{part3}"
        return f"{part1}{letter}{part2}"
    
    @classmethod
    def parse_plate_to_parts(cls, full_plate):
        if not full_plate:
            return {"part1": "", "letter": "", "part2": "", "part3": ""}
        
        plate = full_plate.strip().replace(' ', '')
        
        if '-' in plate:
            main_part, province = plate.split('-')
        else:
            main_part = plate
            province = ""
        
        if len(main_part) == 5:
            return {
                "part1": main_part[:2],
                "letter": main_part[2],
                "part2": main_part[3:],
                "part3": province
            }
        elif len(main_part) == 6:
            return {
                "part1": main_part[:3],
                "letter": main_part[3],
                "part2": main_part[4:],
                "part3": province
            }
        
        return {"part1": "", "letter": "", "part2": "", "part3": ""}
    
    @classmethod
    def get_plate_type(cls, letter, part3=""):
        if letter == 'ت':
            return 'taxi'
        elif letter == 'د':
            return 'diplomatic'
        elif len(part3) == 1:
            return 'governmental'
        return 'personal'
    
    @classmethod
    def get_province_name(cls, part3):
        if part3 in cls.PROVINCE_CODES:
            return cls.PROVINCE_CODES[part3]
        elif len(part3) == 1:
            return "دولتی"
        return "نامشخص"
    
    @classmethod
    def format_parts_for_display(cls, parts):
        if not parts["part1"] or not parts["letter"] or not parts["part2"]:
            return ""
        display = f"{parts['part1']} | {parts['letter']} | {parts['part2']}"
        if parts["part3"]:
            display += f"  ایران  {parts['part3']}"
        return display
    
    @classmethod
    def clean_ocr_text(cls, text):
        """پاکسازی متن OCR برای پلاک ایرانی"""
        # حذف کاراکترهای اضافی
        text = re.sub(r'[^\dآ-ی]', '', text)
        
        # تصحیح حروف مشابه
        replacements = {
            'ب': 'ب', 'پ': 'پ', 'ت': 'ت', 'ث': 'ث',
            'ج': 'ج', 'چ': 'چ', 'ح': 'ح', 'خ': 'خ',
            'د': 'د', 'ذ': 'ذ', 'ر': 'ر', 'ز': 'ز',
            'س': 'س', 'ش': 'ش', 'ص': 'ص', 'ض': 'ض',
            'ط': 'ط', 'ظ': 'ظ', 'ع': 'ع', 'غ': 'غ',
            'ف': 'ف', 'ق': 'ق', 'ک': 'ک', 'گ': 'گ',
            'ل': 'ل', 'م': 'م', 'ن': 'ن', 'و': 'و',
            'ه': 'ه', 'ی': 'ی', 'ا': 'الف'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text


class IranianPlateDisplay(QFrame):
    """ویجت نمایش پلاک به صورت گرافیکی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMaximumHeight(70)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            IranianPlateDisplay {
                background-color: #1a3a6b;
                border: 3px solid #c8a45c;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(0)
        
        left_frame = QFrame()
        left_frame.setStyleSheet("background: transparent; border: none;")
        left_layout = QHBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        plate_style = """
            color: white;
            font-size: 22px;
            font-weight: bold;
            font-family: 'Tahoma', 'B Nazanin';
            background: transparent;
            padding: 0 5px;
        """
        
        self.part1_label = QLabel("۱۲")
        self.part1_label.setStyleSheet(plate_style)
        self.part1_label.setAlignment(Qt.AlignCenter)
        
        self.letter_label = QLabel("الف")
        self.letter_label.setStyleSheet(plate_style)
        self.letter_label.setAlignment(Qt.AlignCenter)
        
        self.part2_label = QLabel("۳۴۵")
        self.part2_label.setStyleSheet(plate_style)
        self.part2_label.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(self.part1_label)
        left_layout.addWidget(self.letter_label)
        left_layout.addWidget(self.part2_label)
        
        iran_frame = QFrame()
        iran_frame.setStyleSheet("""
            QFrame {
                background-color: #e74c3c;
                border: 2px solid white;
                border-radius: 5px;
                margin: 0 10px;
            }
        """)
        iran_layout = QVBoxLayout(iran_frame)
        iran_layout.setContentsMargins(5, 2, 5, 2)
        
        iran_label = QLabel("ایران")
        iran_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold; background: transparent;")
        iran_label.setAlignment(Qt.AlignCenter)
        iran_layout.addWidget(iran_label)
        
        self.province_label = QLabel("۱۱")
        self.province_label.setStyleSheet(plate_style)
        self.province_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(left_frame)
        main_layout.addStretch()
        main_layout.addWidget(iran_frame)
        main_layout.addStretch()
        main_layout.addWidget(self.province_label)
    
    def set_plate_parts(self, part1, letter, part2, part3):
        self.part1_label.setText(part1)
        self.letter_label.setText(letter)
        self.part2_label.setText(part2)
        self.province_label.setText(part3 if part3 else "")
    
    def set_full_plate(self, full_plate):
        parts = IranianPlateValidator.parse_plate_to_parts(full_plate)
        self.set_plate_parts(parts["part1"], parts["letter"], parts["part2"], parts["part3"])


class IranianPlateWidget(QWidget):
    """ویجت ورود پلاک ایرانی"""
    
    plate_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plate_parts = {"part1": "", "letter": "", "part2": "", "part3": ""}
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(8)
        
        field_style = """
            QLineEdit {
                font-size: 16px;
                font-weight: bold;
                font-family: 'Tahoma', 'B Nazanin';
                text-align: center;
                border: 2px solid #c8a45c;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #2980b9;
                background-color: #ebf5fb;
            }
        """
        
        # بخش‌های پلاک
        label1 = QLabel("دو رقم:")
        label1.setStyleSheet("font-size: 10px; color: #7f8c8d; font-weight: bold;")
        self.part1_input = QLineEdit()
        self.part1_input.setPlaceholderText("۱۲")
        self.part1_input.setMaxLength(2)
        self.part1_input.setFixedWidth(70)
        self.part1_input.setAlignment(Qt.AlignCenter)
        self.part1_input.setStyleSheet(field_style)
        self.part1_input.textChanged.connect(self.on_part1_changed)
        
        sep1 = QLabel("|")
        sep1.setStyleSheet("font-size: 20px; color: #c8a45c; font-weight: bold;")
        
        label2 = QLabel("حرف:")
        label2.setStyleSheet("font-size: 10px; color: #7f8c8d; font-weight: bold;")
        self.letter_input = QLineEdit()
        self.letter_input.setPlaceholderText("الف")
        self.letter_input.setMaxLength(1)
        self.letter_input.setFixedWidth(70)
        self.letter_input.setAlignment(Qt.AlignCenter)
        self.letter_input.setStyleSheet(field_style)
        self.letter_input.textChanged.connect(self.on_letter_changed)
        
        sep2 = QLabel("|")
        sep2.setStyleSheet("font-size: 20px; color: #c8a45c; font-weight: bold;")
        
        label3 = QLabel("سه رقم:")
        label3.setStyleSheet("font-size: 10px; color: #7f8c8d; font-weight: bold;")
        self.part2_input = QLineEdit()
        self.part2_input.setPlaceholderText("۳۴۵")
        self.part2_input.setMaxLength(3)
        self.part2_input.setFixedWidth(80)
        self.part2_input.setAlignment(Qt.AlignCenter)
        self.part2_input.setStyleSheet(field_style)
        self.part2_input.textChanged.connect(self.on_part2_changed)
        
        iran_label = QLabel("ایران")
        iran_label.setStyleSheet("""
            font-size: 11px; 
            color: white;
            font-weight: bold;
            background-color: #e74c3c;
            border: 1px solid #c0392b;
            border-radius: 5px;
            padding: 8px 5px;
        """)
        iran_label.setFixedWidth(45)
        iran_label.setAlignment(Qt.AlignCenter)
        
        label4 = QLabel("کد استان:")
        label4.setStyleSheet("font-size: 10px; color: #7f8c8d; font-weight: bold;")
        self.part3_input = QLineEdit()
        self.part3_input.setPlaceholderText("۱۱")
        self.part3_input.setMaxLength(2)
        self.part3_input.setFixedWidth(70)
        self.part3_input.setAlignment(Qt.AlignCenter)
        self.part3_input.setStyleSheet(field_style)
        self.part3_input.textChanged.connect(self.on_plate_changed)
        
        input_layout.addWidget(label1)
        input_layout.addWidget(self.part1_input)
        input_layout.addWidget(sep1)
        input_layout.addWidget(label2)
        input_layout.addWidget(self.letter_input)
        input_layout.addWidget(sep2)
        input_layout.addWidget(label3)
        input_layout.addWidget(self.part2_input)
        input_layout.addWidget(iran_label)
        input_layout.addWidget(label4)
        input_layout.addWidget(self.part3_input)
        input_layout.addStretch()
        
        main_layout.addWidget(input_frame)
        
        # نمایش پلاک
        self.plate_display = IranianPlateDisplay()
        main_layout.addWidget(self.plate_display)
        
        # اعتبارسنجی
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("font-size: 10px; color: #e74c3c;")
        self.validation_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.validation_label)
    
    def on_part1_changed(self, text):
        if len(text) == 2:
            self.letter_input.setFocus()
        self.on_plate_changed()
    
    def on_letter_changed(self, text):
        if text:
            persian_map = {
                'a': 'الف', 'b': 'ب', 'p': 'پ', 't': 'ت', 's': 'ث',
                'j': 'ج', 'h': 'ح', 'k': 'خ', 'd': 'د', 'z': 'ذ',
                'r': 'ر', 'm': 'م', 'n': 'ن', 'v': 'و', 'y': 'ی'
            }
            if text.lower() in persian_map:
                self.letter_input.setText(persian_map[text.lower()])
                self.part2_input.setFocus()
        self.on_plate_changed()
    
    def on_part2_changed(self, text):
        if len(text) == 3:
            self.part3_input.setFocus()
        self.on_plate_changed()
    
    def on_plate_changed(self):
        self.current_plate_parts = {
            "part1": self.part1_input.text().strip(),
            "letter": self.letter_input.text().strip(),
            "part2": self.part2_input.text().strip(),
            "part3": self.part3_input.text().strip()
        }
        
        if self.current_plate_parts["part1"] and self.current_plate_parts["letter"] and self.current_plate_parts["part2"]:
            self.plate_display.set_plate_parts(
                self.current_plate_parts["part1"],
                self.current_plate_parts["letter"],
                self.current_plate_parts["part2"],
                self.current_plate_parts["part3"]
            )
        
        is_valid, message = IranianPlateValidator.validate_plate_parts(
            self.current_plate_parts["part1"],
            self.current_plate_parts["letter"],
            self.current_plate_parts["part2"],
            self.current_plate_parts["part3"]
        )
        
        if self.current_plate_parts["part1"] or self.current_plate_parts["letter"] or self.current_plate_parts["part2"]:
            if is_valid:
                self.validation_label.setText("✅ پلاک معتبر است")
                self.validation_label.setStyleSheet("font-size: 10px; color: #27ae60; font-weight: bold;")
            else:
                self.validation_label.setText(f"❌ {message}")
                self.validation_label.setStyleSheet("font-size: 10px; color: #e74c3c;")
        else:
            self.validation_label.setText("")
        
        self.plate_changed.emit(self.current_plate_parts)
    
    def get_plate(self):
        return IranianPlateValidator.create_full_plate(
            self.current_plate_parts["part1"],
            self.current_plate_parts["letter"],
            self.current_plate_parts["part2"],
            self.current_plate_parts["part3"]
        )
    
    def get_plate_parts(self):
        return self.current_plate_parts
    
    def clear(self):
        self.part1_input.clear()
        self.letter_input.clear()
        self.part2_input.clear()
        self.part3_input.clear()
        self.part1_input.setFocus()
    
    def set_plate_parts(self, part1, letter, part2, part3=""):
        self.part1_input.setText(part1)
        self.letter_input.setText(letter)
        self.part2_input.setText(part2)
        self.part3_input.setText(part3)
    
    def is_valid(self):
        is_valid, _ = IranianPlateValidator.validate_plate_parts(
            self.current_plate_parts["part1"],
            self.current_plate_parts["letter"],
            self.current_plate_parts["part2"],
            self.current_plate_parts["part3"]
        )
        return is_valid and bool(self.get_plate())


class PlateDetector:
    """سیستم تشخیص پلاک با OpenCV و Tesseract"""
    
    def __init__(self):
        self.plate_cascade = None
        self.load_cascade()
    
    def load_cascade(self):
        """بارگذاری cascade classifier"""
        # می‌توانید از مدل‌های آموزش‌دیده استفاده کنید
        cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
        if os.path.exists(cascade_path):
            self.plate_cascade = cv2.CascadeClassifier(cascade_path)
    
    def detect_plate_region(self, image):
        """تشخیص ناحیه پلاک در تصویر"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # کاهش نویز
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # تشخیص لبه‌ها
        edges = cv2.Canny(gray, 50, 150)
        
        # پیدا کردن کانتورها
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        plate_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000:  # فیلتر نواحی کوچک
                continue
            
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4:  # مستطیل
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                
                # نسبت ابعاد پلاک ایرانی تقریباً 3:1 است
                if 2.5 < aspect_ratio < 5:
                    plate_regions.append((x, y, w, h))
        
        # اگر cascade موجود باشد
        if self.plate_cascade:
            plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in plates:
                plate_regions.append((x, y, w, h))
        
        return plate_regions
    
    def preprocess_plate(self, plate_img):
        """پیش‌پردازش تصویر پلاک برای OCR"""
        # تبدیل به grayscale
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # افزایش کنتراست
        gray = cv2.equalizeHist(gray)
        
        # کاهش نویز
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # آستانه‌گذاری تطبیقی
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # عملیات مورفولوژیک برای حذف نویز
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def recognize_plate(self, image):
        """تشخیص و خواندن پلاک از تصویر"""
        plate_regions = self.detect_plate_region(image)
        
        results = []
        for (x, y, w, h) in plate_regions:
            # استخراج ناحیه پلاک
            plate_img = image[y:y+h, x:x+w]
            
            # پیش‌پردازش
            processed = self.preprocess_plate(plate_img)
            
            # OCR با Tesseract
            # تنظیمات برای پلاک ایرانی
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789آابپتثجچحخدذرزسشصضطظعغفقکگلمنوهی'
            
            try:
                text = pytesseract.image_to_string(
                    processed, 
                    lang='fas+eng',  # فارسی و انگلیسی
                    config=custom_config
                )
            except:
                text = pytesseract.image_to_string(
                    processed,
                    config=custom_config
                )
            
            text = IranianPlateValidator.clean_ocr_text(text)
            
            if len(text) >= 7:
                results.append({
                    'text': text,
                    'bbox': (x, y, w, h),
                    'confidence': 0.8  # می‌توانید confidence واقعی را محاسبه کنید
                })
        
        return results


class CameraThread(QThread):
    """thread دوربین برای پردازش زنده"""
    
    frame_captured = pyqtSignal(np.ndarray)
    plate_detected = pyqtSignal(str, float)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.capture = None
        self.detector = PlateDetector()
        self.detect_plate = True
        self.save_frame = False
        self.save_path = "captured_plates"
        
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    def run(self):
        self.running = True
        self.capture = cv2.VideoCapture(0)  # دوربین پیش‌فرض
        
        if not self.capture.isOpened():
            print("خطا در باز کردن دوربین")
            return
        
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                break
            
            # انتشار فریم برای نمایش
            self.frame_captured.emit(frame.copy())
            
            # تشخیص پلاک
            if self.detect_plate:
                results = self.detector.recognize_plate(frame)
                
                for result in results:
                    text = result['text']
                    confidence = result['confidence']
                    bbox = result['bbox']
                    
                    # رسم مستطیل دور پلاک
                    x, y, w, h = bbox
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # ارسال پلاک شناسایی شده
                    self.plate_detected.emit(text, confidence)
                    
                    # ذخیره تصویر
                    if self.save_frame:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{self.save_path}/plate_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
            
            # کوچک کردن فریم برای نمایش
            display_frame = cv2.resize(frame, (640, 480))
            self.frame_captured.emit(display_frame)
            
            self.msleep(100)  # 10 FPS
    
    def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
        self.wait()


class CameraWidget(QWidget):
    """ویجت نمایش دوربین"""
    
    plate_detected_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_thread = None
        self.current_frame = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # نمایش دوربین
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #c8a45c;
                border-radius: 10px;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("📷 دوربین غیرفعال است\nبرای شروع کلیک کنید")
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #c8a45c;
                border: 2px solid #c8a45c;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.camera_label)
        
        # کنترل‌ها
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        
        self.start_btn = QPushButton("🎥 شروع دوربین")
        self.start_btn.setObjectName("refresh_btn")
        self.start_btn.clicked.connect(self.start_camera)
        
        self.stop_btn = QPushButton("⏹️ توقف دوربین")
        self.stop_btn.setObjectName("exit_btn")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        
        self.capture_btn = QPushButton("📸 ثبت تصویر")
        self.capture_btn.setObjectName("golden_btn")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        
        self.auto_detect_cb = QCheckBox("تشخیص خودکار پلاک")
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.setStyleSheet("color: white; font-weight: bold;")
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.capture_btn)
        controls_layout.addWidget(self.auto_detect_cb)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        
        # نوار پیشرفت تشخیص
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def start_camera(self):
        """شروع دوربین"""
        if self.camera_thread and self.camera_thread.isRunning():
            return
        
        self.camera_thread = CameraThread()
        self.camera_thread.frame_captured.connect(self.update_frame)
        self.camera_thread.plate_detected.connect(self.on_plate_detected)
        self.camera_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.capture_btn.setEnabled(True)
        
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #c8a45c;
                border-radius: 10px;
            }
        """)
    
    def stop_camera(self):
        """توقف دوربین"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
        
        self.camera_label.clear()
        self.camera_label.setText("📷 دوربین غیرفعال است\nبرای شروع کلیک کنید")
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #c8a45c;
                border: 2px solid #c8a45c;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
    
    def update_frame(self, frame):
        """بروزرسانی فریم دوربین"""
        self.current_frame = frame
        
        # تبدیل BGR به RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # تبدیل به QImage
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # نمایش در label
        scaled_pixmap = pixmap.scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled_pixmap)
    
    def on_plate_detected(self, plate_text, confidence):
        """وقتی پلاک تشخیص داده شد"""
        self.plate_detected_signal.emit(plate_text)
        
        # نمایش پیشرفت
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(int(confidence * 100))
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def capture_image(self):
        """ثبت تصویر"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # ایجاد پوشه اگر وجود نداشته باشد
            if not os.path.exists("captured_plates"):
                os.makedirs("captured_plates")
            
            filename = f"captured_plates/capture_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            
            QMessageBox.information(self, "موفق", f"تصویر در {filename} ذخیره شد")
    
    def closeEvent(self, event):
        """بستن ویجت"""
        self.stop_camera()
        event.accept()


class PlateHistoryDialog(QDialog):
    """دیالوگ نمایش جزئیات پلاک"""
    
    def __init__(self, history_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 جزئیات پلاک")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui(history_data)
    
    def init_ui(self, data):
        layout = QVBoxLayout(self)
        
        # نمایش پلاک
        plate_display = IranianPlateDisplay()
        if 'plate' in data:
            plate_display.set_full_plate(data['plate'])
        layout.addWidget(plate_display)
        
        # جزئیات
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        details_layout = QGridLayout(details_frame)
        
        fields = [
            ("پلاک کامل:", data.get('plate', '')),
            ("نوع پلاک:", data.get('plate_type', '')),
            ("استان:", data.get('province', '')),
            ("زمان ورود:", data.get('entry_time', '')),
            ("زمان خروج:", data.get('exit_time', '')),
            ("مدت توقف:", f"{data.get('duration_hours', 0)} ساعت"),
            ("هزینه:", f"{data.get('cost', 0):,} تومان"),
            ("تخفیف:", data.get('discount', 'ندارد')),
            ("تصویر:", "📸 موجود" if data.get('has_image') else "❌ ندارد")
        ]
        
        for i, (label, value) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: bold; color: #2c3e50;")
            val = QLabel(str(value))
            val.setStyleSheet("color: #34495e;")
            details_layout.addWidget(lbl, i, 0)
            details_layout.addWidget(val, i, 1)
        
        layout.addWidget(details_frame)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(self.close)
        
        if data.get('has_image'):
            view_image_btn = QPushButton("🖼️ مشاهده تصویر")
            view_image_btn.setObjectName("golden_btn")
            btn_layout.addWidget(view_image_btn)
        
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class ParkingSystem:
    """سیستم مدیریت پارکینگ"""
    
    def __init__(self, hourly_rate=5000, data_file="parking_data.json"):
        self.hourly_rate = hourly_rate
        self.data_file = data_file
        self.active_cars = {}
        self.parking_history = []
        self.images_dir = "captured_plates"
        self.load_data()
        
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
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
    
    def car_entry(self, plate_parts, image_path=None):
        """ثبت ورود خودرو"""
        full_plate = IranianPlateValidator.create_full_plate(
            plate_parts["part1"], plate_parts["letter"],
            plate_parts["part2"], plate_parts.get("part3", "")
        )
        
        if full_plate in self.active_cars:
            return False, "خودرو قبلاً وارد شده است!"
        
        entry_time = datetime.now()
        plate_type = IranianPlateValidator.get_plate_type(
            plate_parts["letter"],
            plate_parts.get("part3", "")
        )
        province = IranianPlateValidator.get_province_name(plate_parts.get("part3", ""))
        
        self.active_cars[full_plate] = {
            'plate_parts': plate_parts,
            'entry_time': entry_time.isoformat(),
            'plate_type': plate_type,
            'province': province,
            'entry_image': image_path
        }
        self.save_data()
        
        type_names = {
            'personal': 'شخصی', 'taxi': 'تاکسی',
            'governmental': 'دولتی', 'military': 'نظامی', 'diplomatic': 'سیاسی'
        }
        
        return True, f"ورود خودرو {type_names.get(plate_type, '')} - استان: {province}"
    
    def car_exit(self, full_plate, image_path=None):
        """ثبت خروج خودرو"""
        if full_plate not in self.active_cars:
            return None, "خودرو در پارکینگ نیست!"
        
        car_info = self.active_cars[full_plate]
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
            'plate': full_plate,
            'plate_parts': car_info['plate_parts'],
            'entry_time': entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'duration_hours': round(total_hours, 2),
            'cost': cost,
            'plate_type': car_info['plate_type'],
            'province': car_info['province'],
            'discount': discount_msg,
            'entry_image': car_info.get('entry_image'),
            'exit_image': image_path,
            'has_image': bool(car_info.get('entry_image') or image_path)
        }
        self.parking_history.append(record)
        del self.active_cars[full_plate]
        self.save_data()
        
        return record, f"خروج موفق - هزینه: {cost:,.0f} تومان{discount_msg}"


class ParkingManagementApp(QMainWindow):
    """رابط کاربری اصلی"""
    
    def __init__(self):
        super().__init__()
        self.parking_system = ParkingSystem()
        self.captured_image_path = None
        self.init_ui()
        self.setup_timer()
        self.apply_theme()
    
    def apply_theme(self):
        """اعمال تم"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0c1929, stop: 0.5 #1a2a40, stop: 1 #0c1929);
            }
            
            QTabWidget::pane {
                border: 2px solid #c8a45c;
                border-radius: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fef9e7, stop: 1 #fdebd0);
                padding: 5px;
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
                border: 1px solid #c8a45c;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 0.5 #d4af6a, stop: 1 #b8944a);
                color: #1a252f;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2980b9, stop: 1 #1a5276);
                color: white;
                border: 2px solid #1a5276;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
            }
            
            QPushButton#exit_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #922b21);
                border: 2px solid #922b21;
            }
            
            QPushButton#refresh_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #1e8449);
                border: 2px solid #1e8449;
            }
            
            QPushButton#golden_btn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 0.5 #d4af6a, stop: 1 #b8944a);
                border: 2px solid #8b6914;
                color: #1a252f;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c8a45c;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                background: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c8a45c, stop: 1 #b8944a);
                color: #1a252f;
                border-radius: 8px;
            }
            
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
            }
            
            QStatusBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
                color: #c8a45c;
                border-top: 2px solid #c8a45c;
                font-weight: bold;
            }
            
            QCheckBox {
                color: white;
                font-weight: bold;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🏢 سیستم مدیریت پارکینگ با دوربین و پلاک‌خوان")
        self.setGeometry(50, 50, 1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # هدر
        header = self.create_header()
        main_layout.addWidget(header)
        
        # اسپلیتر اصلی
        splitter = QSplitter(Qt.Horizontal)
        
        # بخش دوربین (چپ)
        camera_widget = QWidget()
        camera_layout = QVBoxLayout(camera_widget)
        
        self.camera_widget = CameraWidget()
        self.camera_widget.plate_detected_signal.connect(self.on_plate_detected_from_camera)
        camera_layout.addWidget(self.camera_widget)
        
        splitter.addWidget(camera_widget)
        
        # بخش اصلی (راست)
        main_widget = QWidget()
        main_widget_layout = QVBoxLayout(main_widget)
        
        # تب‌ها
        self.tab_widget = QTabWidget()
        
        self.entry_exit_tab = self.create_entry_exit_tab()
        self.tab_widget.addTab(self.entry_exit_tab, "🚗 ورود/خروج")
        
        self.active_tab = self.create_active_tab()
        self.tab_widget.addTab(self.active_tab, "🅿️ پارکینگ فعلی")
        
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📊 تاریخچه")
        
        main_widget_layout.addWidget(self.tab_widget)
        splitter.addWidget(main_widget)
        
        # تنظیم اندازه‌ها
        splitter.setSizes([640, 960])
        
        main_layout.addWidget(splitter)
        
        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # تایمر
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_datetime)
        self.clock_timer.start(1000)
    
    def create_header(self):
        """ایجاد هدر"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a252f, stop: 0.3 #c8a45c, stop: 0.5 #d4af6a, 
                    stop: 0.7 #c8a45c, stop: 1 #1a252f);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(header)
        
        logo = QLabel("🅿️")
        logo.setStyleSheet("font-size: 40px; background: transparent;")
        
        title = QLabel("سیستم مدیریت هوشمند پارکینگ با دوربین و پلاک‌خوان")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a252f; background: transparent;")
        
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("font-size: 14px; color: #1a252f; background: transparent; font-weight: bold;")
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.datetime_label)
        
        return header
    
    def create_entry_exit_tab(self):
        """تب ورود/خروج"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # گروه ورود
        entry_group = QGroupBox("🚗 ثبت ورود خودرو")
        entry_layout = QVBoxLayout()
        
        self.entry_plate_widget = IranianPlateWidget()
        
        entry_btn_layout = QHBoxLayout()
        
        entry_btn = QPushButton("ثبت ورود")
        entry_btn.setObjectName("golden_btn")
        entry_btn.clicked.connect(self.car_entry)
        entry_btn.setMinimumHeight(45)
        
        capture_entry_btn = QPushButton("📸 عکس و ثبت ورود")
        capture_entry_btn.setObjectName("refresh_btn")
        capture_entry_btn.clicked.connect(self.capture_and_entry)
        capture_entry_btn.setMinimumHeight(45)
        
        entry_btn_layout.addWidget(entry_btn)
        entry_btn_layout.addWidget(capture_entry_btn)
        
        entry_layout.addWidget(self.entry_plate_widget)
        entry_layout.addLayout(entry_btn_layout)
        entry_group.setLayout(entry_layout)
        layout.addWidget(entry_group)
        
        # گروه خروج
        exit_group = QGroupBox("🚙 ثبت خروج خودرو")
        exit_layout = QVBoxLayout()
        
        self.exit_plate_widget = IranianPlateWidget()
        
        exit_btn_layout = QHBoxLayout()
        
        exit_btn = QPushButton("محاسبه هزینه و خروج")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self.car_exit)
        exit_btn.setMinimumHeight(45)
        
        capture_exit_btn = QPushButton("📸 عکس و ثبت خروج")
        capture_exit_btn.setObjectName("refresh_btn")
        capture_exit_btn.clicked.connect(self.capture_and_exit)
        capture_exit_btn.setMinimumHeight(45)
        
        exit_btn_layout.addWidget(exit_btn)
        exit_btn_layout.addWidget(capture_exit_btn)
        
        exit_layout.addWidget(self.exit_plate_widget)
        exit_layout.addLayout(exit_btn_layout)
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
        
        self.exit_plate_display = IranianPlateDisplay()
        exit_info_layout.addWidget(self.exit_plate_display)
        
        self.exit_info_label = QLabel("اطلاعات خروج در اینجا نمایش داده می‌شود")
        self.exit_info_label.setAlignment(Qt.AlignCenter)
        self.exit_info_label.setStyleSheet("color: #2c3e50; background: transparent; font-size: 12px;")
        self.exit_info_label.setWordWrap(True)
        exit_info_layout.addWidget(self.exit_info_label)
        
        layout.addWidget(self.exit_info_frame)
        
        return widget
    
    def create_active_tab(self):
        """تب پارکینگ فعلی"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_active_cars)
        
        self.active_count_label = QLabel("تعداد خودروهای حاضر: ۰")
        self.active_count_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.active_count_label)
        layout.addLayout(btn_layout)
        
        self.active_table = QTableWidget()
        self.active_table.setColumnCount(9)
        self.active_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "بخش اول", "حرف", "بخش دوم",
            "کد استان", "نوع", "مدت حضور", "تصویر"
        ])
        self.active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_table.setAlternatingRowColors(True)
        layout.addWidget(self.active_table)
        
        self.refresh_active_cars()
        return widget
    
    def create_history_tab(self):
        """تب تاریخچه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(self.refresh_history)
        
        clear_btn = QPushButton("🗑️ پاک کردن")
        clear_btn.setObjectName("exit_btn")
        clear_btn.clicked.connect(self.clear_history)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels([
            "ردیف", "پلاک", "بخش‌ها", "نوع", "استان",
            "ورود", "خروج", "مدت", "هزینه", "تصاویر"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.cellDoubleClicked.connect(self.show_plate_details)
        layout.addWidget(self.history_table)
        
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("""
            padding: 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2c3e50, stop: 1 #1a252f);
            color: #c8a45c;
            border-radius: 10px;
            font-weight: bold;
        """)
        layout.addWidget(self.stats_label)
        
        self.refresh_history()
        return widget
    
    def on_plate_detected_from_camera(self, plate_text):
        """وقتی دوربین پلاک را تشخیص داد"""
        # نمایش در status bar
        self.status_bar.showMessage(f"🔍 پلاک شناسایی شده: {plate_text}", 5000)
        
        # اگر پلاک معتبر بود، در فیلد ورود قرار بده
        parts = IranianPlateValidator.parse_plate_to_parts(plate_text)
        if parts["part1"] and parts["letter"] and parts["part2"]:
            self.entry_plate_widget.set_plate_parts(
                parts["part1"], parts["letter"], parts["part2"], parts["part3"]
            )
    
    def capture_and_entry(self):
        """عکس گرفتن و ثبت ورود"""
        if self.camera_widget.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_plates/entry_{timestamp}.jpg"
            cv2.imwrite(filename, self.camera_widget.current_frame)
            self.captured_image_path = filename
            
            QMessageBox.information(self, "موفق", f"تصویر در {filename} ذخیره شد")
        
        self.car_entry()
    
    def capture_and_exit(self):
        """عکس گرفتن و ثبت خروج"""
        if self.camera_widget.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_plates/exit_{timestamp}.jpg"
            cv2.imwrite(filename, self.camera_widget.current_frame)
            self.captured_image_path = filename
            
            QMessageBox.information(self, "موفق", f"تصویر در {filename} ذخیره شد")
        
        self.car_exit()
    
    def car_entry(self):
        """ثبت ورود"""
        if not self.entry_plate_widget.is_valid():
            QMessageBox.warning(self, "خطا", "لطفاً پلاک را به صورت کامل وارد کنید!")
            return
        
        plate_parts = self.entry_plate_widget.get_plate_parts()
        success, message = self.parking_system.car_entry(
            plate_parts, 
            self.captured_image_path
        )
        
        if success:
            QMessageBox.information(self, "موفق", message)
            self.entry_plate_widget.clear()
            self.captured_image_path = None
            self.refresh_active_cars()
            self.update_status()
        else:
            QMessageBox.warning(self, "خطا", message)
    
    def car_exit(self):
        """ثبت خروج"""
        if not self.exit_plate_widget.is_valid():
            QMessageBox.warning(self, "خطا", "لطفاً پلاک را به صورت کامل وارد کنید!")
            return
        
        full_plate = self.exit_plate_widget.get_plate()
        record, message = self.parking_system.car_exit(
            full_plate,
            self.captured_image_path
        )
        
        if record:
            self.exit_plate_display.set_full_plate(full_plate)
            
            type_names = {
                'personal': 'شخصی', 'taxi': 'تاکسی',
                'governmental': 'دولتی', 'military': 'نظامی', 'diplomatic': 'سیاسی'
            }
            
            info_text = f"""
            نوع: {type_names.get(record['plate_type'], 'نامشخص')} |
            استان: {record['province']} |
            مدت: {record['duration_hours']:.2f} ساعت |
            هزینه: {record['cost']:,.0f} تومان{record.get('discount', '')}
            """
            self.exit_info_label.setText(info_text)
            self.exit_plate_widget.clear()
            self.captured_image_path = None
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
        
        self.active_count_label.setText(f"تعداد خودروهای حاضر: {len(active_cars)}")
        
        for i, (full_plate, car_info) in enumerate(active_cars.items()):
            parts = car_info['plate_parts']
            entry_time = datetime.fromisoformat(car_info['entry_time'])
            duration = datetime.now() - entry_time
            hours = duration.total_seconds() / 3600
            
            self.active_table.insertRow(i)
            self.active_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            display_plate = IranianPlateValidator.format_parts_for_display(parts)
            self.active_table.setItem(i, 1, QTableWidgetItem(display_plate))
            self.active_table.setItem(i, 2, QTableWidgetItem(parts["part1"]))
            self.active_table.setItem(i, 3, QTableWidgetItem(parts["letter"]))
            self.active_table.setItem(i, 4, QTableWidgetItem(parts["part2"]))
            self.active_table.setItem(i, 5, QTableWidgetItem(parts.get("part3", "-")))
            
            type_names = {'personal': 'شخصی', 'taxi': 'تاکسی', 'governmental': 'دولتی'}
            self.active_table.setItem(i, 6, QTableWidgetItem(type_names.get(car_info['plate_type'], 'شخصی')))
            self.active_table.setItem(i, 7, QTableWidgetItem(f"{hours:.1f} ساعت"))
            self.active_table.setItem(i, 8, QTableWidgetItem("📸" if car_info.get('entry_image') else "❌"))
    
    def refresh_history(self):
        """بروزرسانی تاریخچه"""
        self.history_table.setRowCount(0)
        history = self.parking_system.parking_history[-50:]
        
        for i, record in enumerate(reversed(history)):
            parts = record.get('plate_parts', IranianPlateValidator.parse_plate_to_parts(record['plate']))
            entry_time = datetime.fromisoformat(record['entry_time'])
            exit_time = datetime.fromisoformat(record['exit_time'])
            
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.history_table.setItem(i, 1, QTableWidgetItem(record['plate']))
            
            parts_display = f"{parts.get('part1', '')} | {parts.get('letter', '')} | {parts.get('part2', '')}"
            if parts.get('part3'):
                parts_display += f" | {parts['part3']}"
            self.history_table.setItem(i, 2, QTableWidgetItem(parts_display))
            
            type_names = {'personal': 'شخصی', 'taxi': 'تاکسی', 'governmental': 'دولتی'}
            self.history_table.setItem(i, 3, QTableWidgetItem(type_names.get(record.get('plate_type', 'personal'), 'شخصی')))
            self.history_table.setItem(i, 4, QTableWidgetItem(record.get('province', 'نامشخص')))
            self.history_table.setItem(i, 5, QTableWidgetItem(entry_time.strftime('%H:%M:%S')))
            self.history_table.setItem(i, 6, QTableWidgetItem(exit_time.strftime('%H:%M:%S')))
            self.history_table.setItem(i, 7, QTableWidgetItem(f"{record['duration_hours']:.1f}"))
            self.history_table.setItem(i, 8, QTableWidgetItem(f"{record['cost']:,.0f}"))
            
            # نمایش وضعیت تصاویر
            has_images = record.get('has_image', False)
            self.history_table.setItem(i, 9, QTableWidgetItem("📸" if has_images else "❌"))
        
        # آمار
        today = datetime.now().strftime('%Y-%m-%d')
        today_income = sum(r['cost'] for r in history if r['entry_time'].startswith(today))
        today_count = sum(1 for r in history if r['entry_time'].startswith(today))
        
        self.stats_label.setText(
            f"📊 آمار امروز: {today_count} خودرو | 💰 درآمد: {today_income:,.0f} تومان"
        )
    
    def show_plate_details(self, row, col):
        """نمایش جزئیات با دابل کلیک"""
        if row < len(self.parking_system.parking_history):
            record = list(reversed(self.parking_system.parking_history[-50:]))[row]
            dialog = PlateHistoryDialog(record, self)
            dialog.exec_()
    
    def clear_history(self):
        """پاک کردن تاریخچه"""
        reply = QMessageBox.question(self, "تأیید", "آیا مطمئن هستید؟",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parking_system.parking_history.clear()
            self.parking_system.save_data()
            self.refresh_history()
    
    def update_status(self):
        """بروزرسانی نوار وضعیت"""
        active_count = len(self.parking_system.active_cars)
        total = len(self.parking_system.parking_history)
        self.status_bar.showMessage(
            f"🚗 خودروهای حاضر: {active_count} | 📊 کل ثبت‌ها: {total} | "
            f"💰 نرخ: {self.parking_system.hourly_rate:,} تومان/ساعت | "
            f"📸 تصاویر: {os.path.exists('captured_plates') and len(os.listdir('captured_plates'))} عدد"
        )
    
    def update_datetime(self):
        """بروزرسانی ساعت"""
        self.datetime_label.setText(datetime.now().strftime("%Y/%m/%d - %H:%M:%S"))
    
    def setup_timer(self):
        """تایمر بروزرسانی"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(30000)
    
    def auto_refresh(self):
        """بروزرسانی خودکار"""
        if self.tab_widget.currentIndex() == 1:
            self.refresh_active_cars()
        self.update_status()
    
    def closeEvent(self, event):
        """بستن برنامه"""
        self.camera_widget.stop_camera()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 9))
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = ParkingManagementApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()