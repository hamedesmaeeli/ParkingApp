# ParkingSmart Standard Roadmap

**Project:** ParkingSmart Standard
**Version:** 1.0.0-alpha
**Status:** 🚧 Active Development
**Target Platform:** Windows 10/11
**Deployment:** Offline (CPU Only)
**Language:** Python 3.10 + PyQt5

---

# Sprint 1 — Foundation & ALPR Architecture ✅ (COMPLETED)

هدف: ایجاد معماری استاندارد پروژه و جداسازی کامل UI از موتور پلاک‌خوان.

## Step 1.1 ✅
- [x] ایجاد Package جدید alpr
- [x] ایجاد ALPREngine
- [x] اتصال اولیه CameraWidget به ALPREngine
- [x] رفع مشکلات Import

## Step 1.2 ✅
- [x] ایجاد models.py
- [x] ایجاد PlateResult
- [x] حذف مدل‌های Dictionary
- [x] استفاده از Type Hint

## Step 1.3 ✅
- [x] ایجاد detector.py
- [x] ایجاد ocr.py
- [x] ایجاد validator.py
- [x] ایجاد tracker.py

## Step 1.4 ✅
- [x] Refactor CameraWidget
- [x] انتقال منطق پردازش تصویر
- [x] کاهش وابستگی UI
- [x] استفاده از ALPREngine

## Step 1.5 ✅
- [x] انتقال Contour Detection به detector.py
- [x] حذف منطق پردازش تصویر از UI
- [x] حفظ عملکرد فعلی

## Step 1.6 ✅
- [x] logging (پایه)
- [x] Exception Handling
- [x] Error Messages

## Step 1.7 ✅
- [x] Interface Detector
- [x] Interface OCR
- [x] آماده‌سازی config.yaml

## Step 1.8 ✅ (NEW)
- [x] اضافه کردن حالت Mock به ALPREngine
- [x] یکپارچه‌سازی با EntryWidget
- [x] رسم کادر روی تصاویر
- [x] تست کامل زنجیره ارتباطات

---

# Sprint 2 — Plate Detection with YOLO (⏳ NEXT)

هدف: جایگزینی موتور آزمایشی با تشخیص واقعی پلاک با استفاده از YOLO.

## Step 2.1 ⬜
- [ ] نصب Ultralytics

## Step 2.2 ⬜
- [ ] بارگذاری مدل YOLO

## Step 2.3 ⬜
- [ ] تشخیص پلاک

## Step 2.4 ⬜
- [ ] Crop Plate

## Step 2.5 ⬜
- [ ] Multi Plate Detection

## Step 2.6 ⬜
- [ ] نمایش Bounding Box

## Step 2.7 ⬜
- [ ] Benchmark روی CPU