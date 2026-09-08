"""
تست ALPREngine با YOLO + HezarAI
"""

import cv2
import os
from alpr.engine import ALPREngine

print("🚀 تست ALPREngine...")
print("=" * 50)

# ===== ۱. ایجاد موتور =====
engine = ALPREngine(mock_mode=False)

# ===== ۲. بارگذاری تصویر =====
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "Vehicle Plates/214.png")

if not os.path.exists(image_path):
    print(f"❌ تصویر {image_path} پیدا نشد!")
    exit()

img = cv2.imread(image_path)
print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ===== ۳. پردازش =====
print("\n🔄 در حال پردازش تصویر...")
results = engine.process(img)

# ===== ۴. نمایش نتایج =====
print("\n📊 نتایج نهایی:")
print("-" * 40)

if results:
    for i, result in enumerate(results):
        print(f"🔹 نتیجه {i+1}:")
        print(f"   📝 پلاک: {result.plate}")
        print(f"   📊 اطمینان: {result.confidence:.2%}")
        print(f"   📍 کادر: {result.bbox}")
else:
    print("❌ هیچ پلاکی تشخیص داده نشد!")

# ===== ۵. ذخیره تصویر با کادر =====
results, vis_img = engine.process_with_visualization(img)
cv2.imwrite("output_engine_result.jpg", vis_img)
print("\n✅ تصویر نهایی در output_engine_result.jpg ذخیره شد.")

print("\n🎉 تست کامل شد!")