from app import db
from datetime import datetime

class Customer(db.Model):
    """Model khách hàng"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    points = db.Column(db.Integer, default=0)  # Điểm tích lũy
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    
    @property
    def total_spent(self):
        """Tổng tiền đã chi tiêu"""
        return sum(order.total_amount for order in self.orders)
    
    def add_points(self, amount):
        """Thêm điểm tích lũy (1 điểm cho mỗi 10,000đ)"""
        points_to_add = int(amount // 10000)
        self.points += points_to_add
        return points_to_add
    
    def __repr__(self):
        return f'<Customer {self.name}>'
