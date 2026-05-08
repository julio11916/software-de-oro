from core.db_utils import engine
from services.email_service import mail


def init_extensions(app):
    """Inicializa extensiones Flask en la app modular."""
    mail.init_app(app)
    return app


__all__ = ["mail", "engine", "init_extensions"]
