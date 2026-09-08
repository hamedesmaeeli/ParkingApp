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
- از سیستم کارت‌های فیزیکی برای مدیریت ورود و خروج استفاده کند.
- نصب و نگهداری ساده‌ای داشته باشد.
- قابلیت توسعه به نسخه Enterprise را داشته باشد.

---

# Version Roadmap

| Version | Status | Description |
|----------|--------|-------------|
| v0.1 | ✅ | Foundation & ALPR Architecture |
| v0.2 | ✅ | Plate Detection with YOLO |
| v0.3 | ✅ | OCR with HezarAI |
| v0.4 | 🚧 | Parking Logic with Card System |
| v0.5 | ⬜ | Reports & Dashboard |
| v0.6 | ⬜ | Stability & Optimization |
| v0.7 | ⬜ | Beta Testing |
| v1.0 | ⬜ | Production Release |

---

# Sprint 1 — Foundation & ALPR Architecture ✅

**هدف:** ایجاد معماری استاندارد پروژه و جداسازی کامل UI از موتور پلاک‌خوان.

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

## Step 1.5 ✅
- [x] انتقال Contour Detection به detector.py
- [x] حذف منطق پردازش تصویر از UI

## Step 1.6 ✅
- [x] logging
- [x] Exception Handling
- [x] Error Messages

## Step 1.7 ✅
- [x] Interface Detector
- [x] Interface OCR
- [x] آماده‌سازی config.yaml

## Step 1.8 ✅
- [x] اضافه کردن Mock Mode به ALPREngine
- [x] یکپارچه‌سازی با EntryWidget
- [x] رسم کادر روی تصاویر

---

# Sprint 2 — Plate Detection with YOLO ✅

**هدف:** جایگزینی موتور آزمایشی با تشخیص واقعی پلاک با استفاده از YOLO.

## Step 2.1 ✅
- [x] نصب Ultralytics

## Step 2.2 ✅
- [x] بارگذاری مدل YOLO

## Step 2.3 ✅
- [x] تشخیص پلاک با YOLO

## Step 2.4 ✅
- [x] Crop Plate

## Step 2.5 ✅
- [x] Multi Plate Detection

## Step 2.6 ✅
- [x] نمایش Bounding Box

## Step 2.7 ✅
- [x] Benchmark روی CPU

---

# Sprint 3 — OCR with HezarAI ✅

**هدف:** خواندن دقیق پلاک‌های ایرانی با استفاده از HezarAI.

## Step 3.1 ✅
- [x] نصب HezarAI

## Step 3.2 ✅
- [x] بارگذاری مدل HezarAI

## Step 3.3 ✅
- [x] خواندن متن پلاک

## Step 3.4 ✅
- [x] اعتبارسنجی خروجی

## Step 3.5 ✅
- [x] اصلاح متن (Post-processing)

## Step 3.6 ✅
- [x] Confidence Score

## Step 3.7 ✅
- [x] یکپارچه‌سازی با EntryWidget

---

# Sprint 4 — Parking Logic with Card System 🚧

**هدف:** پیاده‌سازی منطق کامل پارکینگ با سیستم کارت‌های فیزیکی.

## Step 4.1 — Card Management 🎫
- [ ] ایجاد جدول `cards` در دیتابیس
- [ ] پیاده‌سازی متدهای مدیریت کارت (فعال، غیرفعال، رزرو، آزادسازی)
- [ ] ایجاد کارت‌های اولیه (۱۰۰ کارت فعال)

## Step 4.2 — Entry with Card 🚗
- [ ] خواندن کارت توسط کارت‌خوان ورودی
- [ ] رزرو کارت (تغییر وضعیت به 'in_use')
- [ ] تشخیص پلاک توسط دوربین (ALPR)
- [ ] ثبت ورود در دیتابیس (ارتباط کارت و پلاک)
- [ ] تحویل کارت به راننده

## Step 4.3 — Exit with Card 🚙
- [ ] دریافت کارت از راننده
- [ ] خواندن کارت توسط کارت‌خوان خروجی
- [ ] اعتبارسنجی کارت
- [ ] محاسبه مدت زمان و هزینه
- [ ] ثبت خروج و آزادسازی کارت

## Step 4.4 — UI Updates 🖥️
- [ ] به‌روزرسانی EntryWidget برای کارت‌خوان ورودی
- [ ] به‌روزرسانی ExitWidget برای کارت‌خوان خروجی
- [ ] اضافه کردن وضعیت کارت‌ها در UI

## Step 4.5 — Error Handling ⚠️
- [ ] مدیریت کارت نامعتبر
- [ ] مدیریت کارت گمشده
- [ ] ورود دستی پلاک (در صورت خرابی دوربین)
- [ ] خروج دستی (در صورت خرابی کارت‌خوان)

## Step 4.6 — Testing 🧪
- [ ] تست سناریوی کامل ورود/خروج
- [ ] تست سناریوهای خطا
- [ ] تست همزمان چند خودرو

---

# Sprint 5 — Reports & Dashboard ⬜

**هدف:** ایجاد گزارش‌های مدیریتی و داشبورد.

## Step 5.1 — Daily Reports 📊
- [ ] گزارش روزانه ورود/خروج
- [ ] گزارش درآمد روزانه
- [ ] تعداد خودروهای حاضر

## Step 5.2 — Monthly Reports 📈
- [ ] گزارش ماهانه
- [ ] آمار میانگین
- [ ] نمودارهای تحلیلی

## Step 5.3 — Export 📤
- [ ] خروجی Excel
- [ ] خروجی PDF
- [ ] چاپ گزارش

---

# Sprint 6 — Stability & Optimization ⬜

**هدف:** بهبود پایداری و عملکرد سیستم.

## Step 6.1 — Backup & Restore 💾
- [ ] پشتیبان‌گیری خودکار
- [ ] بازیابی اطلاعات
- [ ] مدیریت خطاهای دیتابیس

## Step 6.2 — Performance 🚀
- [ ] بهینه‌سازی سرعت تشخیص پلاک
- [ ] کاهش مصرف حافظه
- [ ] بهبود مدیریت Thread

## Step 6.3 — Security 🔒
- [ ] رمزنگاری دیتابیس
- [ ] مدیریت کاربران
- [ ] ثبت لاگ‌های امنیتی

---

# Sprint 7 — Beta & Release ⬜

**هدف:** آماده‌سازی برای انتشار نسخه ۱.۰.

## Step 7.1 — Installer 🖥️
- [ ] ساخت فایل نصب (exe)
- [ ] تنظیمات مسیرها
- [ ] ایجاد میانبر

## Step 7.2 — Documentation 📚
- [ ] راهنمای کاربر
- [ ] راهنمای نصب
- [ ] مستندات فنی

## Step 7.3 — Final Testing ✅
- [ ] تست در محیط واقعی
- [ ] تست بار (۱۰۰ خودرو)
- [ ] بازخورد و رفع باگ

## Step 7.4 — Release 🎉
- [ ] انتشار نسخه ۱.۰.۰
- [ ] انتشار در گیت‌هاب
- [ ] تگ نسخه

---

# Long Term Roadmap

## Version 1.1
- [ ] پشتیبانی از چند دوربین
- [ ] بهبود OCR با داده‌های جدید
- [ ] افزایش سرعت تشخیص
- [ ] بهبود UI/UX

## Version 2.0 Enterprise
- [ ] PostgreSQL به جای SQLite
- [ ] معماری Client/Server
- [ ] مدیریت چند پارکینگ
- [ ] REST API
- [ ] داشبورد وب
- [ ] مدیریت مرکزی
- [ ] مدیریت نقش‌ها و دسترسی‌ها

---

# Definition of Done

هر Step فقط زمانی Done محسوب می‌شود که:

- پروژه بدون خطا اجرا شود.
- Commit ثبت شده باشد.
- CHANGELOG به‌روزرسانی شده باشد.
- TEST_PLAN پاس شده باشد.
- مستندات به‌روز شده باشند.

---

# Success Criteria

نسخه ۱.۰ باید بتواند:

- پلاک خودروهای ایرانی را تشخیص دهد.
- ورود و خروج خودرو را با استفاده از کارت‌های فیزیکی ثبت کند.
- هزینه پارکینگ را محاسبه کند.
- گزارش تولید کند.
- بدون GPU و بدون اینترنت روی یک کامپیوتر معمولی اجرا شود.
- حداقل در ۵ پارکینگ واقعی قابل استقرار باشد.