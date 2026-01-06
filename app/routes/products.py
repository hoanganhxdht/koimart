from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, InventoryLog

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
def index():
    """Danh sách sản phẩm"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.like(f'%{search}%') | Product.barcode.like(f'%{search}%'))
    
    products = query.order_by(Product.name).paginate(page=page, per_page=20)
    categories = Category.query.all()
    
    return render_template('products/index.html', products=products, categories=categories)

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Thêm sản phẩm mới"""
    if request.method == 'POST':
        initial_stock = int(request.form.get('stock', 0))
        
        product = Product(
            barcode=request.form.get('barcode'),
            name=request.form.get('name'),
            price=float(request.form.get('price', 0)),
            cost=float(request.form.get('cost', 0)),
            stock=0, # Init with 0, updated via log_change
            unit=request.form.get('unit', 'cái'),
            min_stock=int(request.form.get('min_stock', 5)),
            category_id=request.form.get('category_id') or None
        )
        
        db.session.add(product)
        db.session.flush() # Get ID
        
        # Ghi log nhập kho ban đầu
        if initial_stock > 0:
            InventoryLog.log_change(
                product=product,
                change=initial_stock,
                log_type=InventoryLog.TYPE_IMPORT,
                note='Tồn kho ban đầu',
                user_id=current_user.id
            )
        
        db.session.commit()
        flash('Thêm sản phẩm thành công.', 'success')
        return redirect(url_for('products.index'))
    
    categories = Category.query.all()
    return render_template('products/form.html', product=None, categories=categories)

@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Sửa sản phẩm"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.barcode = request.form.get('barcode')
        product.name = request.form.get('name')
        product.price = float(request.form.get('price', 0))
        product.cost = float(request.form.get('cost', 0))
        product.unit = request.form.get('unit', 'cái')
        product.min_stock = int(request.form.get('min_stock', 5))
        product.category_id = request.form.get('category_id') or None
        product.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Cập nhật sản phẩm thành công.', 'success')
        return redirect(url_for('products.index'))
    
    categories = Category.query.all()
    return render_template('products/form.html', product=product, categories=categories)

@products_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Xóa sản phẩm hoàn toàn khỏi database"""
    product = Product.query.get_or_404(id)
    
    # Xóa các inventory logs liên quan
    InventoryLog.query.filter_by(product_id=id).delete()
    
    # Xóa sản phẩm
    db.session.delete(product)
    db.session.commit()
    flash('Đã xóa sản phẩm hoàn toàn.', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    """Xóa nhiều sản phẩm hoàn toàn khỏi database"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return jsonify({'success': False, 'message': 'Không có sản phẩm nào được chọn'}), 400
        
        deleted_count = 0
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if product:
                # Xóa các inventory logs liên quan
                InventoryLog.query.filter_by(product_id=product_id).delete()
                
                # Xóa sản phẩm
                db.session.delete(product)
                deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'deleted_count': deleted_count,
            'message': f'Đã xóa {deleted_count} sản phẩm'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/check-barcode')
@login_required
def check_barcode():
    """Kiểm tra mã vạch đã tồn tại chưa"""
    barcode = request.args.get('barcode', '')
    product_id = request.args.get('product_id', type=int)  # Để loại trừ sản phẩm đang sửa
    
    if not barcode:
        return jsonify({'exists': False})
    
    query = Product.query.filter_by(barcode=barcode)
    if product_id:
        query = query.filter(Product.id != product_id)
    
    existing = query.first()
    
    return jsonify({
        'exists': existing is not None,
        'product_name': existing.name if existing else None
    })

@products_bp.route('/categories')
@login_required
def categories():
    """Danh sách danh mục"""
    categories = Category.query.all()
    return render_template('products/categories.html', categories=categories)

@products_bp.route('/categories/create', methods=['POST'])
@login_required
def create_category():
    """Thêm danh mục"""
    name = request.form.get('name')
    if name:
        category = Category(name=name, description=request.form.get('description'))
        db.session.add(category)
        db.session.commit()
        flash('Thêm danh mục thành công.', 'success')
    return redirect(url_for('products.categories'))

@products_bp.route('/inventory')
@login_required
def inventory():
    """Quản lý kho"""
    page = request.args.get('page', 1, type=int)
    show_low_stock = request.args.get('low_stock', False, type=bool)
    
    query = Product.query.filter_by(is_active=True)
    if show_low_stock:
        query = query.filter(Product.stock <= Product.min_stock)
    
    products = query.order_by(Product.stock).paginate(page=page, per_page=20)
    return render_template('products/inventory.html', products=products)

@products_bp.route('/inventory/import', methods=['POST'])
@login_required
def import_stock():
    """Nhập kho"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    note = request.form.get('note', '')
    
    if product_id and quantity and quantity > 0:
        product = Product.query.get_or_404(product_id)
        InventoryLog.log_change(
            product=product,
            change=quantity,
            log_type=InventoryLog.TYPE_IMPORT,
            note=note,
            user_id=current_user.id
        )
        db.session.commit()
        flash(f'Đã nhập {quantity} {product.unit} vào kho.', 'success')
    
    return redirect(url_for('products.inventory'))

@products_bp.route('/inventory/logs')
@login_required
def inventory_logs():
    """Lịch sử nhập xuất kho"""
    page = request.args.get('page', 1, type=int)
    logs = InventoryLog.query.order_by(InventoryLog.created_at.desc()).paginate(page=page, per_page=30)
    return render_template('products/inventory_logs.html', logs=logs)

@products_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload file dữ liệu sản phẩm"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Vui lòng chọn file để upload.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Vui lòng chọn file để upload.', 'danger')
            return redirect(request.url)
        
        # Kiểm tra định dạng file
        filename = file.filename.lower()
        if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
            flash('Chỉ hỗ trợ file CSV hoặc Excel (.xlsx, .xls)', 'danger')
            return redirect(request.url)
        
        try:
            products_data = []
            
            if filename.endswith('.csv'):
                # Đọc file CSV
                import csv
                import io
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                reader = csv.reader(stream)
                # Bỏ qua header nếu có
                next(reader, None)
                for row in reader:
                    if len(row) >= 5:
                        products_data.append({
                            'name': row[0].strip(),
                            'barcode': row[1].strip(),
                            'cost': row[2].strip(),
                            'price': row[3].strip(),
                            'stock': row[4].strip()
                        })
            else:
                # Đọc file Excel
                try:
                    import openpyxl
                    from io import BytesIO
                    wb = openpyxl.load_workbook(BytesIO(file.read()))
                    ws = wb.active
                    rows = list(ws.iter_rows(min_row=2, values_only=True))  # Bỏ qua header
                    for row in rows:
                        if row and len(row) >= 5 and row[0]:
                            products_data.append({
                                'name': str(row[0]).strip() if row[0] else '',
                                'barcode': str(row[1]).strip() if row[1] else '',
                                'cost': str(row[2]).strip() if row[2] else '0',
                                'price': str(row[3]).strip() if row[3] else '0',
                                'stock': str(row[4]).strip() if row[4] else '0'
                            })
                except ImportError:
                    flash('Cần cài đặt openpyxl để đọc file Excel: pip install openpyxl', 'danger')
                    return redirect(request.url)
            
            # Thêm hoặc cập nhật sản phẩm
            added = 0
            updated = 0
            errors = []
            
            for idx, p in enumerate(products_data, start=2):
                try:
                    name = p['name']
                    barcode = p['barcode']
                    cost = float(p['cost'].replace(',', '')) if p['cost'] else 0
                    price = float(p['price'].replace(',', '')) if p['price'] else 0
                    stock = int(float(p['stock'].replace(',', ''))) if p['stock'] else 0
                    
                    if not name:
                        continue
                    
                    # Kiểm tra sản phẩm đã tồn tại chưa (theo barcode)
                    existing = None
                    if barcode:
                        existing = Product.query.filter_by(barcode=barcode).first()
                    
                    if existing:
                        # Cập nhật sản phẩm
                        old_stock = existing.stock
                        existing.name = name
                        existing.cost = cost
                        existing.price = price
                        
                        # Cập nhật tồn kho nếu có thay đổi
                        if stock != old_stock:
                            stock_change = stock - old_stock
                            InventoryLog.log_change(
                                product=existing,
                                change=stock_change,
                                log_type=InventoryLog.TYPE_ADJUST,
                                note='Cập nhật từ file upload',
                                user_id=current_user.id
                            )
                        updated += 1
                    else:
                        # Thêm sản phẩm mới
                        product = Product(
                            name=name,
                            barcode=barcode if barcode else None,
                            cost=cost,
                            price=price,
                            stock=stock
                        )
                        db.session.add(product)
                        
                        if stock > 0:
                            db.session.flush()  # Để có product.id
                            InventoryLog.log_change(
                                product=product,
                                change=stock,
                                log_type=InventoryLog.TYPE_IMPORT,
                                note='Nhập từ file upload',
                                user_id=current_user.id
                            )
                        added += 1
                        
                except Exception as e:
                    errors.append(f"Dòng {idx}: {str(e)}")
            
            db.session.commit()
            
            msg = f'Hoàn tất! Thêm mới: {added}, Cập nhật: {updated}'
            if errors:
                msg += f'. Lỗi: {len(errors)} dòng'
            flash(msg, 'success' if not errors else 'warning')
            
            return redirect(url_for('products.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi xử lý file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('products/upload.html')

@products_bp.route('/download-template')
@login_required
def download_template():
    """Tải file mẫu CSV"""
    import io
    from flask import Response
    
    output = io.StringIO()
    output.write('Ten san pham,Ma vach,Gia nhap,Gia ban,So luong\n')
    output.write('Coca Cola 390ml,8934588012150,7500,10000,50\n')
    output.write('Pepsi 390ml,8934588012167,7500,10000,50\n')
    
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=mau_san_pham.csv'}
    )
    return response

