# utils/date_utils.py
"""
Date Utils - تبدیل تاریخ میلادی به شمسی
"""

import jdatetime
from datetime import datetime


def to_shamsi(datetime_obj, format='%Y/%m/%d %H:%M:%S'):
    """
    تبدیل تاریخ میلادی به شمسی

    Args:
        datetime_obj: تاریخ میلادی (datetime یا string)
        format: فرمت خروجی

    Returns:
        str: تاریخ شمسی
    """
    if datetime_obj is None:
        return ''

    # اگر رشته است، به datetime تبدیل کن
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj)
        except:
            return datetime_obj

    # تبدیل به شمسی
    shamsi = jdatetime.datetime.fromgregorian(datetime=datetime_obj)
    return shamsi.strftime(format)


def to_shamsi_date(datetime_obj):
    """تبدیل به تاریخ شمسی (فقط تاریخ)"""
    return to_shamsi(datetime_obj, '%Y/%m/%d')


def to_shamsi_time(datetime_obj):
    """تبدیل به تاریخ شمسی (فقط زمان)"""
    return to_shamsi(datetime_obj, '%H:%M:%S')


def to_shamsi_short(datetime_obj):
    """تبدیل به تاریخ شمسی (کوتاه)"""
    return to_shamsi(datetime_obj, '%Y/%m/%d %H:%M')


def now_shamsi(format='%Y/%m/%d %H:%M:%S'):
    """دریافت تاریخ و زمان فعلی شمسی"""
    return to_shamsi(datetime.now(), format)