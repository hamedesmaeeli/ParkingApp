"""
تست ساده - فقط صفحه ورود
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SimpleEntry(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تست ورود پلاک")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                padding: 15px 30px; 
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QLineEdit {
                border: 3px solid #3498db;
                border-radius: 8px;
                padding: 15px;
                font-size: 20px;
                min-width: 80px;
                min-height: 50px;
                text-align: center;
            }
            QLabel { font-size: 16px; color: #2c3e50; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # عنوان
        title = QLabel("🚗 تست ورود پلاک ایرانی")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(title)

        # راهنما
        help_text = QLabel("پلاک را وارد کنید (مثال: 12 الف 345 ایران 11)")
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(help_text)

        # فیلدهای پلاک
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(10)

        # بخش ۱
        self.part1 = QLineEdit()
        self.part1.setPlaceholderText("۱۲")
        self.part1.setMaxLength(2)
        self.part1.setAlignment(Qt.AlignCenter)

        sep1 = QLabel("|")
        sep1.setStyleSheet("font-size: 30px; color: #3498db; font-weight: bold;")

        # بخش ۲
        self.letter = QLineEdit()
        self.letter.setPlaceholderText("الف")
        self.letter.setMaxLength(1)
        self.letter.setAlignment(Qt.AlignCenter)

        sep2 = QLabel("|")
        sep2.setStyleSheet("font-size: 30px; color: #3498db; font-weight: bold;")

        # بخش ۳
        self.part2 = QLineEdit()
        self.part2.setPlaceholderText("۳۴۵")
        self.part2.setMaxLength(3)
        self.part2.setAlignment(Qt.AlignCenter)

        # ایران
        iran = QLabel("ایران")
        iran.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            padding: 15px 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        """)
        iran.setAlignment(Qt.AlignCenter)

        # بخش ۴
        self.part3 = QLineEdit()
        self.part3.setPlaceholderText("۱۱")
        self.part3.setMaxLength(2)
        self.part3.setAlignment(Qt.AlignCenter)

        fields_layout.addWidget(self.part1)
        fields_layout.addWidget(sep1)
        fields_layout.addWidget(self.letter)
        fields_layout.addWidget(sep2)
        fields_layout.addWidget(self.part2)
        fields_layout.addWidget(iran)
        fields_layout.addWidget(self.part3)

        layout.addLayout(fields_layout)

        # نمایش پلاک کامل
        self.display_label = QLabel("پلاک: ----------")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            background-color: #1a3a6b;
            padding: 20px;
            border-radius: 10px;
            border: 3px solid #c8a45c;
        """)
        layout.addWidget(self.display_label)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        submit_btn = QPushButton("✅ ثبت")
        submit_btn.clicked.connect(self.submit)

        clear_btn = QPushButton("🔄 پاک کردن")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                min-height: 50px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        clear_btn.clicked.connect(self.clear)

        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # اتصال رویدادها
        self.part1.textChanged.connect(self.update_display)
        self.letter.textChanged.connect(self.update_display)
        self.part2.textChanged.connect(self.update_display)
        self.part3.textChanged.connect(self.update_display)

    def update_display(self):
        """بروزرسانی نمایش پلاک"""
        p1 = self.part1.text() or "--"
        l = self.letter.text() or "-"
        p2 = self.part2.text() or "---"
        p3 = self.part3.text() or "--"

        plate_text = f"پلاک: {p1} | {l} | {p2}  ایران  {p3}"
        self.display_label.setText(plate_text)

    def submit(self):
        """ثبت"""
        p1 = self.part1.text()
        l = self.letter.text()
        p2 = self.part2.text()
        p3 = self.part3.text()

        if p1 and l and p2:
            plate = f"{p1}{l}{p2}"
            if p3:
                plate += f"-{p3}"
            QMessageBox.information(self, "✅ موفق", f"پلاک ثبت شد:\n{plate}")
            self.clear()
        else:
            QMessageBox.warning(self, "⚠️ خطا", "لطفاً همه بخش‌های پلاک را پر کنید")

    def clear(self):
        """پاک کردن"""
        self.part1.clear()
        self.letter.clear()
        self.part2.clear()
        self.part3.clear()
        self.part1.setFocus()
        self.display_label.setText("پلاک: ----------")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Tahoma", 10))
    app.setLayoutDirection(Qt.RightToLeft)

    window = SimpleEntry()
    window.show()

    sys.exit(app.exec_())