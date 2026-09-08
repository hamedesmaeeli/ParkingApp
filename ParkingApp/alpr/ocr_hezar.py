# alpr/ocr_hezar.py
"""
HezarAI OCR implementation for Persian license plate recognition.
Simple version - no preprocessing, direct inference.
"""

import os
import cv2
from hezar.models import Model


class HezarOCR:
    """
    OCR engine using HezarAI CRNN model fine-tuned on Persian plates.
    """

    def __init__(self, model_name="hezarai/crnn-fa-license-plate-recognition-v2"):
        """
        Initialize the HezarAI OCR model.

        Args:
            model_name (str): Name or path of the HezarAI model.
        """
        self.model_name = model_name
        self.model = None

        # ===== بررسی مسیر محلی =====
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths = [
            os.path.join(base_dir, "models", "crnn-fa-license-plate-recognition-v2"),
            os.path.join(base_dir, "alpr", "models", "crnn-fa-license-plate-recognition-v2"),
            os.path.join(base_dir, "crnn-fa-license-plate-recognition-v2"),
            os.path.join(base_dir, "alpr", "crnn-fa-license-plate-recognition-v2"),
            model_name
        ]

        # پیدا کردن اولین مسیر موجود
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                if os.path.exists(os.path.join(path, "model.pt")) or \
                   os.path.exists(os.path.join(path, "model.bin")):
                    found_path = path
                    break

        if found_path:
            print(f"🔄 Loading HezarAI from local path: {found_path}")
            try:
                self.model = Model.load(found_path)
                print(f"✅ HezarAI OCR loaded successfully from: {found_path}")
                return
            except Exception as e:
                print(f"⚠️ Error loading from local path: {e}")

        # بارگذاری از Hugging Face
        print(f"🔄 Loading HezarAI from Hugging Face: {model_name}")
        try:
            self.model = Model.load(model_name)
            print(f"✅ HezarAI OCR loaded successfully: {model_name}")
        except Exception as e:
            print(f"❌ Error loading HezarAI model: {e}")
            raise

    def read(self, plate_image):
        """
        Read text from a cropped plate image.

        Args:
            plate_image (np.ndarray): Cropped plate image (BGR format).

        Returns:
            str: Detected plate text, or empty string if not detected.
        """
        if plate_image is None or plate_image.size == 0:
            print("⚠️ Plate image is empty.")
            return ""

        if self.model is None:
            print("❌ Model is not loaded!")
            return ""

        temp_path = "temp_plate_simple.jpg"
        cv2.imwrite(temp_path, plate_image)

        try:
            result = self.model.predict(temp_path)

            if result and len(result) > 0:
                if isinstance(result[0], dict):
                    plate_text = result[0].get('text', '')
                else:
                    plate_text = str(result[0])

                plate_text = plate_text.replace(' ', '').replace('-', '')
                print(f"📝 HezarAI OCR: '{plate_text}'")
                return plate_text
            else:
                print("⚠️ No text detected by HezarAI")
                return ""

        except Exception as e:
            print(f"❌ Error in HezarAI OCR: {e}")
            import traceback
            traceback.print_exc()
            return ""
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def set_model(self, model_name):
        """
        Change the model dynamically.

        Args:
            model_name (str): New model name or path
        """
        self.model_name = model_name
        self.model = Model.load(model_name)
        print(f"✅ HezarAI model changed to: {model_name}")