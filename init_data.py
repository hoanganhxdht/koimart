"""
Script khoi tao du lieu mau cho ung dung
Chay: python init_data.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models import User, Category, Product, Customer

def init_data():
    app = create_app()
    
    with app.app_context():
        # Tao tables
        db.create_all()
        
        # Tao admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                fullname='Quan tri vien',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("[OK] Da tao tai khoan admin (admin / admin123)")
        
        # Tao thu ngan
        if not User.query.filter_by(username='thungan').first():
            cashier = User(
                username='thungan',
                fullname='Nhan vien thu ngan',
                role='cashier'
            )
            cashier.set_password('123456')
            db.session.add(cashier)
            print("[OK] Da tao tai khoan thu ngan (thungan / 123456)")
        
        # Tao danh muc
        categories_data = ['Do uong', 'Banh keo', 'Mi - Chao', 'Sua', 'Gia vi', 'Do dung']
        for name in categories_data:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
        db.session.commit()
        print("[OK] Da tao danh muc san pham")
        
        # Tao san pham mau
        products_data = [
            {'barcode': '8934588012150', 'name': 'Coca Cola 390ml', 'price': 10000, 'cost': 7500, 'stock': 50, 'category': 'Do uong'},
            {'barcode': '8934588012167', 'name': 'Pepsi 390ml', 'price': 10000, 'cost': 7500, 'stock': 50, 'category': 'Do uong'},
            {'barcode': '8935049500124', 'name': 'Tra xanh Khong do 500ml', 'price': 12000, 'cost': 9000, 'stock': 40, 'category': 'Do uong'},
            {'barcode': '8936036024074', 'name': 'Nuoc suoi Aquafina 500ml', 'price': 5000, 'cost': 3000, 'stock': 100, 'category': 'Do uong'},
            {'barcode': '8934680022117', 'name': 'Banh Oreo 133g', 'price': 25000, 'cost': 18000, 'stock': 30, 'category': 'Banh keo'},
            {'barcode': '8934680022124', 'name': 'Banh Cosy 144g', 'price': 18000, 'cost': 13000, 'stock': 25, 'category': 'Banh keo'},
            {'barcode': '8934563238018', 'name': 'Mi Hao Hao tom chua cay', 'price': 4500, 'cost': 3500, 'stock': 200, 'category': 'Mi - Chao'},
            {'barcode': '8934563238025', 'name': 'Mi Omachi xot bo ham', 'price': 7000, 'cost': 5500, 'stock': 150, 'category': 'Mi - Chao'},
            {'barcode': '8934673000116', 'name': 'Sua Vinamilk co duong 220ml', 'price': 7500, 'cost': 6000, 'stock': 60, 'category': 'Sua'},
            {'barcode': '8934673000123', 'name': 'Sua TH True Milk 180ml', 'price': 7500, 'cost': 6200, 'stock': 48, 'category': 'Sua'},
        ]
        
        for p in products_data:
            if not Product.query.filter_by(barcode=p['barcode']).first():
                category = Category.query.filter_by(name=p['category']).first()
                product = Product(
                    barcode=p['barcode'],
                    name=p['name'],
                    price=p['price'],
                    cost=p['cost'],
                    stock=p['stock'],
                    category_id=category.id if category else None
                )
                db.session.add(product)
        db.session.commit()
        print("[OK] Da tao san pham mau")
        
        # Tao khach hang mau
        customers_data = [
            {'name': 'Nguyen Van An', 'phone': '0901234567'},
            {'name': 'Tran Thi Binh', 'phone': '0912345678'},
            {'name': 'Le Van Cuong', 'phone': '0923456789'},
        ]
        
        for c in customers_data:
            if not Customer.query.filter_by(phone=c['phone']).first():
                db.session.add(Customer(name=c['name'], phone=c['phone']))
        db.session.commit()
        print("[OK] Da tao khach hang mau")
        
        print("")
        print("=== Khoi tao du lieu thanh cong! ===")
        print("   Chay ung dung: python run.py")
        print("   Truy cap: http://localhost:5000")

if __name__ == '__main__':
    init_data()
