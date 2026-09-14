"""
Login Widget - صفحه ورود
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class LoginWidget(QWidget):
    """صفحه ورود به سیستم"""

    login_success = pyqtSignal(dict)

    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # ===== عنوان =====
        title = QLabel("🚗 سیستم مدیریت پارکینگ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; padding: 20px;")
        layout.addWidget(title)

        # ===== فرم ورود =====
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 15px;
                padding: 30px;
                max-width: 400px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # نام کاربری
        form_layout.addWidget(QLabel("👤 نام کاربری:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #3498db; }
        """)
        form_layout.addWidget(self.username_input)

        # رمز عبور
        form_layout.addWidget(QLabel("🔒 رمز عبور:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #3498db; }
        """)
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.password_input)

        # دکمه ورود
        login_btn = QPushButton("🔓 ورود")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

        # پیام خطا
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 13px; padding: 5px;")
        form_layout.addWidget(self.error_label)

        # قرار دادن فرم در وسط
        layout.addStretch()
        layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        layout.addStretch()

        # ===== راهنما =====
        help_label = QLabel(
            "💡 راهنما:\n"
            "کاربر پیش‌فرض: admin\n"
            "رمز پیش‌فرض: admin123"
        )
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("""
            font-size: 12px; color: #7f8c8d; padding: 10px;
            background-color: #f8f9fa; border-radius: 8px;
        """)
        layout.addWidget(help_label)

    def login(self):
        """تلاش برای ورود"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("⚠️ لطفاً نام کاربری و رمز عبور را وارد کنید!")
            return

        user = self.user_manager.login(username, password)

        if user:
            self.error_label.setText("")
            print(f"✅ ورود موفق: {user['full_name']} ({user['role']})")
            self.login_success.emit(user)
        else:
            self.error_label.setText("❌ نام کاربری یا رمز عبور اشتباه است!")
            self.password_input.clear()