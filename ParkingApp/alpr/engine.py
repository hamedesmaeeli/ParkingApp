"""
ALPR Engine

Responsible for orchestrating:
- Plate Detection
- OCR
- Plate Validation
"""
from .detector import PlateDetector
from typing import List
import numpy as np

from .models import PlateResult


class ALPREngine:
    """
    Main ALPR engine.
    """

    def __init__(self):
        # در Sprintهای بعدی مقداردهی خواهند شد

        self.ocr = None
        self.validator = None
        self.detector = PlateDetector()
    def process(self, frame: np.ndarray) -> List[PlateResult]:
        """
        Process one video frame.

        Args:
            frame: OpenCV image (numpy.ndarray)

        Returns:
            List[PlateResult]
        """

        results: List[PlateResult] = []

        # TODO: Plate Detection (Sprint 2)
        # TODO: OCR (Sprint 3)
        # TODO: Validation (Sprint 3)

        return results

    def detect_candidates(self, frame):
        return self.detector.detect(frame)