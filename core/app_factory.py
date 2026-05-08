from flask import Flask

from core.config import get_config
from core.extensions import init_extensions
from routes import register_blueprints


def create_app():
    """
    Fabrica base para la nueva arquitectura.
    En Fase 0 convive con el app.py legado sin reemplazarlo.
    """
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.jinja_env.auto_reload = app.config.get("TEMPLATES_AUTO_RELOAD", True)

    init_extensions(app)
    register_blueprints(app)
    return app
