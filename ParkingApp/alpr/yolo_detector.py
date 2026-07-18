"""
YOLO-based plate detector using specialized Iranian plate model.
Uses YOLOv8m fine-tuned on Iranian license plates.
"""

import cv2
from ultralytics import YOLO
import numpy as np
import os

class YOLODetector:
    """Detects license plates using a model fine-tuned for Iranian plates."""

    def __init__(self, model_name="YOLOv8m_Iran_license_plate_detection.pt", confidence_threshold=0.25):
        """
        Initializes the YOLO detector.

        Args:
            model_name (str): Name or path of the YOLO model.
            confidence_threshold (float): Minimum confidence score for detections.
        """
        # ===== بررسی وجود فایل مدل =====
        if not os.path.exists(model_name):
            print(f"⚠️ مدل {model_name} در مسیر فعلی پیدا نشد!")
            print("🔄 تلاش برای بارگذاری از Hugging Face...")
            model_name = "shalchianmh/Iran_license_plate_detection_YOLOv8m"

        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold
        print(f"✅ YOLO model (Iranian plates) loaded: {model_name}")

    def detect(self, frame):
        """
        Detects license plates in a given frame.

        Args:
            frame (np.ndarray): Input image (BGR format).

        Returns:
            list: A list of tuples (x, y, w, h) for each detected plate.
        """
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)

        candidates = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # Convert from xywh to x, y, w, h format
                    x_center, y_center, w, h = box.xywh[0].cpu().numpy().astype(int)
                    x = int(x_center - w/2)
                    y = int(y_center - h/2)
                    confidence = float(box.conf[0].cpu().numpy())
                    candidates.append((x, y, w, h, confidence))
                    print(f"🔍 Plate detected: ({x}, {y}, {w}, {h}) conf={confidence:.2f}")

        print(f"📌 Found {len(candidates)} plate candidate(s).")
        return candidates

    def extract_crops(self, frame, candidates, padding_ratio=0.6):  # افزایش از 0.4 به 0.6
        """
        Extract cropped plate images with padding.

        Args:
            frame (np.ndarray): Original image.
            candidates (list): List of (x, y, w, h, confidence) from detect().
            padding_ratio (float): Padding ratio relative to plate size.

        Returns:
            list: List of dicts with 'bbox', 'crop', and 'confidence'.
        """
        crops = []
        h_img, w_img = frame.shape[:2]

        for item in candidates:
            if len(item) == 5:
                x, y, w, h, conf = item
            else:
                x, y, w, h = item
                conf = 0.85

            # محاسبه Padding (بیشتر)
            pad_w = int(w * padding_ratio)
            pad_h = int(h * padding_ratio)

            x_new = max(0, x - pad_w)
            y_new = max(0, y - pad_h)
            w_new = min(w + pad_w * 2, w_img - x_new)
            h_new = min(h + pad_h * 2, h_img - y_new)

            crop = frame[y_new:y_new + h_new, x_new:x_new + w_new]
            crops.append({
                'bbox': (x_new, y_new, w_new, h_new),
                'crop': crop,
                'confidence': conf,
                'original_bbox': (x, y, w, h)
            })
            print(f"📦 Crop extracted: ({x_new}, {y_new}, {w_new}, {h_new}) size={crop.shape[1]}x{crop.shape[0]}")

        return crops