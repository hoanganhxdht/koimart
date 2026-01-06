
# PHẦN MỀM QUẢN LÝ BÁN HÀNG CỬA HÀNG TIỆN LỢI MINI
## Công nghệ: Flask + HTML5 + Database

---

## 1. MỤC TIÊU DỰ ÁN
Xây dựng phần mềm quản lý bán hàng cho cửa hàng tiện lợi mini:
- Bán hàng nhanh, chính xác
- Quản lý sản phẩm, kho, nhân viên
- Báo cáo doanh thu – lợi nhuận
- Có khả năng mở rộng và triển khai thực tế

---

## 2. CÔNG NGHỆ SỬ DỤNG

### Backend
- Python 3.10+
- Flask
- Flask-Login
- Flask-Migrate
- SQLAlchemy (ORM)

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Database
- SQLite (giai đoạn đầu)
- PostgreSQL / MySQL (mở rộng)

---

## 3. KIẾN TRÚC PHẦN MỀM (MVC)

```
project/
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── inventory.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── sales.py
│   │   ├── products.py
│   │   └── reports.py
│   │
│   ├── templates/
│   ├── static/
│   └── services/
│
├── database/
│   └── shop.db
│
├── migrations/
├── config.py
├── run.py
└── requirements.txt
```

---

## 4. THIẾT KẾ CƠ SỞ DỮ LIỆU

### users
- id
- username
- password_hash
- role
- created_at

### products
- id
- barcode
- name
- price
- cost
- stock
- unit
- expiry_date
- category_id

### categories
- id
- name

### customers
- id
- name
- phone
- points

### orders
- id
- user_id
- customer_id
- total_amount
- payment_method
- created_at

### order_items
- id
- order_id
- product_id
- quantity
- price

### inventory_logs
- id
- product_id
- change
- type
- created_at

---

## 5. MODULE CHỨC NĂNG

### 5.1 Xác thực & phân quyền
- Đăng nhập / đăng xuất
- Phân quyền: Admin / Thu ngân / Kho

### 5.2 Bán hàng
- Giao diện POS
- Quét mã vạch / tìm sản phẩm
- Tạo hóa đơn
- Thanh toán
- Lưu lịch sử bán

### 5.3 Quản lý sản phẩm & kho
- CRUD sản phẩm
- Nhập kho
- Xuất kho
- Cảnh báo tồn kho thấp

### 5.4 Khách hàng
- Lưu thông tin khách
- Lịch sử mua hàng
- Tích điểm

### 5.5 Báo cáo
- Doanh thu theo ngày / tháng
- Lợi nhuận
- Xuất Excel / PDF

---

## 6. LUỒNG HOẠT ĐỘNG BÁN HÀNG

1. Nhân viên đăng nhập
2. Mở màn hình bán hàng
3. Quét mã / chọn sản phẩm
4. Hệ thống tính tiền
5. Thanh toán
6. Trừ kho
7. Lưu hóa đơn

---

## 7. ROADMAP PHÁT TRIỂN

### Giai đoạn 1 – MVP
- Login
- Bán hàng
- Quản lý sản phẩm
- SQLite

### Giai đoạn 2
- Kho
- Báo cáo
- Khách hàng

### Giai đoạn 3
- Cloud DB
- Nhiều chi nhánh
- Mobile / API

---

## 8. BẢO MẬT & SAO LƯU
- Hash mật khẩu
- Phân quyền rõ ràng
- Backup dữ liệu định kỳ

---

## 9. TRIỂN KHAI
- Local PC
- VPS / Cloud
- Docker (nâng cao)

---

## 10. ĐỊNH HƯỚNG MỞ RỘNG
- Máy quét mã vạch
- Máy in hóa đơn
- Quản lý online
- App mobile

---

Tài liệu này dùng làm chuẩn để phát triển phần mềm quản lý bán hàng bằng Flask.
