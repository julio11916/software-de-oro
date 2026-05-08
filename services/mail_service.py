"""
Servicio de correo y notificaciones de pedidos/pagos.
Extrae logica de notificaciones para reducir app.py.
"""

from datetime import datetime
import os
from pathlib import Path

import pandas as pd
from flask import flash, session, url_for


def obtener_contacto_notificacion_pedido(id_usuario, cargar_usuarios_df, normalizar_email):
    usuarios = cargar_usuarios_df()
    if usuarios.empty or "email" not in usuarios.columns:
        return {}

    usuarios = usuarios.copy()
    usuarios["email"] = usuarios["email"].fillna("").astype(str).str.strip()
    usuarios["nombre"] = usuarios["nombre"].fillna("").astype(str).str.strip() if "nombre" in usuarios.columns else ""

    id_num = pd.to_numeric(id_usuario, errors="coerce")
    if pd.notna(id_num) and "id_usuario" in usuarios.columns:
        usuarios["id_usuario_num"] = pd.to_numeric(usuarios["id_usuario"], errors="coerce")
        coincidencias = usuarios[usuarios["id_usuario_num"] == int(id_num)]
        if not coincidencias.empty:
            usuario = coincidencias.iloc[0]
            return {
                "email": normalizar_email(usuario.get("email", "")),
                "nombre": str(usuario.get("nombre", "")).strip(),
            }

    email_posible = normalizar_email(id_usuario)
    if email_posible:
        coincidencias = usuarios[usuarios["email"].str.lower() == email_posible]
        if not coincidencias.empty:
            usuario = coincidencias.iloc[0]
            return {
                "email": normalizar_email(usuario.get("email", "")),
                "nombre": str(usuario.get("nombre", "")).strip(),
            }
    return {}


def notificar_actualizacion_pedido_cliente(
    id_pedido,
    id_usuario,
    obtener_contacto_notificacion_pedido_fn,
    normalizar_email,
    email_es_valido,
    enviar_actualizacion_pedido,
    etiqueta_estado_pedido,
    etiqueta_estado_pago,
    estado_pedido="",
    estado_pago="",
    tipo_actualizacion="pedido",
):
    contacto = obtener_contacto_notificacion_pedido_fn(id_usuario)
    email = normalizar_email(contacto.get("email", ""))
    if not email_es_valido(email):
        return "sin_email"

    ok = enviar_actualizacion_pedido(
        email=email,
        id_pedido=id_pedido,
        nombre=contacto.get("nombre", ""),
        estado_pedido=estado_pedido,
        estado_pedido_label=etiqueta_estado_pedido(estado_pedido),
        estado_pago=estado_pago,
        estado_pago_label=etiqueta_estado_pago(estado_pago),
        tipo_actualizacion=tipo_actualizacion,
        url_pedidos=url_for("user_orders", _external=True),
    )
    return "enviado" if ok else "fallo"


def flash_resultado_notificacion_pedido(resultado, id_pedido):
    if resultado == "enviado":
        flash(f"Se notifico al cliente por correo sobre el pedido #{id_pedido}.", "success")
    elif resultado == "fallo":
        flash(f"El pedido #{id_pedido} fue actualizado, pero no se pudo enviar el correo al cliente.", "warning")
    elif resultado == "sin_email":
        flash(
            f"El pedido #{id_pedido} fue actualizado, pero no se encontro un correo valido para notificar al cliente.",
            "warning",
        )


def obtener_items_personalizados_carrito(carrito):
    items_personalizados = []
    for item in carrito if isinstance(carrito, list) else []:
        if not isinstance(item, dict):
            continue
        tiene_flag_personalizado = bool(item.get("personalizado"))
        id_orden_personalizada = pd.to_numeric(item.get("id_orden_personalizada"), errors="coerce")
        if not tiene_flag_personalizado and pd.isna(id_orden_personalizada):
            continue
        items_personalizados.append(item)
    return items_personalizados


def notificar_pago_personalizado_admin(
    id_pedido,
    carrito,
    total_final,
    cliente_telefono,
    cliente_direccion,
    metodo_pago,
    app_config,
    normalizar_email,
    email_es_valido,
    formatear_cop,
    enviar_notificacion_pago_personalizado_admin,
    obtener_items_personalizados_carrito_fn,
    promo_aplicada=None,
    descuento_promo=0,
):
    destinatario = normalizar_email(app_config.get("TRANSFER_SUPPORT_EMAIL", "")) or normalizar_email(
        app_config.get("MAIL_DEFAULT_SENDER", "")
    )
    if not email_es_valido(destinatario):
        return False

    items_personalizados = obtener_items_personalizados_carrito_fn(carrito)
    if not items_personalizados:
        return False

    productos = []
    for item in items_personalizados:
        productos.append(
            {
                "nombre": str(item.get("nombre", "") or "Prenda personalizada").strip(),
                "talla": str(item.get("talla", "") or "").strip(),
                "cantidad": int(pd.to_numeric(item.get("cantidad", 0), errors="coerce") or 0),
                "subtotal": formatear_cop(item.get("subtotal", 0)),
                "id_orden_personalizada": int(pd.to_numeric(item.get("id_orden_personalizada"), errors="coerce") or 0),
            }
        )

    cliente = {
        "nombre": str(session.get("nombre", "") or "").strip(),
        "email": normalizar_email(session.get("usuario", "")),
        "telefono": str(cliente_telefono or "").strip(),
        "direccion": str(cliente_direccion or "").strip(),
    }

    return enviar_notificacion_pago_personalizado_admin(
        destinatario=destinatario,
        id_pedido=id_pedido,
        cliente=cliente,
        productos=productos,
        total=formatear_cop(total_final),
        metodo_pago=str(metodo_pago or "").strip(),
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
        promo_codigo=promo_aplicada.get("codigo", "") if promo_aplicada else "",
        descuento=formatear_cop(descuento_promo) if promo_aplicada else "",
    )


def notificar_transferencia_admin(
    id_pedido,
    carrito,
    total_final,
    cliente_telefono,
    cliente_direccion,
    comprobante_url,
    app_config,
    app_root_path,
    normalizar_email,
    email_es_valido,
    formatear_cop,
    enviar_notificacion_transferencia_admin,
    promo_aplicada=None,
    descuento_promo=0,
):
    destinatario = normalizar_email(app_config.get("TRANSFER_SUPPORT_EMAIL", "")) or normalizar_email(
        app_config.get("MAIL_DEFAULT_SENDER", "")
    )
    if not email_es_valido(destinatario):
        return False

    comprobante_path = Path(app_root_path) / "static" / str(comprobante_url or "").replace("/", os.sep)
    productos = []
    items_carrito = carrito if isinstance(carrito, list) else []
    for item in items_carrito:
        productos.append(
            {
                "nombre": str(item.get("nombre", "") or "Producto").strip(),
                "talla": str(item.get("talla", "") or "").strip(),
                "cantidad": int(pd.to_numeric(item.get("cantidad", 0), errors="coerce") or 0),
                "subtotal": formatear_cop(item.get("subtotal", 0)),
            }
        )

    cliente = {
        "nombre": str(session.get("nombre", "") or "").strip(),
        "email": normalizar_email(session.get("usuario", "")),
        "telefono": str(cliente_telefono or "").strip(),
        "direccion": str(cliente_direccion or "").strip(),
    }

    return enviar_notificacion_transferencia_admin(
        destinatario=destinatario,
        id_pedido=id_pedido,
        cliente=cliente,
        productos=productos,
        total=formatear_cop(total_final),
        comprobante_path=str(comprobante_path),
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
        promo_codigo=promo_aplicada.get("codigo", "") if promo_aplicada else "",
        descuento=formatear_cop(descuento_promo) if promo_aplicada else "",
    )
