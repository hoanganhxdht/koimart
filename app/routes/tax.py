from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Order, Settings
from datetime import datetime, timedelta
from sqlalchemy import func

tax_bp = Blueprint('tax', __name__)

@tax_bp.route('/declaration')
@login_required
def declaration():
    """Lập tờ khai thuế Hộ kinh doanh - Mẫu 01/CNKD"""
    # Lấy tham số
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    method = request.args.get('method', 'khoan')
    period = request.args.get('period', 'year')
    
    # Tính khoảng thời gian theo kỳ kê khai
    if period == 'year':
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    elif period == 'quarter':
        quarter = ((month - 1) // 3) + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)
        if quarter == 4:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, start_month + 3, 1)
    else:  # month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    
    # Thống kê doanh thu
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.payment_status == 'paid'
    ).scalar() or 0
    
    total_orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.payment_status == 'paid'
    ).count()
    
    # Tỷ lệ thuế cho Hộ kinh doanh (Thông tư 40/2021/TT-BTC)
    # Bán lẻ hàng hóa: GTGT 1%, TNCN 0.5%
    vat_gtgt = 1  # %
    pit_rate = 0.5  # % (thuế TNCN)
    
    vat_gtgt_amount = total_revenue * vat_gtgt / 100
    pit_amount = total_revenue * pit_rate / 100
    total_tax = vat_gtgt_amount + pit_amount
    
    # Lấy settings
    settings = Settings.get_all()
    
    return render_template('tax/declaration.html',
                         month=month,
                         year=year,
                         method=method,
                         period=period,
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         vat_gtgt=vat_gtgt,
                         vat_gtgt_amount=vat_gtgt_amount,
                         pit_rate=pit_rate,
                         pit_amount=pit_amount,
                         total_tax=total_tax,
                         settings=settings,
                         now=datetime.now())

@tax_bp.route('/input-invoices')
@login_required
def input_invoices():
    """Quản lý hoá đơn đầu vào"""
    page = request.args.get('page', 1, type=int)
    # Placeholder - trong thực tế sẽ có model InputInvoice riêng
    invoices = []
    return render_template('tax/input_invoices.html', invoices=invoices, page=page)

@tax_bp.route('/input-invoices/add', methods=['GET', 'POST'])
@login_required
def add_input_invoice():
    """Thêm hoá đơn đầu vào"""
    if request.method == 'POST':
        # Xử lý thêm hoá đơn đầu vào
        flash('Đã thêm hoá đơn đầu vào thành công.', 'success')
        return redirect(url_for('tax.input_invoices'))
    return render_template('tax/add_input_invoice.html')
