from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from app.extensions import db, csrf
from app.models.product import Category, Product, Review
from app.models.user import Wishlist
from app.utils.helpers import serialize_product

catalog_bp = Blueprint('catalog', __name__)


# PAGE ROUTES

@catalog_bp.route('/', methods=['GET'])
def index():
    featured_products = Product.query.order_by(Product.id.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', featured_products=featured_products, categories=categories)


@catalog_bp.route('/shop', methods=['GET'])
def shop():
    categories = Category.query.all()
    initial_products = Product.query.limit(12).all()
    return render_template('shop.html', categories=categories, products=initial_products)


@catalog_bp.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id
    ).limit(4).all()
    reviews = Review.query.filter_by(product_id=product_id).all()
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first() is not None
    return render_template(
        'product_detail.html',
        product=product,
        related_products=related_products,
        reviews=reviews,
        in_wishlist=in_wishlist
    )


# API ROUTES

@catalog_bp.route('/api/products', methods=['GET'])
def api_get_products():
    query = Product.query

    # Filter search query
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))

    # Filter category
    category = request.args.get('category', '').strip()
    if category:
        if category.isdigit():
            query = query.filter(Product.category_id == int(category))
        else:
            cat = Category.query.filter_by(slug=category).first()
            if cat:
                query = query.filter(Product.category_id == cat.id)
            else:
                query = query.join(Category).filter(
                    (Category.slug == category) | (Category.name.ilike(f'%{category}%'))
                )

    # Filter min price
    min_price = request.args.get('min_price')
    if min_price:
        try:
            query = query.filter(Product.price >= float(min_price))
        except ValueError:
            pass

    # Filter max price
    max_price = request.args.get('max_price')
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass

    # Filter size
    size = request.args.get('size', '').strip()
    if size and hasattr(Product, 'sizes'):
        query = query.filter(Product.sizes.ilike(f'%{size}%'))

    # Filter color
    color = request.args.get('color', '').strip()
    if color and hasattr(Product, 'colors'):
        query = query.filter(Product.colors.ilike(f'%{color}%'))

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating' and hasattr(Product, 'rating'):
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.id.desc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'data': [serialize_product(p) for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })


@catalog_bp.route('/api/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    serialized_reviews = [
        r.to_dict() if hasattr(r, 'to_dict') else {
            'id': r.id,
            'product_id': r.product_id,
            'user_id': getattr(r, 'user_id', None),
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') and r.created_at else None
        } for r in reviews
    ]

    return jsonify({
        'success': True,
        'data': {
            'product': serialize_product(product),
            'reviews': serialized_reviews,
            'related_products': [serialize_product(p) for p in related_products]
        }
    })


@catalog_bp.route('/api/reviews', methods=['POST'])
@login_required
@csrf.exempt
def api_create_review():
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    if not product_id or rating is None:
        return jsonify({'success': False, 'error': 'product_id and rating are required'}), 400

    try:
        rating = int(rating)
    except ValueError:
        return jsonify({'success': False, 'error': 'rating must be an integer'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )

    try:
        db.session.add(review)
        db.session.commit()
        serialized = review.to_dict() if hasattr(review, 'to_dict') else {
            'id': review.id,
            'product_id': review.product_id,
            'user_id': review.user_id,
            'rating': review.rating,
            'comment': review.comment
        }
        return jsonify({'success': True, 'data': serialized}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@catalog_bp.route('/api/search', methods=['GET'])
def api_search():
    return api_get_products()
