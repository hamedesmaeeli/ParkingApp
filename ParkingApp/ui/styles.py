"""
استایل‌های CSS برنامه با تم ایرانی-مدرن
"""

class ParkingStyles:
    """کلاس مدیریت استایل‌های برنامه"""

    # رنگ‌های اصلی
    PRIMARY_DARK = "#1a252f"
    PRIMARY = "#2c3e50"
    GOLD = "#c8a45c"
    GOLD_LIGHT = "#d4af6a"
    GOLD_DARK = "#b8944a"
    SUCCESS = "#27ae60"
    DANGER = "#e74c3c"
    INFO = "#3498db"
    WARNING = "#f39c12"
    BACKGROUND = "#f5f6fa"

    @classmethod
    def get_main_stylesheet(cls):
        """استایل اصلی برنامه"""
        return f"""
            QMainWindow {{
                background-color: {cls.PRIMARY_DARK};
            }}
            
            QWidget {{
                font-family: 'Tahoma', 'Segoe UI', sans-serif;
                font-size: 12px;
            }}
            
            QTabWidget::pane {{
                border: 2px solid {cls.GOLD};
                border-radius: 10px;
                background-color: #fef9e7;
                padding: 5px;
            }}
            
            QTabBar::tab {{
                background-color: {cls.PRIMARY};
                color: {cls.GOLD};
                padding: 10px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                border: 1px solid {cls.GOLD};
                border-bottom: none;
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.GOLD};
                color: {cls.PRIMARY_DARK};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: #34495e;
                color: #f4d03f;
            }}
            
            QPushButton {{
                background-color: {cls.INFO};
                color: white;
                border: 2px solid #1a5276;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }}
            
            QPushButton:hover {{
                background-color: #3498db;
            }}
            
            QPushButton:pressed {{
                background-color: #1a5276;
            }}
            
            QPushButton#exitBtn {{
                background-color: {cls.DANGER};
                border: 2px solid #922b21;
            }}
            
            QPushButton#exitBtn:hover {{
                background-color: #e74c3c;
            }}
            
            QPushButton#successBtn {{
                background-color: {cls.SUCCESS};
                border: 2px solid #1e8449;
            }}
            
            QPushButton#successBtn:hover {{
                background-color: #2ecc71;
            }}
            
            QPushButton#goldenBtn {{
                background-color: {cls.GOLD};
                border: 2px solid {cls.GOLD_DARK};
                color: {cls.PRIMARY_DARK};
                font-weight: bold;
            }}
            
            QPushButton#goldenBtn:hover {{
                background-color: {cls.GOLD_LIGHT};
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 2px solid {cls.GOLD};
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
                padding-top: 25px;
                background-color: rgba(255, 255, 255, 0.95);
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {cls.GOLD};
                color: {cls.PRIMARY_DARK};
                border-radius: 5px;
            }}
            
            QLineEdit {{
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 14px;
                background-color: white;
                color: {cls.PRIMARY};
                min-height: 20px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {cls.GOLD};
                background-color: #fef9e7;
            }}
            
            QSpinBox, QDoubleSpinBox, QComboBox {{
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }}
            
            QTableWidget {{
                border: 2px solid {cls.GOLD};
                border-radius: 8px;
                gridline-color: #e8d5b7;
                background-color: white;
                alternate-background-color: #fef9e7;
                selection-background-color: {cls.GOLD};
                selection-color: {cls.PRIMARY_DARK};
            }}
            
            QHeaderView::section {{
                background-color: {cls.PRIMARY};
                color: {cls.GOLD};
                padding: 8px;
                border: 1px solid {cls.GOLD_DARK};
                font-weight: bold;
            }}
            
            QStatusBar {{
                background-color: {cls.PRIMARY};
                color: {cls.GOLD};
                border-top: 2px solid {cls.GOLD};
                font-weight: bold;
                padding: 5px;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: #fef9e7;
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.GOLD_DARK};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.GOLD};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QProgressBar {{
                border: 2px solid {cls.GOLD};
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 20px;
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.SUCCESS};
                border-radius: 3px;
            }}
        """

    @classmethod
    def get_plate_style(cls):
        """استایل پلاک ایرانی"""
        return f"""
            QFrame#plateFrame {{
                background-color: #1a3a6b;
                border: 3px solid {cls.GOLD};
                border-radius: 12px;
                padding: 10px;
            }}
            
            QLabel#plateText {{
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Tahoma', 'B Nazanin';
                background: transparent;
            }}
            
            QLabel#iranLabel {{
                color: white;
                font-size: 12px;
                font-weight: bold;
                background-color: #e74c3c;
                border: 1px solid white;
                border-radius: 5px;
                padding: 5px;
            }}
        """

    @classmethod
    def get_card_style(cls):
        """استایل کارت‌های اطلاعاتی"""
        return f"""
            QFrame#infoCard {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }}
            
            QFrame#infoCard:hover {{
                border: 2px solid {cls.GOLD};
                background: #fef9e7;
            }}
        """

    @classmethod
    def get_plate_input_style(cls):
        """استایل فیلدهای ورود پلاک"""
        return f"""
            QLineEdit {{
                font-size: 18px;
                font-weight: bold;
                font-family: 'Tahoma', 'B Nazanin';
                text-align: center;
                border: 2px solid {cls.GOLD};
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                color: {cls.PRIMARY};
                min-width: 60px;
                max-width: 80px;
                min-height: 40px;
            }}
            QLineEdit:focus {{
                border: 2px solid #2980b9;
                background-color: #ebf5fb;
            }}
        """

    @classmethod
    def get_plate_display_style(cls):
        """استایل نمایش پلاک"""
        return f"""
            QFrame#plateFrame {{
                background-color: #1a3a6b;
                border: 3px solid {cls.GOLD};
                border-radius: 10px;
                padding: 10px;
                min-height: 60px;
                max-height: 80px;
            }}
            
            QLabel#plateText {{
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Tahoma', 'B Nazanin';
                background: transparent;
            }}
            
            QLabel#iranLabel {{
                color: white;
                font-size: 11px;
                font-weight: bold;
                background-color: #e74c3c;
                border: 1px solid white;
                border-radius: 4px;
                padding: 5px;
                min-width: 40px;
            }}
        """