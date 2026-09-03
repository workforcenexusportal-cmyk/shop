from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.extensions import db, csrf
from app.models.cart import Cart, CartItem
from app.models.user import Wishlist
from app.models.product import Product
from app.forms.checkout import CheckoutForm
from app.utils.helpers import get_or_create_cart, serialize_cart_item, get_cart_count, serialize_product

cart_bp = Blueprint('cart', __name__)


def compute_cart_total(cart):
    if not cart or not getattr(cart, 'items', None):
        return 0.0
    total = 0.0
    for item in cart.items:
        price = getattr(item, 'price', None)
        if price is None and getattr(item, 'product', None):
            price = getattr(item.product, 'price', 0.0)
        quantity = getattr(item, 'quantity', 1)
        total += float(price or 0.0) * quantity
    return round(total, 2)


# PAGE ROUTES

@cart_bp.route('/cart', methods=['GET'])
def view_cart():
    cart = get_or_create_cart()
    cart_items = [serialize_cart_item(item) for item in cart.items] if hasattr(cart, 'items') and cart.items else []
    cart_total = compute_cart_total(cart)
    return render_template('cart.html', cart=cart, cart_items=cart_items, cart_total=cart_total)


@cart_bp.route('/checkout', methods=['GET'])
def checkout():
    cart = get_or_create_cart()
    cart_items = [serialize_cart_item(item) for item in cart.items] if hasattr(cart, 'items') and cart.items else []
    cart_total = compute_cart_total(cart)
    form = CheckoutForm()

    if current_user.is_authenticated:
        if hasattr(form, 'email') and not form.email.data:
            form.email.data = current_user.email
        if hasattr(form, 'full_name') and not form.full_name.data:
            form.full_name.data = getattr(current_user, 'full_name', '')

    return render_template('checkout.html', cart=cart, cart_items=cart_items, cart_total=cart_total, form=form)


# API ROUTES

@cart_bp.route('/api/cart', methods=['GET'])
def api_get_cart():
    cart = get_or_create_cart()
    items = [serialize_cart_item(i) for i in cart.items] if hasattr(cart, 'items') and cart.items else []
    total = compute_cart_total(cart)
    return jsonify({
        'success': True,
        'data': items,
        'total': total,
        'cart_count': get_cart_count(cart)
    })


@cart_bp.route('/api/cart', methods=['POST'])
@csrf.exempt
def api_add_to_cart():
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    size = data.get('size')
    color = data.get('color')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'error': 'product_id is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    cart = get_or_create_cart()

    filter_kwargs = {'cart_id': cart.id, 'product_id': product_id}
    if hasattr(CartItem, 'size') and size is not None:
        filter_kwargs['size'] = size
    if hasattr(CartItem, 'color') and color is not None:
        filter_kwargs['color'] = color

    existing_item = CartItem.query.filter_by(**filter_kwargs).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item_kwargs = {
            'cart_id': cart.id,
            'product_id': product_id,
            'quantity': quantity
        }
        if hasattr(CartItem, 'size'):
            new_item_kwargs['size'] = size
        if hasattr(CartItem, 'color'):
            new_item_kwargs['color'] = color

        item = CartItem(**new_item_kwargs)
        db.session.add(item)

    try:
        db.session.commit()
        cart = get_or_create_cart()
        items = [serialize_cart_item(i) for i in cart.items] if hasattr(cart, 'items') and cart.items else []
        return jsonify({
            'success': True,
            'data': items,
            'cart_count': get_cart_count(cart)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@cart_bp.route('/api/cart/<int:item_id>', methods=['PUT'])
@csrf.exempt
def api_update_cart_item(item_id):
    data = request.get_json(silent=True) or {}
    quantity = int(data.get('quantity', 0))

    item = CartItem.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': 'Cart item not found'}), 404

    try:
        if quantity <= 0:
            db.session.delete(item)
            db.session.commit()
            cart = get_or_create_cart()
            return jsonify({
                'success': True,
                'data': None,
                'cart_count': get_cart_count(cart)
            })
        else:
            item.quantity = quantity
            db.session.commit()
            cart = get_or_create_cart()
            return jsonify({
                'success': True,
                'data': serialize_cart_item(item),
                'cart_count': get_cart_count(cart)
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@cart_bp.route('/api/cart/<int:item_id>', methods=['DELETE'])
@csrf.exempt
def api_delete_cart_item(item_id):
    item = CartItem.query.get(item_id)
    if item:
        try:
            db.session.delete(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    cart = get_or_create_cart()
    return jsonify({
        'success': True,
        'cart_count': get_cart_count(cart)
    })


@cart_bp.route('/api/wishlist', methods=['POST'])
@login_required
@csrf.exempt
def api_toggle_wishlist():
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'error': 'product_id is required'}), 400

    wishlist_item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    try:
        if wishlist_item:
            db.session.delete(wishlist_item)
            in_wishlist = False
        else:
            new_item = Wishlist(user_id=current_user.id, product_id=product_id)
            db.session.add(new_item)
            in_wishlist = True

        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': in_wishlist})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@cart_bp.route('/api/wishlist', methods=['GET'])
@login_required
def api_get_wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = []
    for item in wishlist_items:
        if hasattr(item, 'product') and item.product:
            products.append(serialize_product(item.product))
        elif hasattr(item, 'product_id') and item.product_id:
            p = Product.query.get(item.product_id)
            if p:
                products.append(serialize_product(p))
    return jsonify({'success': True, 'data': products})
