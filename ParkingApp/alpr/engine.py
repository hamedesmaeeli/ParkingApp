from typing import List
import random
import numpy as np

from .detector import PlateDetector
from .ocr import PlateOCR
from .validator import PlateValidator
from .models import PlateResult


class ALPREngine:

    def __init__(self, mock_mode=False):  # <-- پارامتر جدید
        self.mock_mode = mock_mode

        self.ocr = PlateOCR()
        self.validator = PlateValidator()
        self.detector = PlateDetector()

        self.letters = [
            'الف', 'ب', 'پ', 'ت', 'ث', 'ج',
            'چ', 'ح', 'خ', 'د', 'س', 'ص',
            'ط', 'ع', 'ق', 'ل', 'م',
            'ن', 'و', 'ه', 'ی'
        ]

    def process(self, frame):
        results = []

        # ===== اگر حالت Mock فعال باشد =====
        if self.mock_mode:
            print("🧪 [MOCK] ALPR در حالت تست اجرا می‌شود")
            h, w = frame.shape[:2]

            # یک کادر فرضی در مرکز تصویر
            x = int(w * 0.25)
            y = int(h * 0.35)
            box_w = int(w * 0.5)
            box_h = int(h * 0.15)

            # یک پلاک نمونه
            mock_plate = f"{random.randint(10, 99):02d}{random.choice(self.letters)}{random.randint(100, 999):03d}-{random.randint(10, 99):02d}"

            results.append(
                PlateResult(
                    plate=mock_plate,
                    confidence=0.95,
                    bbox=(x, y, box_w, box_h),
                    image=frame[y:y + box_h, x:x + box_w]
                )
            )

            print(f"   📝 پلاک Mock: {mock_plate}")
            print(f"   📦 کادر Mock: ({x}, {y}, {box_w}, {box_h})")
            return results
        # =====================================

        candidates = self.detector.detect(frame)
        print(f"📌 تعداد کاندیداها: {len(candidates)}")

        for x, y, w, h in candidates:
            crop = frame[y:y + h, x:x + w]
            if crop.size == 0:
                continue

            plate = self.ocr.read(crop)
            valid = self.validator.validate(plate)

            results.append(
                PlateResult(
                    plate=plate,
                    confidence=0.85,
                    bbox=(x, y, w, h),
                    image=crop
                )
            )

        return results