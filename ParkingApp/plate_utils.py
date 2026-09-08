"""
Utility class for Iranian license plates.
"""

import re


class IranianPlate:
    """Iranian license plate handler."""

    # ===== حروف معتبر پلاک ایران =====
    VALID_LETTERS = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ',
        'د', 'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص', 'ض',
        'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل',
        'م', 'ن', 'و', 'ه', 'ی'
    ]

    # ===== انواع پلاک بر اساس حرف =====
    PLATE_TYPES = {
        'الف': 'دولتی',
        'ب': 'شخصی',
        'پ': 'شخصی',
        'ت': 'شخصی',
        'ث': 'شخصی',
        'ج': 'شخصی',
        'چ': 'شخصی',
        'ح': 'شخصی',
        'خ': 'شخصی',
        'د': 'دولتی',
        'ذ': 'دولتی',
        'ر': 'شخصی',
        'ز': 'شخصی',
        'ژ': 'شخصی',
        'س': 'شخصی',
        'ش': 'شخصی',
        'ص': 'شخصی',
        'ض': 'شخصی',
        'ط': 'شخصی',
        'ظ': 'شخصی',
        'ع': 'شخصی',
        'غ': 'شخصی',
        'ف': 'شخصی',
        'ق': 'شخصی',
        'ک': 'شخصی',
        'گ': 'شخصی',
        'ل': 'شخصی',
        'م': 'شخصی',
        'ن': 'شخصی',
        'و': 'شخصی',
        'ه': 'شخصی',
        'ی': 'شخصی'
    }

    # ===== استان‌های ایران بر اساس کد =====
    PROVINCES = {
        '1': 'تهران',
        '2': 'آذربایجان شرقی',
        '3': 'آذربایجان غربی',
        '4': 'اردبیل',
        '5': 'اصفهان',
        '6': 'البرز',
        '7': 'ایلام',
        '8': 'بوشهر',
        '9': 'چهارمحال و بختیاری',
        '10': 'خراسان جنوبی',
        '11': 'خراسان رضوی',
        '12': 'خراسان شمالی',
        '13': 'خوزستان',
        '14': 'زنجان',
        '15': 'سمنان',
        '16': 'سیستان و بلوچستان',
        '17': 'فارس',
        '18': 'قزوین',
        '19': 'قم',
        '20': 'کردستان',
        '21': 'کرمان',
        '22': 'کرمانشاه',
        '23': 'کهگیلویه و بویراحمد',
        '24': 'گلستان',
        '25': 'گیلان',
        '26': 'لرستان',
        '27': 'مازندران',
        '28': 'مرکزی',
        '29': 'هرمزگان',
        '30': 'همدان',
        '31': 'یزد'
    }

    def __init__(self, part1="", letter="", part2="", part3=""):
        self.part1 = part1.strip()
        self.letter = letter.strip()
        self.part2 = part2.strip()
        self.part3 = part3.strip()
        self._province = None  # برای کش کردن استان

    @property
    def is_valid(self):
        """بررسی اعتبار پلاک."""
        if not all([self.part1, self.letter, self.part2]):
            return False

        if len(self.part1) != 2 or not self.part1.isdigit():
            return False

        if len(self.part2) != 3 or not self.part2.isdigit():
            return False

        if self.letter not in self.VALID_LETTERS:
            return False

        if self.part3 and (len(self.part3) != 2 or not self.part3.isdigit()):
            return False

        return True

    @property
    def full_plate(self):
        """پلاک کامل با خط تیره."""
        if self.part3:
            return f"{self.part1}{self.letter}{self.part2}-{self.part3}"
        else:
            return f"{self.part1}{self.letter}{self.part2}"

    @property
    def display_format(self):
        """فرمت نمایش پلاک (همان full_plate)."""
        return self.full_plate

    @property
    def type_display(self):
        """نوع پلاک بر اساس حرف."""
        if self.letter in self.PLATE_TYPES:
            return self.PLATE_TYPES[self.letter]
        return 'نامشخص'

    @property
    def province(self):
        """استان بر اساس دو رقم اول."""
        if self._province is None:
            code = self.part1[:1]  # رقم اول از part1
            self._province = self.PROVINCES.get(code, 'نامشخص')
        return self._province

    def to_dict(self):
        """تبدیل به دیکشنری."""
        return {
            'plate_number': self.full_plate,
            'plate_part1': self.part1,
            'plate_letter': self.letter,
            'plate_part2': self.part2,
            'plate_part3': self.part3,
            'plate_type': self.type_display,
            'province': self.province
        }

    @classmethod
    def from_full_plate(cls, full_plate):
        """
        ایجاد شی از پلاک کامل.
        فرمت‌های پشتیبانی شده:
        - 12الف345-67
        - 12الف34567
        - 12الف345
        """
        if not full_plate:
            return cls()

        full_plate = full_plate.replace(' ', '')

        # فرمت 1: 12الف345-67
        match = re.match(r'^([0-9]{2})([^0-9])([0-9]{3})-([0-9]{2})$', full_plate)
        if match:
            return cls(match.group(1), match.group(2), match.group(3), match.group(4))

        # فرمت 2: 12الف34567
        match = re.match(r'^([0-9]{2})([^0-9])([0-9]{3})([0-9]{2})$', full_plate)
        if match:
            return cls(match.group(1), match.group(2), match.group(3), match.group(4))

        # فرمت 3: 12الف345 (بدون part3)
        match = re.match(r'^([0-9]{2})([^0-9])([0-9]{3})$', full_plate)
        if match:
            return cls(match.group(1), match.group(2), match.group(3), "")

        return cls()