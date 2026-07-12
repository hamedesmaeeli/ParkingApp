"""
ویجت دوربین و پلاک‌خوانی - نسخه نهایی
"""

from alpr.engine import ALPREngine
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGroupBox, QCheckBox,
    QComboBox, QProgressBar, QMessageBox,
    QSizePolicy, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from datetime import datetime
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PlateDetectorThread(QThread):
    """Thread تشخیص پلاک برای دوربین زنده"""

    frame_processed = pyqtSignal(np.ndarray)
    plate_detected = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        self.running = False
        self.detect_enabled = True
        self.current_frame = None
        self.alpr_engine = ALPREngine()

    def run(self):
        self.running = True
        while self.running:
            if self.current_frame is not None and self.detect_enabled:
                frame = self.current_frame.copy()
                results = self.detect_plates(frame)

                for result in results:

                    x, y, w, h = result.bbox

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        3
                    )

                    cv2.putText(
                        frame,
                        result.plate,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 255, 0),
                        2
                    )

                    if result.confidence > 0.6:
                        self.plate_detected.emit(
                            result.plate,
                            result.confidence
                        )
                        self.plate_detected.emit(plate_text, confidence)
                self.frame_processed.emit(frame)
            self.msleep(100)

    def detect_plates(self, frame):
        return self.alpr_engine.process(frame)

class CameraWidget(QWidget):
    """ویجت دوربین با تشخیص پلاک"""

    plate_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.camera_active = False
        self.capture = None
        self.detector_thread = None
        self.current_frame = None
        self.detected_count = 0
        self.last_detected_plate = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)

        # عنوان
        title = QLabel("📷 دوربین و پلاک‌خوانی")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 15px;")
        layout.addWidget(title)

        # نمایشگر
        camera_group = QGroupBox("نمایش زنده دوربین")
        camera_group.setStyleSheet("""
            QGroupBox { font-size: 16px; font-weight: bold; border: 2px solid #3498db;
                border-radius: 10px; margin-top: 15px; padding: 15px; padding-top: 35px; background-color: white; }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #3498db; color: white; border-radius: 5px; }
        """)
        camera_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setMinimumHeight(400)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(
            "QLabel { background-color: #1a1a1a; color: #95a5a6; border: 2px solid #34495e; border-radius: 10px; font-size: 20px; font-weight: bold; }")
        self.camera_label.setText("📷 دوربین غیرفعال است\n\nبرای شروع روی دکمه زیر کلیک کنید\nیا یک عکس بارگذاری کنید")
        camera_layout.addWidget(self.camera_label)
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)

        # کنترل‌ها
        controls_group = QGroupBox("🎮 کنترل‌ها")
        controls_group.setStyleSheet("""
            QGroupBox { font-size: 16px; font-weight: bold; border: 2px solid #27ae60;
                border-radius: 10px; margin-top: 15px; padding: 15px; padding-top: 35px; background-color: white; }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #27ae60; color: white; border-radius: 5px; }
        """)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_style = "QPushButton { color: white; font-weight: bold; padding: 12px 20px; border-radius: 8px; font-size: 14px; border: none; min-height: 45px; } QPushButton:disabled { background-color: #95a5a6; }"

        self.start_btn = QPushButton("🎥 شروع دوربین")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; " + btn_style + " } QPushButton:hover { background-color: #2ecc71; }")
        self.start_btn.clicked.connect(self.start_camera)
        self.start_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #e74c3c; " + btn_style + " } QPushButton:hover { background-color: #c0392b; }")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.capture_btn = QPushButton("📸 عکس")
        self.capture_btn.setStyleSheet(
            "QPushButton { background-color: #f39c12; " + btn_style + " } QPushButton:hover { background-color: #e67e22; }")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        self.capture_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.load_btn = QPushButton("📂 بارگذاری عکس")
        self.load_btn.setStyleSheet(
            "QPushButton { background-color: #9b59b6; " + btn_style + " } QPushButton:hover { background-color: #8e44ad; }")
        self.load_btn.clicked.connect(self.load_image)
        self.load_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.load_btn)
        controls_layout.addLayout(btn_layout)

        # تنظیمات
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(20)
        settings_layout.addWidget(QLabel("📷 دوربین:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["دوربین ۰", "دوربین ۱", "دوربین ۲"])
        self.camera_combo.setStyleSheet(
            "font-size: 13px; padding: 8px; border: 2px solid #ddd; border-radius: 6px; min-width: 130px;")
        settings_layout.addWidget(self.camera_combo)
        settings_layout.addStretch()
        self.auto_detect_cb = QCheckBox("🔍 تشخیص خودکار")
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        self.auto_save_cb = QCheckBox("💾 ذخیره تصاویر")
        self.auto_save_cb.setChecked(True)
        self.auto_save_cb.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        settings_layout.addWidget(self.auto_detect_cb)
        settings_layout.addWidget(self.auto_save_cb)
        controls_layout.addLayout(settings_layout)

        # وضعیت
        self.status_label = QLabel("🟢 آماده به کار")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #27ae60; padding: 8px; background-color: #f8f9fa; border-radius: 6px;")
        controls_layout.addWidget(self.status_label)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # آمار
        stats_group = QGroupBox("📊 آمار تشخیص")
        stats_group.setStyleSheet("""
            QGroupBox { font-size: 16px; font-weight: bold; border: 2px solid #9b59b6;
                border-radius: 10px; margin-top: 15px; padding: 15px; padding-top: 35px; background-color: white; }
            QGroupBox::title { left: 15px; padding: 8px 20px; background-color: #9b59b6; color: white; border-radius: 5px; }
        """)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        self.detected_count_label = QLabel("🔍 تشخیص: ۰")
        self.last_detected_label = QLabel("📋 آخرین پلاک: ---")
        self.saved_count_label = QLabel("💾 ذخیره: ۰")
        for lbl in [self.detected_count_label, self.last_detected_label, self.saved_count_label]:
            lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")
            stats_layout.addWidget(lbl)
        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

    # ==================== دوربین ====================

    def start_camera(self):
        try:
            idx = int(self.camera_combo.currentText().split()[-1])
            self.capture = cv2.VideoCapture(idx)
            if not self.capture.isOpened():
                QMessageBox.warning(self, "⚠️ خطا", f"دوربین {idx} در دسترس نیست")
                return
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_active = True
            self.detector_thread = PlateDetectorThread()
            self.detector_thread.frame_processed.connect(self.update_frame)
            self.detector_thread.plate_detected.connect(self.on_plate_detected)
            self.detector_thread.start()
            self.frame_timer = QTimer()
            self.frame_timer.timeout.connect(self.capture_frame)
            self.frame_timer.start(100)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.capture_btn.setEnabled(True)
            self.status_label.setText("🔴 دوربین فعال")
            self.status_label.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #e74c3c; padding: 8px; background-color: #fadbd8; border-radius: 6px;")
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", str(e))

    def capture_frame(self):
        if self.capture and self.camera_active:
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame.copy()
                if self.detector_thread and self.auto_detect_cb.isChecked():
                    self.detector_thread.current_frame = frame.copy()
                else:
                    self.display_frame(frame)

    def update_frame(self, frame):
        self.display_frame(frame)

    def display_frame(self, frame):
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qt_img)
            self.camera_label.setPixmap(
                pix.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            pass

    def stop_camera(self):
        self.camera_active = False
        if hasattr(self, 'frame_timer'): self.frame_timer.stop()
        if self.detector_thread: self.detector_thread.stop(); self.detector_thread = None
        if self.capture: self.capture.release(); self.capture = None
        self.start_btn.setEnabled(True);
        self.stop_btn.setEnabled(False);
        self.capture_btn.setEnabled(False)
        self.camera_label.clear()
        self.camera_label.setText("📷 دوربین غیرفعال است\n\nبرای شروع کلیک کنید\nیا عکس بارگذاری کنید")
        self.camera_label.setStyleSheet(
            "QLabel { background-color: #1a1a1a; color: #95a5a6; border: 2px solid #34495e; border-radius: 10px; font-size: 20px; font-weight: bold; }")
        self.status_label.setText("🟢 آماده به کار")
        self.status_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #27ae60; padding: 8px; background-color: #f8f9fa; border-radius: 6px;")

    # ==================== بارگذاری عکس ====================

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب عکس", "",
                                                   "Images (*.jpg *.jpeg *.png *.bmp);;All (*.*)")
        if not file_path: return
        try:
            frame = cv2.imread(file_path)
            if frame is None: return QMessageBox.warning(self, "⚠️", "فایل نامعتبر")

            h, w = frame.shape[:2]
            self.status_label.setText(f"📂 سایز اصلی: {w}×{h}")
            QApplication.processEvents()

            # بزرگ کردن عکس‌های کوچک
            if w < 1000:
                scale = 1000 / w
                frame = cv2.resize(frame, (1000, int(h * scale)), interpolation=cv2.INTER_CUBIC)

            self.current_frame = frame.copy()
            self.status_label.setText(f"📂 سایز: {frame.shape[1]}×{frame.shape[0]} - تشخیص...")
            self.status_label.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #9b59b6; padding: 8px; background-color: #f5eef8; border-radius: 6px;")
            QApplication.processEvents()

            self.display_frame(frame)
            self.detect_on_image(frame)
        except Exception as e:
            QMessageBox.critical(self, "❌", str(e))

       # ==================== رویدادها ====================

    def on_plate_detected(self, plate_text, confidence):
        if plate_text != self.last_detected_plate:
            self.detected_count += 1
            self.last_detected_plate = plate_text
            self.detected_count_label.setText(f"🔍 تشخیص: {self.detected_count}")
            self.last_detected_label.setText(f"📋 {plate_text}")
            self.plate_detected.emit(plate_text)
            if self.auto_save_cb.isChecked() and self.current_frame is not None:
                self.save_image()

    def save_image(self):
        try:
            d = "captured_plates"
            os.makedirs(d, exist_ok=True)
            fn = f"{d}/plate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(fn, self.current_frame)
            self.saved_count_label.setText(f"💾 ذخیره: {len(os.listdir(d))}")
        except:
            pass

    def capture_image(self):
        if self.current_frame is not None:
            self.save_image()
            QMessageBox.information(self, "✅", "تصویر ذخیره شد")

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()