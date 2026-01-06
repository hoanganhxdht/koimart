from app import db
from datetime import datetime

class Settings(db.Model):
    """Model lưu trữ cấu hình hệ thống"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Các key mặc định
    KEY_STORE_NAME = 'store_name'
    KEY_STORE_ADDRESS = 'store_address'
    KEY_STORE_PHONE = 'store_phone'
    KEY_STORE_EMAIL = 'store_email'
    KEY_TAX_CODE = 'tax_code'
    
    # Cài đặt thanh toán QR
    KEY_BANK_NAME = 'bank_name'
    KEY_BANK_ACCOUNT = 'bank_account'
    KEY_BANK_ACCOUNT_NAME = 'bank_account_name'
    KEY_BANK_BRANCH = 'bank_branch'
    KEY_QR_TEMPLATE = 'qr_template'
    
    # Cài đặt thuế
    KEY_VAT_RATE = 'vat_rate'  # 0, 8, 10
    KEY_INVOICE_PREFIX = 'invoice_prefix'
    KEY_INVOICE_FOOTER = 'invoice_footer'
    
    @classmethod
    def get(cls, key, default=None):
        """Lấy giá trị cấu hình theo key"""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set(cls, key, value, description=None):
        """Cập nhật hoặc tạo mới cấu hình"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @classmethod
    def get_all(cls):
        """Lấy tất cả cấu hình dưới dạng dict"""
        settings = cls.query.all()
        return {s.key: s.value for s in settings}
    
    @classmethod
    def init_defaults(cls):
        """Khởi tạo các giá trị mặc định"""
        defaults = {
            cls.KEY_STORE_NAME: ('KOI MART', 'Tên cửa hàng'),
            cls.KEY_STORE_ADDRESS: ('123 Đường ABC, Quận XYZ, TP.HCM', 'Địa chỉ cửa hàng'),
            cls.KEY_STORE_PHONE: ('0901234567', 'Số điện thoại'),
            cls.KEY_STORE_EMAIL: ('contact@koimart.vn', 'Email liên hệ'),
            cls.KEY_TAX_CODE: ('0123456789', 'Mã số thuế'),
            cls.KEY_BANK_NAME: ('Techcombank', 'Tên ngân hàng'),
            cls.KEY_BANK_ACCOUNT: ('1411939393', 'Số tài khoản'),
            cls.KEY_BANK_ACCOUNT_NAME: ('KOI MART', 'Tên chủ tài khoản'),
            cls.KEY_BANK_BRANCH: ('Chi nhánh TP.HCM', 'Chi nhánh'),
            cls.KEY_VAT_RATE: ('10', 'Thuế suất GTGT (%)'),
            cls.KEY_INVOICE_PREFIX: ('KM', 'Tiền tố mã hoá đơn'),
            cls.KEY_INVOICE_FOOTER: ('Cảm ơn quý khách đã mua hàng!', 'Footer hoá đơn'),
        }
        
        for key, (value, desc) in defaults.items():
            if not cls.query.filter_by(key=key).first():
                db.session.add(cls(key=key, value=value, description=desc))
        db.session.commit()
