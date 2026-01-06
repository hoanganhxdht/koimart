from app import db
from datetime import datetime

class Category(db.Model):
    """Model danh mục sản phẩm"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Model sản phẩm"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Giá bán
    cost = db.Column(db.Float, default=0)  # Giá vốn
    stock = db.Column(db.Integer, default=0)  # Số lượng tồn kho
    unit = db.Column(db.String(20), default='cái')  # Đơn vị tính
    min_stock = db.Column(db.Integer, default=5)  # Số lượng tối thiểu (cảnh báo)
    expiry_date = db.Column(db.Date)  # Ngày hết hạn
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    inventory_logs = db.relationship('InventoryLog', backref='product', lazy='dynamic')
    
    @property
    def profit_margin(self):
        """Tính lợi nhuận mỗi sản phẩm"""
        if self.cost > 0:
            return self.price - self.cost
        return 0
    
    @property
    def is_low_stock(self):
        """Kiểm tra tồn kho thấp"""
        return self.stock <= self.min_stock
    
    def __repr__(self):
        return f'<Product {self.name}>'
