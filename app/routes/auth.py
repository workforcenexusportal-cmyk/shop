from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, csrf
from app.models.user import User
from app.models.order import Order
from app.forms.login import LoginForm
from app.forms.register import RegistrationForm

auth_bp = Blueprint('auth', __name__)


def verify_user_password(user, password):
    if hasattr(user, 'check_password') and callable(user.check_password):
        return user.check_password(password)
    elif hasattr(user, 'verify_password') and callable(user.verify_password):
        return user.verify_password(password)
    elif hasattr(user, 'password_hash') and user.password_hash:
        from werkzeug.security import check_password_hash
        return check_password_hash(user.password_hash, password)
    elif hasattr(user, 'password'):
        return user.password == password
    return False


def set_user_password(user, password):
    if hasattr(user, 'set_password') and callable(user.set_password):
        user.set_password(password)
    elif hasattr(user, 'password_hash'):
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(password)
    else:
        user.password = password


def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'full_name': getattr(user, 'full_name', ''),
        'is_admin': getattr(user, 'is_admin', False)
    }


# PAGE ROUTES

@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and verify_user_password(user, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('catalog.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('register.html', form=form)
        user = User(email=email, full_name=form.full_name.data.strip())
        set_user_password(user, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful! Welcome.', 'success')
        return redirect(url_for('catalog.index'))
    return render_template('register.html', form=form)


@auth_bp.route('/auth/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('catalog.index'))


@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        if full_name:
            current_user.full_name = full_name.strip()
        address = request.form.get('address') or request.form.get('addresses') or request.form.get('address_line1')
        if address:
            if hasattr(current_user, 'address'):
                current_user.address = address
            elif hasattr(current_user, 'addresses'):
                current_user.addresses = address
            elif hasattr(current_user, 'shipping_address'):
                current_user.shipping_address = address
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile.', 'danger')
        return redirect(url_for('auth.account'))

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template('account.html', user=current_user, orders=orders)


# API ROUTES

@auth_bp.route('/api/auth/login', methods=['POST'])
@csrf.exempt
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_user_password(user, password):
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

    login_user(user)
    return jsonify({'success': True, 'data': {'user': serialize_user(user)}})


@auth_bp.route('/api/auth/register', methods=['POST'])
@csrf.exempt
def api_register():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    if not email or not password or not full_name:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 400

    user = User(email=email, full_name=full_name)
    set_user_password(user, password)

    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({'success': True, 'data': {'user': serialize_user(user)}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/me', methods=['GET'])
def api_me():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    return jsonify({'success': True, 'data': {'user': serialize_user(current_user)}})
