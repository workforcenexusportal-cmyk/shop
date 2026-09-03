from app.routes.auth import auth_bp
from app.routes.catalog import catalog_bp
from app.routes.cart import cart_bp
from app.routes.orders import orders_bp
from app.routes.admin import admin_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
