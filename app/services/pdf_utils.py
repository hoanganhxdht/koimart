"""
PDF Invoice Generator for KOI MART
Uses ReportLab to create professional PDF invoices
"""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def generate_invoice_pdf(order, settings=None):
    """
    Generate a PDF invoice for an order
    
    Args:
        order: Order object with items, customer, etc.
        settings: Dict of store settings (name, address, phone, etc.)
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#22c55e'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#334155')
    )
    
    right_style = ParagraphStyle(
        'RightAlign',
        parent=normal_style,
        alignment=TA_RIGHT
    )
    
    # Build document content
    elements = []
    
    # Store name / title
    store_name = settings.get('store_name', 'KOI MART') if settings else 'KOI MART'
    elements.append(Paragraph(store_name, title_style))
    
    # Store info
    store_address = settings.get('store_address', '') if settings else ''
    store_phone = settings.get('store_phone', '') if settings else ''
    if store_address or store_phone:
        info_text = f"{store_address}<br/>{store_phone}" if store_address and store_phone else (store_address or store_phone)
        elements.append(Paragraph(info_text, subtitle_style))
    
    elements.append(Spacer(1, 10*mm))
    
    # Invoice header
    elements.append(Paragraph("HÓA ĐƠN BÁN HÀNG", heading_style))
    
    # Order info table
    order_info = [
        ['Mã hóa đơn:', order.order_code, 'Ngày:', order.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Khách hàng:', order.customer.name if order.customer else 'Khách lẻ', 'Thu ngân:', order.user.fullname or order.user.username if order.user else 'N/A'],
    ]
    
    info_table = Table(order_info, colWidths=[80, 150, 80, 150])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#1e293b')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))
    
    # Items table
    items_data = [['STT', 'Sản phẩm', 'ĐVT', 'SL', 'Đơn giá', 'Thành tiền']]
    
    for idx, item in enumerate(order.items, 1):
        items_data.append([
            str(idx),
            item.product.name if item.product else 'N/A',
            item.product.unit if item.product else '',
            str(item.quantity),
            format_money(item.price),
            format_money(item.quantity * item.price)
        ])
    
    items_table = Table(items_data, colWidths=[30, 180, 40, 40, 80, 90])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Body
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#334155')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # STT
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),  # ĐVT, SL
        ('ALIGN', (4, 1), (5, -1), 'RIGHT'),   # Prices
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#16a34a')),
        
        # Alternating rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))
    
    # Totals
    subtotal = sum(item.quantity * item.price for item in order.items)
    discount = order.discount or 0
    total = order.total_amount
    
    totals_data = [
        ['', '', '', '', 'Tổng cộng:', format_money(subtotal)],
        ['', '', '', '', 'Giảm giá:', format_money(discount)],
        ['', '', '', '', 'TỔNG THANH TOÁN:', format_money(total)],
    ]
    
    totals_table = Table(totals_data, colWidths=[30, 180, 40, 40, 80, 90])
    totals_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (4, 0), (4, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (5, 0), (5, 1), colors.HexColor('#1e293b')),
        ('ALIGN', (4, 0), (5, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        
        # Total row
        ('FONTNAME', (4, 2), (5, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (4, 2), (5, 2), 12),
        ('TEXTCOLOR', (4, 2), (4, 2), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (5, 2), (5, 2), colors.HexColor('#22c55e')),
        ('LINEABOVE', (4, 2), (5, 2), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (4, 2), (5, 2), 10),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))
    
    # Payment info
    payment_methods = {
        'cash': 'Tiền mặt',
        'card': 'Thẻ',
        'transfer': 'Chuyển khoản',
        'momo': 'Ví MoMo'
    }
    payment_text = f"Phương thức thanh toán: <b>{payment_methods.get(order.payment_method, order.payment_method)}</b>"
    elements.append(Paragraph(payment_text, normal_style))
    
    if order.note:
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(f"Ghi chú: {order.note}", normal_style))
    
    elements.append(Spacer(1, 15*mm))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Cảm ơn quý khách đã mua hàng!", footer_style))
    elements.append(Paragraph("Hẹn gặp lại!", footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def format_money(value):
    """Format number as Vietnamese currency"""
    try:
        return "{:,.0f}đ".format(value)
    except:
        return "0đ"
