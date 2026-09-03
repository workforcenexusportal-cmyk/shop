import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from app.extensions import db, csrf
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.forms.checkout import CheckoutForm
from app.utils.helpers import get_or_create_cart, serialize_order

orders_bp = Blueprint('orders', __name__)


# PAGE ROUTES

@orders_bp.route('/checkout', methods=['POST'])
def checkout_submit():
    form = CheckoutForm()
    cart = get_or_create_cart()

    if not getattr(cart, 'items', None):
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('cart.cart_view'))

    if form.validate_on_submit():
        address_parts = [
            form.address_line1.data,
            form.address_line2.data,
            form.city.data,
            form.state.data,
            form.zip_code.data,
            form.country.data
        ]
        shipping_address = ", ".join([p for p in address_parts if p])
        total_amount = sum(
            float(getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)) * item.quantity
            for item in cart.items
        )

        order_kwargs = {
            'email': form.email.data,
            'shipping_address': shipping_address,
            'shipping_method': form.shipping_method.data,
            'total_amount': total_amount,
            'status': 'pending'
        }
        if current_user.is_authenticated:
            order_kwargs['user_id'] = current_user.id

        order = Order(**order_kwargs)
        db.session.add(order)
        db.session.flush()

        for item in cart.items:
            price = getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)
            item_kwargs = {
                'order_id': order.id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': price
            }
            if hasattr(OrderItem, 'size') and hasattr(item, 'size'):
                item_kwargs['size'] = item.size
            if hasattr(OrderItem, 'color') and hasattr(item, 'color'):
                item_kwargs['color'] = item.color

            db.session.add(OrderItem(**item_kwargs))

        for item in list(cart.items):
            db.session.delete(item)

        try:
            db.session.commit()
            flash('Order placed successfully!', 'success')
            if current_user.is_authenticated:
                return redirect(url_for('auth.account'))
            return redirect(url_for('catalog.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order.', 'danger')
            return redirect(url_for('cart.checkout_view'))

    cart_items = [item for item in cart.items] if hasattr(cart, 'items') else []
    cart_total = sum(
        float(getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)) * item.quantity
        for item in cart_items
    )
    return render_template('checkout.html', cart=cart, cart_items=cart_items, cart_total=cart_total, form=form)


# API ROUTES

@orders_bp.route('/api/checkout', methods=['POST'])
@csrf.exempt
def api_checkout():
    data = request.get_json(silent=True) or {}
    cart = get_or_create_cart()

    if not getattr(cart, 'items', None):
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400

    email = data.get('email') or (current_user.email if current_user.is_authenticated else '')
    shipping_address = data.get('shipping_address')
    if isinstance(shipping_address, dict):
        shipping_address = ", ".join([f"{v}" for k, v in shipping_address.items() if v])

    shipping_method = data.get('shipping_method', 'standard')

    total_amount = sum(
        float(getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)) * item.quantity
        for item in cart.items
    )

    order_kwargs = {
        'email': email,
        'shipping_address': shipping_address or '',
        'shipping_method': shipping_method,
        'total_amount': total_amount,
        'status': 'pending'
    }
    if current_user.is_authenticated:
        order_kwargs['user_id'] = current_user.id

    order = Order(**order_kwargs)
    db.session.add(order)
    db.session.flush()

    for item in cart.items:
        price = getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)
        item_kwargs = {
            'order_id': order.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': price
        }
        if hasattr(OrderItem, 'size') and hasattr(item, 'size'):
            item_kwargs['size'] = item.size
        if hasattr(OrderItem, 'color') and hasattr(item, 'color'):
            item_kwargs['color'] = item.color

        db.session.add(OrderItem(**item_kwargs))

    stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY') or os.environ.get('STRIPE_SECRET_KEY')
    stripe_session_url = None
    session_id = None

    if stripe_secret_key:
        try:
            import stripe
            stripe.api_key = stripe_secret_key
            line_items = []
            for item in cart.items:
                p_name = item.product.name if getattr(item, 'product', None) else f"Product #{item.product_id}"
                p_price = getattr(item, 'price', None) or (item.product.price if getattr(item, 'product', None) else 0.0)
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': p_name},
                        'unit_amount': int(float(p_price) * 100),
                    },
                    'quantity': item.quantity,
                })
            domain = request.host_url.rstrip('/')
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{domain}/account?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain}/checkout",
                client_reference_id=str(order.id),
                metadata={'order_id': str(order.id)}
            )
            stripe_session_url = checkout_session.url
            session_id = checkout_session.id
            if hasattr(order, 'stripe_session_id'):
                order.stripe_session_id = session_id
        except Exception as e:
            current_app.logger.error(f"Stripe integration error: {e}")

    for item in list(cart.items):
        db.session.delete(item)

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'data': {
                'order_id': order.id,
                'stripe_session_url': stripe_session_url,
                'session_id': session_id,
                'order': serialize_order(order)
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return jsonify({
        'success': True,
        'data': [serialize_order(o) for o in orders]
    })


@orders_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def api_get_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    return jsonify({
        'success': True,
        'data': serialize_order(order)
    })


@orders_bp.route('/api/stripe/webhook', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET') or os.environ.get('STRIPE_WEBHOOK_SECRET')

    event = None

    if endpoint_secret and sig_header:
        try:
            import stripe
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except Exception as e:
            current_app.logger.error(f"Webhook signature verification failed: {e}")
            return jsonify({'error': str(e)}), 400
    else:
        event = request.get_json(silent=True) or {}

    if event and event.get('type') == 'checkout.session.completed':
        session_obj = event.get('data', {}).get('object', {})
        order_id = session_obj.get('client_reference_id') or session_obj.get('metadata', {}).get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if order:
                order.status = 'paid'
                db.session.commit()

    return jsonify({'status': 'success'}), 200
