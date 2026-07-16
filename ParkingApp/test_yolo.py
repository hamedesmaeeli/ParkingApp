from ultralytics import YOLO
import cv2

# ===== استفاده از مدل‌های پیش‌فرض Ultralytics =====
print("🔄 در حال بارگذاری مدل YOLO...")
try:
    # مدل پایه YOLOv8n (سریع‌ترین و سبک‌ترین)
    model = YOLO("yolov8n.pt")  # این مدل حتماً وجود دارد
    print("✅ مدل YOLOv8n بارگذاری شد.")

    # یک تست ساده با یک تصویر ساختگی
    import numpy as np

    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    results = model(dummy_image)
    print(f"✅ تست اولیه با موفقیت انجام شد. تعداد نتایج: {len(results)}")

except Exception as e:
    print(f"❌ خطا در بارگذاری مدل: {e}")