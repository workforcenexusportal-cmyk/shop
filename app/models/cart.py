from datetime import datetime
from app.extensions import db


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items if item.quantity is not None)

    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    size = db.Column(db.String(10), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=True)

    # Relationships
    product = db.relationship('Product')

    @property
    def subtotal(self):
        if self.product and self.product.price is not None and self.quantity is not None:
            return self.product.price * self.quantity
        return 0.0

    def __repr__(self):
        return f'<CartItem {self.id}>'
