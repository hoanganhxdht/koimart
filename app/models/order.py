from app import db
from datetime import datetime

class Order(db.Model):
    """Model đơn hàng / hóa đơn"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(20), unique=True)  # Mã hóa đơn
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    subtotal = db.Column(db.Float, default=0)  # Tổng tiền hàng
    discount = db.Column(db.Float, default=0)  # Giảm giá
    total_amount = db.Column(db.Float, default=0)  # Tổng thanh toán
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, transfer
    payment_status = db.Column(db.String(20), default='paid')  # paid, pending, cancelled
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def generate_order_code(self):
        """Tạo mã hóa đơn dạng HD + ngày + số thứ tự"""
        date_str = datetime.now().strftime('%Y%m%d')
        last_order = Order.query.filter(Order.order_code.like(f'HD{date_str}%')).order_by(Order.id.desc()).first()
        if last_order:
            last_num = int(last_order.order_code[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        self.order_code = f'HD{date_str}{new_num:04d}'
    
    def calculate_total(self):
        """Tính tổng tiền đơn hàng"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.total_amount = self.subtotal - self.discount
    
    @property
    def total_profit(self):
        """Tính lợi nhuận đơn hàng"""
        return sum((item.price - item.product.cost) * item.quantity for item in self.items if item.product)
    
    def __repr__(self):
        return f'<Order {self.order_code}>'


class OrderItem(db.Model):
    """Model chi tiết đơn hàng"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Giá tại thời điểm mua
    discount = db.Column(db.Float, default=0)
    
    @property
    def subtotal(self):
        """Tính thành tiền"""
        return (self.price * self.quantity) - self.discount
    
    def __repr__(self):
        return f'<OrderItem {self.product_id} x {self.quantity}>'
