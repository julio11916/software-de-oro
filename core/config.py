import os

from dotenv import load_dotenv

from core import config_email

load_dotenv()


class BaseConfig:
    """Configuracion central del proyecto para la migracion a arquitectura modular."""

    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()

    TEMPLATES_AUTO_RELOAD = True

    MAIL_SERVER = os.getenv("MAIL_SERVER", config_email.MAIL_SERVER)
    MAIL_PORT = int(os.getenv("MAIL_PORT", str(config_email.MAIL_PORT)))
    MAIL_USE_TLS = str(os.getenv("MAIL_USE_TLS", str(config_email.MAIL_USE_TLS))).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", config_email.MAIL_USERNAME)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", config_email.MAIL_PASSWORD)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", config_email.MAIL_DEFAULT_SENDER)

    PROJECT_NAME = os.getenv("PROJECT_NAME", "NACHOHERS").strip() or "NACHOHERS"
    TRANSFER_QR_IMAGE = os.getenv("TRANSFER_QR_IMAGE", "img/qr/qr.jpeg").strip() or "img/qr/qr.jpeg"
    TRANSFER_SUPPORT_EMAIL = os.getenv("TRANSFER_SUPPORT_EMAIL", MAIL_DEFAULT_SENDER).strip()
    TRANSFER_SUPPORT_WHATSAPP = os.getenv("TRANSFER_SUPPORT_WHATSAPP", "").strip()


def get_config():
    return BaseConfig
