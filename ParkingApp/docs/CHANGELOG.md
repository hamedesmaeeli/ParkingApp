# Changelog

All notable changes to this project will be documented here.

---

## Sprint 4 — Parking Logic with Card System 🚧

### Step 4.1 — Card Management 🎫
- [ ] ایجاد جدول `cards` در دیتابیس
- [ ] پیاده‌سازی متدهای مدیریت کارت
- [ ] ایجاد کارت‌های اولیه (۱۰۰ کارت فعال)

### Step 4.2 — Entry with Card 🚗
- [ ] خواندن کارت توسط کارت‌خوان ورودی
- [ ] رزرو کارت (تغییر وضعیت به 'in_use')
- [ ] تشخیص پلاک توسط دوربین (ALPR)
- [ ] ثبت ورود در دیتابیس (ارتباط کارت و پلاک)
- [ ] تحویل کارت به راننده

### Step 4.3 — Exit with Card 🚙
- [ ] دریافت کارت از راننده
- [ ] خواندن کارت توسط کارت‌خوان خروجی
- [ ] اعتبارسنجی کارت
- [ ] محاسبه مدت زمان و هزینه
- [ ] ثبت خروج و آزادسازی کارت

### Step 4.4 — UI Updates 🖥️
- [ ] به‌روزرسانی EntryWidget برای کارت‌خوان ورودی
- [ ] به‌روزرسانی ExitWidget برای کارت‌خوان خروجی
- [ ] اضافه کردن وضعیت کارت‌ها در UI

### Step 4.5 — Error Handling ⚠️
- [ ] مدیریت کارت نامعتبر
- [ ] مدیریت کارت گمشده
- [ ] ورود دستی پلاک (در صورت خرابی دوربین)
- [ ] خروج دستی (در صورت خرابی کارت‌خوان)

---

## Sprint 3 — OCR with HezarAI ✅ (Completed)

### Step 3.1 ✅
- [x] نصب HezarAI

### Step 3.2 ✅
- [x] بارگذاری مدل HezarAI

### Step 3.3 ✅
- [x] خواندن متن پلاک

### Step 3.4 ✅
- [x] اعتبارسنجی خروجی

### Step 3.5 ✅
- [x] اصلاح متن (Post-processing)

### Step 3.6 ✅
- [x] Confidence Score

### Step 3.7 ✅
- [x] یکپارچه‌سازی با EntryWidget

---

## Sprint 2 — Plate Detection with YOLO ✅ (Completed)

### Step 2.1 ✅
- [x] نصب Ultralytics

### Step 2.2 ✅
- [x] بارگذاری مدل YOLO

### Step 2.3 ✅
- [x] تشخیص پلاک با YOLO

### Step 2.4 ✅
- [x] Crop Plate

### Step 2.5 ✅
- [x] Multi Plate Detection

### Step 2.6 ✅
- [x] نمایش Bounding Box

### Step 2.7 ✅
- [x] Benchmark روی CPU

---

## Sprint 1 — Foundation & ALPR Architecture ✅ (Completed)

### Step 1.1 ✅
- [x] ایجاد Package جدید alpr
- [x] ایجاد ALPREngine
- [x] اتصال اولیه CameraWidget به ALPREngine

### Step 1.2 ✅
- [x] ایجاد models.py
- [x] ایجاد PlateResult

### Step 1.3 ✅
- [x] ایجاد detector.py
- [x] ایجاد ocr.py
- [x] ایجاد validator.py
- [x] ایجاد tracker.py

### Step 1.4 ✅
- [x] Refactor CameraWidget

### Step 1.5 ✅
- [x] انتقال Contour Detection به detector.py

### Step 1.6 ✅
- [x] logging
- [x] Exception Handling

### Step 1.7 ✅
- [x] Interface Detector
- [x] Interface OCR

### Step 1.8 ✅
- [x] اضافه کردن Mock Mode به ALPREngine
- [x] یکپارچه‌سازی با EntryWidget