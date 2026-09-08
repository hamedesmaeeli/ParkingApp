"""
تست EasyOCR روی تصویر پلاک
"""

import easyocr
import cv2
import os
import numpy as np

print("🚀 تست EasyOCR روی تصویر پلاک...")

# ===== ۱. راه‌اندازی EasyOCR =====
try:
    # GPU=False برای اجرا روی CPU
    reader = easyocr.Reader(['fa', 'en'], gpu=False)
    print("✅ EasyOCR مقداردهی شد.")
except Exception as e:
    print(f"❌ خطا در مقداردهی EasyOCR: {e}")
    exit()

# ===== ۲. بارگذاری تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "test_pelak_crop1.jpg")  # ← نام عکس خود را قرار دهید

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    print("لطفاً یک تصویر پلاک در مسیر پروژه قرار دهید.")
    exit()

img = cv2.imread(image_path)
if img is None:
    print("❌ خطا در خواندن تصویر!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")


# ===== ۳. پیش‌پردازش تصویر =====
def preprocess_image(img):
    """پیش‌پردازش تصویر برای بهبود تشخیص"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # افزایش کنتراست
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # کاهش نویز
    gray = cv2.medianBlur(gray, 3)

    # افزایش وضوح
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, kernel)

    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


processed_img = preprocess_image(img)

# ===== ۴. تشخیص متن =====
print("🔄 در حال تشخیص متن...")
result = reader.readtext(processed_img, detail=1, paragraph=False)

# ===== ۵. نمایش نتایج =====
print("\n📊 نتایج تشخیص:")
print("-" * 50)

if result:
    for i, (bbox, text, confidence) in enumerate(result):
        print(f"🔹 نتیجه {i + 1}:")
        print(f"   📝 متن: {text}")
        print(f"   📊 اطمینان: {confidence:.2%}")

        # رسم کادر روی تصویر اصلی
        for point in bbox:
            cv2.circle(img, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

        # رسم مستطیل دور متن
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(img, text, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
else:
    print("❌ هیچ متنی تشخیص داده نشد!")

# ===== ۶. ذخیره و نمایش تصویر =====
output_path = os.path.join(base_dir, "easyocr_result.jpg")
cv2.imwrite(output_path, img)
print(f"✅ تصویر با کادرها در {output_path} ذخیره شد.")

cv2.imshow("EasyOCR Result", img)
print("برای بستن تصویر، هر کلیدی را بزنید...")
cv2.waitKey(0)
cv2.destroyAllWindows()