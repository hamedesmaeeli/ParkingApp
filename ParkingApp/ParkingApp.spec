# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # ===== اضافه کردن فایل‌های مدل =====
        ('alpr/models', 'alpr/models'),
        # ===== اضافه کردن فایل‌های دیتابیس اولیه =====
        ('data', 'data'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cv2',
        'torch',
        'ultralytics',
        'hezar',
        'jdatetime',
        'openpyxl',
        'reportlab',
        'serial',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ===== حذف کتابخانه‌های غیرضروری =====
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ===== حالت onedir (بدون onefile) =====
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # ← مهم: فایل‌های باینری جدا می‌شوند
    name='ParkingApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # ← برای دیباگ True، بعداً False کنید
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # ← اگر آیکون دارید
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ParkingApp',  # ← نام پوشه خروجی
)