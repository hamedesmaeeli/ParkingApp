# ParkingSmart Standard Roadmap

**Project:** ParkingSmart Standard

**Version:** 1.0.0-alpha

**Status:** 🚧 Active Development

**Target Platform:** Windows 10/11

**Deployment:** Offline (CPU Only)

**Language:** Python 3.10 + PyQt5

---

# Vision

توسعه یک نرم‌افزار مدیریت هوشمند پارکینگ برای پارکینگ‌های کوچک و متوسط که:

- بدون اینترنت کار کند.
- روی کامپیوترهای معمولی (بدون GPU) اجرا شود.
- پلاک خودروهای ایرانی را با دقت بالا تشخیص دهد.
- نصب و نگهداری ساده‌ای داشته باشد.
- قابلیت توسعه به نسخه Enterprise را داشته باشد.

---

# Version Roadmap

| Version | Status | Description |
|----------|--------|-------------|
| v0.1 | 🚧 | Foundation |
| v0.2 | ⬜ | ALPR Engine |
| v0.3 | ⬜ | OCR |
| v0.4 | ⬜ | Parking Logic |
| v0.5 | ⬜ | Reports |
| v0.6 | ⬜ | Stability |
| v0.7 | ⬜ | Beta |
| v1.0 | ⬜ | Production Release |

---

# Sprint 1 — Foundation & ALPR Architecture

هدف:
ایجاد معماری استاندارد پروژه و جداسازی کامل UI از موتور پلاک‌خوان.

## Step 1.1 ✅

- [x] ایجاد Package جدید alpr
- [x] ایجاد ALPREngine
- [x] اتصال اولیه CameraWidget به ALPREngine
- [x] رفع مشکلات Import

Commit

Sprint1-Step1 Create ALPR package

---

## Step 1.2 🚧

ایجاد مدل‌های داده

- [ ] ایجاد models.py
- [ ] ایجاد PlateResult
- [ ] حذف مدل‌های Dictionary
- [ ] استفاده از Type Hint

Commit

Sprint1-Step2 Create PlateResult model

---

## Step 1.3

تکمیل ساختار ALPR

- [ ] ایجاد detector.py
- [ ] ایجاد ocr.py
- [ ] ایجاد validator.py
- [ ] ایجاد tracker.py

Commit

Sprint1-Step3 Create ALPR modules

---

## Step 1.4

Refactor CameraWidget

- [ ] انتقال منطق پردازش تصویر
- [ ] کاهش وابستگی UI
- [ ] استفاده از ALPREngine

Commit

Sprint1-Step4 Refactor CameraWidget

---

## Step 1.5

Detector Refactor

- [ ] انتقال Contour Detection به detector.py
- [ ] حذف منطق پردازش تصویر از UI
- [ ] حفظ عملکرد فعلی

Commit

Sprint1-Step5 Move detector logic

---

## Step 1.6

Logging & Error Handling

- [ ] logging
- [ ] Exception Handling
- [ ] Error Messages

Commit

Sprint1-Step6 Improve logging

---

## Step 1.7

Prepare for YOLO

- [ ] Interface Detector
- [ ] Interface OCR
- [ ] آماده‌سازی config.yaml

Commit

Sprint1-Step7 Prepare YOLO interface

---

# Sprint 2 — Plate Detection

هدف:
جایگزینی موتور آزمایشی با تشخیص واقعی پلاک.

## Step 2.1

- [ ] نصب Ultralytics

## Step 2.2

- [ ] بارگذاری مدل YOLO

## Step 2.3

- [ ] تشخیص پلاک

## Step 2.4

- [ ] Crop Plate

## Step 2.5

- [ ] Multi Plate Detection

## Step 2.6

- [ ] نمایش Bounding Box

## Step 2.7

- [ ] Benchmark روی CPU

---

# Sprint 3 — OCR

هدف:
خواندن دقیق پلاک‌های ایرانی.

- [ ] نصب PaddleOCR
- [ ] خواندن متن پلاک
- [ ] اعتبارسنجی
- [ ] اصلاح متن
- [ ] Confidence Score

---

# Sprint 4 — Parking Core

- [ ] ثبت ورود
- [ ] ثبت خروج
- [ ] جلوگیری از ثبت تکراری
- [ ] ذخیره تصویر
- [ ] SQLite

---

# Sprint 5 — Parking Business Logic

- [ ] محاسبه زمان توقف
- [ ] محاسبه تعرفه
- [ ] تخفیف
- [ ] اشتراک
- [ ] چاپ رسید

---

# Sprint 6 — Reports

- [ ] گزارش روزانه
- [ ] گزارش ماهانه
- [ ] Excel
- [ ] PDF
- [ ] Dashboard

---

# Sprint 7 — Stability

- [ ] Backup
- [ ] Restore
- [ ] Reconnect Camera
- [ ] Config Manager
- [ ] Logging

---

# Sprint 8 — Release

- [ ] Installer
- [ ] User Manual
- [ ] Final Testing
- [ ] Release Notes
- [ ] Version 1.0.0

---

# Definition of Done

هر Step فقط زمانی Done محسوب می‌شود که:

- پروژه بدون خطا اجرا شود.
- Commit ثبت شده باشد.
- CHANGELOG به‌روزرسانی شده باشد.
- TEST_PLAN پاس شده باشد.
- مستندات به‌روز شده باشند.

---

# Long Term Roadmap

## Version 1.1

- چند دوربین
- بهبود OCR
- افزایش سرعت
- UI Improvements

---

## Version 2.0 Enterprise

- PostgreSQL
- Client/Server
- Multi Parking
- REST API
- Web Dashboard
- Central Management
- Role Management

---

# Success Criteria

نسخه 1.0 باید بتواند:

- پلاک خودروهای ایرانی را تشخیص دهد.
- ورود و خروج خودرو را ثبت کند.
- هزینه پارکینگ را محاسبه کند.
- گزارش تولید کند.
- بدون GPU و بدون اینترنت روی یک کامپیوتر معمولی اجرا شود.
- حداقل در ۵ پارکینگ واقعی قابل استقرار باشد.