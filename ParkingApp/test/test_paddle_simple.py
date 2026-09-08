"""
تست PaddleOCR روی تصویر پلاک با پیش‌پردازش
"""

from paddleocr import PaddleOCR
import cv2
import os

print("🚀 تست PaddleOCR روی تصویر پلاک...")

# ===== ۱. راه‌اندازی OCR =====
try:
    ocr = PaddleOCR(
        lang='fa',
        use_textline_orientation=True,
        det_db_thresh=0.1,
        det_db_box_thresh=0.1,
        drop_score=0.1
    )
    print("✅ PaddleOCR مقداردهی شد.")
except Exception as e:
    print(f"❌ خطا در مقداردهی: {e}")
    exit()

# ===== ۲. بارگذاری تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "test_pelak_crop1.jpg")

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    exit()

img = cv2.imread(image_path)
if img is None:
    print("❌ خطا در خواندن تصویر!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ===== ۳. پیش‌پردازش تصویر =====
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

processed_img = preprocess_image(img)

# ===== ۴. تشخیص متن =====
print("🔄 در حال تشخیص متن...")
result = ocr.ocr(processed_img, cls=True)

# ===== ۵. نمایش نتایج =====
print("\n📊 نتایج تشخیص:")
print("-" * 50)

if result and result[0]:
    for i, line in enumerate(result[0]):
        bbox = line[0]
        text = line[1][0]
        confidence = line[1][1]

        print(f"🔹 نتیجه {i+1}:")
        print(f"   📝 متن: {text}")
        print(f"   📊 اطمینان: {confidence:.2%}")

        # رسم کادر
        for point in bbox:
            cv2.circle(img, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)
else:
    print("❌ هیچ متنی تشخیص داده نشد!")

# ===== ۶. نمایش تصویر =====
cv2.imshow("PaddleOCR Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()