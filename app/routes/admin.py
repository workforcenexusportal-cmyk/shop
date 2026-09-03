from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from app.extensions import db, csrf
from app.models.product import Category, Product
from app.models.order import Order
from app.models.user import User
from app.utils.helpers import serialize_product, serialize_order

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Admin privilege required'}), 403
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('catalog.index'))
        return f(*args, **kwargs)
    return decorated_function


# PAGE ROUTES

@admin_bp.route('/admin', methods=['GET'])
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()

    total_revenue_result = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(Order.status == 'paid').scalar()
    total_revenue = float(total_revenue_result or 0.0)

    low_stock_products = Product.query.filter(Product.stock < 5).all() if hasattr(Product, 'stock') else []

    page = request.args.get('page', 1, type=int)
    products_pagination = Product.query.paginate(page=page, per_page=10, error_out=False)
    recent_orders = Order.query.order_by(Order.id.desc()).limit(10).all()

    stats = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'low_stock_count': len(low_stock_products)
    }

    return render_template(
        'admin_dashboard.html',
        stats=stats,
        products=products_pagination,
        orders=recent_orders,
        low_stock_products=low_stock_products
    )


# API ROUTES

@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def api_admin_stats():
    total_products = Product.query.count()
    total_orders = Order.query.count()

    total_revenue_result = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(Order.status == 'paid').scalar()
    total_revenue = float(total_revenue_result or 0.0)

    low_stock_count = Product.query.filter(Product.stock < 5).count() if hasattr(Product, 'stock') else 0

    return jsonify({
        'success': True,
        'data': {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'low_stock_count': low_stock_count
        }
    })


@admin_bp.route('/api/admin/products', methods=['GET'])
@admin_required
def api_admin_products():
    products = Product.query.all()
    return jsonify({
        'success': True,
        'data': [serialize_product(p) for p in products]
    })


@admin_bp.route('/api/admin/products', methods=['POST'])
@admin_required
@csrf.exempt
def api_admin_create_product():
    data = request.get_json(silent=True) or request.form.to_dict()

    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    category_id = data.get('category_id')
    sizes = data.get('sizes')
    colors = data.get('colors')
    stock = data.get('stock', 0)
    images = data.get('images')

    if not name or price is None or not category_id:
        return jsonify({'success': False, 'error': 'Name, price, and category_id are required'}), 400

    try:
        price = float(price)
        category_id = int(category_id)
        stock = int(stock)
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid format for price, category_id, or stock'}), 400

    if isinstance(sizes, list):
        sizes = ",".join(sizes)
    if isinstance(colors, list):
        colors = ",".join(colors)
    if isinstance(images, list):
        images = ",".join(images)

    product_kwargs = {
        'name': name,
        'description': description,
        'price': price,
        'category_id': category_id,
    }
    if hasattr(Product, 'stock'):
        product_kwargs['stock'] = stock
    if hasattr(Product, 'sizes') and sizes is not None:
        product_kwargs['sizes'] = sizes
    if hasattr(Product, 'colors') and colors is not None:
        product_kwargs['colors'] = colors
    if hasattr(Product, 'images') and images is not None:
        product_kwargs['images'] = images

    product = Product(**product_kwargs)
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': serialize_product(product)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/products/<int:id>', methods=['PUT'])
@admin_required
@csrf.exempt
def api_admin_update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json(silent=True) or request.form.to_dict()

    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        try:
            product.price = float(data['price'])
        except ValueError:
            pass
    if 'category_id' in data:
        try:
            product.category_id = int(data['category_id'])
        except ValueError:
            pass
    if 'stock' in data and hasattr(product, 'stock'):
        try:
            product.stock = int(data['stock'])
        except ValueError:
            pass
    if 'sizes' in data and hasattr(product, 'sizes'):
        sizes = data['sizes']
        product.sizes = ",".join(sizes) if isinstance(sizes, list) else sizes
    if 'colors' in data and hasattr(product, 'colors'):
        colors = data['colors']
        product.colors = ",".join(colors) if isinstance(colors, list) else colors
    if 'images' in data and hasattr(product, 'images'):
        images = data['images']
        product.images = ",".join(images) if isinstance(images, list) else images

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'data': serialize_product(product)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/products/<int:id>', methods=['DELETE'])
@admin_required
@csrf.exempt
def api_admin_delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/orders', methods=['GET'])
@admin_required
def api_admin_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return jsonify({
        'success': True,
        'data': [serialize_order(o) for o in orders]
    })


@admin_bp.route('/api/admin/orders/<int:id>/status', methods=['PUT'])
@admin_required
@csrf.exempt
def api_admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    data = request.get_json(silent=True) or request.form.to_dict()

    new_status = data.get('status')
    if not new_status:
        return jsonify({'success': False, 'error': 'status field is required'}), 400

    order.status = new_status
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'data': serialize_order(order)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
