from typing import List
import random
import numpy as np

from .models import PlateResult
from .detector import PlateDetector


class ALPREngine:

    def __init__(self):

        self.detector = PlateDetector()

        self.ocr = None
        self.validator = None

        self.letters = [
            'الف', 'ب', 'پ', 'ت', 'ث', 'ج',
            'چ', 'ح', 'خ', 'د', 'س', 'ص',
            'ط', 'ع', 'ق', 'ل', 'م',
            'ن', 'و', 'ه', 'ی'
        ]

    def process(self, frame: np.ndarray) -> List[PlateResult]:

        results = []

        candidates = self.detector.detect(frame)

        for x, y, w, h in candidates:

            # فقط موقت (تا Sprint2)
            plate = (
                f"{random.randint(10,99):02d}"
                f"{random.choice(self.letters)}"
                f"{random.randint(100,999):03d}-"
                f"{random.randint(10,99):02d}"
            )

            results.append(
                PlateResult(
                    plate=plate,
                    confidence=0.85,
                    bbox=(x, y, w, h),
                    image=frame[y:y+h, x:x+w]
                )
            )

        return results