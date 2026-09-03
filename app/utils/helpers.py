import json
import uuid
from flask import session
from flask_login import current_user
from app.extensions import db


def _parse_json(val, default=None):
    """Helper to parse JSON string or return existing data structure."""
    if default is None:
        default = []
    if val is None:
        return default
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return default
    return default


def get_or_create_cart():
    """Retrieve existing cart or create a new one for user/session."""
    try:
        from app.models import Cart
    except ImportError:
        return None

    cart = None
    session_id = session.get('cart_session_id')

    if current_user and current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            if session_id:
                cart = Cart.query.filter_by(session_id=session_id).first()
                if cart:
                    cart.user_id = current_user.id
                    db.session.commit()
            if not cart:
                cart = Cart(user_id=current_user.id)
                db.session.add(cart)
                db.session.commit()
    else:
        if not session_id:
            session_id = str(uuid.uuid4())
            session['cart_session_id'] = session_id

        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()

    return cart


def serialize_product(product):
    """Serialize product instance into a dictionary."""
    if not product:
        return {}

    images = _parse_json(getattr(product, 'images', None), default=[])
    sizes = _parse_json(getattr(product, 'sizes', None), default=[])
    colors = _parse_json(getattr(product, 'colors', None), default=[])

    reviews = getattr(product, 'reviews', []) or []
    if reviews:
        ratings = [r.rating for r in reviews if hasattr(r, 'rating') and r.rating is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
    else:
        avg_rating = 0.0

    created_date = None
    if getattr(product, 'created_date', None):
        if hasattr(product.created_date, 'isoformat'):
            created_date = product.created_date.isoformat()
        else:
            created_date = str(product.created_date)

    category_name = None
    if getattr(product, 'category', None):
        category_name = product.category.name

    return {
        'id': product.id,
        'name': getattr(product, 'name', ''),
        'description': getattr(product, 'description', ''),
        'price': getattr(product, 'price', 0.0),
        'category': category_name,
        'category_id': getattr(product, 'category_id', None),
        'images': images,
        'sizes': sizes,
        'colors': colors,
        'stock': getattr(product, 'stock', 0),
        'created_date': created_date,
        'average_rating': avg_rating
    }


def serialize_cart_item(item):
    """Serialize cart item instance into a dictionary."""
    if not item:
        return {}

    product = getattr(item, 'product', None)
    product_name = getattr(item, 'product_name', None) or (product.name if product else None)
    product_price = getattr(item, 'product_price', None) or (product.price if product else 0.0)

    images = _parse_json(getattr(product, 'images', None), default=[]) if product else []
    product_image = images[0] if (images and isinstance(images, list) and len(images) > 0) else None

    quantity = getattr(item, 'quantity', 1)
    subtotal = round((product_price or 0.0) * quantity, 2)

    return {
        'id': item.id,
        'product_id': getattr(item, 'product_id', None),
        'product_name': product_name,
        'product_price': product_price,
        'product_image': product_image,
        'size': getattr(item, 'size', None),
        'color': getattr(item, 'color', None),
        'quantity': quantity,
        'subtotal': subtotal
    }


def get_cart_count(cart=None):
    """Return total count of items in the current user/session cart.

    Accepts an optional pre-fetched cart to avoid a redundant DB query.
    """
    try:
        if cart is None:
            cart = get_or_create_cart()
        if not cart or not hasattr(cart, 'items') or not cart.items:
            return 0
        return sum(getattr(item, 'quantity', 1) for item in cart.items)
    except Exception:
        return 0


def serialize_order(order):
    """Serialize order instance into a dictionary."""
    if not order:
        return {}

    created_date = None
    if getattr(order, 'created_date', None):
        if hasattr(order.created_date, 'isoformat'):
            created_date = order.created_date.isoformat()
        else:
            created_date = str(order.created_date)

    shipping_address = _parse_json(getattr(order, 'shipping_address', None), default={})
    items = [serialize_order_item(i) for i in order.items] if getattr(order, 'items', None) else []

    return {
        'id': order.id,
        'user_id': getattr(order, 'user_id', None),
        'email': getattr(order, 'email', None),
        'total': getattr(order, 'total', 0.0),
        'status': getattr(order, 'status', 'pending'),
        'shipping_address': shipping_address,
        'shipping_method': getattr(order, 'shipping_method', None),
        'stripe_session_id': getattr(order, 'stripe_session_id', None),
        'created_date': created_date,
        'items': items
    }


def serialize_order_item(item):
    """Serialize order item instance into a dictionary."""
    if not item:
        return {}

    quantity = getattr(item, 'quantity', 1)
    price = getattr(item, 'product_price', 0.0) or 0.0
    subtotal = round(price * quantity, 2)

    return {
        'id': item.id,
        'product_id': getattr(item, 'product_id', None),
        'product_name': getattr(item, 'product_name', None),
        'product_price': price,
        'size': getattr(item, 'size', None),
        'color': getattr(item, 'color', None),
        'quantity': quantity,
        'subtotal': subtotal
    }
