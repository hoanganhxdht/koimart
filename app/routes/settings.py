from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def index():
    """Trang cài đặt chính"""
    # Khởi tạo giá trị mặc định nếu chưa có
    Settings.init_defaults()
    settings = Settings.get_all()
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/store', methods=['GET', 'POST'])
@login_required
def store_info():
    """Cài đặt thông tin cửa hàng"""
    if request.method == 'POST':
        Settings.set(Settings.KEY_STORE_NAME, request.form.get('store_name', ''))
        Settings.set(Settings.KEY_STORE_ADDRESS, request.form.get('store_address', ''))
        Settings.set(Settings.KEY_STORE_PHONE, request.form.get('store_phone', ''))
        Settings.set(Settings.KEY_STORE_EMAIL, request.form.get('store_email', ''))
        Settings.set(Settings.KEY_TAX_CODE, request.form.get('tax_code', ''))
        flash('Đã lưu thông tin cửa hàng.', 'success')
        return redirect(url_for('settings.store_info'))
    
    settings = Settings.get_all()
    return render_template('settings/store_info.html', settings=settings)

@settings_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """Cài đặt thanh toán QR / Ngân hàng"""
    if request.method == 'POST':
        Settings.set(Settings.KEY_BANK_NAME, request.form.get('bank_name', ''))
        Settings.set(Settings.KEY_BANK_ACCOUNT, request.form.get('bank_account', ''))
        Settings.set(Settings.KEY_BANK_ACCOUNT_NAME, request.form.get('bank_account_name', ''))
        Settings.set(Settings.KEY_BANK_BRANCH, request.form.get('bank_branch', ''))
        flash('Đã lưu thông tin thanh toán.', 'success')
        return redirect(url_for('settings.payment'))
    
    settings = Settings.get_all()
    return render_template('settings/payment.html', settings=settings)

@settings_bp.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice():
    """Cài đặt hoá đơn"""
    if request.method == 'POST':
        Settings.set(Settings.KEY_INVOICE_PREFIX, request.form.get('invoice_prefix', 'KM'))
        Settings.set(Settings.KEY_INVOICE_FOOTER, request.form.get('invoice_footer', ''))
        # Options hiển thị QR và Logo
        show_qr = 'true' if request.form.get('show_qr_on_invoice') else 'false'
        show_logo = 'true' if request.form.get('show_logo_on_invoice') else 'false'
        Settings.set('show_qr_on_invoice', show_qr)
        Settings.set('show_logo_on_invoice', show_logo)
        flash('Đã lưu cài đặt hoá đơn.', 'success')
        return redirect(url_for('settings.invoice'))
    
    settings = Settings.get_all()
    return render_template('settings/invoice.html', settings=settings)

@settings_bp.route('/tax', methods=['GET', 'POST'])
@login_required
def tax():
    """Cài đặt thuế suất"""
    if request.method == 'POST':
        Settings.set(Settings.KEY_VAT_RATE, request.form.get('vat_rate', '10'))
        flash('Đã lưu cài đặt thuế.', 'success')
        return redirect(url_for('settings.tax'))
    
    settings = Settings.get_all()
    return render_template('settings/tax.html', settings=settings)
