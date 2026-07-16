"""
OCR interface.
"""

import random


class PlateOCR:
    """Temporary OCR implementation - returns mock plates."""

    LETTERS = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ',
        'ح', 'خ', 'د', 'س', 'ص', 'ط', 'ع',
        'ق', 'ل', 'م', 'ن', 'و', 'ه', 'ی'
    ]

    def read(self, plate_image) -> str:
        """Returns a mock Persian plate number."""
        return (
            f"{random.randint(10,99):02d}"
            f"{random.choice(self.LETTERS)}"
            f"{random.randint(100,999):03d}-"
            f"{random.randint(10,99):02d}"
        )