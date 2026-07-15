"""
پنجره اصلی - نسخه کامل با تمام تب‌ها
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import ParkingDatabase
from plate_utils import IranianPlate
from ui.entry_widget import EntryWidget
from ui.exit_widget import ExitWidget
from ui.active_tab import ActiveTab
from ui.history_tab import HistoryTab
from ui.settings_tab import SettingsTab
from ui.camera_widget import CameraWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = ParkingDatabase()
        self.VERSION = "3.0.0"
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
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
            
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
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

        # تب ۱: ورود
        self.entry_widget = EntryWidget(self.db)
        entry_scroll = QScrollArea()
        entry_scroll.setWidgetResizable(True)
        entry_scroll.setWidget(self.entry_widget)
        entry_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_widget.addTab(entry_scroll, "  🚗  ورود خودرو  ")

        # تب ۲: خروج
        self.exit_widget = ExitWidget(self.db)
        self.exit_widget.car_exited.connect(self.on_car_event)
        exit_scroll = QScrollArea()
        exit_scroll.setWidgetResizable(True)
        exit_scroll.setWidget(self.exit_widget)
        exit_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_widget.addTab(exit_scroll, "  🚙  خروج خودرو  ")

        # تب ۳: خودروهای حاضر
        self.active_tab = ActiveTab(self.db)
        active_scroll = QScrollArea()
        active_scroll.setWidgetResizable(True)
        active_scroll.setWidget(self.active_tab)
        active_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_widget.addTab(active_scroll, "  🅿️  خودروهای حاضر  ")

        # تب ۴: تاریخچه
        self.history_tab = HistoryTab(self.db)
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setWidget(self.history_tab)
        history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_widget.addTab(history_scroll, "  📊  تاریخچه  ")



        # تب ۶: تنظیمات
        self.settings_tab = SettingsTab(self.db)
        self.settings_tab.settings_changed.connect(self.on_settings_changed)
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setWidget(self.settings_tab)
        settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_widget.addTab(settings_scroll, "  ⚙️  تنظیمات  ")

        main_layout.addWidget(self.tab_widget)

        # ============ فوتر ============
        footer = self.create_footer()
        main_layout.addWidget(footer)

        # ============ نوار وضعیت ============
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()

    def create_header(self):
        """ایجاد هدر"""
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
        header_layout.addWidget(self.time_label)

        return header

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
        copyright_label = QLabel("© ۱۴۰۳")
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
        self.time_label.setText(now.strftime("%Y/%m/%d  %H:%M:%S"))
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


    def on_settings_changed(self):
        """تغییر تنظیمات"""
        self.update_status()

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