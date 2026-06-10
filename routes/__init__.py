from .admin import admin_bp
from .auth import auth_bp
from .checkout import checkout_bp
from .custom_orders import custom_orders_bp
from .main import main_bp
from .user import user_bp


def register_blueprints(app):
    """
    Registro centralizado de blueprints.
    Fase 0: estructura base sin mover aun las rutas del app.py legado.
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(custom_orders_bp)
    return app


__all__ = ["register_blueprints"]

