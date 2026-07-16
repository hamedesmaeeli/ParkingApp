exit
"""
تست مدل تخصصی تشخیص پلاک ایران
YOLOv8m_Iran_license_plate_detection
با استفاده از عکس پیش‌فرض در مسیر پروژه
"""

from ultralytics import YOLO
import cv2
import os

def test_iran_plate_model(image_name="test_pelak1.jpg"):
    """
    تست مدل تشخیص پلاک ایران روی یک تصویر مشخص

    Args:
        image_name (str): نام فایل تصویر در مسیر پروژه
    """

    print("🚀 شروع تست مدل تشخیص پلاک ایران...")
    print("=" * 50)

    # ===== مسیرهای فایل‌ها =====
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "YOLOv8m_Iran_license_plate_detection.pt")
    image_path = os.path.join(base_dir, image_name)
    output_path = os.path.join(base_dir, "output_iran_plate.jpg")

    # ===== ۱. بررسی وجود فایل مدل =====
    print("🔄 در حال بارگذاری مدل...")
    if not os.path.exists(model_path):
        print(f"❌ فایل مدل در مسیر {model_path} پیدا نشد!")
        print("لطفاً مدل را از Hugging Face دانلود کنید:")
        print("https://huggingface.co/shalchianmh/Iran_license_plate_detection_YOLOv8m")
        return

    try:
        model = YOLO(model_path)
        print("✅ مدل با موفقیت بارگذاری شد!")
    except Exception as e:
        print(f"❌ خطا در بارگذاری مدل: {e}")
        return

    # ===== ۲. بررسی وجود فایل تصویر =====
    if not os.path.exists(image_path):
        print(f"❌ تصویر {image_name} در مسیر {image_path} پیدا نشد!")
        print("لطفاً یک تصویر از ماشین با پلاک در مسیر پروژه قرار دهید.")
        return

    img = cv2.imread(image_path)
    print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

    # ===== ۳. تشخیص پلاک با مدل =====
    print("🔄 در حال تشخیص پلاک...")
    results = model(image_path)

    # ===== ۴. نمایش نتایج =====
    print("\n📊 نتایج تشخیص:")
    print("-" * 50)

    img_with_boxes = img.copy()
    detected_count = 0

    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                x_center, y_center, w, h = box.xywh[0].cpu().numpy().astype(int)
                x = int(x_center - w/2)
                y = int(y_center - h/2)
                confidence = float(box.conf[0].cpu().numpy())
                detected_count += 1

                # اطلاعات پلاک
                print(f"🔹 پلاک {detected_count}:")
                print(f"   📍 موقعیت: ({x}, {y})")
                print(f"   📏 اندازه: {w}x{h}")
                print(f"   📊 اطمینان: {confidence:.2%}")

                # رسم کادر سبز
                cv2.rectangle(img_with_boxes, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(img_with_boxes, f"Plate {detected_count}: {confidence:.0%}",
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (0, 255, 0), 2)

    if detected_count == 0:
        print("❌ هیچ پلاکی تشخیص داده نشد!")
    else:
        print(f"\n✅ {detected_count} پلاک تشخیص داده شد.")

    # ===== ۵. نمایش تصویر =====
    print("\n📸 نمایش تصویر با کادرهای تشخیص داده شده...")
    cv2.imshow("Iranian Plate Detection - YOLOv8m", img_with_boxes)
    print("برای بستن تصویر، هر کلیدی را بزنید...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # ===== ۶. ذخیره تصویر =====
    cv2.imwrite(output_path, img_with_boxes)
    print(f"✅ تصویر نهایی در {output_path} ذخیره شد.")

    print("\n🎉 تست کامل شد!")

if __name__ == "__main__":
    # ===== نام عکس را اینجا تغییر دهید =====
    test_iran_plate_model("test_pelak3.jpg")  # ← نام عکس خود را قرار دهید