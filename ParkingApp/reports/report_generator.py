"""
Report Generator - تولید گزارش‌های مختلف
"""

from datetime import datetime, timedelta
from .excel_exporter import ExcelExporter
from .pdf_exporter import PDFExporter


class ReportGenerator:
    """تولید گزارش‌های مختلف"""

    def __init__(self, db):
        self.db = db
        self.excel = ExcelExporter(db)
        self.pdf = PDFExporter(db)

    def daily_report(self, date=None):
        """گزارش روزانه"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        return {
            'date': date,
            'stats': self.db.get_statistics(date),
            'excel': self.excel.export_daily_summary(date),
        }

    def monthly_report(self, year=None, month=None):
        """گزارش ماهانه"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        date_from = f"{year}-{month:02d}-01"
        if month == 12:
            date_to = f"{year + 1}-01-01"
        else:
            date_to = f"{year}-{month + 1:02d}-01"

        return {
            'year': year,
            'month': month,
            'date_from': date_from,
            'date_to': date_to,
            'excel': self.excel.export_history(date_from, date_to),
            'pdf': self.pdf.export_history(date_from, date_to),
        }

    def custom_report(self, date_from, date_to):
        """گزارش سفارشی"""
        return {
            'date_from': date_from,
            'date_to': date_to,
            'excel': self.excel.export_history(date_from, date_to),
            'pdf': self.pdf.export_history(date_from, date_to),
        }