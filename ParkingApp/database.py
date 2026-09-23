"""
مدیریت پایگاه داده SQLite با پشتیبانی از سیستم کارت
نسخه 4.0 - Sprint 4
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading


class ParkingDatabase:
    """مدیریت پایگاه داده SQLite با پشتیبانی همزمانی و سیستم کارت"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance



    def __init__(self, db_path=None):
        if not hasattr(self, 'initialized'):
            # ===== مسیر ثابت بر اساس محل فایل database.py =====
            if db_path is None:
                # مسیر فایل database.py
                current_file = os.path.abspath(__file__)
                # پوشه‌ای که database.py در آن است (ریشه پروژه)
                project_root = os.path.dirname(current_file)
                db_path = os.path.join(project_root, "data", "parking.db")

            self.db_path = db_path
            print(f"📁 [Database] مسیر دیتابیس: {os.path.abspath(self.db_path)}")
            self._ensure_data_dir()
            self.init_database()
            self.initialized = True

    def _ensure_data_dir(self):
        """اطمینان از وجود پوشه‌های مورد نیاز"""
        directories = ['data', 'backups', 'exports', 'captured_plates', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """مدیریت اتصال به پایگاه داده با context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """ایجاد جداول پایگاه داده"""
        with self.get_connection() as conn:
            c = conn.cursor()

            # جدول تنظیمات
            c.execute('''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # جدول کارت‌های پارکینگ
            c.execute('''CREATE TABLE IF NOT EXISTS cards (
                        card_number TEXT PRIMARY KEY,
                        uid TEXT UNIQUE,  -- ← ستون uid اضافه شد
                        status TEXT DEFAULT 'active',
                        assigned_to TEXT,
                        assigned_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

            # جدول خودروهای فعال
            c.execute('''CREATE TABLE IF NOT EXISTS active_cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE NOT NULL,
                plate_part1 TEXT NOT NULL,
                plate_letter TEXT NOT NULL,
                plate_part2 TEXT NOT NULL,
                plate_part3 TEXT,
                card_number TEXT UNIQUE,
                entry_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                entry_image TEXT,
                plate_type TEXT DEFAULT 'personal',
                province TEXT,
                operator_name TEXT,
                notes TEXT,
                FOREIGN KEY (card_number) REFERENCES cards(card_number)
            )''')

            # جدول تاریخچه
            c.execute('''CREATE TABLE IF NOT EXISTS parking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                plate_part1 TEXT,
                plate_letter TEXT,
                plate_part2 TEXT,
                plate_part3 TEXT,
                card_number TEXT,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER NOT NULL,
                duration_hours REAL NOT NULL,
                cost REAL NOT NULL,
                entry_image TEXT,
                exit_image TEXT,
                plate_type TEXT,
                province TEXT,
                discount_type TEXT DEFAULT 'none',
                discount_percent REAL DEFAULT 0,
                final_cost REAL NOT NULL,
                operator_name TEXT,
                payment_method TEXT DEFAULT 'cash',
                payment_status TEXT DEFAULT 'paid',
                notes TEXT
            )''')

            # جدول اپراتورها
            c.execute('''CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'operator',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # ===== جدول کاربران =====
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'operator',
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # ===== جدول لاگ ورود =====
            c.execute('''CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )''')

            # ایندکس‌های جدول کاربران
            c.execute('''CREATE INDEX IF NOT EXISTS idx_users_username 
                        ON users(username)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_login_logs_user 
                        ON login_logs(user_id)''')
            # جدول لاگ رویدادها
            c.execute('''CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                plate_number TEXT,
                card_number TEXT,
                description TEXT,
                operator_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # جدول نرخ‌های ویژه
            c.execute('''CREATE TABLE IF NOT EXISTS special_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                plate_type TEXT DEFAULT 'personal',
                discount_percent REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                start_time TEXT,
                end_time TEXT,
                description TEXT
            )''')

            # ایجاد ایندکس‌ها
            c.execute('''CREATE INDEX IF NOT EXISTS idx_history_plate 
                        ON parking_history(plate_number)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_history_exit_time 
                        ON parking_history(exit_time)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_history_date 
                        ON parking_history(date(exit_time))''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_active_plate 
                        ON active_cars(plate_number)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_active_entry 
                        ON active_cars(entry_time)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_active_card 
                        ON active_cars(card_number)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_cards_status 
                        ON cards(status)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_cards_assigned 
                        ON cards(assigned_to)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_logs_card 
                        ON event_logs(card_number)''')

            # درج داده‌های پیش‌فرض
            self._insert_default_settings(c)
            self._insert_default_operator(c)
            self._insert_default_rates(c)
            self._insert_default_cards(c)

    def _insert_default_settings(self, cursor):
        """درج تنظیمات پیش‌فرض"""
        defaults = [
            ('parking_name', 'پارکینگ اصلی', 'نام پارکینگ'),
            # ===== نرخ‌های جدید =====
            ('first_hour_rate', '10000', 'نرخ ساعت اول (تومان)'),
            ('next_hours_rate', '5000', 'نرخ ساعت دوم به بعد (تومان)'),
            # ========================
            ('free_minutes', '15', 'دقایق رایگان'),
            ('max_daily_cost', '50000', 'سقف هزینه روزانه (تومان)'),
            ('currency_unit', 'تومان', 'واحد پول'),
            ('backup_enabled', 'true', 'فعال بودن بکاپ خودکار'),
            ('backup_interval_hours', '24', 'فاصله بکاپ (ساعت)'),
            ('company_name', 'شرکت مدیریت پارکینگ', 'نام شرکت'),
            ('company_phone', '', 'تلفن شرکت'),
            ('report_header', 'صورتحساب پارکینگ', 'عنوان گزارش'),
            ('camera_index', '0', 'شاخص دوربین'),
            ('camera_resolution', '640x480', 'رزولوشن دوربین'),
            ('auto_detect_plate', 'true', 'تشخیص خودکار پلاک'),
            ('theme', 'طلایی-سرمه‌ای', 'تم برنامه'),
            ('font_size', '9', 'اندازه فونت'),
            # ===== تنظیمات دوربین =====
            ('camera_type', 'webcam', 'نوع دوربین (webcam/ip)'),
            ('camera_index', '0', 'شماره وب‌کم'),
            ('camera_ip', '', 'آدرس IP دوربین'),
            ('camera_port', '554', 'پورت دوربین IP'),
            ('camera_username', 'admin', 'نام کاربری دوربین IP'),
            ('camera_password', '', 'رمز عبور دوربین IP'),
            ('camera_rtsp_path', '/Streaming/Channels/101', 'مسیر RTSP دوربین'),
        ]
        for key, value, desc in defaults:
            cursor.execute('''INSERT OR IGNORE INTO settings (key, value, description) 
                            VALUES (?, ?, ?)''', (key, value, desc))

    def _insert_default_operator(self, cursor):
        """درج اپراتور پیش‌فرض"""
        cursor.execute('''INSERT OR IGNORE INTO operators (username, full_name, role) 
                        VALUES (?, ?, ?)''', ('admin', 'مدیر سیستم', 'admin'))

    def _insert_default_rates(self, cursor):
        """درج نرخ‌های ویژه پیش‌فرض"""
        cursor.execute("DELETE FROM special_rates")

        rates = [
            {'name': 'تاکسی', 'plate_type': 'taxi', 'discount_percent': 30, 'is_active': 1,
             'start_time': None, 'end_time': None, 'description': 'تخفیف ویژه تاکسی‌ها'},
            {'name': 'دولتی', 'plate_type': 'governmental', 'discount_percent': 30, 'is_active': 1,
             'start_time': None, 'end_time': None, 'description': 'تخفیف خودروهای دولتی'},
            {'name': 'شبانه', 'plate_type': 'personal', 'discount_percent': 20, 'is_active': 1,
             'start_time': '22:00', 'end_time': '06:00', 'description': 'تخفیف شبانه (۲۲ تا ۶ صبح)'}
        ]

        for rate in rates:
            try:
                cursor.execute('''
                    INSERT INTO special_rates 
                    (name, plate_type, discount_percent, is_active, 
                     start_time, end_time, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (rate['name'], rate['plate_type'], rate['discount_percent'],
                      rate['is_active'], rate['start_time'], rate['end_time'], rate['description']))
            except Exception as e:
                print(f"Warning: Could not insert rate '{rate['name']}': {e}")

    def _insert_default_cards(self, cursor):
        """درج کارت‌های اولیه"""
        cursor.execute("SELECT COUNT(*) FROM cards")
        if cursor.fetchone()[0] == 0:
            for i in range(1, 101):
                card_number = f"{i:05d}"
                cursor.execute(
                    "INSERT OR IGNORE INTO cards (card_number) VALUES (?)",
                    (card_number,)
                )
            print("✅ 100 کارت اولیه ایجاد شدند.")

    # ==================== مدیریت کارت‌ها ====================

    def initialize_cards(self, count=100):
        """ایجاد کارت‌های اولیه در دیتابیس"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cards")
            if cursor.fetchone()[0] > 0:
                print("⚠️ کارت‌ها قبلاً ایجاد شده‌اند.")
                return

            for i in range(1, count + 1):
                card_number = f"{i:05d}"
                cursor.execute(
                    "INSERT OR IGNORE INTO cards (card_number) VALUES (?)",
                    (card_number,)
                )
            conn.commit()
            print(f"✅ {count} کارت اولیه با موفقیت ایجاد شدند.")

    def get_available_card(self):
        """دریافت یک کارت موجود (active)"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT card_number, uid FROM cards WHERE status = 'active' LIMIT 1"
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def reserve_card(self, card_number):
        """رزرو کارت (تغییر وضعیت به 'in_use')"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "UPDATE cards SET status = 'in_use' WHERE card_number = ? AND status = 'active'",
                (card_number,)
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise Exception(f"کارت {card_number} در دسترس نیست!")

    def release_card(self, card_number):
        """آزادسازی کارت (تغییر وضعیت به 'active')"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE cards SET status = 'active', assigned_to = NULL, assigned_at = NULL WHERE card_number = ?",
                (card_number,)
            )
            conn.commit()

    def assign_card_to_vehicle(self, card_number, plate):
        """اختصاص کارت به خودرو"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE cards SET assigned_to = ?, assigned_at = CURRENT_TIMESTAMP WHERE card_number = ?",
                (plate, card_number)
            )
            conn.commit()

    def get_card_status(self, card_number):
        """دریافت وضعیت یک کارت"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT status, assigned_to FROM cards WHERE card_number = ?",
                (card_number,)
            )
            return cursor.fetchone()

    def get_all_cards(self, status_filter=None):
        """دریافت لیست همه کارت‌ها با فیلتر وضعیت"""
        with self.get_connection() as conn:
            query = "SELECT * FROM cards"
            params = []
            if status_filter:
                query += " WHERE status = ?"
                params.append(status_filter)
            query += " ORDER BY card_number"

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_active_car_by_card(self, card_number):
        """دریافت خودروی فعال بر اساس شماره کارت"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM active_cars WHERE card_number = ?",
                (card_number,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ==================== عملیات اصلی با کارت ====================

    def car_entry_with_card(self, plate_data, card_number):
        """
        ثبت ورود خودرو با کارت (بدون رزرو مجدد)
        """
        # ===== استفاده از یک اتصال واحد برای همه عملیات =====
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # ۱. بررسی تکراری نبودن
            cursor.execute("SELECT id FROM active_cars WHERE plate_number = ?",
                           (plate_data['plate_number'],))
            if cursor.fetchone():
                raise ValueError(f"خودرو با پلاک {plate_data['plate_number']} قبلاً ثبت شده است")

            # ۲. ثبت ورود با کارت
            cursor.execute('''INSERT INTO active_cars (
                plate_number, plate_part1, plate_letter, plate_part2, plate_part3,
                entry_time, entry_image, plate_type, province, operator_name, notes, card_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                plate_data['plate_number'],
                plate_data['plate_part1'],
                plate_data['plate_letter'],
                plate_data['plate_part2'],
                plate_data.get('plate_part3', ''),
                datetime.now().isoformat(),
                plate_data.get('entry_image'),
                plate_data.get('plate_type', 'personal'),
                plate_data.get('province', ''),
                plate_data.get('operator_name', ''),
                plate_data.get('notes', ''),
                card_number
            ))

            # ۳. اختصاص کارت به خودرو (در همان اتصال)
            cursor.execute(
                "UPDATE cards SET assigned_to = ?, assigned_at = CURRENT_TIMESTAMP WHERE card_number = ?",
                (plate_data['plate_number'], card_number)
            )

            # ۴. ثبت لاگ
            self._log_event(cursor, 'entry', plate_data['plate_number'], card_number,
                            f'ورود با کارت {card_number}', plate_data.get('operator_name', ''))

            return cursor.lastrowid
    def car_exit_by_card(self, card_number, exit_data=None):
        """ثبت خروج خودرو با کارت"""
        if exit_data is None:
            exit_data = {}

        # ۱. دریافت خودرو بر اساس کارت
        car = self.get_active_car_by_card(card_number)
        if not car:
            raise ValueError(f"کارت {card_number} معتبر نیست یا به خودرویی اختصاص ندارد!")

        # ۲. ثبت خروج با پلاک
        result = self.car_exit(car['plate_number'], exit_data)

        # ۳. آزادسازی کارت
        self.release_card(card_number)

        # ۴. ثبت لاگ خروج با کارت
        with self.get_connection() as conn:
            self._log_event(conn.cursor(), 'exit', car['plate_number'], card_number,
                            f'خروج با کارت {card_number}', exit_data.get('operator_name', ''))

        return result

    # ==================== عملیات اصلی (بدون کارت) ====================

    def car_entry(self, plate_data):
        """ثبت ورود خودرو (بدون کارت - برای سازگاری)"""
        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("SELECT id FROM active_cars WHERE plate_number = ?",
                      (plate_data['plate_number'],))
            if c.fetchone():
                raise ValueError(f"خودرو با پلاک {plate_data['plate_number']} قبلاً ثبت شده است")

            c.execute('''INSERT INTO active_cars (
                plate_number, plate_part1, plate_letter, plate_part2, plate_part3,
                entry_time, entry_image, plate_type, province, operator_name, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                plate_data['plate_number'],
                plate_data['plate_part1'],
                plate_data['plate_letter'],
                plate_data['plate_part2'],
                plate_data.get('plate_part3', ''),
                datetime.now().isoformat(),
                plate_data.get('entry_image'),
                plate_data.get('plate_type', 'personal'),
                plate_data.get('province', ''),
                plate_data.get('operator_name', ''),
                plate_data.get('notes', '')
            ))

            self._log_event(c, 'entry', plate_data['plate_number'], None,
                            'ورود خودرو', plate_data.get('operator_name', ''))

            return c.lastrowid

    def car_exit(self, plate_number, exit_data=None):
        """ثبت خروج خودرو و محاسبه هزینه با نرخ ساعت اول و دوم"""
        if exit_data is None:
            exit_data = {}

        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM active_cars WHERE plate_number = ?", (plate_number,))
            car = c.fetchone()

            if not car:
                raise ValueError(f"خودرو با پلاک {plate_number} یافت نشد")

            entry_time = datetime.fromisoformat(car['entry_time'])
            exit_time = datetime.now()
            duration = exit_time - entry_time
            total_minutes = int(duration.total_seconds() / 60)
            total_hours = total_minutes / 60

            # ===== دریافت تنظیمات نرخ‌ها =====
            first_hour_rate = float(self.get_setting('first_hour_rate', '10000'))
            next_hours_rate = float(self.get_setting('next_hours_rate', '5000'))
            free_minutes = int(self.get_setting('free_minutes', '15'))
            max_daily = float(self.get_setting('max_daily_cost', '50000'))

            # ===== محاسبه هزینه =====
            if total_minutes <= free_minutes:
                cost = 0
                discount_type = 'free_short_stop'
                discount_percent = 100
            else:
                # ===== نرخ ساعت اول و دوم =====
                if total_hours <= 1:
                    # فقط ساعت اول
                    cost = first_hour_rate
                else:
                    # ساعت اول + ساعات بعدی
                    extra_hours = int(total_hours)  # تعداد ساعات کامل اضافه
                    cost = first_hour_rate + (extra_hours * next_hours_rate)

                # بررسی سقف روزانه
                if cost > max_daily:
                    cost = max_daily

                # بررسی تخفیف‌های ویژه
                discount_percent = self._calculate_discount(car['plate_type'])
                discount_type = 'special' if discount_percent > 0 else 'none'
                if discount_percent > 0:
                    cost = cost * (1 - discount_percent / 100)

            final_cost = cost

            # ذخیره کارت قبل از حذف
            card_number = car['card_number']

            c.execute('''INSERT INTO parking_history (
                plate_number, plate_part1, plate_letter, plate_part2, plate_part3,
                card_number, entry_time, exit_time, duration_minutes, duration_hours,
                cost, entry_image, exit_image, plate_type, province,
                discount_type, discount_percent, final_cost,
                operator_name, payment_method, payment_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                car['plate_number'], car['plate_part1'], car['plate_letter'],
                car['plate_part2'], car['plate_part3'], card_number,
                car['entry_time'], exit_time.isoformat(),
                total_minutes, round(total_hours, 2),
                cost, car['entry_image'], exit_data.get('exit_image'),
                car['plate_type'], car['province'],
                discount_type, discount_percent, final_cost,
                exit_data.get('operator_name', ''),
                exit_data.get('payment_method', 'cash'),
                'paid', exit_data.get('notes', '')
            ))

            history_id = c.lastrowid

            c.execute("DELETE FROM active_cars WHERE plate_number = ?", (plate_number,))

            self._log_event(c, 'exit', plate_number, card_number,
                            f'خروج خودرو - هزینه: {final_cost:,.0f} تومان',
                            exit_data.get('operator_name', ''))

            return {
                'history_id': history_id,
                'plate_number': plate_number,
                'entry_time': car['entry_time'],
                'exit_time': exit_time.isoformat(),
                'duration_minutes': total_minutes,
                'duration_hours': round(total_hours, 2),
                'base_cost': cost,
                'discount_percent': discount_percent,
                'final_cost': final_cost,
                'discount_type': discount_type,
                'card_number': card_number
            }
    def _calculate_discount(self, plate_type):
        """محاسبه درصد تخفیف بر اساس نوع پلاک و زمان"""
        with self.get_connection() as conn:
            c = conn.cursor()
            current_time = datetime.now().strftime('%H:%M')

            c.execute('''SELECT discount_percent FROM special_rates 
                         WHERE plate_type = ? AND is_active = 1 
                         AND (start_time IS NULL OR start_time <= ?)
                         AND (end_time IS NULL OR end_time >= ?)
                         ORDER BY discount_percent DESC
                         LIMIT 1''',
                      (plate_type, current_time, current_time))

            result = c.fetchone()
            return result['discount_percent'] if result else 0

    # ==================== عملیات خواندن ====================

    def get_active_cars(self):
        """دریافت لیست خودروهای فعال"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM active_cars ORDER BY entry_time DESC")
            cars = []

            for row in c.fetchall():
                car = dict(row)
                entry_time = datetime.fromisoformat(car['entry_time'])
                duration = datetime.now() - entry_time
                car['duration_hours'] = round(duration.total_seconds() / 3600, 1)
                car['duration_minutes'] = int(duration.total_seconds() / 60)

                hourly_rate = float(self.get_setting('hourly_rate', '5000'))
                free_minutes = int(self.get_setting('free_minutes', '15'))

                if car['duration_minutes'] > free_minutes:
                    hours = max(1, int(car['duration_hours'] + 0.99))
                    car['estimated_cost'] = hours * hourly_rate
                    discount = self._calculate_discount(car.get('plate_type', 'personal'))
                    if discount > 0:
                        car['estimated_cost'] *= (1 - discount / 100)
                else:
                    car['estimated_cost'] = 0

                cars.append(car)

            return cars

    def get_history(self, page=1, per_page=50, date_from=None, date_to=None,
                    plate_number=None, plate_type=None):
        """دریافت تاریخچه با فیلتر و صفحه‌بندی"""
        with self.get_connection() as conn:
            c = conn.cursor()

            query = "FROM parking_history WHERE 1=1"
            params = []

            if date_from:
                query += " AND date(exit_time) >= date(?)"
                params.append(date_from)

            if date_to:
                query += " AND date(exit_time) <= date(?)"
                params.append(date_to)

            if plate_number:
                query += " AND plate_number LIKE ?"
                params.append(f'%{plate_number}%')

            if plate_type:
                query += " AND plate_type = ?"
                params.append(plate_type)

            c.execute(f"SELECT COUNT(*) {query}", params)
            total = c.fetchone()[0]

            offset = (page - 1) * per_page
            c.execute(f"SELECT * {query} ORDER BY exit_time DESC LIMIT ? OFFSET ?",
                      params + [per_page, offset])

            records = [dict(row) for row in c.fetchall()]

            return {
                'records': records,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': max(1, (total + per_page - 1) // per_page)
            }

    def get_statistics(self, date=None):
        """دریافت آمار"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute('''SELECT 
                        COUNT(*) as count, 
                        COALESCE(SUM(final_cost), 0) as income,
                        COALESCE(AVG(duration_hours), 0) as avg_duration,
                        COUNT(DISTINCT plate_number) as unique_cars
                        FROM parking_history 
                        WHERE date(exit_time) = ?''', (date,))
            daily = dict(c.fetchone())

            c.execute('''SELECT plate_type, COUNT(*) as count, 
                        COALESCE(SUM(final_cost), 0) as income
                        FROM parking_history 
                        WHERE date(exit_time) = ?
                        GROUP BY plate_type''', (date,))
            by_type = [dict(row) for row in c.fetchall()]

            c.execute('''SELECT strftime('%H', exit_time) as hour, 
                        COUNT(*) as count
                        FROM parking_history 
                        WHERE date(exit_time) = ?
                        GROUP BY hour
                        ORDER BY count DESC
                        LIMIT 5''', (date,))
            peak_hours = [dict(row) for row in c.fetchall()]

            return {
                'daily': daily,
                'by_plate_type': by_type,
                'peak_hours': peak_hours,
                'date': date,
                'active_cars': len(self.get_active_cars())
            }

    def search_plate(self, query):
        """جستجوی پلاک"""
        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM active_cars WHERE plate_number LIKE ?",
                      (f'%{query}%',))
            active = [dict(row) for row in c.fetchall()]

            c.execute('''SELECT * FROM parking_history 
                        WHERE plate_number LIKE ? 
                        ORDER BY exit_time DESC LIMIT 10''',
                      (f'%{query}%',))
            history = [dict(row) for row in c.fetchall()]

            return {'active': active, 'history': history}

    # ==================== تنظیمات ====================

    def get_setting(self, key, default=None):
        """دریافت یک تنظیم"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = c.fetchone()
            return result['value'] if result else default

    def set_setting(self, key, value):
        """تنظیم یک مقدار"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO settings (key, value, updated_at) 
                        VALUES (?, ?, CURRENT_TIMESTAMP)''', (key, str(value)))

    def get_all_settings(self):
        """دریافت همه تنظیمات"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM settings")
            return {row['key']: row['value'] for row in c.fetchall()}

    # ==================== لاگ‌ها ====================

    def _log_event(self, cursor, event_type, plate_number, card_number, description, operator_name=''):
        """ثبت لاگ رویداد (نیاز به cursor فعال)"""
        cursor.execute('''INSERT INTO event_logs 
                        (event_type, plate_number, card_number, description, operator_name)
                        VALUES (?, ?, ?, ?, ?)''',
                       (event_type, plate_number, card_number, description, operator_name))

    def get_recent_logs(self, limit=100):
        """دریافت لاگ‌های اخیر"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM event_logs ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in c.fetchall()]

    # ==================== عملیات کمکی ====================

    def backup_database(self):
        """تهیه نسخه پشتیبان"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"backups/parking_backup_{timestamp}.db"

        shutil.copy2(self.db_path, backup_path)

        backups = sorted(os.listdir('backups'))
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                try:
                    os.remove(os.path.join('backups', old_backup))
                except:
                    pass

        return backup_path

    def export_to_excel(self, date_from=None, date_to=None):
        """خروجی Excel از تاریخچه"""
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "تاریخچه پارکینگ"
            ws.sheet_view.rightToLeft = True

            headers = [
                'ردیف', 'پلاک', 'کارت', 'نوع', 'استان',
                'زمان ورود', 'زمان خروج', 'مدت (ساعت)',
                'هزینه پایه', 'تخفیف', 'هزینه نهایی',
                'اپراتور', 'روش پرداخت'
            ]

            header_font = Font(name='Tahoma', size=11, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='2c3e50', end_color='2c3e50', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center')

            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

            history = self.get_history(date_from=date_from, date_to=date_to, per_page=10000)

            for i, record in enumerate(history['records'], 1):
                row_data = [
                    i,
                    record['plate_number'],
                    record.get('card_number', '-'),
                    record.get('plate_type', 'شخصی'),
                    record.get('province', ''),
                    record['entry_time'][:16],
                    record['exit_time'][:16],
                    f"{record['duration_hours']:.1f}",
                    f"{record['cost']:,.0f}",
                    f"{record['discount_percent']}%" if record['discount_percent'] > 0 else "-",
                    f"{record['final_cost']:,.0f}",
                    record.get('operator_name', '-'),
                    record.get('payment_method', 'نقدی')
                ]

                for col, value in enumerate(row_data, 1):
                    cell = ws.cell(row=i + 1, column=col, value=value)
                    cell.font = Font(name='Tahoma', size=10)
                    cell.alignment = Alignment(horizontal='center', vertical='center')

                    if col == 11 and record['final_cost'] > 0:
                        cell.font = Font(name='Tahoma', size=10, bold=True, color='c0392b')

            for col in range(1, len(headers) + 1):
                ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 15

            os.makedirs('exports', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exports/parking_report_{timestamp}.xlsx"
            wb.save(filename)

            return filename

        except ImportError:
            raise ImportError("کتابخانه openpyxl نصب نیست. لطفاً اجرا کنید: pip install openpyxl")
        except Exception as e:
            raise Exception(f"خطا در خروجی Excel: {str(e)}")

    def get_database_info(self):
        """دریافت اطلاعات پایگاه داده"""
        with self.get_connection() as conn:
            c = conn.cursor()

            info = {}

            c.execute("SELECT COUNT(*) FROM active_cars")
            info['active_cars'] = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM parking_history")
            info['total_history'] = c.fetchone()[0]

            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COALESCE(SUM(final_cost), 0) FROM parking_history WHERE date(exit_time) = ?", (today,))
            info['today_income'] = c.fetchone()[0]

            month = datetime.now().strftime('%Y-%m')
            c.execute("SELECT COALESCE(SUM(final_cost), 0) FROM parking_history WHERE strftime('%Y-%m', exit_time) = ?",
                      (month,))
            info['month_income'] = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM cards WHERE status = 'active'")
            info['available_cards'] = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM cards WHERE status = 'in_use'")
            info['used_cards'] = c.fetchone()[0]

            if os.path.exists(self.db_path):
                info['db_size'] = os.path.getsize(self.db_path) / (1024 * 1024)

            if os.path.exists('backups'):
                info['backup_count'] = len(os.listdir('backups'))

            return info

# database.py (بخش‌های اضافه‌شده)

    def get_card_by_uid(self, uid):
        """دریافت اطلاعات کارت بر اساس UID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cards WHERE uid = ?",
                (uid,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None


    def update_card(self, card_number, uid=None, status=None, assigned_to=None):
        """به‌روزرسانی کارت"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []

            if uid is not None:
                updates.append("uid = ?")
                params.append(uid if uid else None)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if assigned_to is not None:
                updates.append("assigned_to = ?")
                params.append(assigned_to if assigned_to else None)

            if updates:
                query = f"UPDATE cards SET {', '.join(updates)} WHERE card_number = ?"
                params.append(card_number)
                cursor.execute(query, params)
                conn.commit()
    def get_card_by_card_number(self, card_number):
        """دریافت اطلاعات کارت بر اساس شماره کارت"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cards WHERE card_number = ?",
                (card_number,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None


    def add_card(self, card_number, uid=None, status='active', assigned_to=None):
        """افزودن کارت جدید"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cards (card_number, uid, status, assigned_to)
                VALUES (?, ?, ?, ?)
            """, (card_number, uid, status, assigned_to))
            conn.commit()


    def update_card(self, card_number, uid=None, status=None, assigned_to=None):
        """به‌روزرسانی کارت"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []

            if uid is not None:
                updates.append("uid = ?")
                params.append(uid if uid else None)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if assigned_to is not None:
                updates.append("assigned_to = ?")
                params.append(assigned_to if assigned_to else None)

            if updates:
                query = f"UPDATE cards SET {', '.join(updates)} WHERE card_number = ?"
                params.append(card_number)
                cursor.execute(query, params)
                conn.commit()


    def delete_card(self, card_number):
        """حذف کارت"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cards WHERE card_number = ?", (card_number,))
            conn.commit()


    def delete_all_cards(self):
        """حذف همه کارت‌ها"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cards")
            conn.commit()


    def get_all_cards(self, status_filter=None):
        """دریافت لیست همه کارت‌ها"""
        with self.get_connection() as conn:
            query = "SELECT * FROM cards"
            params = []
            if status_filter:
                query += " WHERE status = ?"
                params.append(status_filter)
            query += " ORDER BY card_number"

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

# ==================== تست ====================

if __name__ == "__main__":
    print("🧪 تست پایگاه داده...")

    try:
        db = ParkingDatabase()
        print("✅ پایگاه داده ایجاد شد")

        # تست کارت‌ها
        available = db.get_available_card()
        print(f"✅ کارت موجود: {available}")

        if available:
            db.reserve_card(available)
            print(f"✅ کارت {available} رزرو شد")

            status = db.get_card_status(available)
            print(f"✅ وضعیت کارت: {status}")

            db.release_card(available)
            print(f"✅ کارت {available} آزاد شد")

        # تست ورود با کارت
        try:
            card = db.get_available_card()
            if card:
                entry_id = db.car_entry_with_card({
                    'plate_number': '12A345-67',
                    'plate_part1': '12',
                    'plate_letter': 'A',
                    'plate_part2': '345',
                    'plate_part3': '67',
                    'plate_type': 'personal',
                    'operator_name': 'admin'
                }, card)
                print(f"✅ ورود با کارت ثبت شد: {entry_id}")

                # تست خروج با کارت
                result = db.car_exit_by_card(card, {'operator_name': 'admin'})
                print(f"✅ خروج با کارت ثبت شد - هزینه: {result['final_cost']:,.0f} تومان")
        except Exception as e:
            print(f"⚠️ {e}")

        # تست اطلاعات پایگاه داده
        info = db.get_database_info()
        print(f"✅ اطلاعات: {info}")

        print("\n🎉 همه تست‌ها با موفقیت انجام شد!")

    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()

