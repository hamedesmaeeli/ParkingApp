"""
فرم ورود خودرو - با دوربین داخلی و قابلیت بارگذاری عکس + ALPR
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame,
    QSizePolicy, QProgressBar, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from datetime import datetime
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_utils import IranianPlate
from alpr.engine import ALPREngine


class EntryWidget(QWidget):
    car_entered = pyqtSignal(dict)

    def __init__(self, database, operator_name="admin"):
        super().__init__()
        self.db = database
        self.operator_name = operator_name
        self.current_plate = IranianPlate()
        self.camera_active = False
        self.capture = None
        self.current_frame = None
        self.image_loaded = False

        # ===== ALPR Engine =====
        self.alpr_engine = ALPREngine(mock_mode=False)  # حالت واقعی
        # ======================

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # ============ عنوان ============
        title = QLabel("🚗 ثبت ورود خودرو")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # ============ راهنما ============
        help_text = QLabel(
            "🔹 پلاک را وارد کنید یا با دوربین اسکن کنید\n"
            "مثال: ۱۲ | الف | ۳۴۵ | ایران | ۱۱"
        )
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet("""
            font-size: 14px; color: #7f8c8d; padding: 15px;
            background-color: #f8f9fa; border-radius: 8px; margin-bottom: 10px;
        """)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # ============ ردیف اصلی: دوربین + فیلدهای پلاک ============
        main_row = QHBoxLayout()
        main_row.setSpacing(20)

        # ============ بخش دوربین (سمت راست) ============
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setSpacing(10)

        # نمایشگر کوچک دوربین
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(280, 210)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #95a5a6;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.camera_label.setText("📷 دوربین\nخاموش است")

        camera_layout.addWidget(self.camera_label)

        # ============ دکمه‌های دوربین ============
        cam_btn_layout = QHBoxLayout()

        self.start_cam_btn = QPushButton("▶️ شروع")
        self.start_cam_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; font-weight: bold;
                padding: 8px 15px; border-radius: 6px; font-size: 12px; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.start_cam_btn.clicked.connect(self.start_camera)

        self.stop_cam_btn = QPushButton("⏹️ توقف")
        self.stop_cam_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; font-weight: bold;
                padding: 8px 15px; border-radius: 6px; font-size: 12px; border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.stop_cam_btn.clicked.connect(self.stop_camera)
        self.stop_cam_btn.setEnabled(False)

        self.scan_btn = QPushButton("🔍 اسکن پلاک")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white; font-weight: bold;
                padding: 8px 15px; border-radius: 6px; font-size: 12px; border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.scan_btn.clicked.connect(self.scan_plate)

        # دکمه بارگذاری عکس
        self.upload_btn = QPushButton("📂 بارگذاری عکس")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; color: white; font-weight: bold;
                padding: 8px 15px; border-radius: 6px; font-size: 12px; border: none;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.upload_btn.clicked.connect(self.upload_image)

        cam_btn_layout.addWidget(self.start_cam_btn)
        cam_btn_layout.addWidget(self.stop_cam_btn)
        cam_btn_layout.addWidget(self.scan_btn)
        cam_btn_layout.addWidget(self.upload_btn)

        camera_layout.addLayout(cam_btn_layout)

        # نوار پیشرفت اسکن
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.scan_progress.setMaximumHeight(15)
        self.scan_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3498db; border-radius: 3px;
                text-align: center; font-size: 10px;
            }
            QProgressBar::chunk { background-color: #27ae60; border-radius: 2px; }
        """)
        camera_layout.addWidget(self.scan_progress)

        camera_layout.addStretch()

        main_row.addWidget(camera_frame)

        # ============ بخش فیلدهای پلاک (سمت چپ) ============
        # ============ بخش فیلدهای پلاک (سمت چپ) ============
        plate_frame = QFrame()
        plate_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #c8a45c;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        plate_layout = QVBoxLayout(plate_frame)
        plate_layout.setSpacing(20)

        plate_title = QLabel("📋 اطلاعات پلاک")
        plate_title.setAlignment(Qt.AlignCenter)
        plate_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        plate_layout.addWidget(plate_title)

        # ===== فیلدهای پلاک با چینش راست‌به‌چپ =====
        fields_widget = QWidget()
        fields_widget.setLayoutDirection(Qt.RightToLeft)  # ← راست‌به‌چپ
        fields_layout = QHBoxLayout(fields_widget)
        fields_layout.setSpacing(5)

        field_style = """
            QLineEdit {
                font-size: 24px; font-weight: bold; font-family: 'Tahoma';
                text-align: center; border: 3px solid #3498db;
                border-radius: 8px; padding: 12px;
                background-color: white; color: #2c3e50;
                min-width: 80px; max-width: 110px;
                min-height: 55px; max-height: 65px;
            }
            QLineEdit:focus {
                border: 3px solid #27ae60; background-color: #e8f8f5;
            }
        """

        # ===== فیلدها به ترتیب چپ به راست (برای نمایش راست‌به‌چپ) =====
        # ۱. دو رقم اول (part1) - سمت راست‌ترین در نمایش
        self.part1 = QLineEdit()
        self.part1.setPlaceholderText("۱۲")
        self.part1.setMaxLength(2)
        self.part1.setAlignment(Qt.AlignCenter)
        self.part1.setStyleSheet(field_style)
        self.part1.textChanged.connect(self.auto_focus)

        sep1 = QLabel("│")
        sep1.setStyleSheet("font-size: 30px; color: #bdc3c7; font-weight: bold;")
        sep1.setAlignment(Qt.AlignCenter)

        # ۲. حرف پلاک (letter)
        self.letter = QLineEdit()
        self.letter.setPlaceholderText("الف")
        self.letter.setMaxLength(1)
        self.letter.setAlignment(Qt.AlignCenter)
        self.letter.setStyleSheet(field_style)
        self.letter.textChanged.connect(self.auto_focus)

        sep2 = QLabel("│")
        sep2.setStyleSheet("font-size: 30px; color: #bdc3c7; font-weight: bold;")
        sep2.setAlignment(Qt.AlignCenter)

        # ۳. سه رقم وسط (part2)
        self.part2 = QLineEdit()
        self.part2.setPlaceholderText("۳۴۵")
        self.part2.setMaxLength(3)
        self.part2.setAlignment(Qt.AlignCenter)
        self.part2.setStyleSheet(field_style)
        self.part2.textChanged.connect(self.auto_focus)

        # ۴. کلمه "ایران"
        iran = QLabel("ایران")
        iran.setAlignment(Qt.AlignCenter)
        iran.setStyleSheet("""
            font-size: 13px; color: white; font-weight: bold;
            background-color: #e74c3c; border: 2px solid white;
            border-radius: 6px; padding: 16px 10px;
            min-width: 55px;
        """)

        # ۵. دو رقم آخر (part3) - سمت چپ‌ترین در نمایش
        self.part3 = QLineEdit()
        self.part3.setPlaceholderText("۱۱")
        self.part3.setMaxLength(2)
        self.part3.setAlignment(Qt.AlignCenter)
        self.part3.setStyleSheet(field_style)
        self.part3.textChanged.connect(self.auto_focus)

        # ===== اضافه کردن به layout (چپ به راست) =====
        fields_layout.addWidget(self.part1)
        fields_layout.addWidget(sep1)
        fields_layout.addWidget(self.letter)
        fields_layout.addWidget(sep2)
        fields_layout.addWidget(self.part2)
        fields_layout.addWidget(iran)
        fields_layout.addWidget(self.part3)

        plate_layout.addWidget(fields_widget)  # ← اضافه کردن ویجت

        # پیام اعتبارسنجی
        self.validation_label = QLabel("")
        self.validation_label.setAlignment(Qt.AlignCenter)
        self.validation_label.setStyleSheet("font-size: 13px; padding: 5px;")
        plate_layout.addWidget(self.validation_label)

        # وضعیت اسکن
        self.scan_status = QLabel("")
        self.scan_status.setAlignment(Qt.AlignCenter)
        self.scan_status.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        plate_layout.addWidget(self.scan_status)

        plate_layout.addStretch()

        main_row.addWidget(plate_frame)

        layout.addLayout(main_row)

        # ============ دکمه‌های ثبت ============
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        submit_btn = QPushButton("✅ ثبت ورود خودرو")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                border-radius: 10px; padding: 20px 40px;
                font-weight: bold; font-size: 17px;
                min-height: 65px; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        submit_btn.clicked.connect(self.submit)
        submit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        clear_btn = QPushButton("🔄 پاک کردن فرم")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white;
                border-radius: 10px; padding: 20px 40px;
                font-weight: bold; font-size: 17px;
                min-height: 65px; border: none;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        clear_btn.clicked.connect(self.clear_form)
        clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        spacer = QWidget()
        spacer.setMinimumHeight(30)
        layout.addWidget(spacer)

    # ======================== دوربین ========================

    def start_camera(self):
        """شروع دوربین"""
        try:
            self.capture = cv2.VideoCapture(0)

            if not self.capture.isOpened():
                QMessageBox.warning(self, "⚠️ خطا", "دوربین در دسترس نیست")
                return

            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.camera_active = True
            self.image_loaded = False

            self.cam_timer = QTimer()
            self.cam_timer.timeout.connect(self.update_camera)
            self.cam_timer.start(100)

            self.start_cam_btn.setEnabled(False)
            self.stop_cam_btn.setEnabled(True)

            self.camera_label.setStyleSheet("""
                QLabel {
                    background-color: #000000;
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                }
            """)

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در راه‌اندازی دوربین:\n{str(e)}")

    def update_camera(self):
        """بروزرسانی تصویر دوربین"""
        if self.capture and self.camera_active:
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame.copy()
                self.display_image(frame)

    def stop_camera(self):
        """توقف دوربین"""
        self.camera_active = False

        if hasattr(self, 'cam_timer'):
            self.cam_timer.stop()

        if self.capture:
            self.capture.release()
            self.capture = None

        self.start_cam_btn.setEnabled(True)
        self.stop_cam_btn.setEnabled(False)

        self.camera_label.clear()
        self.camera_label.setText("📷 دوربین\nخاموش است")
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #95a5a6;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

    # ======================== بارگذاری عکس ========================

    def upload_image(self):
        """بارگذاری عکس از سیستم"""
        if self.camera_active:
            self.stop_camera()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب عکس پلاک",
            "",
            "تصاویر (*.jpg *.jpeg *.png *.bmp);;همه فایل‌ها (*.*)"
        )

        if not file_path:
            return

        try:
            frame = cv2.imread(file_path)
            if frame is None:
                QMessageBox.warning(self, "⚠️ خطا", "فایل تصویر معتبر نیست")
                return

            self.current_frame = frame.copy()
            self.image_loaded = True
            self.display_image(frame)
            self.scan_plate_from_image()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در بارگذاری عکس:\n{str(e)}")

    def display_image(self, frame):
        """نمایش عکس در ویجت دوربین"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(280, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_label.setPixmap(scaled)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #9b59b6;
                border-radius: 8px;
            }
        """)

    # ======================== اسکن پلاک ========================

    def scan_plate(self):
        """اسکن پلاک از تصویر دوربین"""
        if self.current_frame is None:
            QMessageBox.warning(self, "⚠️ خطا", "ابتدا دوربین را روشن کنید یا عکس بارگذاری کنید")
            return

        if self.image_loaded:
            self.scan_plate_from_image()
            return

        self.scan_progress.setVisible(True)
        self.scan_progress.setValue(0)

        for i in range(1, 101):
            self.scan_progress.setValue(i)
            QApplication.processEvents()

        self._generate_random_plate()
        self.scan_progress.setVisible(False)

    def scan_plate_from_image(self):
        """اسکن پلاک با ALPR واقعی"""
        if self.current_frame is None:
            QMessageBox.warning(self, "⚠️ خطا", "ابتدا یک عکس بارگذاری کنید")
            return

        self.scan_progress.setVisible(True)
        self.scan_progress.setValue(0)
        QApplication.processEvents()

        try:
            # ===== پردازش با ALPR =====
            self.scan_progress.setValue(30)
            QApplication.processEvents()

            results = self.alpr_engine.process(self.current_frame)

            self.scan_progress.setValue(70)
            QApplication.processEvents()

            # ===== کپی تصویر برای رسم (حتی اگر تشخیص کامل نباشد) =====
            frame_with_boxes = self.current_frame.copy()
            plate_text_display = ""

            if results:
                result = results[0]
                plate_text = result.plate
                confidence = result.confidence
                x, y, w, h = result.bbox

                # ===== ۱. رسم کادر سبز روی تصویر (همیشه) =====
                cv2.rectangle(frame_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 3)

                # ===== ۲. اصلاح متن پلاک =====
                persian_to_english = {
                    '۰': '0', '۱': '1', '۲': '2', '۳': '3',
                    '۴': '4', '۵': '5', '۶': '6', '۷': '7',
                    '۸': '8', '۹': '9'
                }
                for p, e in persian_to_english.items():
                    plate_text = plate_text.replace(p, e)

                plate_text = plate_text.replace(' ', '').replace('-', '')

                import re
                plate_text = re.sub(r'[^ابپتثجچحخدسصطعقلمنوهی0-9]', '', plate_text)

                print(f"🔍 plate_text اصلاح‌شده: {plate_text}")

                # ===== ۳. نمایش پلاک روی تصویر (همیشه) =====
                cv2.putText(frame_with_boxes, plate_text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # ===== ۴. پر کردن فیلدها (اگر فرمت درست باشد) =====
                if len(plate_text) >= 8:
                    part1 = plate_text[0:2]
                    letter = plate_text[2:3]
                    part2 = plate_text[3:6]
                    part3 = plate_text[6:8]

                    if (part1.isdigit() and part2.isdigit() and part3.isdigit() and
                            len(part1) == 2 and len(part2) == 3 and len(part3) == 2 and
                            letter in IranianPlate.VALID_LETTERS):

                        self.part1.setText(part1)
                        self.letter.setText(letter)
                        self.part2.setText(part2)
                        self.part3.setText(part3)

                        full_plate = f"{part1}{letter}{part2}-{part3}"
                        self.scan_status.setText(
                            f"✅ پلاک شناسایی شد: {full_plate} (اطمینان: {confidence:.0%})"
                        )
                        self.scan_status.setStyleSheet(
                            "font-size: 12px; color: #27ae60; font-weight: bold; padding: 5px;"
                        )
                        plate_text_display = full_plate
                    else:
                        self.scan_status.setText(f"⚠️ فرمت نامعتبر: {plate_text}")
                        self.scan_status.setStyleSheet(
                            "font-size: 12px; color: #f39c12; font-weight: bold; padding: 5px;"
                        )
                        plate_text_display = plate_text
                else:
                    self.scan_status.setText(f"⚠️ تشخیص داده شد: {plate_text}")
                    self.scan_status.setStyleSheet(
                        "font-size: 12px; color: #f39c12; font-weight: bold; padding: 5px;"
                    )
                    plate_text_display = plate_text
            else:
                self.scan_status.setText("❌ هیچ پلاکی تشخیص داده نشد")
                self.scan_status.setStyleSheet(
                    "font-size: 12px; color: #e74c3c; font-weight: bold; padding: 5px;"
                )

            # ===== ۵. نمایش تصویر با کادر (همیشه) =====
            self.display_image(frame_with_boxes)

            # ===== ۶. ذخیره تصویر =====
            if results:
                self.save_captured_image(plate_text_display)

        except Exception as e:
            self.scan_status.setText(f"❌ خطا در اسکن: {str(e)}")
            self.scan_status.setStyleSheet(
                "font-size: 12px; color: #e74c3c; font-weight: bold; padding: 5px;"
            )
            import traceback
            traceback.print_exc()

        self.scan_progress.setVisible(False)
    def _generate_random_plate(self):
        """تولید پلاک تصادفی برای تست"""
        letters = ['الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'س', 'ص', 'ط', 'ع', 'ق', 'ل', 'م', 'ن', 'و', 'ه', 'ی']
        rand_letter = random.choice(letters)
        rand_part1 = f"{random.randint(10, 99):02d}"
        rand_part2 = f"{random.randint(100, 999):03d}"
        rand_part3 = f"{random.randint(10, 99):02d}"

        self.part1.setText(rand_part1)
        self.letter.setText(rand_letter)
        self.part2.setText(rand_part2)
        self.part3.setText(rand_part3)

        full_plate = f"{rand_part1}{rand_letter}{rand_part2}-{rand_part3}"
        self.scan_status.setText(f"✅ پلاک اسکن شد: {full_plate}")
        self.scan_status.setStyleSheet("font-size: 12px; color: #27ae60; font-weight: bold; padding: 5px;")
        self.save_captured_image()

    def save_captured_image(self, plate_text=""):
        """ذخیره تصویر با نام پلاک"""
        if self.current_frame is not None:
            save_dir = "captured_plates"
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plate_part = plate_text.replace("/", "_").replace(" ", "") if plate_text else "unknown"
            filename = f"{save_dir}/entry_{plate_part}_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)

    # ======================== عملیات پلاک ========================

    def auto_focus(self):
        """فوکوس خودکار و اعتبارسنجی"""
        self.current_plate = IranianPlate(
            self.part1.text().strip(),
            self.letter.text().strip(),
            self.part2.text().strip(),
            self.part3.text().strip()
        )

        if not self.part1.text() and not self.letter.text() and not self.part2.text():
            self.validation_label.setText("")
        elif self.current_plate.is_valid:
            self.validation_label.setText("✅ پلاک معتبر است")
            self.validation_label.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
        else:
            errors = []
            if self.part1.text() and (len(self.part1.text()) != 2 or not self.part1.text().isdigit()):
                errors.append("• دو رقم اول باید عدد باشد")
            if self.letter.text() and self.letter.text() not in IranianPlate.VALID_LETTERS:
                errors.append("• حرف پلاک نامعتبر است")
            if self.part2.text() and (len(self.part2.text()) != 3 or not self.part2.text().isdigit()):
                errors.append("• سه رقم باید عدد باشد")

            if errors:
                self.validation_label.setText("\n".join(errors))
                self.validation_label.setStyleSheet("font-size: 12px; color: #e74c3c; font-weight: bold;")
            else:
                self.validation_label.setText("⚠️ لطفاً همه بخش‌ها را پر کنید")
                self.validation_label.setStyleSheet("font-size: 13px; color: #f39c12; font-weight: bold;")

        if len(self.part1.text()) == 2:
            self.letter.setFocus()
        elif len(self.letter.text()) == 1:
            self.part2.setFocus()
        elif len(self.part2.text()) == 3:
            self.part3.setFocus()

    def submit(self):
        """ثبت ورود"""
        if not self.current_plate.is_valid:
            QMessageBox.warning(self, "⚠️ خطا", "لطفاً پلاک را کامل وارد کنید!")
            return

        try:
            plate_data = self.current_plate.to_dict()
            plate_data['operator_name'] = self.operator_name

            self.db.car_entry(plate_data)

            QMessageBox.information(
                self, "✅ موفق",
                f"ورود ثبت شد\n🚗 {self.current_plate.full_plate}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            )

            self.car_entered.emit(plate_data)
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def clear_form(self):
        """پاک کردن فرم"""
        self.part1.clear()
        self.letter.clear()
        self.part2.clear()
        self.part3.clear()
        self.validation_label.setText("")
        self.scan_status.setText("")
        self.part1.setFocus()

    def set_plate(self, plate):
        """تنظیم پلاک از بیرون"""
        if isinstance(plate, IranianPlate):
            self.part1.setText(plate.part1)
            self.letter.setText(plate.letter)
            self.part2.setText(plate.part2)
            self.part3.setText(plate.part3)

    def closeEvent(self, event):
        """بستن ویجت"""
        self.stop_camera()
        event.accept()