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
                    x = int(x_center - w / 2)
                    y = int(y_center - h / 2)
                    confidence = float(box.conf[0].cpu().numpy())
                    candidates.append((x, y, w, h))
                    print(f"🔍 Plate detected: ({x}, {y}, {w}, {h}) conf={confidence:.2f}")

        print(f"📌 Found {len(candidates)} plate candidate(s).")
        return candidates