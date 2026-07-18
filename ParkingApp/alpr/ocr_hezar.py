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
    Simple version without preprocessing.
    """

    def __init__(self, model_name="hezarai/crnn-fa-license-plate-recognition-v2"):
        self.model_name = model_name

        if os.path.exists(model_name):
            print(f"🔄 Loading HezarAI from local path: {model_name}")
        else:
            print(f"🔄 Loading HezarAI from Hugging Face: {model_name}")

        try:
            self.model = Model.load(model_name)
            print(f"✅ HezarAI OCR loaded successfully: {model_name}")
        except Exception as e:
            print(f"❌ Error loading HezarAI model: {e}")
            raise

    def read(self, plate_image):
        """Read text from a cropped plate image. No preprocessing."""
        if plate_image is None or plate_image.size == 0:
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

                # فقط حذف فاصله و خط تیره
                plate_text = plate_text.replace(' ', '').replace('-', '')
                print(f"📝 HezarAI OCR: '{plate_text}'")
                return plate_text
        except Exception as e:
            print(f"❌ Error in HezarAI OCR: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return ""