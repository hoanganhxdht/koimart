from flask import Blueprint, render_template, jsonify
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from app.models import Product, Order, Customer
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    today = datetime.now().date()
    
    # Thống kê nhanh
    stats = {
        'total_products': Product.query.filter_by(is_active=True).count(),
        'low_stock_products': Product.query.filter(Product.stock <= Product.min_stock, Product.is_active == True).count(),
        'total_customers': Customer.query.count(),
        'today_orders': Order.query.filter(func.date(Order.created_at) == today).count(),
        'today_revenue': db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today,
            Order.payment_status == 'paid'
        ).scalar() or 0
    }
    
    # Đơn hàng gần đây
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Sản phẩm sắp hết hàng
    low_stock = Product.query.filter(
        Product.stock <= Product.min_stock,
        Product.is_active == True
    ).limit(5).all()
    
    # Dữ liệu biểu đồ 7 ngày gần nhất
    chart_data = {
        'labels': [],
        'revenue': [],
        'orders': []
    }
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_data['labels'].append(date.strftime('%d/%m'))
        
        daily_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == date,
            Order.payment_status == 'paid'
        ).scalar() or 0
        chart_data['revenue'].append(float(daily_revenue))
        
        daily_orders = Order.query.filter(func.date(Order.created_at) == date).count()
        chart_data['orders'].append(daily_orders)
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          recent_orders=recent_orders, 
                          low_stock=low_stock,
                          chart_data=chart_data)

from app import db
