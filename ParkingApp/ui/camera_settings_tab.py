"""
تب تنظیمات دوربین - نسخه کامل با پیش‌نمایش زنده
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CameraSettingsTab(QWidget):
    """تب تنظیمات دوربین"""

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.capture = None
        self.timer = None
        self.preview_active = False
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # ===== عنوان =====
        title = QLabel("📷 تنظیمات دوربین")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # ===== نوع دوربین =====
        type_group = QGroupBox("🎥 نوع دوربین")
        type_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #3498db; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #3498db; color: white; border-radius: 5px; }
        """)
        type_layout = QFormLayout()

        self.camera_type_combo = QComboBox()
        self.camera_type_combo.addItems(["وب‌کم (USB)", "دوربین IP (شبکه)"])
        self.camera_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px; border: 2px solid #ddd; border-radius: 5px;
                font-size: 14px; min-height: 40px;
            }
        """)
        self.camera_type_combo.currentIndexChanged.connect(self.on_camera_type_changed)
        type_layout.addRow("نوع دوربین:", self.camera_type_combo)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # ===== تنظیمات وب‌کم =====
        self.webcam_group = QGroupBox("📹 وب‌کم (USB)")
        self.webcam_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #27ae60; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #27ae60; color: white; border-radius: 5px; }
        """)
        webcam_layout = QFormLayout()

        self.camera_index_input = QLineEdit()
        self.camera_index_input.setPlaceholderText("مثال: 0")
        self.camera_index_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        webcam_layout.addRow("شماره وب‌کم:", self.camera_index_input)

        self.webcam_group.setLayout(webcam_layout)
        layout.addWidget(self.webcam_group)

        # ===== تنظیمات دوربین IP =====
        self.ip_group = QGroupBox("🌐 دوربین IP (شبکه)")
        self.ip_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #9b59b6; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #9b59b6; color: white; border-radius: 5px; }
        """)
        ip_layout = QFormLayout()
        ip_layout.setSpacing(10)

        self.camera_ip_input = QLineEdit()
        self.camera_ip_input.setPlaceholderText("مثال: 192.168.1.100")
        self.camera_ip_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        ip_layout.addRow("آدرس IP:", self.camera_ip_input)

        self.camera_port_input = QLineEdit()
        self.camera_port_input.setPlaceholderText("مثال: 554")
        self.camera_port_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        ip_layout.addRow("پورت:", self.camera_port_input)

        self.camera_username_input = QLineEdit()
        self.camera_username_input.setPlaceholderText("مثال: admin")
        self.camera_username_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        ip_layout.addRow("نام کاربری:", self.camera_username_input)

        self.camera_password_input = QLineEdit()
        self.camera_password_input.setPlaceholderText("رمز عبور")
        self.camera_password_input.setEchoMode(QLineEdit.Password)
        self.camera_password_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        ip_layout.addRow("رمز عبور:", self.camera_password_input)

        self.camera_rtsp_path_input = QLineEdit()
        self.camera_rtsp_path_input.setPlaceholderText("مثال: /Streaming/Channels/101")
        self.camera_rtsp_path_input.setStyleSheet(
            "padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;")
        ip_layout.addRow("مسیر RTSP:", self.camera_rtsp_path_input)

        # ===== راهنمای مسیر RTSP =====
        rtsp_help = QLabel(
            "💡 راهنمای مسیر RTSP برندهای رایج:\n"
            "• Hikvision:  /Streaming/Channels/101\n"
            "• Dahua:      /cam/realmonitor?channel=1&subtype=0\n"
            "• Uniview:    /media/video1\n"
            "• Axis:       /axis-media/media.amp\n"
            "• Reolink:    /h264Preview_01_main"
        )
        rtsp_help.setStyleSheet("""
            font-size: 12px; color: #7f8c8d; padding: 10px;
            background-color: #f8f9fa; border-radius: 6px;
            line-height: 1.6;
        """)
        rtsp_help.setWordWrap(True)
        ip_layout.addRow("", rtsp_help)

        self.ip_group.setLayout(ip_layout)
        layout.addWidget(self.ip_group)

        # ===== دکمه‌ها =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.test_btn = QPushButton("🔍 تست اتصال")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 12px 25px; border-radius: 8px;
                font-weight: bold; font-size: 14px; border: none;
                min-height: 45px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_btn)

        self.preview_btn = QPushButton("▶️ شروع پیش‌نمایش")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; color: white;
                padding: 12px 25px; border-radius: 8px;
                font-weight: bold; font-size: 14px; border: none;
                min-height: 45px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.preview_btn.clicked.connect(self.toggle_preview)
        btn_layout.addWidget(self.preview_btn)

        self.save_btn = QPushButton("💾 ذخیره تنظیمات")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 12px 25px; border-radius: 8px;
                font-weight: bold; font-size: 14px; border: none;
                min-height: 45px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ===== پیش‌نمایش =====
        preview_group = QGroupBox("📺 پیش‌نمایش زنده")
        preview_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px; font-weight: bold;
                border: 2px solid #e67e22; border-radius: 10px;
                padding: 20px; padding-top: 35px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #e67e22; color: white; border-radius: 5px; }
        """)
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("📷 پیش‌نمایش دوربین\n\nبرای شروع روی 'شروع پیش‌نمایش' کلیک کنید")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a; color: #95a5a6;
                border: 2px solid #34495e; border-radius: 8px;
                font-size: 14px; font-weight: bold;
            }
        """)
        preview_layout.addWidget(self.preview_label)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        layout.addStretch()

    def on_camera_type_changed(self, index):
        """تغییر نوع دوربین"""
        is_ip = (index == 1)

        self.webcam_group.setEnabled(not is_ip)
        self.ip_group.setEnabled(is_ip)

    def load_settings(self):
        """بارگذاری تنظیمات"""
        try:
            camera_type = self.db.get_setting('camera_type', 'webcam')
            self.camera_type_combo.setCurrentIndex(1 if camera_type == 'ip' else 0)

            self.camera_index_input.setText(self.db.get_setting('camera_index', '0'))
            self.camera_ip_input.setText(self.db.get_setting('camera_ip', ''))
            self.camera_port_input.setText(self.db.get_setting('camera_port', '554'))
            self.camera_username_input.setText(self.db.get_setting('camera_username', 'admin'))
            self.camera_password_input.setText(self.db.get_setting('camera_password', ''))
            self.camera_rtsp_path_input.setText(self.db.get_setting('camera_rtsp_path', '/Streaming/Channels/101'))

            self.on_camera_type_changed(self.camera_type_combo.currentIndex())

        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")

    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            camera_type = 'ip' if self.camera_type_combo.currentIndex() == 1 else 'webcam'

            self.db.set_setting('camera_type', camera_type)
            self.db.set_setting('camera_index', self.camera_index_input.text())
            self.db.set_setting('camera_ip', self.camera_ip_input.text())
            self.db.set_setting('camera_port', self.camera_port_input.text())
            self.db.set_setting('camera_username', self.camera_username_input.text())
            self.db.set_setting('camera_password', self.camera_password_input.text())
            self.db.set_setting('camera_rtsp_path', self.camera_rtsp_path_input.text())

            QMessageBox.information(self, "✅ موفق", "تنظیمات دوربین ذخیره شد.")

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def test_connection(self):
        """تست اتصال دوربین"""
        try:
            if self.camera_type_combo.currentIndex() == 0:
                index = int(self.camera_index_input.text() or "0")
                cap = cv2.VideoCapture(index)
                source = f"وب‌کم {index}"
            else:
                ip = self.camera_ip_input.text().strip()
                port = self.camera_port_input.text().strip() or "554"
                username = self.camera_username_input.text().strip()
                password = self.camera_password_input.text().strip()
                rtsp_path = self.camera_rtsp_path_input.text().strip() or "/Streaming/Channels/101"

                if not ip:
                    QMessageBox.warning(self, "⚠️ خطا", "آدرس IP را وارد کنید!")
                    return

                rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}{rtsp_path}"
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                source = f"دوربین IP ({ip})"

            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()

                if ret:
                    QMessageBox.information(
                        self, "✅ موفق",
                        f"اتصال به {source} برقرار شد.\n"
                        f"سایز تصویر: {frame.shape[1]}x{frame.shape[0]}"
                    )
                else:
                    QMessageBox.warning(self, "⚠️ خطا", "فریمی دریافت نشد.")
            else:
                QMessageBox.critical(self, "❌ خطا", f"اتصال به {source} برقرار نشد.")

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def toggle_preview(self):
        """شروع/توقف پیش‌نمایش"""
        if self.preview_active:
            self.stop_preview()
        else:
            self.start_preview()

    def start_preview(self):
        """شروع پیش‌نمایش"""
        try:
            if self.camera_type_combo.currentIndex() == 0:
                index = int(self.camera_index_input.text() or "0")
                self.capture = cv2.VideoCapture(index)
            else:
                ip = self.camera_ip_input.text().strip()
                port = self.camera_port_input.text().strip() or "554"
                username = self.camera_username_input.text().strip()
                password = self.camera_password_input.text().strip()
                rtsp_path = self.camera_rtsp_path_input.text().strip() or "/Streaming/Channels/101"

                if not ip:
                    QMessageBox.warning(self, "⚠️ خطا", "آدرس IP را وارد کنید!")
                    return

                rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}{rtsp_path}"
                self.capture = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

            if not self.capture.isOpened():
                QMessageBox.warning(self, "⚠️ خطا", "دوربین در دسترس نیست!")
                return

            self.preview_active = True
            self.preview_btn.setText("⏹️ توقف پیش‌نمایش")
            self.preview_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c; color: white;
                    padding: 12px 25px; border-radius: 8px;
                    font-weight: bold; font-size: 14px; border: none;
                    min-height: 45px;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)

            self.timer = QTimer()
            self.timer.timeout.connect(self.update_preview)
            self.timer.start(50)

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def update_preview(self):
        """به‌روزرسانی پیش‌نمایش"""
        if self.capture and self.preview_active:
            ret, frame = self.capture.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qt_img = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
                pix = QPixmap.fromImage(qt_img)
                self.preview_label.setPixmap(
                    pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

    def stop_preview(self):
        """توقف پیش‌نمایش"""
        self.preview_active = False

        if self.timer:
            self.timer.stop()

        if self.capture:
            self.capture.release()
            self.capture = None

        self.preview_btn.setText("▶️ شروع پیش‌نمایش")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; color: white;
                padding: 12px 25px; border-radius: 8px;
                font-weight: bold; font-size: 14px; border: none;
                min-height: 45px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)

        self.preview_label.clear()
        self.preview_label.setText("📷 پیش‌نمایش دوربین\n\nبرای شروع روی 'شروع پیش‌نمایش' کلیک کنید")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a; color: #95a5a6;
                border: 2px solid #34495e; border-radius: 8px;
                font-size: 14px; font-weight: bold;
            }
        """)

    def closeEvent(self, event):
        """بستن تب"""
        self.stop_preview()
        event.accept()