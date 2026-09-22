"""
تب مدیریت کاربران
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
import sys, os
from utils import to_shamsi

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import UserManager


class UsersTab(QWidget):
    """تب مدیریت کاربران"""

    user_changed = pyqtSignal()

    def __init__(self, database, user_manager):
        super().__init__()
        self.db = database
        self.user_manager = user_manager
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ===== عنوان =====
        title = QLabel("👥 مدیریت کاربران")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # ===== دکمه‌ها =====
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ افزودن کاربر")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.setStyleSheet("padding: 10px 20px; border: 2px solid #3498db; border-radius: 5px;")
        refresh_btn.clicked.connect(self.load_users)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ===== جدول کاربران =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "نام کاربری", "نام کامل", "نقش", "وضعیت", "آخرین ورود", "عملیات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd; border-radius: 5px;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #2c3e50; color: white;
                padding: 10px; font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

    def load_users(self):
        """بارگذاری لیست کاربران"""
        try:
            users = self.user_manager.get_all_users()
            self.table.setRowCount(len(users))

            for i, user in enumerate(users):
                # نام کاربری
                self.table.setItem(i, 0, QTableWidgetItem(user['username']))

                # نام کامل
                self.table.setItem(i, 1, QTableWidgetItem(user.get('full_name', '')))

                # نقش
                role_text = "مدیر" if user['role'] == 'admin' else "اپراتور"
                role_item = QTableWidgetItem(role_text)
                if user['role'] == 'admin':
                    role_item.setForeground(QBrush(QColor('#e74c3c')))
                self.table.setItem(i, 2, role_item)

                # وضعیت
                status_text = "✅ فعال" if user['is_active'] else "❌ غیرفعال"
                status_item = QTableWidgetItem(status_text)
                if user['is_active']:
                    status_item.setForeground(QBrush(QColor('#27ae60')))
                else:
                    status_item.setForeground(QBrush(QColor('#e74c3c')))
                self.table.setItem(i, 3, status_item)

                # آخرین ورود
                # ===== کد اصلاح‌شده (شمسی) =====
                last_login = user.get('last_login', '')
                if last_login:
                    last_login = to_shamsi(last_login, '%Y/%m/%d %H:%M')
                else:
                    last_login = '—'
                self.table.setItem(i, 4, QTableWidgetItem(last_login))

                # عملیات
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(5)

                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.setToolTip("ویرایش")
                edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))
                edit_btn.setStyleSheet("""
                    QPushButton { background-color: #3498db; color: white; border: none; border-radius: 5px; }
                    QPushButton:hover { background-color: #2980b9; }
                """)
                btn_layout.addWidget(edit_btn)

                password_btn = QPushButton("🔑")
                password_btn.setFixedSize(30, 30)
                password_btn.setToolTip("تغییر رمز")
                password_btn.clicked.connect(lambda checked, u=user: self.change_password(u))
                password_btn.setStyleSheet("""
                    QPushButton { background-color: #f39c12; color: white; border: none; border-radius: 5px; }
                    QPushButton:hover { background-color: #e67e22; }
                """)
                btn_layout.addWidget(password_btn)

                if user['username'] != 'admin':
                    delete_btn = QPushButton("🗑️")
                    delete_btn.setFixedSize(30, 30)
                    delete_btn.setToolTip("حذف")
                    delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))
                    delete_btn.setStyleSheet("""
                        QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 5px; }
                        QPushButton:hover { background-color: #c0392b; }
                    """)
                    btn_layout.addWidget(delete_btn)

                self.table.setCellWidget(i, 5, btn_widget)

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def add_user(self):
        """افزودن کاربر جدید"""
        dialog = UserDialog(self.user_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
            self.user_changed.emit()

    def edit_user(self, user):
        """ویرایش کاربر"""
        dialog = UserDialog(self.user_manager, self, user_data=user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
            self.user_changed.emit()

    def change_password(self, user):
        """تغییر رمز عبور"""
        dialog = PasswordDialog(self.user_manager, user, self)
        dialog.exec_()

    def delete_user(self, user):
        """حذف کاربر"""
        reply = QMessageBox.question(
            self, "تأیید حذف",
            f"آیا از حذف کاربر {user['username']} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.user_manager.delete_user(user['id'])
                QMessageBox.information(self, "✅ موفق", "کاربر حذف شد.")
                self.load_users()
                self.user_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", str(e))


class UserDialog(QDialog):
    """دیالوگ افزودن/ویرایش کاربر"""

    def __init__(self, user_manager, parent=None, user_data=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.user_data = user_data
        self.setWindowTitle("افزودن کاربر" if not user_data else "ویرایش کاربر")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

        if user_data:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("نام کاربری:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("رمز عبور:", self.password_input)

        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("نام کامل")
        self.full_name_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("نام کامل:", self.full_name_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["اپراتور", "مدیر"])
        self.role_combo.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("نقش:", self.role_combo)

        self.active_cb = QCheckBox("فعال")
        self.active_cb.setChecked(True)
        form_layout.addRow("", self.active_cb)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_data(self):
        """بارگذاری داده‌های کاربر"""
        self.username_input.setText(self.user_data['username'])
        if self.user_data:
            self.username_input.setReadOnly(True)

        self.full_name_input.setText(self.user_data.get('full_name', ''))

        role_text = "مدیر" if self.user_data['role'] == 'admin' else "اپراتور"
        self.role_combo.setCurrentText(role_text)

        self.active_cb.setChecked(bool(self.user_data.get('is_active', 1)))

    def accept(self):
        """ذخیره کاربر"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()
        role = 'admin' if self.role_combo.currentText() == 'مدیر' else 'operator'
        is_active = self.active_cb.isChecked()

        if not username:
            QMessageBox.warning(self, "⚠️ خطا", "نام کاربری الزامی است!")
            return

        try:
            if self.user_data:
                # ویرایش
                self.user_manager.update_user(
                    self.user_data['id'],
                    full_name=full_name,
                    role=role,
                    is_active=is_active
                )
                if password:
                    self.user_manager.change_password(self.user_data['id'], password)
            else:
                # افزودن
                if not password:
                    QMessageBox.warning(self, "⚠️ خطا", "رمز عبور الزامی است!")
                    return

                success = self.user_manager.create_user(
                    username, password, full_name, role
                )
                if not success:
                    QMessageBox.warning(self, "⚠️ خطا", "نام کاربری تکراری است!")
                    return

            QMessageBox.information(self, "✅ موفق", "کاربر ذخیره شد.")
            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))


class PasswordDialog(QDialog):
    """دیالوگ تغییر رمز عبور"""

    def __init__(self, user_manager, user, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.user = user
        self.setWindowTitle(f"تغییر رمز {user['username']}")
        self.setModal(True)
        self.resize(350, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form_layout = QFormLayout()

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("رمز عبور جدید")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("رمز جدید:", self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("تکرار رمز عبور")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        form_layout.addRow("تکرار رمز:", self.confirm_password)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        """ذخیره رمز جدید"""
        new_pass = self.new_password.text()
        confirm = self.confirm_password.text()

        if not new_pass:
            QMessageBox.warning(self, "⚠️ خطا", "رمز عبور جدید الزامی است!")
            return

        if new_pass != confirm:
            QMessageBox.warning(self, "⚠️ خطا", "رمز عبور و تکرار آن مطابقت ندارند!")
            return

        try:
            self.user_manager.change_password(self.user['id'], new_pass)
            QMessageBox.information(self, "✅ موفق", "رمز عبور تغییر کرد.")
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))