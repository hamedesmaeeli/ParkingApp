"""
پنجره اصلی - نسخه کامل با تمام تب‌ها
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QLabel, QFrame, QScrollArea, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import sys, os
from utils import now_shamsi
from ui.reports_tab import ReportsTab

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import ParkingDatabase
from plate_utils import IranianPlate
from ui.entry_widget import EntryWidget
from ui.exit_widget import ExitWidget
from ui.active_tab import ActiveTab
from ui.history_tab import HistoryTab
from ui.settings_tab import SettingsTab
from ui.camera_widget import CameraWidget
from ui.cards_tab import CardsTab  # اضافه کنید
from ui.unified_widget import UnifiedWidget
from rfid import RFIDIntegration
class MainWindow(QMainWindow):
    def __init__(self, db, user_manager=None):
        super().__init__()
        self.db = db
        self.user_manager = user_manager

        # ===== لاگ =====
        print("\n" + "=" * 50)
        print("🔍 [MainWindow.__init__]")
        print(f"   user_manager: {user_manager}")
        if user_manager:
            print(f"   is_logged_in: {user_manager.is_logged_in()}")
            current = user_manager.get_current_user()
            print(f"   current_user: {current}")
            if current:
                print(f"   current_user.role: {current['role']}")
        print("=" * 50 + "\n")
        # =================

        self.rfid = RFIDIntegration()
        self.rfid.start()
        self.VERSION = "3.0.0"
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        print("\n🔍 [init_ui] شروع")
        print(f"   user_manager: {self.user_manager}")
        if self.user_manager:
            print(f"   is_logged_in: {self.user_manager.is_logged_in()}")
            current = self.user_manager.get_current_user()
            if current:
                print(f"   current_user: {current['username']} | {current['role']}")

        self.setWindowTitle("🏢 سیستم مدیریت پارکینگ")
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(1000, 650)

        # ============ استایل کلی ============
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #f5f6fa; 
            }
            QTabWidget::pane { 
                border: 1px solid #ddd; 
                background-color: white; 
                border-radius: 5px; 
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 12px 35px;
                margin-right: 3px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
            QScrollArea { 
                border: none; 
                background-color: transparent; 
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 11px;
                padding: 3px;
            }
        """)

        # ============ ویجت مرکزی ============
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ============ هدر ============
        header = self.create_header()
        main_layout.addWidget(header)

        # ============ تب‌ها ============
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # ===== تب ۱: ورود/خروج یکپارچه =====
        if self.has_access('entry'):
            print("   ✅ اضافه کردن تب ورود/خروج")
            self.unified_widget = UnifiedWidget(self.db, self.rfid)
            unified_scroll = QScrollArea()
            unified_scroll.setWidgetResizable(True)
            unified_scroll.setWidget(self.unified_widget)
            unified_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(unified_scroll, "  🚦  ورود/خروج یکپارچه  ")

        # ===== تب ۲: خودروهای حاضر =====
        if self.has_access('view_active'):
            print("   ✅ اضافه کردن تب خودروهای حاضر")
            self.active_tab = ActiveTab(self.db)
            active_scroll = QScrollArea()
            active_scroll.setWidgetResizable(True)
            active_scroll.setWidget(self.active_tab)
            active_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(active_scroll, "  🅿️  خودروهای حاضر  ")

        # ===== تب ۳: تاریخچه =====
        if self.has_access('view_history'):
            print("   ✅ اضافه کردن تب تاریخچه")
            self.history_tab = HistoryTab(self.db)
            history_scroll = QScrollArea()
            history_scroll.setWidgetResizable(True)
            history_scroll.setWidget(self.history_tab)
            history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(history_scroll, "  📊  تاریخچه  ")

        # ===== تب ۴: مدیریت کارت‌ها =====
        if self.has_access('card_management'):
            print("   ✅ اضافه کردن تب مدیریت کارت‌ها")
            self.cards_tab = CardsTab(self.db, self.rfid)
            cards_scroll = QScrollArea()
            cards_scroll.setWidgetResizable(True)
            cards_scroll.setWidget(self.cards_tab)
            cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(cards_scroll, "  🎫  مدیریت کارت‌ها  ")

        # ===== تب ۵: تنظیمات (فقط admin) =====
        if self.has_access('settings'):
            print("   ✅ اضافه کردن تب تنظیمات")
            self.settings_tab = SettingsTab(self.db)
            self.settings_tab.settings_changed.connect(self.on_settings_changed)
            settings_scroll = QScrollArea()
            settings_scroll.setWidgetResizable(True)
            settings_scroll.setWidget(self.settings_tab)
            settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(settings_scroll, "  ⚙️  تنظیمات  ")

        # ===== تب ۶: گزارش‌ها =====
        if self.has_access('reports'):
            print("   ✅ اضافه کردن تب گزارش‌ها")
            self.reports_tab = ReportsTab(self.db)
            reports_scroll = QScrollArea()
            reports_scroll.setWidgetResizable(True)
            reports_scroll.setWidget(self.reports_tab)
            reports_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(reports_scroll, "  📊  گزارش‌ها  ")

        # ===== تب ۷: مدیریت کاربران (فقط admin) =====
        if self.has_access('user_management'):
            print("   ✅ اضافه کردن تب مدیریت کاربران")
            from ui.users_tab import UsersTab
            self.users_tab = UsersTab(self.db, self.user_manager)
            users_scroll = QScrollArea()
            users_scroll.setWidgetResizable(True)
            users_scroll.setWidget(self.users_tab)
            users_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.tab_widget.addTab(users_scroll, "  👥  مدیریت کاربران  ")

        # ============ اضافه کردن tab_widget به layout (بیرون از شرط‌ها) ============
        main_layout.addWidget(self.tab_widget)

        # ============ فوتر ============
        footer = self.create_footer()
        main_layout.addWidget(footer)

        # ============ نوار وضعیت ============
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()

        print(f"✅ [init_ui] کامل شد - {self.tab_widget.count()} تب اضافه شد")

    def create_header(self):
        """ایجاد هدر با نمایش کاربر و دکمه خروج"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a252f, stop:0.5 #2c3e50, stop:1 #1a252f);
                padding: 12px 15px;
                min-height: 55px;
                max-height: 55px;
                border-bottom: 2px solid #3498db;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(15)

        # لوگو
        logo = QLabel("🅿️")
        logo.setStyleSheet("font-size: 28px; background: transparent;")

        # عنوان
        title = QLabel("سیستم مدیریت هوشمند پارکینگ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: transparent;
            font-family: 'Tahoma', 'B Nazanin';
        """)

        # ===== اطلاعات کاربر =====
        self.user_label = QLabel()
        self.update_user_label()
        self.user_label.setStyleSheet("""
            font-size: 12px;
            color: white;
            background-color: #27ae60;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 4px;
        """)

        # ===== دکمه خروج =====
        self.logout_btn = QPushButton("🚪 خروج")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setToolTip("خروج از حساب کاربری")

        # ساعت
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            font-size: 13px;
            color: #bdc3c7;
            background: transparent;
            font-weight: bold;
            padding: 3px 8px;
            border: 1px solid #3498db;
            border-radius: 4px;
        """)

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.user_label)
        header_layout.addWidget(self.logout_btn)
        header_layout.addWidget(self.time_label)

        return header

    def update_user_label(self):
        """به‌روزرسانی نمایش نام کاربر"""
        if self.user_manager and self.user_manager.is_logged_in():
            user = self.user_manager.get_current_user()
            role_text = "مدیر" if user['role'] == 'admin' else "اپراتور"
            self.user_label.setText(f"👤 {user['full_name']} ({role_text})")
            self.user_label.setStyleSheet("""
                font-size: 12px;
                color: white;
                background-color: #27ae60;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            """)
        else:
            self.user_label.setText("👤 مهمان")
            self.user_label.setStyleSheet("""
                font-size: 12px;
                color: white;
                background-color: #95a5a6;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            """)

    def logout(self):
        """خروج از حساب کاربری"""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "خروج از حساب",
            "آیا از خروج از حساب کاربری اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.user_manager:
                self.user_manager.logout()

            self.close()
            self.show_login()

    def show_login(self):
        """نمایش صفحه ورود"""
        from auth.login_widget import LoginWidget

        if self.user_manager:
            self.login_widget = LoginWidget(self.user_manager)
            self.login_widget.login_success.connect(self.on_login)
            self.login_widget.show()

    def on_login(self, user):
        """ورود مجدد"""
        if hasattr(self, 'login_widget'):
            self.login_widget.close()

        self.new_window = MainWindow(self.db, self.user_manager)
        self.new_window.show()

    def create_footer(self):
        """ایجاد فوتر باریک"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                padding: 4px 15px;
                min-height: 30px;
                max-height: 30px;
                border-top: 1px solid #3498db;
            }
        """)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        footer_layout.setSpacing(15)

        # نام و ورژن
        app_info = QLabel(f"🏢 سیستم مدیریت پارکینگ | نسخه {self.VERSION}")
        app_info.setStyleSheet("font-size: 11px; color: #bdc3c7; background: transparent;")

        # جداکننده
        sep = QLabel("|")
        sep.setStyleSheet("color: #7f8c8d; background: transparent; font-size: 12px;")

        # کپی‌رایت
        copyright_label = QLabel(f"© {now_shamsi('%Y')}")

        copyright_label.setStyleSheet("font-size: 10px; color: #95a5a6; background: transparent;")

        footer_layout.addWidget(app_info)
        footer_layout.addWidget(sep)
        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()

        # آمار زنده
        self.footer_stats = QLabel("🚗 ۰ | 💰 ۰ تومان")
        self.footer_stats.setStyleSheet("""
            font-size: 11px;
            color: #3498db;
            background: transparent;
            font-weight: bold;
        """)
        footer_layout.addWidget(self.footer_stats)

        return footer

    def setup_timers(self):
        """تنظیم تایمرها"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        """بروزرسانی زمان"""
        now = datetime.now()
        #self.time_label.setText(now.strftime("%Y/%m/%d  %H:%M:%S"))
        self.time_label.setText(now_shamsi())
        self.update_status()

    def update_status(self):
        """بروزرسانی وضعیت"""
        try:
            active = len(self.db.get_active_cars())
            stats = self.db.get_statistics()
            rate = self.db.get_setting('hourly_rate', '5000')

            # نوار وضعیت
            self.status_bar.showMessage(
                f"🚗 حاضر: {active} | 💰 نرخ: {rate} تومان | 📊 امروز: {stats['daily']['count']} خودرو - {stats['daily']['income']:,.0f} تومان"
            )

            # فوتر
            self.footer_stats.setText(
                f"🚗 حاضر: {active} | 📊 امروز: {stats['daily']['count']} | 💰 {stats['daily']['income']:,.0f} تومان"
            )

        except:
            self.status_bar.showMessage("آماده به کار")
            self.footer_stats.setText("🚗 ۰ | 💰 ۰ تومان")

    def on_car_event(self, data):
        """رویداد ورود/خروج خودرو"""
        self.update_status()
        # بروزرسانی تب خودروهای حاضر
        if hasattr(self, 'active_tab'):
            self.active_tab.refresh_data()

    def on_card_changed(self):
        """وقتی کارت‌ها تغییر می‌کنند"""
        self.update_status()  # بروزرسانی آمار
    def on_settings_changed(self):
        """تغییر تنظیمات"""
        self.update_status()

    def has_access(self, permission):
        """بررسی دسترسی کاربر به یک بخش"""
        # اگر user_manager وجود ندارد، همه دسترسی‌ها آزاد است
        if not self.user_manager:
            return True

        # اگر کاربر لاگین نکرده، دسترسی ندارد
        if not self.user_manager.is_logged_in():
            return False

        # بررسی دسترسی از طریق UserManager
        return self.user_manager.has_permission(permission)

    def closeEvent(self, event):
        """بستن برنامه"""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, 'خروج',
            "آیا از خروج از برنامه اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # بکاپ قبل از خروج
            try:
                self.db.backup_database()
            except:
                pass

            # توقف دوربین
            if hasattr(self, 'camera_widget'):
                self.camera_widget.stop_camera()

            event.accept()
        else:
            event.ignore()