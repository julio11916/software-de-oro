import os

from dotenv import load_dotenv

try:
    from core import config_email
except ImportError:
    config_email = None

load_dotenv()


class BaseConfig:
    """Configuración central del proyecto para la migración a arquitectura modular."""

    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()

    TEMPLATES_AUTO_RELOAD = True

    MAIL_SERVER_DEFAULT = getattr(config_email, "MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT_DEFAULT = getattr(config_email, "MAIL_PORT", 587)
    MAIL_USE_TLS_DEFAULT = getattr(config_email, "MAIL_USE_TLS", True)
    MAIL_USERNAME_DEFAULT = getattr(config_email, "MAIL_USERNAME", "")
    MAIL_PASSWORD_DEFAULT = getattr(config_email, "MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER_DEFAULT = getattr(config_email, "MAIL_DEFAULT_SENDER", MAIL_USERNAME_DEFAULT)

    MAIL_SERVER = os.getenv("MAIL_SERVER", MAIL_SERVER_DEFAULT)
    MAIL_PORT = int(os.getenv("MAIL_PORT", str(MAIL_PORT_DEFAULT)))
    MAIL_USE_TLS = str(os.getenv("MAIL_USE_TLS", str(MAIL_USE_TLS_DEFAULT))).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", MAIL_USERNAME_DEFAULT)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", MAIL_PASSWORD_DEFAULT)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_DEFAULT_SENDER_DEFAULT)

    PROJECT_NAME = os.getenv("PROJECT_NAME", "NACHOHERS").strip() or "NACHOHERS"
    TRANSFER_QR_IMAGE = os.getenv("TRANSFER_QR_IMAGE", "img/qr/qr.jpeg").strip() or "img/qr/qr.jpeg"
    TRANSFER_SUPPORT_EMAIL = os.getenv("TRANSFER_SUPPORT_EMAIL", MAIL_DEFAULT_SENDER).strip()
    TRANSFER_SUPPORT_WHATSAPP = os.getenv("TRANSFER_SUPPORT_WHATSAPP", "").strip()


def get_config():
    return BaseConfig
