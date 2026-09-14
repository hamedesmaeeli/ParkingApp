# ui/unified_widget.py
"""
فرم یکپارچه ورود/خروج با دوربین و کارت‌خوان
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGroupBox, QMessageBox,
    QFileDialog, QApplication, QProgressBar, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_utils import IranianPlate
from alpr.engine import ALPREngine
from rfid import RFIDIntegration


class UnifiedWidget(QWidget):
    """فرم یکپارچه ورود/خروج"""

    car_entered = pyqtSignal(dict)
    car_exited = pyqtSignal(dict)

    def __init__(self, database, rfid, operator_name="admin"):
        super().__init__()
        self.db = database
        self.operator_name = operator_name
        self.camera_active = False
        self.capture = None
        self.current_frame = None
        self.current_card = None
        self.current_plate = None
        self.card_info = None
        self.mode = None  # 'entry' یا 'exit'

        # ===== ALPR =====
        self.alpr_engine = ALPREngine(mock_mode=False)

        # ===== RFID =====
        self.rfid = rfid
        self.rfid.card_scanned.connect(self.on_card_scanned)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ===== عنوان =====
        title = QLabel("🚦 ورود/خروج یکپارچه")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # ===== ردیف اصلی =====
        main_row = QHBoxLayout()
        main_row.setSpacing(20)

        # ===== بخش چپ: دوربین =====
        camera_group = QGroupBox("📷 دوربین")
        camera_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #3498db; border-radius: 10px;
                padding: 15px; padding-top: 30px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 5px 15px; background-color: #3498db; color: white; border-radius: 5px; }
        """)
        camera_layout = QVBoxLayout()

        self.camera_label = QLabel()
        self.camera_label.setFixedSize(400, 300)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #95a5a6;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.camera_label.setText("📷 دوربین خاموش است\n\nبرای شروع کلیک کنید")
        camera_layout.addWidget(self.camera_label)

        # دکمه‌های دوربین
        cam_btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ شروع")
        self.start_btn.clicked.connect(self.start_camera)
        self.start_btn.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px 20px; border-radius: 5px; border: none;")

        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px 20px; border-radius: 5px; border: none;")

        self.upload_btn = QPushButton("📂 بارگذاری عکس")
        self.upload_btn.clicked.connect(self.upload_image)
        self.upload_btn.setStyleSheet(
            "background-color: #9b59b6; color: white; padding: 8px 20px; border-radius: 5px; border: none;")

        cam_btn_layout.addWidget(self.start_btn)
        cam_btn_layout.addWidget(self.stop_btn)
        cam_btn_layout.addWidget(self.upload_btn)
        camera_layout.addLayout(cam_btn_layout)

        # نوار پیشرفت
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.scan_progress.setMaximumHeight(15)
        camera_layout.addWidget(self.scan_progress)

        camera_group.setLayout(camera_layout)
        main_row.addWidget(camera_group)

        # ===== بخش راست: اطلاعات =====
        info_group = QGroupBox("🎫 اطلاعات کارت و خودرو")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #c8a45c; border-radius: 10px;
                padding: 15px; padding-top: 30px;
                background-color: white;
            }
            QGroupBox::title { left: 15px; padding: 5px 15px; background-color: #c8a45c; color: white; border-radius: 5px; }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        # وضعیت کارت
        self.card_status_label = QLabel("📇 وضعیت کارت: منتظر کارت...")
        self.card_status_label.setStyleSheet("font-size: 14px; padding: 5px;")
        info_layout.addWidget(self.card_status_label)

        # شماره کارت
        self.card_number_label = QLabel("🆔 شماره کارت: ---")
        self.card_number_label.setStyleSheet("font-size: 14px; padding: 5px;")
        info_layout.addWidget(self.card_number_label)

        # پلاک
        self.plate_label = QLabel("🚗 پلاک: ---")
        self.plate_label.setStyleSheet("font-size: 14px; padding: 5px;")
        info_layout.addWidget(self.plate_label)

        # زمان ورود
        self.entry_time_label = QLabel("⏰ زمان ورود: ---")
        self.entry_time_label.setStyleSheet("font-size: 14px; padding: 5px;")
        info_layout.addWidget(self.entry_time_label)

        # مدت توقف
        self.duration_label = QLabel("⏱️ مدت توقف: ---")
        self.duration_label.setStyleSheet("font-size: 14px; padding: 5px;")
        info_layout.addWidget(self.duration_label)

        # هزینه
        self.cost_label = QLabel("💰 هزینه: ---")
        self.cost_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #e74c3c; padding: 10px; background-color: #fadbd8; border-radius: 5px;")
        info_layout.addWidget(self.cost_label)

        # ورود دستی پلاک
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("پلاک دستی:"))
        self.manual_plate_input = QLineEdit()
        self.manual_plate_input.setPlaceholderText("مثال: 12الف345-67")
        self.manual_plate_input.setStyleSheet("padding: 8px; border: 2px solid #ddd; border-radius: 5px;")
        manual_layout.addWidget(self.manual_plate_input)

        self.manual_btn = QPushButton("📝 ثبت دستی")
        self.manual_btn.clicked.connect(self.manual_entry)
        self.manual_btn.setStyleSheet(
            "background-color: #f39c12; color: white; padding: 8px 15px; border-radius: 5px; border: none;")
        manual_layout.addWidget(self.manual_btn)
        info_layout.addLayout(manual_layout)

        # دکمه‌های عملیاتی
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.entry_btn = QPushButton("✅ ثبت ورود")
        self.entry_btn.clicked.connect(self.confirm_entry)
        self.entry_btn.setEnabled(False)
        self.entry_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 15px; border-radius: 8px; font-weight: bold;
                border: none; font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)

        self.exit_btn = QPushButton("✅ ثبت خروج")
        self.exit_btn.clicked.connect(self.confirm_exit)
        self.exit_btn.setEnabled(False)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                padding: 15px; border-radius: 8px; font-weight: bold;
                border: none; font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)

        self.clear_btn = QPushButton("🔄 پاک کردن")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white;
                padding: 15px; border-radius: 8px; font-weight: bold;
                border: none; font-size: 14px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)

        btn_layout.addWidget(self.entry_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addWidget(self.clear_btn)
        info_layout.addLayout(btn_layout)

        # وضعیت سیستم
        self.status_label = QLabel("🔄 آماده به کار...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        info_layout.addWidget(self.status_label)

        info_group.setLayout(info_layout)
        main_row.addWidget(info_group)

        layout.addLayout(main_row)

    # ======================== دوربین ========================

    def start_camera(self):
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                QMessageBox.warning(self, "⚠️ خطا", "دوربین در دسترس نیست")
                return

            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_active = True

            self.cam_timer = QTimer()
            self.cam_timer.timeout.connect(self.update_camera)
            self.cam_timer.start(50)

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("🔴 دوربین فعال")
            self.status_label.setStyleSheet("font-size: 12px; color: #e74c3c; padding: 5px;")

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def update_camera(self):
        if self.capture and self.camera_active:
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame.copy()
                self.display_frame(frame)
                # تشخیص خودکار پلاک (در صورت وجود کارت)
                if self.current_card and self.mode == 'entry' and not self.current_plate:
                    self.scan_plate()

    def display_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_img)
        self.camera_label.setPixmap(
            pix.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def stop_camera(self):
        self.camera_active = False
        if hasattr(self, 'cam_timer'):
            self.cam_timer.stop()
        if self.capture:
            self.capture.release()
            self.capture = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.camera_label.clear()
        self.camera_label.setText("📷 دوربین خاموش است\n\nبرای شروع کلیک کنید")
        self.status_label.setText("🟢 دوربین غیرفعال")
        self.status_label.setStyleSheet("font-size: 12px; color: #27ae60; padding: 5px;")

    def upload_image(self):
        if self.camera_active:
            self.stop_camera()

        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب عکس پلاک", "",
            "Images (*.jpg *.jpeg *.png *.bmp);;All (*.*)"
        )
        if not file_path:
            return

        try:
            frame = cv2.imread(file_path)
            if frame is None:
                QMessageBox.warning(self, "⚠️ خطا", "فایل تصویر معتبر نیست")
                return

            self.current_frame = frame.copy()
            self.display_frame(frame)
            self.scan_plate()
            self.status_label.setText("📂 عکس بارگذاری شد")

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    # ======================== RFID ========================

    def on_card_scanned(self, uid):
        """وقتی کارت RFID اسکن شد"""
        print(f"📇 کارت اسکن شد: {uid}")

        try:
            self.card_info = self.db.get_card_by_uid(uid)
            print(f"🔍 اطلاعات کارت: {self.card_info}")

            if not self.card_info:
                self.status_label.setText(f"❌ کارت {uid} در سیستم ثبت نشده است")
                self.status_label.setStyleSheet("font-size: 12px; color: #e74c3c; padding: 5px;")
                self.clear_form()
                return

            self.current_card = uid
            card_number = self.card_info['card_number']
            status = self.card_info['status']

            self.card_number_label.setText(f"🆔 شماره کارت: {card_number}")

            if status == 'active':
                # کارت آزاد است → ورود
                self.mode = 'entry'
                self.card_status_label.setText("📇 وضعیت: ✅ فعال (ورود)")
                self.card_status_label.setStyleSheet(
                    "font-size: 14px; padding: 5px; color: #27ae60; font-weight: bold;")
                self.entry_btn.setEnabled(False)
                self.exit_btn.setEnabled(False)
                self.status_label.setText("🔄 در حال تشخیص پلاک...")
                self.status_label.setStyleSheet("font-size: 12px; color: #3498db; padding: 5px;")

                # اگر دوربین روشن است، پلاک را تشخیص بده
                if self.current_frame is not None:
                    self.scan_plate()
                else:
                    self.status_label.setText("📷 لطفاً دوربین را روشن کنید یا عکس بارگذاری کنید")
                    self.status_label.setStyleSheet("font-size: 12px; color: #f39c12; padding: 5px;")

            elif status == 'in_use':
                # کارت در حال استفاده است → خروج
                self.mode = 'exit'
                self.card_status_label.setText("📇 وضعیت: 🔄 در حال استفاده (خروج)")
                self.card_status_label.setStyleSheet(
                    "font-size: 14px; padding: 5px; color: #f39c12; font-weight: bold;")

                plate = self.card_info.get('assigned_to')
                if plate:
                    self.current_plate = plate
                    self.plate_label.setText(f"🚗 پلاک: {plate}")
                    self.show_exit_info(plate)
                    self.exit_btn.setEnabled(True)
                    self.entry_btn.setEnabled(False)
                else:
                    self.status_label.setText("⚠️ کارت به خودرویی اختصاص ندارد")
                    self.status_label.setStyleSheet("font-size: 12px; color: #e74c3c; padding: 5px;")

            else:
                self.status_label.setText(f"⚠️ وضعیت کارت نامعتبر: {status}")
                self.status_label.setStyleSheet("font-size: 12px; color: #e74c3c; padding: 5px;")

        except Exception as e:
            print(f"❌ خطا: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"❌ خطا: {str(e)}")

    # ======================== تشخیص پلاک ========================

    def scan_plate(self):
        """تشخیص پلاک از تصویر فعلی"""
        if self.current_frame is None:
            return

        self.scan_progress.setVisible(True)
        self.scan_progress.setValue(30)
        QApplication.processEvents()

        try:
            results = self.alpr_engine.process(self.current_frame)
            self.scan_progress.setValue(80)
            QApplication.processEvents()

            if results:
                result = results[0]
                plate_text = result.plate

                # اصلاح متن پلاک
                if isinstance(plate_text, dict):
                    plate_text = plate_text.get('text', '')

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

                print(f"🔍 پلاک تشخیص داده شد: {plate_text}")

                if len(plate_text) >= 8:
                    part1 = plate_text[0:2]
                    letter = plate_text[2:3]
                    part2 = plate_text[3:6]
                    part3 = plate_text[6:8]

                    if (part1.isdigit() and part2.isdigit() and part3.isdigit() and
                            len(part1) == 2 and len(part2) == 3 and len(part3) == 2 and
                            letter in IranianPlate.VALID_LETTERS):

                        self.current_plate = f"{part1}{letter}{part2}-{part3}"
                        self.plate_label.setText(f"🚗 پلاک: {self.current_plate}")

                        if self.mode == 'entry':
                            self.entry_btn.setEnabled(True)
                            self.status_label.setText(f"✅ پلاک شناسایی شد: {self.current_plate}")
                            self.status_label.setStyleSheet("font-size: 12px; color: #27ae60; padding: 5px;")

                        # رسم کادر روی تصویر
                        if self.current_frame is not None:
                            x, y, w, h = result.bbox
                            frame_with_box = self.current_frame.copy()
                            cv2.rectangle(frame_with_box, (x, y), (x + w, y + h), (0, 255, 0), 3)
                            cv2.putText(frame_with_box, self.current_plate, (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            self.display_frame(frame_with_box)

                    else:
                        self.status_label.setText(f"⚠️ فرمت پلاک نامعتبر: {plate_text}")
                        self.status_label.setStyleSheet("font-size: 12px; color: #f39c12; padding: 5px;")
                else:
                    self.status_label.setText(f"⚠️ پلاک تشخیص داده شد اما ناقص است: {plate_text}")
                    self.status_label.setStyleSheet("font-size: 12px; color: #f39c12; padding: 5px;")
            else:
                if self.mode == 'entry':
                    self.status_label.setText("⚠️ پلاکی تشخیص داده نشد! لطفاً دستی وارد کنید.")
                    self.status_label.setStyleSheet("font-size: 12px; color: #f39c12; padding: 5px;")

        except Exception as e:
            print(f"❌ خطا در تشخیص پلاک: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"❌ خطا در تشخیص پلاک: {str(e)}")

        self.scan_progress.setVisible(False)

    # ======================== ورود دستی ========================

    def manual_entry(self):
        """ورود دستی پلاک"""
        plate_text = self.manual_plate_input.text().strip()
        if not plate_text:
            QMessageBox.warning(self, "⚠️ خطا", "لطفاً پلاک را وارد کنید!")
            return

        try:
            plate = IranianPlate.from_full_plate(plate_text)
            if plate.is_valid:
                self.current_plate = plate.full_plate
                self.plate_label.setText(f"🚗 پلاک: {self.current_plate}")

                if self.mode == 'entry':
                    self.entry_btn.setEnabled(True)
                    self.status_label.setText(f"✅ پلاک دستی ثبت شد: {self.current_plate}")
                    self.status_label.setStyleSheet("font-size: 12px; color: #27ae60; padding: 5px;")
                else:
                    QMessageBox.warning(self, "⚠️ خطا", "لطفاً ابتدا کارت را روی کارت‌خوان قرار دهید!")
            else:
                QMessageBox.warning(self, "⚠️ خطا", f"پلاک نامعتبر: {plate_text}")
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    # ======================== ورود ========================

    def confirm_entry(self):
        """تأیید ورود"""
        if not self.current_card or not self.current_plate:
            QMessageBox.warning(self, "⚠️ خطا", "اطلاعات کارت یا پلاک کامل نیست!")
            return

        try:
            card_number = self.card_info['card_number']

            # رزرو کارت
            self.db.reserve_card(card_number)

            # ثبت ورود
            plate = IranianPlate.from_full_plate(self.current_plate)
            plate_data = plate.to_dict()
            plate_data['operator_name'] = self.operator_name

            self.db.car_entry_with_card(plate_data, card_number)

            QMessageBox.information(
                self, "✅ ورود ثبت شد",
                f"🚗 پلاک: {self.current_plate}\n"
                f"🆔 کارت: {card_number}\n"
                f"⏰ زمان: {datetime.now().strftime('%H:%M:%S')}"
            )

            self.car_entered.emit(plate_data)
            self.clear_form()
            self.rfid.reader.buzzer(5)  # بوق موفقیت

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    # ======================== خروج ========================

    def show_exit_info(self, plate):
        """نمایش اطلاعات خروج با نرخ ساعت اول و دوم"""
        try:
            cars = self.db.get_active_cars()
            for car in cars:
                if car['plate_number'] == plate:
                    entry_time = datetime.fromisoformat(car['entry_time'])
                    self.entry_time_label.setText(f"⏰ زمان ورود: {entry_time.strftime('%H:%M:%S')}")

                    duration = datetime.now() - entry_time
                    hours = duration.total_seconds() / 3600
                    minutes = int(duration.total_seconds() / 60)

                    if hours >= 1:
                        self.duration_label.setText(f"⏱️ مدت توقف: {hours:.1f} ساعت ({minutes} دقیقه)")
                    else:
                        self.duration_label.setText(f"⏱️ مدت توقف: {minutes} دقیقه")

                    # ===== محاسبه هزینه با نرخ ساعت اول و دوم =====
                    first_hour_rate = float(self.db.get_setting('first_hour_rate', '10000'))
                    next_hours_rate = float(self.db.get_setting('next_hours_rate', '5000'))
                    free_minutes = int(self.db.get_setting('free_minutes', '15'))
                    max_daily = float(self.db.get_setting('max_daily_cost', '50000'))

                    if minutes <= free_minutes:
                        cost = 0
                        self.cost_label.setText("💰 هزینه: 🎉 رایگان (کمتر از ۱۵ دقیقه)")
                    else:
                        if hours <= 1:
                            # فقط ساعت اول
                            cost = first_hour_rate
                            detail = f"ساعت اول: {first_hour_rate:,.0f}"
                        else:
                            # ساعت اول + ساعات بعدی
                            extra_hours = int(hours)
                            cost = first_hour_rate + (extra_hours * next_hours_rate)
                            detail = (
                                f"ساعت اول: {first_hour_rate:,.0f} + "
                                f"{extra_hours} ساعت بعدی: {extra_hours * next_hours_rate:,.0f}"
                            )

                        # بررسی سقف روزانه
                        if cost > max_daily:
                            cost = max_daily
                            detail += " (سقف روزانه)"

                        self.cost_label.setText(
                            f"💰 هزینه: {cost:,.0f} تومان\n"
                            f"({detail})"
                        )
                        self.cost_label.setStyleSheet("""
                            font-size: 16px;
                            font-weight: bold;
                            color: #e74c3c;
                            padding: 10px;
                            background-color: #fadbd8;
                            border-radius: 8px;
                        """)

                    self.status_label.setText(f"✅ خودرو با پلاک {plate} پیدا شد")
                    self.status_label.setStyleSheet("font-size: 12px; color: #27ae60; padding: 5px;")
                    return

            self.status_label.setText(f"❌ خودرو با پلاک {plate} در پارکینگ نیست")
            self.status_label.setStyleSheet("font-size: 12px; color: #e74c3c; padding: 5px;")

        except Exception as e:
            print(f"❌ خطا: {e}")
            import traceback
            traceback.print_exc()

    def confirm_exit(self):
        """تأیید خروج"""
        if not self.current_card or not self.current_plate:
            QMessageBox.warning(self, "⚠️ خطا", "اطلاعات کارت یا پلاک کامل نیست!")
            return

        try:
            card_number = self.card_info['card_number']

            reply = QMessageBox.question(
                self, "تأیید خروج",
                f"آیا از خروج خودرو {self.current_plate} اطمینان دارید؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                result = self.db.car_exit_by_card(card_number, {
                    'operator_name': self.operator_name,
                    'payment_method': 'cash'
                })

                QMessageBox.information(
                    self, "✅ خروج موفق",
                    f"خروج ثبت شد\n\n"
                    f"🚗 پلاک: {self.current_plate}\n"
                    f"⏱️ مدت: {result['duration_hours']:.1f} ساعت\n"
                    f"💰 هزینه: {result['final_cost']:,.0f} تومان"
                )

                self.car_exited.emit(result)
                self.clear_form()
                self.rfid.reader.buzzer(5)  # بوق موفقیت

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    # ======================== فرم ========================

    def clear_form(self):
        """پاک کردن فرم"""
        self.current_card = None
        self.current_plate = None
        self.card_info = None
        self.mode = None

        self.card_status_label.setText("📇 وضعیت کارت: منتظر کارت...")
        self.card_status_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.card_number_label.setText("🆔 شماره کارت: ---")
        self.plate_label.setText("🚗 پلاک: ---")
        self.entry_time_label.setText("⏰ زمان ورود: ---")
        self.duration_label.setText("⏱️ مدت توقف: ---")
        self.cost_label.setText("💰 هزینه: ---")
        self.entry_btn.setEnabled(False)
        self.exit_btn.setEnabled(False)
        self.manual_plate_input.clear()
        self.status_label.setText("🔄 آماده به کار...")
        self.status_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")

    def closeEvent(self, event):
        self.stop_camera()

        event.accept()