import random
import string

from flask import current_app, render_template
from flask_mail import Mail, Message

mail = Mail()


def generar_codigo_verificacion():
    """Genera un codigo de verificacion de 6 digitos."""
    return ''.join(random.choices(string.digits, k=6))


def enviar_codigo_verificacion(email, codigo, tipo='registro', minutos_expiracion=7):
    """
    Envia un codigo de verificacion por correo.

    Args:
        email: Correo destino.
        codigo: Codigo de 6 digitos.
        tipo: Contexto del mensaje ('registro' o 'autenticacion').
        minutos_expiracion: Minutos de validez del codigo.
    """
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHER')).strip() or 'NACHOHER'
        es_registro = str(tipo).strip().lower() == 'registro'
        asunto = (
            f"Tu codigo de verificacion para {proyecto}"
            if es_registro
            else f"Codigo de autenticacion para {proyecto}"
        )

        msg = Message(
            subject=asunto,
            recipients=[email],
        )

        msg.html = render_template(
            'emails/codigo_verificacion.html',
            codigo=codigo,
            proyecto=proyecto,
            minutos_expiracion=int(minutos_expiracion),
            es_registro=es_registro,
        )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False


def enviar_recuperacion_password(email, enlace_recuperacion, minutos_expiracion=30):
    """Envia el correo con enlace para recuperar contrasena."""
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHER')).strip() or 'NACHOHER'
        msg = Message(
            subject=f"Recuperacion de contrasena - {proyecto}",
            recipients=[email],
        )
        msg.html = render_template(
            'emails/recuperar_password.html',
            proyecto=proyecto,
            enlace_recuperacion=enlace_recuperacion,
            minutos_expiracion=int(minutos_expiracion),
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo de recuperacion: {str(e)}")
        return False
