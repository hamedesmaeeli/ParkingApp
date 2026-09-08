"""
تست کامل: YOLO برای تشخیص کادر + HezarAI برای OCR
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from hezar.models import Model

print("🚀 تست کامل YOLO + HezarAI روی تصویر پلاک...")
print("=" * 60)

# ===== ۱. بارگذاری مدل YOLO =====
print("🔄 در حال بارگذاری مدل YOLO...")
yolo_model_path = "YOLOv8m_Iran_license_plate_detection.pt"

if not os.path.exists(yolo_model_path):
    print(f"❌ فایل مدل YOLO در {yolo_model_path} پیدا نشد!")
    exit()

try:
    yolo_model = YOLO(yolo_model_path)
    print("✅ مدل YOLO با موفقیت بارگذاری شد!")
except Exception as e:
    print(f"❌ خطا در بارگذاری YOLO: {e}")
    exit()

# ===== ۲. بارگذاری مدل HezarAI =====
print("🔄 در حال بارگذاری مدل HezarAI...")
try:
    hezar_model = Model.load("hezarai/crnn-fa-license-plate-recognition-v2")
    print("✅ مدل HezarAI با موفقیت بارگذاری شد!")
except Exception as e:
    print(f"❌ خطا در بارگذاری HezarAI: {e}")
    exit()

# ===== ۳. بارگذاری تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "test_pelak2.jpg")

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    exit()

img = cv2.imread(image_path)
if img is None:
    print("❌ خطا در خواندن تصویر!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ===== ۴. تشخیص پلاک با YOLO =====
print("\n🔄 مرحله 1: تشخیص پلاک با YOLO...")
results = yolo_model(image_path)

detections = []
for r in results:
    boxes = r.boxes
    if boxes is not None:
        for box in boxes:
            x_center, y_center, w, h = box.xywh[0].cpu().numpy().astype(int)
            x = int(x_center - w / 2)
            y = int(y_center - h / 2)
            confidence = float(box.conf[0].cpu().numpy())
            detections.append((x, y, w, h, confidence))
            print(f"   🔹 پلاک: ({x}, {y}, {w}, {h}) با اطمینان {confidence:.2%}")

if len(detections) == 0:
    print("❌ هیچ پلاکی تشخیص داده نشد!")
    exit()

print(f"✅ {len(detections)} پلاک تشخیص داده شد.")


# ===== ۵. استخراج Crop با Padding =====
def extract_plate_crop(img, x, y, w, h, padding_ratio=0.3):
    """
    استخراج Crop پلاک با Padding
    """
    h_img, w_img = img.shape[:2]

    pad_w = int(w * padding_ratio)
    pad_h = int(h * padding_ratio)

    x_new = max(0, x - pad_w)
    y_new = max(0, y - pad_h)
    w_new = min(w + pad_w * 2, w_img - x_new)
    h_new = min(h + pad_h * 2, h_img - y_new)

    crop = img[y_new:y_new + h_new, x_new:x_new + w_new]
    return crop, (x_new, y_new, w_new, h_new)


print("\n🔄 مرحله 2: استخراج Crop پلاک...")
x, y, w, h, conf = detections[0]
plate_crop, crop_bbox = extract_plate_crop(img, x, y, w, h, padding_ratio=0.4)
print(f"   📦 Crop: {crop_bbox}")
print(f"   📏 اندازه Crop: {plate_crop.shape[1]}x{plate_crop.shape[0]}")

# ذخیره Crop خام
cv2.imwrite("crop_raw.jpg", plate_crop)
print("   ✅ Crop خام در crop_raw.jpg ذخیره شد.")


# ===== ۶. پیش‌پردازش Crop =====
def preprocess_plate(crop):
    """
    پیش‌پردازش تخصصی برای پلاک
    """
    # ۱. تبدیل به خاکستری
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # ۲. افزایش کنتراست (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # ۳. کاهش نویز
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # ۴. افزایش وضوح
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, kernel)

    # ۵. تنظیم اندازه (حداقل عرض 150 پیکسل)
    h, w = gray.shape[:2]
    if w < 150:
        scale = 150 / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    return gray


print("\n🔄 مرحله 3: پیش‌پردازش Crop...")
processed_crop = preprocess_plate(plate_crop)
print(f"   ✅ اندازه پس از پیش‌پردازش: {processed_crop.shape[1]}x{processed_crop.shape[0]}")

# ===== ۷. تشخیص OCR با HezarAI =====
temp_path = "temp_crop_optimized.jpg"
cv2.imwrite(temp_path, processed_crop)
print(f"\n🔄 مرحله 4: تشخیص OCR با HezarAI...")
result = hezar_model.predict(temp_path)

# ===== ۸. نمایش نتیجه نهایی =====
print("\n" + "=" * 60)
print("📊 نتیجه نهایی:")
print("-" * 40)

if result and len(result) > 0:
    if isinstance(result[0], dict):
        plate_text = result[0].get('text', '')
    else:
        plate_text = str(result[0])
    print(f"✅ پلاک تشخیص داده شده: {plate_text}")
else:
    print("❌ هیچ پلاکی تشخیص داده نشد!")

# ===== ۹. ذخیره تصویر نهایی =====
img_with_boxes = img.copy()
x2, y2, w2, h2 = crop_bbox
cv2.rectangle(img_with_boxes, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 3)
if plate_text:
    cv2.putText(img_with_boxes, plate_text, (x2, y2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
cv2.imwrite("output_yolo_hezar.jpg", img_with_boxes)
print("\n✅ تصویر نهایی در output_yolo_hezar.jpg ذخیره شد.")

# ===== ۱۰. پاک کردن فایل‌های موقت =====
if os.path.exists(temp_path):
    os.remove(temp_path)
    print("✅ فایل‌های موقت پاک شدند.")

print("\n🎉 تست کامل YOLO + HezarAI با موفقیت انجام شد!")