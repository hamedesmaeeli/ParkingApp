"""
Backup Manager - مدیریت پشتیبان‌گیری از دیتابیس
"""

import os
import shutil
from datetime import datetime


class BackupManager:
    """مدیریت بکاپ‌گیری از دیتابیس"""

    def __init__(self, db):
        self.db = db
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, backup_name=None):
        """
        ایجاد بکاپ از دیتابیس

        Args:
            backup_name (str): نام بکاپ (اختیاری)

        Returns:
            str: مسیر فایل بکاپ
        """
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"parking_backup_{timestamp}.db"

        if not backup_name.endswith('.db'):
            backup_name += '.db'

        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            # کپی فایل دیتابیس
            shutil.copy2(self.db.db_path, backup_path)
            print(f"✅ بکاپ ایجاد شد: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ خطا در ایجاد بکاپ: {e}")
            raise

    def restore_backup(self, backup_path):
        """
        بازیابی از فایل بکاپ

        Args:
            backup_path (str): مسیر فایل بکاپ
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"فایل بکاپ پیدا نشد: {backup_path}")

        try:
            # کپی فایل بکاپ به جای دیتابیس اصلی
            shutil.copy2(backup_path, self.db.db_path)
            print(f"✅ بازیابی انجام شد: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ خطا در بازیابی: {e}")
            raise

    def get_backups(self):
        """
        دریافت لیست بکاپ‌ها

        Returns:
            list: لیست دیکشنری‌های بکاپ
        """
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created_at': datetime.fromtimestamp(stat.st_mtime),
                    'created_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })

        # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

    def delete_backup(self, backup_path):
        """حذف یک بکاپ"""
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"🗑️ بکاپ حذف شد: {backup_path}")

    def delete_old_backups(self, keep_count=30):
        """حذف بکاپ‌های قدیمی"""
        backups = self.get_backups()
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                self.delete_backup(backup['filepath'])
            print(f"🗑️ {len(backups) - keep_count} بکاپ قدیمی حذف شد.")

    def get_backup_info(self):
        """دریافت اطلاعات بکاپ‌ها"""
        backups = self.get_backups()
        total_size = sum(b['size'] for b in backups)

        return {
            'count': len(backups),
            'total_size_mb': total_size / (1024 * 1024),
            'last_backup': backups[0]['created_str'] if backups else None,
            'backups': backups
        }