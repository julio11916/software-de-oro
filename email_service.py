import random
import string

from flask import render_template
from flask_mail import Mail, Message

mail = Mail()


def generar_codigo_verificacion():
    """Genera un código de verificación de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=6))


def enviar_codigo_verificacion(email, codigo):
    """
    Envía un código de verificación al correo del usuario.

    Args:
        email: Dirección de correo del destinatario.
        codigo: Código de verificación de 6 dígitos.

    Returns:
        bool: True si se envió correctamente, False en caso contrario.
    """
    try:
        msg = Message(
            subject='Código de autenticación - Nachoher',
            sender='noreply@nachoher.com',
            recipients=[email],
        )

        msg.html = render_template('emails/codigo_verificacion.html', codigo=codigo)

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False
