from app import db
from datetime import datetime

class InventoryLog(db.Model):
    """Model lịch sử nhập xuất kho"""
    __tablename__ = 'inventory_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    change = db.Column(db.Integer, nullable=False)  # Số lượng thay đổi (+/-)
    type = db.Column(db.String(20), nullable=False)  # import, export, sale, adjust
    note = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='inventory_logs')
    
    TYPE_IMPORT = 'import'  # Nhập kho
    TYPE_EXPORT = 'export'  # Xuất kho
    TYPE_SALE = 'sale'      # Bán hàng
    TYPE_ADJUST = 'adjust'  # Điều chỉnh
    
    @classmethod
    def log_change(cls, product, change, log_type, note=None, user_id=None):
        """Ghi log thay đổi kho và cập nhật tồn kho"""
        log = cls(
            product_id=product.id,
            change=change,
            type=log_type,
            note=note,
            user_id=user_id
        )
        product.stock += change
        db.session.add(log)
        return log
    
    def __repr__(self):
        return f'<InventoryLog {self.product_id} {self.change:+d}>'
