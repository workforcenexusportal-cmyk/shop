from datetime import datetime
from app.extensions import db


class Order(db.Model):
    STATUS_CHOICES = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), nullable=True)  # for guest orders
    total = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=True, index=True)
    shipping_address = db.Column(db.Text, nullable=True)  # JSON
    shipping_method = db.Column(db.String(50), nullable=True)
    stripe_session_id = db.Column(db.String(255), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=True)
    product_price = db.Column(db.Float, nullable=True)
    size = db.Column(db.String(10), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<OrderItem {self.id}>'
