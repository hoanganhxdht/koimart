from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app import db
from app.models import Order, Product, OrderItem
from datetime import datetime, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Trang báo cáo tổng quan"""
    return render_template('reports/index.html')

@reports_bp.route('/revenue')
@login_required
def revenue():
    """Báo cáo doanh thu"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    # Doanh thu theo ngày
    daily_revenue = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.created_at >= start,
        Order.created_at < end,
        Order.payment_status == 'paid'
    ).group_by(func.date(Order.created_at)).all()
    
    # Tổng hợp
    totals = db.session.query(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_revenue')
    ).filter(
        Order.created_at >= start,
        Order.created_at < end,
        Order.payment_status == 'paid'
    ).first()
    
    return render_template('reports/revenue.html', 
                         daily_revenue=daily_revenue, 
                         totals=totals,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/products')
@login_required
def products_report():
    """Báo cáo sản phẩm bán chạy"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    # Top sản phẩm bán chạy
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_qty'),
        func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
    ).join(OrderItem).join(Order).filter(
        Order.created_at >= start,
        Order.created_at < end,
        Order.payment_status == 'paid'
    ).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(20).all()
    
    return render_template('reports/products.html', 
                         top_products=top_products,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/profit')
@login_required
def profit():
    """Báo cáo lợi nhuận"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    # Tính lợi nhuận
    profit_data = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue'),
        func.sum(OrderItem.quantity * Product.cost).label('cost')
    ).join(OrderItem).join(Product).filter(
        Order.created_at >= start,
        Order.created_at < end,
        Order.payment_status == 'paid'
    ).group_by(func.date(Order.created_at)).all()
    
    return render_template('reports/profit.html',
                         profit_data=profit_data,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    """Xuất báo cáo Excel"""
    try:
        from openpyxl import Workbook
        from io import BytesIO
        
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        orders = Order.query.filter(
            Order.created_at >= start,
            Order.created_at < end
        ).all()
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Báo cáo doanh thu"
        
        # Header
        ws.append(['Mã HĐ', 'Ngày', 'Khách hàng', 'Tổng tiền', 'Thanh toán', 'Trạng thái'])
        
        for order in orders:
            ws.append([
                order.order_code,
                order.created_at.strftime('%d/%m/%Y %H:%M'),
                order.customer.name if order.customer else 'Khách lẻ',
                order.total_amount,
                order.payment_method,
                order.payment_status
            ])
        
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=bao_cao_{start_date}_{end_date}.xlsx'
        
        return response
    except ImportError:
        return "Vui lòng cài đặt openpyxl: pip install openpyxl", 500
