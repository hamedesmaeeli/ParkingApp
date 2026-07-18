"""
ALPR Engine - Orchestrates YOLO detection and HezarAI OCR.
"""

import cv2
import numpy as np
from .yolo_detector import YOLODetector
from .ocr_hezar import HezarOCR
from .validator import PlateValidator
from .models import PlateResult


class ALPREngine:
    """
    Main ALPR engine combining YOLO for detection and HezarAI for OCR.
    """

    def __init__(self, mock_mode=False):
        """
        Initialize the ALPR engine.

        Args:
            mock_mode (bool): If True, use mock detector and OCR for testing.
        """
        self.mock_mode = mock_mode

        # ===== انتخاب کامپوننت‌ها =====
        if mock_mode:
            # حالت تست: استفاده از Mock
            from .detector import PlateDetector
            from .ocr import PlateOCR as MockOCR
            self.detector = PlateDetector()
            self.ocr = MockOCR()
            print("🧪 ALPR Engine: MOCK mode enabled")
        else:
            # حالت واقعی: YOLO + HezarAI
            self.detector = YOLODetector()  # تشخیص کادر
            self.ocr = HezarOCR()           # خواندن متن
            print("🤖 ALPR Engine: REAL mode (YOLO + HezarAI)")
        # =================================

        self.validator = PlateValidator()
        print("✅ ALPR Engine initialized successfully")

    def process(self, frame):
        """
        Process a frame: detect plates, crop, OCR, validate.

        Args:
            frame (np.ndarray): Input image (BGR format).

        Returns:
            List[PlateResult]: Detection results with plate text and metadata.
        """
        results = []

        if frame is None or frame.size == 0:
            print("⚠️ Empty frame received")
            return results

        try:
            # ===== مرحله ۱: تشخیص کادر با YOLO =====
            candidates = self.detector.detect(frame)
            print(f"📌 YOLO found {len(candidates)} candidate(s)")

            if not candidates:
                print("⚠️ No plate candidates found")
                return results

            # ===== مرحله ۲: استخراج Crop با Padding =====
            crops = self.detector.extract_crops(frame, candidates, padding_ratio=0.4)
            print(f"📦 Extracted {len(crops)} crop(s)")

            # ===== مرحله ۳: OCR روی هر Crop =====
            for crop_info in crops:
                x, y, w, h = crop_info['bbox']
                crop = crop_info['crop']
                confidence = crop_info['confidence']

                # OCR با HezarAI
                plate_text = self.ocr.read(crop)

                if not plate_text:
                    print(f"⚠️ No text detected for crop at ({x}, {y})")
                    continue

                # اعتبارسنجی
                if self.validator.validate(plate_text):
                    # ایجاد نتیجه
                    result = PlateResult(
                        plate=plate_text,
                        confidence=confidence,
                        bbox=(x, y, w, h),
                        image=crop
                    )
                    results.append(result)
                    print(f"✅ Valid plate: '{plate_text}' (conf={confidence:.2f})")
                else:
                    print(f"❌ Invalid plate: '{plate_text}'")

        except Exception as e:
            print(f"❌ Error in ALPR process: {e}")
            import traceback
            traceback.print_exc()

        print(f"📌 Final results: {len(results)} plate(s)")
        return results

    def process_with_visualization(self, frame):
        """
        Process a frame and return results with visualization.

        Args:
            frame (np.ndarray): Input image (BGR format).

        Returns:
            tuple: (List[PlateResult], np.ndarray) results and visualized image.
        """
        results = self.process(frame)

        # رسم کادرها روی تصویر
        vis_frame = frame.copy()
        for result in results:
            x, y, w, h = result.bbox
            cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(vis_frame, result.plate, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return results, vis_frame

    def set_confidence_threshold(self, threshold):
        """
        Set confidence threshold for YOLO detector.

        Args:
            threshold (float): Value between 0.0 and 1.0.
        """
        if hasattr(self.detector, 'confidence_threshold'):
            self.detector.confidence_threshold = threshold
            print(f"✅ Confidence threshold set to {threshold}")
        else:
            print("⚠️ Current detector doesn't support confidence threshold")