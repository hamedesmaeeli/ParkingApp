"""
ابزارهای مدیریت پلاک ایرانی
نسخه اصلاح شده - بدون import حلقوی
"""

import re
from datetime import datetime


class IranianPlate:
    """کلاس مدیریت پلاک ایرانی"""

    VALID_LETTERS = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د',
        'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ',
        'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و', 'ه', 'ی'
    ]

    PROVINCE_CODES = {
        '01': 'تهران مرکزی', '02': 'تهران شرق', '03': 'تهران غرب',
        '04': 'تهران شمال', '05': 'تهران جنوب',
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

    def __init__(self, part1='', letter='', part2='', part3=''):
        self.part1 = part1
        self.letter = letter
        self.part2 = part2
        self.part3 = part3

    @classmethod
    def from_full_plate(cls, full_plate):
        """ساخت از پلاک کامل"""
        if not full_plate:
            return cls()

        plate = full_plate.strip().replace(' ', '')

        if '-' in plate:
            main, province = plate.split('-')
        else:
            main = plate
            province = ''

        if len(main) == 5:
            return cls(main[:2], main[2], main[3:], province)
        elif len(main) == 6:
            return cls(main[:3], main[3], main[4:], province)

        return cls()

    @property
    def full_plate(self):
        """پلاک کامل"""
        base = f"{self.part1}{self.letter}{self.part2}"
        if self.part3:
            base += f"-{self.part3}"
        return base

    @property
    def display_format(self):
        """فرمت نمایشی زیبا"""
        if not self.part1 or not self.letter or not self.part2:
            return ""

        display = f"{self.part1} | {self.letter} | {self.part2}"
        if self.part3:
            display += f"  ایران  {self.part3}"
        return display

    @property
    def is_valid(self):
        """اعتبارسنجی پلاک"""
        if not self.part1 or not self.letter or not self.part2:
            return False

        if len(self.part1) != 2 or not self.part1.isdigit():
            return False

        if self.letter not in self.VALID_LETTERS:
            return False

        if len(self.part2) != 3 or not self.part2.isdigit():
            return False

        if self.part3 and not self.part3.isdigit():
            return False

        return True

    @property
    def plate_type(self):
        """نوع پلاک"""
        if self.letter == 'ت':
            return 'taxi'
        elif self.letter == 'د':
            return 'diplomatic'
        elif len(self.part3) == 1:
            return 'governmental'
        return 'personal'

    @property
    def province(self):
        """نام استان"""
        if self.part3 in self.PROVINCE_CODES:
            return self.PROVINCE_CODES[self.part3]
        if len(self.part3) == 1:
            return 'دولتی'
        return 'نامشخص'

    @property
    def type_display(self):
        """نمایش فارسی نوع پلاک"""
        types = {
            'personal': 'شخصی',
            'taxi': 'تاکسی',
            'governmental': 'دولتی',
            'diplomatic': 'سیاسی',
            'military': 'نظامی'
        }
        return types.get(self.plate_type, 'شخصی')

    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'plate_number': self.full_plate,
            'plate_part1': self.part1,
            'plate_letter': self.letter,
            'plate_part2': self.part2,
            'plate_part3': self.part3,
            'plate_type': self.plate_type,
            'province': self.province
        }

    def __str__(self):
        return self.display_format

    def __repr__(self):
        return f"IranianPlate({self.full_plate})"


class IranianPlateValidator:
    """اعتبارسنجی پلاک‌های ایرانی (کلاس کمکی)"""

    @staticmethod
    def validate_plate_parts(part1, letter, part2, part3=""):
        """اعتبارسنجی بخش‌های پلاک"""
        if not part1 or not letter or not part2:
            return False, "همه بخش‌ها باید پر شوند"

        if not part1.isdigit() or len(part1) != 2:
            return False, "بخش اول باید ۲ رقم باشد"

        if not part2.isdigit() or len(part2) != 3:
            return False, "بخش سوم باید ۳ رقم باشد"

        if letter not in IranianPlate.VALID_LETTERS:
            return False, "حرف پلاک نامعتبر است"

        if part3 and not part3.isdigit():
            return False, "کد استان باید عددی باشد"

        return True, ""

    @staticmethod
    def create_full_plate(part1, letter, part2, part3=""):
        """ساخت پلاک کامل از بخش‌ها"""
        if part3:
            return f"{part1}{letter}{part2}-{part3}"
        return f"{part1}{letter}{part2}"

    @staticmethod
    def parse_plate_to_parts(full_plate):
        """تبدیل پلاک کامل به بخش‌های مجزا"""
        plate = IranianPlate.from_full_plate(full_plate)
        return {
            "part1": plate.part1,
            "letter": plate.letter,
            "part2": plate.part2,
            "part3": plate.part3
        }

    @staticmethod
    def get_plate_type(letter, part3=""):
        """تشخیص نوع پلاک"""
        if letter == 'ت':
            return 'taxi'
        elif letter == 'د':
            return 'diplomatic'
        elif len(part3) == 1:
            return 'governmental'
        return 'personal'

    @staticmethod
    def get_province_name(part3):
        """دریافت نام استان"""
        plate = IranianPlate()
        return plate.PROVINCE_CODES.get(part3, 'نامشخص') if part3 else 'نامشخص'

    @staticmethod
    def format_parts_for_display(parts):
        """فرمت‌بندی بخش‌های پلاک برای نمایش"""
        if not parts.get("part1") or not parts.get("letter") or not parts.get("part2"):
            return ""

        display = f"{parts['part1']} | {parts['letter']} | {parts['part2']}"
        if parts.get("part3"):
            display += f"  ایران  {parts['part3']}"
        return display

    @staticmethod
    def clean_ocr_text(text):
        """پاکسازی متن OCR برای پلاک ایرانی"""
        # حذف کاراکترهای اضافی
        text = re.sub(r'[^\d\u0600-\u06FF]', '', text)
        return text.strip()