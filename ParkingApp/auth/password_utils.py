"""
Password Utils - ابزارهای رمز عبور
"""

import hashlib
import os


class PasswordUtils:
    """ابزارهای رمزنگاری رمز عبور"""

    @staticmethod
    def hash_password(password, salt=None):
        """
        هش کردن رمز عبور با SHA-256

        Args:
            password (str): رمز عبور
            salt (str): نمک (اختیاری)

        Returns:
            tuple: (hash, salt)
        """
        if salt is None:
            salt = os.urandom(16).hex()

        # ترکیب رمز عبور با نمک
        salted = password + salt
        hashed = hashlib.sha256(salted.encode()).hexdigest()

        return hashed, salt

    @staticmethod
    def verify_password(password, stored_hash, salt):
        """
        بررسی رمز عبور

        Args:
            password (str): رمز عبور وارد شده
            stored_hash (str): هش ذخیره شده
            salt (str): نمک ذخیره شده

        Returns:
            bool: True اگر رمز صحیح باشد
        """
        hashed, _ = PasswordUtils.hash_password(password, salt)
        return hashed == stored_hash