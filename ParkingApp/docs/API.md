# API Documentation - ParkingSmart

**Version:** 1.0.0  
**Last Updated:** 2026-07-22

---

## Database API

### Card Management

#### `get_available_card()`
دریافت یک کارت موجود ('active').

**Returns:** `str` - شماره کارت یا `None` اگر کارتی موجود نباشد.

---

#### `reserve_card(card_number)`
رزرو کارت (تغییر وضعیت به 'in_use').

**Args:**
- `card_number` (str): شماره کارت

**Raises:** `Exception` اگر کارت در دسترس نباشد.

---

#### `release_card(card_number)`
آزادسازی کارت (تغییر وضعیت به 'active').

**Args:**
- `card_number` (str): شماره کارت

---

#### `get_card_status(card_number)`
دریافت وضعیت کارت.

**Args:**
- `card_number` (str): شماره کارت

**Returns:** `tuple` - (status, assigned_to) یا `None`

---

### Entry & Exit

#### `car_entry(plate_data)`
ثبت ورود خودرو.

**Args:**
- `plate_data` (dict): اطلاعات پلاک شامل `plate`, `operator`, `part1`, `letter`, `part2`, `part3`

**Returns:** `str` - شماره کارت اختصاص‌یافته

**Raises:** `Exception` اگر خودرو قبلاً وارد شده باشد.

---

#### `car_exit(card_number)`
ثبت خروج خودرو با کارت.

**Args:**
- `card_number` (str): شماره کارت

**Returns:** `dict` - اطلاعات خروج شامل `plate`, `duration`, `cost`

**Raises:** `Exception` اگر کارت نامعتبر باشد.

---

#### `get_active_cars()`
دریافت لیست خودروهای حاضر.

**Returns:** `list` - لیست دیکشنری‌های خودروها

---

#### `get_history(filters)`
دریافت تاریخچه ترددها.

**Args:**
- `filters` (dict): فیلترهای تاریخ، پلاک، اپراتور

**Returns:** `list` - لیست دیکشنری‌های تاریخچه

---

### Settings

#### `get_setting(key)`
دریافت مقدار تنظیمات.

**Args:**
- `key` (str): کلید تنظیمات

**Returns:** `str` - مقدار تنظیمات

---

#### `set_setting(key, value)`
تنظیم مقدار تنظیمات.

**Args:**
- `key` (str): کلید تنظیمات
- `value` (str): مقدار جدید

---

## ALPR API

### `ALPREngine.process(frame)`
پردازش تصویر و تشخیص پلاک.

**Args:**
- `frame` (np.ndarray): تصویر ورودی

**Returns:** `list` - لیست `PlateResult`

---

### `PlateResult`
نتیجه تشخیص پلاک.

| Attribute | Type | Description |
|-----------|------|-------------|
| `plate` | str | متن پلاک تشخیص داده شده |
| `confidence` | float | درصد اطمینان |
| `bbox` | tuple | مختصات کادر (x, y, w, h) |
| `image` | np.ndarray | تصویر برش‌خورده پلاک |

---

## UI API

### Signal: `EntryWidget.car_entered(plate_data)`
وقتی خودرو وارد می‌شود.

**Args:**
- `plate_data` (dict): اطلاعات پلاک

---

### Signal: `ExitWidget.car_exited(data)`
وقتی خودرو خارج می‌شود.

**Args:**
- `data` (dict): اطلاعات خروج

---

### Signal: `CameraWidget.plate_detected(plate)`
وقتی پلاکی تشخیص داده می‌شود.

**Args:**
- `plate` (str): متن پلاک