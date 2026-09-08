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
        self.mock_mode = mock_mode

        if mock_mode:
            from .detector import PlateDetector
            from .ocr import PlateOCR as MockOCR
            self.detector = PlateDetector()
            self.ocr = MockOCR()
            print("🧪 ALPR Engine: MOCK mode enabled")
        else:
            self.detector = YOLODetector()
            self.ocr = HezarOCR()
            print("🤖 ALPR Engine: REAL mode (YOLO + HezarAI)")

        self.validator = PlateValidator()
        print("✅ ALPR Engine initialized successfully")

    def process(self, frame):
        """
        Process a frame: detect plates, crop, OCR, validate.
        """
        results = []

        if frame is None or frame.size == 0:
            print("⚠️ Empty frame received")
            return results

        try:
            candidates = self.detector.detect(frame)
            print(f"📌 تعداد کاندیداها: {len(candidates)}")

            if not candidates:
                return results

            for item in candidates:
                if len(item) == 5:
                    x, y, w, h, confidence = item
                else:
                    x, y, w, h = item
                    confidence = 0.85

                crop = frame[y:y + h, x:x + w]
                if crop.size == 0:
                    continue

                # ===== OCR =====
                plate_text = self.ocr.read(crop)

                # ===== اطمینان از رشته بودن =====
                if isinstance(plate_text, dict):
                    plate_text = plate_text.get('text', '')
                    print(f"   🔍 استخراج از دیکشنری در engine: '{plate_text}'")

                # ===== اگر هنوز دیکشنری بود یا شبیه آن =====
                if isinstance(plate_text, dict) or ('{' in str(plate_text) and 'text' in str(plate_text)):
                    import re
                    text_str = str(plate_text)
                    match = re.search(r"'text':\s*'([^']*)'", text_str)
                    if match:
                        plate_text = match.group(1)
                        print(f"   🔍 استخراج با regex در engine: '{plate_text}'")

                print(f"   📝 خروجی OCR نهایی: '{plate_text}'")

                # ===== اعتبارسنجی =====
                valid = self.validator.validate(plate_text)
                print(f"   ✅ اعتبارسنجی: {valid}")

                results.append(
                    PlateResult(
                        plate=plate_text,
                        confidence=confidence,
                        bbox=(x, y, w, h),
                        image=crop
                    )
                )

        except Exception as e:
            print(f"❌ Error in ALPR process: {e}")
            import traceback
            traceback.print_exc()

        print(f"📌 تعداد نتایج نهایی: {len(results)}")
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

        vis_frame = frame.copy()
        for result in results:
            x, y, w, h = result.bbox
            cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(vis_frame, result.plate, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return results, vis_frame