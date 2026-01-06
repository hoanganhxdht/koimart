from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, Response
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem, Customer, InventoryLog

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/')
@login_required
def pos():
    """Giao diện POS bán hàng"""
    products = Product.query.filter_by(is_active=True).all()
    customers = Customer.query.all()
    return render_template('sales/pos.html', products=products, customers=customers)

@sales_bp.route('/search-product')
@login_required
def search_product():
    """Tìm kiếm sản phẩm theo barcode hoặc tên"""
    query = request.args.get('q', '')
    products = Product.query.filter(
        Product.is_active == True,
        (Product.barcode.like(f'%{query}%') | Product.name.like(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'barcode': p.barcode,
        'name': p.name,
        'price': p.price,
        'stock': p.stock,
        'unit': p.unit
    } for p in products])

@sales_bp.route('/create-order', methods=['POST'])
@login_required
def create_order():
    """Tạo đơn hàng mới"""
    try:
        data = request.get_json()
        
        # Tạo đơn hàng
        order = Order(
            user_id=current_user.id,
            customer_id=data.get('customer_id'),
            payment_method=data.get('payment_method', 'cash'),
            discount=data.get('discount', 0),
            note=data.get('note')
        )
        order.generate_order_code()
        db.session.add(order)
        
        # Thêm sản phẩm vào đơn
        for item in data.get('items', []):
            product = Product.query.get(item['product_id'])
            if not product:
                continue
            
            if product.stock < item['quantity']:
                return jsonify({'success': False, 'message': f'Sản phẩm {product.name} không đủ tồn kho'}), 400
            
            order_item = OrderItem(
                order=order,
                product_id=product.id,
                quantity=item['quantity'],
                price=product.price,
                discount=item.get('discount', 0)
            )
            db.session.add(order_item)
            
            # Trừ kho
            InventoryLog.log_change(
                product=product,
                change=-item['quantity'],
                log_type=InventoryLog.TYPE_SALE,
                note=f'Bán hàng - Đơn {order.order_code}',
                user_id=current_user.id
            )
        
        # Tính tổng và tích điểm cho khách
        order.calculate_total()
        
        if order.customer:
            order.customer.add_points(order.total_amount)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'order_code': order.order_code,
            'total': order.total_amount,
            'items': [{'name': item.product.name, 'quantity': item.quantity, 'subtotal': item.quantity * item.price} for item in order.items],
            'message': 'Tạo đơn hàng thành công'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@sales_bp.route('/orders')
@login_required
def order_list():
    """Danh sách đơn hàng"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('sales/orders.html', orders=orders)

@sales_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """Chi tiết đơn hàng"""
    order = Order.query.get_or_404(id)
    return render_template('sales/order_detail.html', order=order)

@sales_bp.route('/orders/<int:id>/print')
@login_required
def print_order(id):
    """In hóa đơn"""
    from app.models import Settings
    order = Order.query.get_or_404(id)
    settings = Settings.get_all()
    return render_template('sales/print_order.html', order=order, settings=settings)

@sales_bp.route('/orders/<int:id>/pdf')
@login_required
def download_pdf(id):
    """Tải hóa đơn PDF"""
    from app.models import Settings
    from app.services.pdf_utils import generate_invoice_pdf
    
    order = Order.query.get_or_404(id)
    settings = Settings.get_all()
    
    # Generate PDF
    pdf_buffer = generate_invoice_pdf(order, settings)
    
    # Send as downloadable file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hoadon_{order.order_code}.pdf'
    )

@sales_bp.route('/einvoices')
@login_required
def einvoices():
    """Danh sách hoá đơn điện tử"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(payment_status='paid').order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('sales/einvoices.html', orders=orders)

@sales_bp.route('/einvoices/<int:id>/issue', methods=['POST'])
@login_required
def issue_einvoice(id):
    """Phát hành hoá đơn điện tử"""
    order = Order.query.get_or_404(id)
    # Giả lập phát hành hoá đơn điện tử
    flash(f'Đã phát hành hoá đơn điện tử cho đơn hàng {order.order_code}', 'success')
    return redirect(url_for('sales.einvoices'))

