import os
import click
from flask import Flask, request, jsonify, render_template
from app.extensions import db, login_manager, csrf, migrate, mail
from app.config import config


def create_app(config_class=None):
    """Flask application factory."""
    if config_class is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
        config_class = config.get(config_name, config['default'])
    elif isinstance(config_class, str):
        config_class = config.get(config_class, config['default'])

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from app.models import User
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Register blueprints
    try:
        from app.routes import register_blueprints
        register_blueprints(app)
    except ImportError:
        pass

    # Context processors
    @app.context_processor
    def inject_global_context():
        categories = []
        try:
            from app.models import Category
            categories = Category.query.all()
        except Exception:
            categories = []

        try:
            from app.utils.helpers import get_cart_count
            cart_count = get_cart_count()
        except Exception:
            cart_count = 0

        return {
            'categories': categories,
            'cart_count': cart_count
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        try:
            return render_template('errors/404.html'), 404
        except Exception:
            return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            return jsonify({'error': 'Internal server error'}), 500

    # Shell context processor for flask shell
    @app.shell_context_processor
    def make_shell_context():
        context = {'db': db}
        try:
            from app import models
            for attr_name in dir(models):
                attr = getattr(models, attr_name)
                if isinstance(attr, type) and hasattr(attr, '__tablename__'):
                    context[attr_name] = attr
        except ImportError:
            pass
        return context

    # CLI command: flask seed
    @app.cli.command('seed')
    def seed_db():
        """Seed database with initial data."""
        try:
            import seed
            if hasattr(seed, 'seed') and callable(seed.seed):
                seed.seed()
            elif hasattr(seed, 'main') and callable(seed.main):
                seed.main()
            else:
                click.echo("seed.py found but no callable seed() or main() found.")
        except ImportError:
            click.echo("seed.py not found.")

    # Import models at bottom for migrations detection
    try:
        from app import models  # noqa: F401
    except ImportError:
        pass

    return app
