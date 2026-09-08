## 📄 **فایل کامل `DATABASE.md`**

```markdown
# ParkingSmart Database Schema

**Database:** SQLite  
**Version:** 1.0.0  
**Last Updated:** 2026-07-22

---

## Overview

این مستندات ساختار دیتابیس پروژه ParkingSmart را توضیح می‌دهد. دیتابیس از SQLite استفاده می‌کند و شامل جداول زیر است:

- **cards**: مدیریت کارت‌های فیزیکی پارکینگ
- **active_cars**: خودروهای حاضر در پارکینگ
- **history**: تاریخچه کامل ترددها
- **settings**: تنظیمات سیستم
- **users**: مدیریت کاربران (اختیاری)

---

## Tables

### cards 🎫

جدول مدیریت کارت‌های فیزیکی پارکینگ.

| Column | Type | Description |
|--------|------|-------------|
| `card_number` | TEXT (PK) | شماره منحصر‌به‌فرد کارت (۵ رقمی) |
| `status` | TEXT | وضعیت کارت: `'active'`, `'in_use'`, `'expired'` |
| `assigned_to` | TEXT | پلاک خودرو (در صورت استفاده) - FK به active_cars.plate |
| `assigned_at` | DATETIME | زمان اختصاص کارت به خودرو |
| `created_at` | DATETIME | زمان ایجاد کارت در سیستم |

**نکات:**
- کارت‌های `'active'` آماده استفاده هستند.
- کارت‌های `'in_use'` به یک خودرو اختصاص یافته‌اند.
- کارت‌های `'expired'` غیرفعال هستند و قابل استفاده نمی‌باشند.

**SQL:**
```sql
CREATE TABLE cards (
    card_number TEXT PRIMARY KEY,
    status TEXT DEFAULT 'active',
    assigned_to TEXT,
    assigned_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES active_cars(plate)
);
```

---

### active_cars 🚗

جدول خودروهای حاضر در پارکینگ.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | شناسه خودکار رکورد |
| `plate` | TEXT (UNIQUE) | پلاک کامل خودرو (مانند `12الف345-67`) |
| `card_number` | TEXT (FK) | شماره کارت اختصاص‌یافته |
| `entry_time` | DATETIME | زمان ورود به پارکینگ |
| `operator` | TEXT | نام اپراتور ثبت‌کننده |
| `part1` | TEXT | دو رقم اول پلاک |
| `letter` | TEXT | حرف پلاک |
| `part2` | TEXT | سه رقم وسط پلاک |
| `part3` | TEXT | دو رقم آخر پلاک |
| `image_path` | TEXT | مسیر تصویر ثبت‌شده (اختیاری) |

**نکات:**
- یک خودرو فقط یک بار در این جدول می‌تواند باشد (ورود تکراری ممنوع).
- ارتباط با جدول `cards` از طریق `card_number` برقرار است.

**SQL:**
```sql
CREATE TABLE active_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT UNIQUE NOT NULL,
    card_number TEXT UNIQUE NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    operator TEXT,
    part1 TEXT,
    letter TEXT,
    part2 TEXT,
    part3 TEXT,
    image_path TEXT,
    FOREIGN KEY (card_number) REFERENCES cards(card_number)
);
```

---

### history 📜

جدول تاریخچه کامل ترددهای پارکینگ.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | شناسه خودکار رکورد |
| `plate` | TEXT | پلاک کامل خودرو |
| `card_number` | TEXT | شماره کارت استفاده‌شده |
| `entry_time` | DATETIME | زمان ورود |
| `exit_time` | DATETIME | زمان خروج |
| `duration` | INTEGER | مدت زمان پارک (دقیقه) |
| `cost` | INTEGER | هزینه نهایی (تومان) |
| `operator` | TEXT | نام اپراتور |
| `part1` | TEXT | دو رقم اول پلاک |
| `letter` | TEXT | حرف پلاک |
| `part2` | TEXT | سه رقم وسط پلاک |
| `part3` | TEXT | دو رقم آخر پلاک |

**نکات:**
- این جدول فقط خواندنی است (برای گزارش‌گیری).
- داده‌ها از `active_cars` پس از خروج خودرو به اینجا منتقل می‌شوند.

**SQL:**
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT NOT NULL,
    card_number TEXT,
    entry_time DATETIME,
    exit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER,
    cost INTEGER,
    operator TEXT,
    part1 TEXT,
    letter TEXT,
    part2 TEXT,
    part3 TEXT
);
```

---

### settings ⚙️

جدول تنظیمات سیستم.

| Column | Type | Description |
|--------|------|-------------|
| `key` | TEXT (PK) | کلید تنظیمات |
| `value` | TEXT | مقدار تنظیمات |
| `updated_at` | DATETIME | زمان آخرین بروزرسانی |

**تنظیمات پیش‌فرض:**
| کلید | مقدار | توضیح |
|------|-------|-------|
| `hourly_rate` | `5000` | نرخ ساعتی پارکینگ (تومان) |
| `free_minutes` | `15` | دقیقه رایگان اولیه |
| `max_capacity` | `100` | حداکثر ظرفیت پارکینگ |
| `company_name` | `"پارکینگ هوشمند"` | نام پارکینگ |

**SQL:**
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### users 👤 (اختیاری)

جدول مدیریت کاربران سیستم.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | شناسه خودکار |
| `username` | TEXT (UNIQUE) | نام کاربری |
| `password_hash` | TEXT | هش رمز عبور |
| `role` | TEXT | نقش کاربر: `'admin'`, `'operator'` |
| `created_at` | DATETIME | زمان ایجاد |

**SQL:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'operator',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔗 **Relationships**

```
┌─────────────────┐         ┌─────────────────┐
│     cards        │         │   active_cars   │
│─────────────────│         │─────────────────│
│ card_number (PK)│◄────────│ card_number (FK)│
│ status           │         │ plate (PK)      │
│ assigned_to      │────────►│ entry_time      │
│ assigned_at      │         │ operator        │
└─────────────────┘         └─────────────────┘
                                           │
                                           │ (خروج خودرو)
                                           ▼
                              ┌─────────────────┐
                              │    history      │
                              │─────────────────│
                              │ plate           │
                              │ card_number     │
                              │ entry_time      │
                              │ exit_time       │
                              │ duration        │
                              │ cost            │
                              └─────────────────┘
```

---

## 📊 **Sample Data**

### cards
```sql
INSERT INTO cards (card_number, status) VALUES
('00001', 'active'),
('00002', 'active'),
...
('00100', 'active');
```

### settings
```sql
INSERT INTO settings (key, value) VALUES
('hourly_rate', '5000'),
('free_minutes', '15'),
('max_capacity', '100');
```

---

## 🛠️ **Migrations**

برای به‌روزرسانی دیتابیس به نسخه جدید، از فایل‌های migration استفاده می‌شود.

### Migration 1: Add cards table
```sql
-- migration_001.sql
CREATE TABLE IF NOT EXISTS cards (
    card_number TEXT PRIMARY KEY,
    status TEXT DEFAULT 'active',
    assigned_to TEXT,
    assigned_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد کارت‌های اولیه
INSERT INTO cards (card_number) 
SELECT printf('%05d', value) 
FROM generate_series(1, 100);
```

### Migration 2: Update active_cars
```sql
-- migration_002.sql
ALTER TABLE active_cars ADD COLUMN card_number TEXT;
ALTER TABLE active_cars ADD COLUMN image_path TEXT;

-- ایجاد ارتباط با cards
CREATE INDEX idx_active_cars_card ON active_cars(card_number);
```

---

## 🔐 **Backup & Restore**

### Backup
```sql
-- ایجاد پشتیبان
VACUUM INTO 'backup.db';
```

### Restore
```bash
# کپی فایل پشتیبان به جای فایل اصلی
copy backup.db parking.db
```

---

## 📋 **Changelog**

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-22 | نسخه اولیه دیتابیس با جداول cards, active_cars, history, settings |
| 0.3.0 | 2026-07-15 | اضافه شدن validator و ocr |
| 0.2.0 | 2026-07-10 | اضافه شدن یافتن خودرو با کارت |
| 0.1.0 | 2026-07-01 | ساختار اولیه دیتابیس |
```

---

## 🚀 **مرحله بعد**

آیا این فایل `DATABASE.md` مورد تأیید شماست؟ اگر تغییر یا اضافه‌ای مد نظر دارید، بفرمایید تا اصلاح کنم. در غیر این صورت، می‌توانیم شروع به پیاده‌سازی Step 4.1 (مدیریت کارت‌ها در دیتابیس) کنیم. 😊