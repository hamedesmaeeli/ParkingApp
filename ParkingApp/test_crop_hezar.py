"""
تست کامل HezarAI روی Crop پلاک با پیش‌پردازش و Padding
"""

import os
import cv2
import numpy as np
from hezar.models import Model

print("🚀 تست HezarAI روی Crop پلاک با پیش‌پردازش...")
print("=" * 50)

# ===== ۱. بارگذاری مدل =====
print("🔄 در حال بارگذاری مدل HezarAI...")
try:
    model = Model.load("hezarai/crnn-fa-license-plate-recognition-v2")
    print("✅ مدل با موفقیت بارگذاری شد!")
except Exception as e:
    print(f"❌ خطا در بارگذاری مدل: {e}")
    exit()

# ===== ۲. بارگذاری تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "test_pelak1.jpg")

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    print("لطفاً یک تصویر از پلاک در مسیر پروژه قرار دهید.")
    exit()

img = cv2.imread(image_path)
if img is None:
    print("❌ خطا در خواندن تصویر!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ===== ۳. مختصات از YOLO =====
x, y, w, h = 350, 357, 105, 33
print(f"📌 مختصات YOLO: ({x}, {y}, {w}, {h})")


# ===== ۴. Crop با Padding =====
def crop_with_padding(img, x, y, w, h, padding_ratio=0.3):
    """
    برش تصویر با اضافه کردن padding به اطراف
    """
    pad_w = int(w * padding_ratio)
    pad_h = int(h * padding_ratio)

    x_new = max(0, x - pad_w)
    y_new = max(0, y - pad_h)
    w_new = min(w + pad_w * 2, img.shape[1] - x_new)
    h_new = min(h + pad_h * 2, img.shape[0] - y_new)

    crop = img[y_new:y_new + h_new, x_new:x_new + w_new]
    return crop, (x_new, y_new, w_new, h_new)


plate_crop, new_bbox = crop_with_padding(img, x, y, w, h, padding_ratio=0.5)
print(f"✅ Crop با Padding: {new_bbox}")
print(f"   اندازه Crop: {plate_crop.shape[1]}x{plate_crop.shape[0]}")

# ذخیره Crop اولیه
cv2.imwrite("crop_raw.jpg", plate_crop)
print("✅ Crop خام در crop_raw.jpg ذخیره شد.")


# ===== ۵. پیش‌پردازش Crop =====
def preprocess_plate(crop):
    """
    پیش‌پردازش تخصصی برای پلاک
    """
    # ۱. تبدیل به خاکستری
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # ۲. افزایش کنتراست (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # ۳. کاهش نویز با Bilateral Filter
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # ۴. افزایش وضوح (Sharpening)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, kernel)

    # ۵. تنظیم اندازه (برای HezarAI بهتر است)
    h, w = gray.shape[:2]
    if w < 150:
        scale = 150 / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        print(f"   اندازه تنظیم شد: {new_w}x{new_h}")

    return gray


processed_crop = preprocess_plate(plate_crop)
print("✅ پیش‌پردازش انجام شد.")

# ===== ۶. ذخیره و تشخیص =====
temp_path = "temp_crop_optimized.jpg"
cv2.imwrite(temp_path, processed_crop)
print(f"✅ تصویر پیش‌پردازش‌شده در {temp_path} ذخیره شد.")

print("🔄 در حال تشخیص پلاک با HezarAI...")
result = model.predict(temp_path)

# ===== ۷. نمایش نتیجه =====
print("\n📊 نتیجه تشخیص:")
print("-" * 40)

if result and len(result) > 0:
    if isinstance(result[0], dict):
        plate_text = result[0].get('text', '')
    else:
        plate_text = str(result[0])
    print(f"✅ پلاک تشخیص داده شد: {plate_text}")

    # ذخیره تصویر با کادر
    img_with_box = img.copy()
    x2, y2, w2, h2 = new_bbox
    cv2.rectangle(img_with_box, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 3)
    cv2.putText(img_with_box, plate_text, (x2, y2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imwrite("output_crop_result.jpg", img_with_box)
    print("✅ تصویر نهایی در output_crop_result.jpg ذخیره شد.")
else:
    print("❌ هیچ پلاکی تشخیص داده نشد!")

# ===== ۸. نمایش اطلاعات بیشتر =====
print("\n📋 اطلاعات تشخیص:")
print(f"   - مختصات اصلی YOLO: ({x}, {y}, {w}, {h})")
print(f"   - مختصات نهایی با Padding: ({x2}, {y2}, {w2}, {h2})")
print(f"   - اندازه Crop نهایی: {plate_crop.shape[1]}x{plate_crop.shape[0]}")

# ===== ۹. پاک کردن فایل‌های موقت =====
if os.path.exists(temp_path):
    os.remove(temp_path)
    print("✅ فایل‌های موقت پاک شدند.")

print("\n🎉 تست کامل شد!")