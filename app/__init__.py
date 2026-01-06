from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
login_manager.login_message_category = 'warning'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Tạo thư mục database nếu chưa có
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import models
    from app.models import User, Product, Category, Customer, Order, OrderItem, InventoryLog
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Đăng ký blueprints
    from app.routes.auth import auth_bp
    from app.routes.sales import sales_bp
    from app.routes.products import products_bp
    from app.routes.reports import reports_bp
    from app.routes.main import main_bp
    from app.routes.tax import tax_bp
    from app.routes.settings import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(tax_bp, url_prefix='/tax')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Tạo database tables và dữ liệu mặc định
    with app.app_context():
        db.create_all()
        
        # Tự động tạo admin user nếu chưa có (cho hosting)
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                fullname='Quan tri vien',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[Auto] Created admin user")
        
        # Tạo tài khoản thu ngân nếu chưa có
        if not User.query.filter_by(username='thungan').first():
            cashier = User(
                username='thungan',
                fullname='Nhan vien thu ngan',
                role='staff'
            )
            cashier.set_password('thungan123')
            db.session.add(cashier)
            db.session.commit()
            print("[Auto] Created cashier user")
        
        # Tạo categories mặc định
        if not Category.query.first():
            categories = ['Do uong', 'Banh keo', 'Mi - Chao', 'Sua', 'Gia vi', 'Do dung']
            for name in categories:
                db.session.add(Category(name=name))
            db.session.commit()
            print("[Auto] Created default categories")
    
    return app
