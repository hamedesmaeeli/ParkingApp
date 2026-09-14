"""
Auto Backup - بکاپ خودکار زمان‌بندی‌شده
"""

import threading
import time
from datetime import datetime, timedelta


class AutoBackup:
    """مدیریت بکاپ خودکار"""

    def __init__(self, backup_manager, interval_hours=24):
        self.backup_manager = backup_manager
        self.interval_hours = interval_hours
        self.is_running = False
        self.thread = None
        self.last_backup = None

    def start(self):
        """شروع بکاپ خودکار"""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.thread.start()
        print(f"✅ بکاپ خودکار فعال شد (هر {self.interval_hours} ساعت)")

    def stop(self):
        """توقف بکاپ خودکار"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        print("⏹️ بکاپ خودکار متوقف شد")

    def _backup_loop(self):
        """حلقه بکاپ خودکار"""
        while self.is_running:
            try:
                # بررسی زمان آخرین بکاپ
                now = datetime.now()
                if self.last_backup is None or \
                        (now - self.last_backup) >= timedelta(hours=self.interval_hours):
                    # ایجاد بکاپ
                    backup_path = self.backup_manager.create_backup()
                    self.last_backup = now
                    print(f"✅ بکاپ خودکار ایجاد شد: {backup_path}")

                    # حذف بکاپ‌های قدیمی
                    self.backup_manager.delete_old_backups(keep_count=30)

                # بررسی هر ساعت
                time.sleep(3600)

            except Exception as e:
                print(f"❌ خطا در بکاپ خودکار: {e}")
                time.sleep(3600)

    def set_interval(self, hours):
        """تنظیم فاصله بکاپ"""
        self.interval_hours = hours
        print(f"🔄 فاصله بکاپ به {hours} ساعت تغییر کرد.")

    def get_status(self):
        """دریافت وضعیت"""
        return {
            'is_running': self.is_running,
            'interval_hours': self.interval_hours,
            'last_backup': self.last_backup.strftime('%Y-%m-%d %H:%M:%S') if self.last_backup else None
        }