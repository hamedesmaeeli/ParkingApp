"""
تست مستقل HezarAI روی تصویر پلاک (بدون وابستگی به ALPREngine)
"""

import os
import cv2
import numpy as np
from hezar.models import Model

print("🚀 تست مستقل HezarAI روی تصویر پلاک...")
print("=" * 50)

# ===== ۱. بارگذاری مدل =====
print("🔄 در حال بارگذاری مدل HezarAI...")
try:
    model = Model.load("hezarai/crnn-fa-license-plate-recognition-v2")
    print("✅ مدل با موفقیت بارگذاری شد!")
except Exception as e:
    print(f"❌ خطا در بارگذاری مدل: {e}")
    exit()

# ===== ۲. بررسی وجود تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "test_pelak1.jpg")

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    print("لطفاً یک تصویر از پلاک در مسیر پروژه قرار دهید.")
    exit()

# ===== ۳. بارگذاری تصویر =====
img = cv2.imread(image_path)
if img is None:
    print("❌ خطا در خواندن تصویر!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ===== ۴. برش (Crop) ناحیه پلاک =====
# با توجه به خروجی YOLO: (350, 357, 105, 33)
h, w = img.shape[:2]
x = 350
y = 357
w_plate = 105
h_plate = 33

# اطمینان از اینکه کادر از تصویر خارج نشود
x = max(0, min(x, w - 10))
y = max(0, min(y, h - 10))
w_plate = min(w_plate, w - x)
h_plate = min(h_plate, h - y)

plate_crop = img[y:y+h_plate, x:x+w_plate]

if plate_crop.size == 0:
    print("❌ ناحیه پلاک خالی است!")
    exit()

print(f"✅ ناحیه پلاک برش خورد: {plate_crop.shape[1]}x{plate_crop.shape[0]}")

# ===== ۵. پیش‌پردازش تصویر برش‌خورده =====
def preprocess_plate(crop):
    """پیش‌پردازش تصویر پلاک برای بهبود تشخیص"""
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # افزایش کنتراست (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # کاهش نویز
    gray = cv2.medianBlur(gray, 3)

    # افزایش وضوح
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    gray = cv2.filter2D(gray, -1, kernel)

    temp_path = "temp_plate_crop.jpg"
    cv2.imwrite(temp_path, gray)
    return temp_path

temp_crop_path = preprocess_plate(plate_crop)
print(f"✅ تصویر پیش‌پردازش‌شده ذخیره شد: {temp_crop_path}")

# ===== ۶. تشخیص با HezarAI =====
print("🔄 در حال تشخیص پلاک با HezarAI...")
try:
    result = model.predict(temp_crop_path)

    # ===== ۷. نمایش نتیجه =====
    print("\n📊 نتیجه تشخیص:")
    print("-" * 40)

    if result and len(result) > 0:
        # ===== استخراج متن از دیکشنری =====
        if isinstance(result[0], dict):
            plate_text = result[0].get('text', '')
        else:
            plate_text = str(result[0])

        print(f"✅ پلاک تشخیص داده شده: {plate_text}")

        # ذخیره تصویر با نتیجه
        img_with_text = img.copy()
        cv2.rectangle(img_with_text, (x, y), (x+w_plate, y+h_plate), (0, 255, 0), 3)
        cv2.putText(img_with_text, plate_text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite("output_hezar_plate.jpg", img_with_text)
        print("✅ تصویر نهایی در output_hezar_plate.jpg ذخیره شد.")
    else:
        print("❌ هیچ پلاکی تشخیص داده نشد!")

except Exception as e:
    print(f"❌ خطا در تشخیص: {e}")

# ===== ۸. پاک کردن فایل‌های موقت =====
if os.path.exists(temp_crop_path):
    os.remove(temp_crop_path)
    print("✅ فایل‌های موقت پاک شدند.")

print("\n🎉 تست HezarAI کامل شد!")