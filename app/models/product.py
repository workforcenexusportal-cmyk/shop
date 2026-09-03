import json
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    slug = db.Column(db.String(100), unique=True, nullable=True, index=True)

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    images = db.Column(db.Text, nullable=True)  # JSON-serialized list of URL strings
    sizes = db.Column(db.Text, nullable=True)   # JSON-serialized list e.g. ["XS","S","M","L","XL"]
    colors = db.Column(db.Text, nullable=True)  # JSON-serialized list e.g. ["Black","White"]
    stock = db.Column(db.Integer, default=0, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

    # Helper methods for JSON fields
    def get_images(self):
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_images(self, images_list):
        self.images = json.dumps(images_list) if images_list is not None else json.dumps([])

    def get_sizes(self):
        if not self.sizes:
            return []
        try:
            return json.loads(self.sizes)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_sizes(self, sizes_list):
        self.sizes = json.dumps(sizes_list) if sizes_list is not None else json.dumps([])

    def get_colors(self):
        if not self.colors:
            return []
        try:
            return json.loads(self.colors)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_colors(self, colors_list):
        self.colors = json.dumps(colors_list) if colors_list is not None else json.dumps([])

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        ratings = [r.rating for r in self.reviews if r.rating is not None]
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 1)

    @property
    def in_stock(self):
        return (self.stock or 0) > 0

    def __repr__(self):
        return f'<Product {self.name}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='reviews', lazy=True)

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def __repr__(self):
        return f'<Review Product:{self.product_id} Rating:{self.rating}>'
