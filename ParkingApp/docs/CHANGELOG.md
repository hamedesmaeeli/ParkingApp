# Changelog

All notable changes to this project will be documented here.

---

## Sprint 1 - Foundation & ALPR Architecture

### Step 1.1 ✅
- ایجاد Package جدید alpr
- ایجاد ALPREngine
- اتصال اولیه CameraWidget به ALPREngine

### Step 1.2 ✅
- ایجاد models.py
- ایجاد PlateResult
- استفاده از Type Hint

### Step 1.3 ✅
- ایجاد detector.py
- ایجاد ocr.py
- ایجاد validator.py
- ایجاد tracker.py

### Step 1.4 ✅
- Refactor CameraWidget
- انتقال منطق پردازش تصویر
- استفاده از ALPREngine

### Step 1.5 ✅
- انتقال Contour Detection به detector.py
- استفاده از PlateResult در سراسر ALPR

### Step 1.6 ✅
- افزودن Logging (پایه)
- مدیریت خطا (Exception Handling)

### Step 1.7 ✅
- طراحی Interface برای Detector و OCR
- آماده‌سازی config.yaml

### Step 1.8 ✅ (NEW)
- اضافه کردن حالت Mock به ALPREngine برای تست بدون نیاز به تشخیص واقعی
- یکپارچه‌سازی ALPREngine با EntryWidget
- اضافه کردن رسم کادر (Bounding Box) روی تصاویر بارگذاری شده
- رفع مشکل پر کردن فیلدهای پلاک از PlateResult
- تست کامل زنجیره: بارگذاری عکس → تشخیص → نمایش کادر → پر کردن فیلدها
- حذف تب تکراری دوربین از main_window

---

## Sprint 2 - Plate Detection (YOLO) - ⏳ در انتظار شروع

### Step 2.1 ⬜
- [ ] نصب Ultralytics

### Step 2.2 ⬜
- [ ] بارگذاری مدل YOLO

### Step 2.3 ⬜
- [ ] تشخیص پلاک با YOLO

### Step 2.4 ⬜
- [ ] Crop Plate

### Step 2.5 ⬜
- [ ] Multi Plate Detection

### Step 2.6 ⬜
- [ ] نمایش Bounding Box

### Step 2.7 ⬜
- [ ] Benchmark روی CPU