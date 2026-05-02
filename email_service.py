import random
import string
import mimetypes
import os

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
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
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
    except Exception as e:
        print(f"Error al enviar correo de recuperacion: {str(e)}")
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
    except Exception as e:
        print(f"Error al enviar correo de actualizacion de pedido: {str(e)}")
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
    except Exception as e:
        print(f"Error al enviar notificacion de transferencia al administrador: {str(e)}")
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
    except Exception as e:
        print(f"Error al enviar notificacion de pago personalizado al administrador: {str(e)}")
        return False
