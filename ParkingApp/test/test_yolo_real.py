"""
تست YOLO روی یک عکس واقعی
"""

from alpr.engine import ALPREngine
import cv2

print("🚀 شروع تست YOLO...")

# بارگذاری تصویر
img_path = "test_pelak2.jpg"  # نام تصویر خود را قرار دهید
img = cv2.imread(img_path)

if img is None:
    print(f"❌ تصویر {img_path} پیدا نشد!")
    exit()

print(f"✅ تصویر با سایز {img.shape[1]}x{img.shape[0]} بارگذاری شد.")

# ایجاد موتور ALPR در حالت واقعی
engine = ALPREngine(mock_mode=False)

# پردازش تصویر
print("🔄 در حال پردازش تصویر...")
results = engine.process(img)

# نمایش نتایج
print(f"\n📊 تعداد نتایج: {len(results)}")
for i, result in enumerate(results):
    print(f"   نتیجه {i + 1}:")
    print(f"      پلاک: {result.plate}")
    print(f"      اطمینان: {result.confidence:.2f}")
    print(f"      کادر: {result.bbox}")

    # رسم کادر روی تصویر
    x, y, w, h = result.bbox
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(img, result.plate, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# نمایش تصویر
if len(results) > 0:
    cv2.imshow("YOLO Detection Result", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("❌ هیچ پلاکی تشخیص داده نشد!")