"""
PDF Exporter - خروجی PDF از داده‌های پارکینگ
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


class PDFExporter:
    """تولید فایل PDF از گزارش‌ها"""

    def __init__(self, db):
        self.db = db
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)

    def export_history(self, date_from=None, date_to=None, filename=None):
        """خروجی PDF از تاریخچه"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"parking_report_{timestamp}.pdf"

        filepath = os.path.join(self.export_dir, filename)

        # ===== ایجاد PDF =====
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm
        )

        # ===== استایل =====
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20
        )

        # ===== محتوا =====
        elements = []

        # عنوان
        elements.append(Paragraph("گزارش پارکینگ", title_style))
        elements.append(Spacer(1, 0.5 * cm))

        # تاریخ
        date_text = f"از تاریخ: {date_from or 'ابتدا'} تا {date_to or 'اکنون'}"
        elements.append(Paragraph(date_text, styles['Normal']))
        elements.append(Spacer(1, 0.5 * cm))

        # ===== جدول =====
        history = self.db.get_history(
            date_from=date_from,
            date_to=date_to,
            per_page=1000
        )

        # هدر جدول
        table_data = [['ردیف', 'پلاک', 'ورود', 'خروج', 'مدت', 'هزینه']]

        for i, record in enumerate(history['records'][:50], 1):  # فقط ۵۰ رکورد اول
            table_data.append([
                str(i),
                record['plate_number'],
                record['entry_time'][11:16],
                record['exit_time'][11:16],
                f"{record['duration_hours']:.1f}",
                f"{record['final_cost']:,.0f}"
            ])

        # ساخت جدول
        table = Table(table_data, colWidths=[1.5 * cm, 3 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.5 * cm))

        # جمع کل
        total_income = sum(r['final_cost'] for r in history['records'])
        elements.append(Paragraph(
            f"<b>جمع کل درآمد: {total_income:,.0f} تومان</b>",
            styles['Normal']
        ))

        # ساخت PDF
        doc.build(elements)

        return filepath