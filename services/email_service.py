import base64
import logging
import mimetypes
import os
import random
import smtplib
import string
from email.utils import parseaddr

import requests
from flask import current_app, render_template
from flask_mail import Connection, Mail, Message

logger = logging.getLogger(__name__)


class TimeoutConnection(Connection):
    """Conexion Flask-Mail con limite para evitar bloquear workers web."""

    def configure_host(self):
        timeout = float(current_app.config.get("MAIL_TIMEOUT", 10))
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port, timeout=timeout)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port, timeout=timeout)

        host.set_debuglevel(int(self.mail.debug))
        if self.mail.use_tls:
            host.starttls()
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)
        return host


class TimeoutMail(Mail):
    def connect(self):
        app = getattr(self, "app", None) or current_app
        try:
            return TimeoutConnection(app.extensions["mail"])
        except KeyError as exc:
            raise RuntimeError(
                "La aplicacion no tiene configurada la extension de correo."
            ) from exc

    def send(self, message):
        provider = str(current_app.config.get("MAIL_PROVIDER", "smtp")).strip().lower()
        if provider == "brevo":
            self._send_with_brevo(message)
            return
        super().send(message)

    @staticmethod
    def _address_payload(address, default_name=""):
        if isinstance(address, (tuple, list)) and len(address) >= 2:
            name = str(address[0] or "").strip()
            email = str(address[1] or "").strip()
        else:
            name, email = parseaddr(str(address or "").strip())

        payload = {"email": email}
        if name or default_name:
            payload["name"] = name or default_name
        return payload

    def _send_with_brevo(self, message):
        api_key = str(current_app.config.get("BREVO_API_KEY", "")).strip()
        if not api_key:
            raise RuntimeError(
                "MAIL_PROVIDER esta configurado como brevo, pero falta BREVO_API_KEY."
            )

        sender = message.sender or current_app.config.get("MAIL_DEFAULT_SENDER", "")
        sender_payload = self._address_payload(
            sender,
            default_name=str(current_app.config.get("MAIL_SENDER_NAME", "Nachohers")).strip(),
        )
        if not sender_payload.get("email"):
            raise RuntimeError(
                "Falta MAIL_DEFAULT_SENDER para enviar correos mediante Brevo."
            )

        recipients = [
            self._address_payload(address)
            for address in (message.recipients or [])
        ]
        recipients = [item for item in recipients if item.get("email")]
        if not recipients:
            raise RuntimeError("El correo no tiene destinatarios validos.")

        payload = {
            "sender": sender_payload,
            "to": recipients,
            "subject": str(message.subject or "").strip(),
        }
        if message.html:
            payload["htmlContent"] = message.html
        elif message.body:
            payload["textContent"] = message.body
        else:
            raise RuntimeError("El correo no tiene contenido HTML ni texto.")

        for source_attr, target_key in (("cc", "cc"), ("bcc", "bcc")):
            addresses = getattr(message, source_attr, None) or []
            values = [self._address_payload(address) for address in addresses]
            values = [item for item in values if item.get("email")]
            if values:
                payload[target_key] = values

        reply_to = getattr(message, "reply_to", None)
        if reply_to:
            payload["replyTo"] = self._address_payload(reply_to)

        attachments = []
        for attachment in message.attachments or []:
            raw_data = attachment.data
            if isinstance(raw_data, str):
                raw_data = raw_data.encode("utf-8")
            attachments.append(
                {
                    "name": attachment.filename or "adjunto",
                    "content": base64.b64encode(raw_data).decode("ascii"),
                }
            )
        if attachments:
            payload["attachment"] = attachments

        response = requests.post(
            str(current_app.config.get("BREVO_API_URL")).strip(),
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=float(current_app.config.get("BREVO_TIMEOUT", 15)),
        )
        if not response.ok:
            detail = response.text[:500].strip()
            raise RuntimeError(
                f"Brevo rechazo el correo con estado {response.status_code}: {detail}"
            )


mail = TimeoutMail()


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
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHERS')).strip() or 'NACHOHERS'
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
    except Exception:
        logger.exception("Error al enviar correo")
        return False


def enviar_recuperacion_password(email, enlace_recuperacion, minutos_expiracion=30):
    """Envia el correo con enlace para recuperar contrasena."""
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHERS')).strip() or 'NACHOHERS'
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
    except Exception:
        logger.exception("Error al enviar correo de recuperación")
        return False


def _contenido_actualizacion_pedido(tipo_actualizacion, estado_pedido, estado_pago, estado_pedido_label, estado_pago_label):
    tipo = str(tipo_actualizacion or '').strip().lower()
    pedido = str(estado_pedido or '').strip().lower()
    pago = str(estado_pago or '').strip().lower()

    if tipo == 'pago':
        if pago == 'aprobado':
            return (
                'Pago aprobado',
                'Confirmamos el pago de tu pedido.',
                'Tu pedido quedo confirmado y continuara con el proceso de preparacion.'
            )
        if pago == 'rechazado':
            return (
                'Pago rechazado',
                'No pudimos aprobar el comprobante de pago enviado.',
                'El pedido quedo cancelado. Si crees que se trata de un error, comunicate con nuestro equipo para revisarlo.'
            )
        if pago == 'en_revision':
            return (
                'Pago en revision',
                'Estamos revisando el comprobante de pago de tu pedido.',
                'Te avisaremos cuando el equipo confirme la informacion del pago.'
            )
        return (
            'Pago actualizado',
            f'El estado del pago ahora es: {estado_pago_label or pago or "Actualizado"}.',
            'Puedes consultar el detalle del pedido desde tu cuenta.'
        )

    mensajes_pedido = {
        'confirmado': (
            'Pedido confirmado',
            'Tu pedido fue confirmado correctamente.',
            'Nuestro equipo empezara a preparar los productos para continuar con el despacho.'
        ),
        'empaquetado': (
            'Pedido empaquetado',
            'Tu pedido ya fue empaquetado.',
            'Estamos dejando todo listo para el siguiente paso del envio.'
        ),
        'enviado': (
            'Pedido enviado',
            'Tu pedido ya fue enviado.',
            'Muy pronto recibiras o podras consultar las novedades de entrega.'
        ),
        'entregado': (
            'Pedido entregado',
            'Marcamos tu pedido como entregado.',
            'Gracias por confiar en nosotros. Esperamos que todo haya llegado correctamente.'
        ),
        'cancelado': (
            'Pedido cancelado',
            'Tu pedido fue marcado como cancelado.',
            'Si necesitas mas informacion, puedes comunicarte con nuestro equipo de atencion.'
        ),
        'pago_en_revision': (
            'Pedido en revision de pago',
            'Tu pedido esta pendiente de validacion de pago.',
            'Revisaremos la informacion y te notificaremos cuando haya una novedad.'
        ),
    }
    return mensajes_pedido.get(
        pedido,
        (
            'Pedido actualizado',
            f'El estado de tu pedido ahora es: {estado_pedido_label or pedido or "Actualizado"}.',
            'Puedes consultar el avance desde tu cuenta.'
        )
    )


def enviar_actualizacion_pedido(
    email,
    id_pedido,
    nombre='',
    estado_pedido='',
    estado_pedido_label='',
    estado_pago='',
    estado_pago_label='',
    tipo_actualizacion='pedido',
    url_pedidos='',
):
    """Envia una notificacion transaccional cuando cambia el estado de un pedido."""
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHERS')).strip() or 'NACHOHERS'
        titulo, resumen, detalle = _contenido_actualizacion_pedido(
            tipo_actualizacion,
            estado_pedido,
            estado_pago,
            estado_pedido_label,
            estado_pago_label,
        )
        msg = Message(
            subject=f"Actualizacion de tu pedido #{id_pedido} - {proyecto}",
            recipients=[email],
        )
        msg.html = render_template(
            'emails/actualizacion_pedido.html',
            proyecto=proyecto,
            nombre=str(nombre or '').strip(),
            id_pedido=id_pedido,
            titulo=titulo,
            resumen=resumen,
            detalle=detalle,
            estado_pedido_label=estado_pedido_label,
            estado_pago_label=estado_pago_label,
            tipo_actualizacion=str(tipo_actualizacion or '').strip().lower(),
            url_pedidos=str(url_pedidos or '').strip(),
        )
        mail.send(msg)
        return True
    except Exception:
        logger.exception("Error al enviar correo de actualización de pedido")
        return False


def enviar_notificacion_transferencia_admin(
    destinatario,
    id_pedido,
    cliente,
    productos,
    total,
    comprobante_path,
    fecha='',
    promo_codigo='',
    descuento='',
):
    """Notifica al administrador sobre una transferencia nueva y adjunta el comprobante."""
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHERS')).strip() or 'NACHOHERS'
        email_destino = str(destinatario or '').strip()
        if not email_destino:
            return False

        msg = Message(
            subject=f"Nuevo pedido por transferencia #{id_pedido} - {proyecto}",
            recipients=[email_destino],
        )
        msg.html = render_template(
            'emails/nuevo_pedido_transferencia.html',
            proyecto=proyecto,
            id_pedido=id_pedido,
            cliente=cliente or {},
            productos=productos or [],
            total=total,
            fecha=fecha,
            promo_codigo=promo_codigo,
            descuento=descuento,
        )

        ruta_comprobante = str(comprobante_path or '').strip()
        if not ruta_comprobante or not os.path.isfile(ruta_comprobante):
            return False

        filename = os.path.basename(ruta_comprobante)
        content_type = mimetypes.guess_type(ruta_comprobante)[0] or 'application/octet-stream'
        with open(ruta_comprobante, 'rb') as adjunto:
            msg.attach(filename, content_type, adjunto.read())

        mail.send(msg)
        return True
    except Exception:
        logger.exception("Error al enviar notificación de transferencia al administrador")
        return False


def enviar_notificacion_pago_personalizado_admin(
    destinatario,
    id_pedido,
    cliente,
    productos,
    total,
    metodo_pago='',
    fecha='',
    promo_codigo='',
    descuento='',
):
    """Notifica al administrador cuando se confirma un pago con prendas personalizadas."""
    try:
        proyecto = str(current_app.config.get('PROJECT_NAME', 'NACHOHERS')).strip() or 'NACHOHERS'
        email_destino = str(destinatario or '').strip()
        if not email_destino:
            return False

        msg = Message(
            subject=f"Pago confirmado de prenda personalizada #{id_pedido} - {proyecto}",
            recipients=[email_destino],
        )
        msg.html = render_template(
            'emails/nuevo_pago_prenda_personalizada_admin.html',
            proyecto=proyecto,
            id_pedido=id_pedido,
            cliente=cliente or {},
            productos=productos or [],
            total=total,
            metodo_pago=str(metodo_pago or '').strip() or 'No especificado',
            fecha=fecha,
            promo_codigo=promo_codigo,
            descuento=descuento,
        )
        mail.send(msg)
        return True
    except Exception:
        logger.exception("Error al enviar notificación de pago personalizado al administrador")
        return False
