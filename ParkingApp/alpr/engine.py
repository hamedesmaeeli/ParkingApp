"""
ALPR Engine - Core module for license plate recognition.
Orchestrates detection, OCR, and validation.
"""

from typing import List
import random
import numpy as np

from .detector import PlateDetector
from .ocr import PlateOCR
from .validator import PlateValidator
from .models import PlateResult
from .yolo_detector import YOLODetector


class ALPREngine:
    """
    Main engine for Automatic License Plate Recognition.
    Handles the complete pipeline: detection -> OCR -> validation.
    """

    def __init__(self, mock_mode=False):
        """
        Initialize the ALPR engine.

        Args:
            mock_mode (bool): If True, uses mock data for testing without real detection.
        """
        self.mock_mode = mock_mode

        # Initialize components
        self.ocr = PlateOCR()
        self.validator = PlateValidator()

        # ===== Select detector based on mode =====
        if mock_mode:
            # Use OpenCV contour detector for mock mode (no external dependencies)
            self.detector = PlateDetector()
            print("🧪 ALPR Engine: Running in MOCK mode (using OpenCV contours)")
        else:
            # Use YOLO detector for real detection
            self.detector = YOLODetector()
            print("🤖 ALPR Engine: Running in REAL mode (using YOLO)")
        # =========================================

        self.letters = [
            'الف', 'ب', 'پ', 'ت', 'ث', 'ج',
            'چ', 'ح', 'خ', 'د', 'س', 'ص',
            'ط', 'ع', 'ق', 'ل', 'م',
            'ن', 'و', 'ه', 'ی'
        ]

    def process(self, frame):
        """
        Process a single frame and extract license plate information.

        Args:
            frame (np.ndarray): Input image in BGR format.

        Returns:
            List[PlateResult]: List of detected plates with their information.
        """
        results = []

        # ===== MOCK MODE: Generate fake plates =====
        if self.mock_mode:
            print("🧪 [MOCK] ALPR در حالت تست اجرا می‌شود")
            h, w = frame.shape[:2]

            # Generate a mock bounding box in the center of the image
            x = int(w * 0.25)
            y = int(h * 0.35)
            box_w = int(w * 0.5)
            box_h = int(h * 0.15)

            # Generate a random Persian plate
            mock_plate = f"{random.randint(10, 99):02d}{random.choice(self.letters)}{random.randint(100, 999):03d}-{random.randint(10, 99):02d}"

            # Create a PlateResult object
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
        # ==========================================

        # ===== REAL MODE: Use YOLO detector =====
        # Step 1: Detect plate candidates
        candidates = self.detector.detect(frame)
        print(f"📌 تعداد کاندیداها: {len(candidates)}")

        # Step 2: Process each candidate
        for x, y, w, h in candidates:
            # Crop the plate region
            crop = frame[y:y + h, x:x + w]
            if crop.size == 0:
                print("   ❌ crop خالی است")
                continue

            # Step 3: OCR on the cropped region
            plate = self.ocr.read(crop)
            print(f"   📝 خروجی OCR: {plate}")

            # Step 4: Validate the plate
            valid = self.validator.validate(plate)
            print(f"   ✅ اعتبارسنجی: {valid}")

            # Step 5: Create result object
            results.append(
                PlateResult(
                    plate=plate,
                    confidence=0.85,  # Default confidence for now
                    bbox=(x, y, w, h),
                    image=crop
                )
            )

        print(f"📌 تعداد نتایج نهایی: {len(results)}")
        return results

    def set_detector_confidence(self, confidence: float):
        """
        Set the confidence threshold for the detector.

        Args:
            confidence (float): Threshold between 0.0 and 1.0.
        """
        if hasattr(self.detector, 'set_confidence'):
            self.detector.set_confidence(confidence)
        else:
            print("⚠️ Current detector doesn't support confidence threshold")