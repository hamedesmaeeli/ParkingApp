"""
User Manager - مدیریت کاربران
"""

from datetime import datetime
from .password_utils import PasswordUtils


class UserManager:
    """مدیریت کاربران سیستم"""

    def __init__(self, db):
        self.db = db
        self.current_user = None

    def create_default_users(self):
        """ایجاد کاربران پیش‌فرض"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # بررسی وجود کاربر admin
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # ایجاد admin
                hashed, salt = PasswordUtils.hash_password("admin123")
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("admin", hashed, salt, "مدیر سیستم", "admin", 1))
                print("✅ کاربر admin ایجاد شد (رمز: admin123)")

            conn.commit()

    def login(self, username, password):
        """
        ورود کاربر

        Args:
            username (str): نام کاربری
            password (str): رمز عبور

        Returns:
            dict: اطلاعات کاربر یا None
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                return None

            user = dict(user)

            # بررسی رمز عبور
            if PasswordUtils.verify_password(password, user['password_hash'], user['salt']):
                self.current_user = user
                # بروزرسانی آخرین ورود
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user['id'],)
                )
                conn.commit()
                return user

            return None

    def logout(self):
        """خروج کاربر"""
        self.current_user = None

    def is_logged_in(self):
        """بررسی ورود کاربر"""
        return self.current_user is not None

    def get_current_user(self):
        """دریافت کاربر فعلی"""
        return self.current_user

    def has_permission(self, permission):
        """
        بررسی دسترسی کاربر

        Args:
            permission (str): نام دسترسی

        Returns:
            bool: True اگر کاربر دسترسی داشته باشد
        """
        if not self.current_user:
            return False

        role = self.current_user['role']

        # مدیر همه دسترسی‌ها را دارد
        if role == 'admin':
            return True

        # دسترسی‌های اپراتور
        operator_permissions = [
            'entry', 'exit', 'view_active', 'view_history',
            'card_management',
        ]

        if role == 'operator':
            return permission in operator_permissions

        return False

    def create_user(self, username, password, full_name, role='operator'):
        """ایجاد کاربر جدید"""
        hashed, salt = PasswordUtils.hash_password(password)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (username, hashed, salt, full_name, role))
                conn.commit()
                return True
            except Exception as e:
                print(f"❌ خطا در ایجاد کاربر: {e}")
                return False

    def update_user(self, user_id, full_name=None, role=None, is_active=None):
        """به‌روزرسانی کاربر"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if full_name is not None:
                updates.append("full_name = ?")
                params.append(full_name)
            if role is not None:
                updates.append("role = ?")
                params.append(role)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if updates:
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                params.append(user_id)
                cursor.execute(query, params)
                conn.commit()

    def change_password(self, user_id, new_password):
        """تغییر رمز عبور"""
        hashed, salt = PasswordUtils.hash_password(new_password)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (hashed, salt, user_id)
            )
            conn.commit()

    def delete_user(self, user_id):
        """حذف کاربر"""
        # جلوگیری از حذف admin اصلی
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user and user['username'] == 'admin':
                raise Exception("کاربر admin قابل حذف نیست!")

            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

    def get_all_users(self):
        """دریافت لیست همه کاربران"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY username")
            return [dict(row) for row in cursor.fetchall()]

    def get_user(self, user_id):
        """دریافت یک کاربر"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None