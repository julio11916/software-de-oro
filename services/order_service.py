"""
Servicio de pedidos y pagos.
Extrae logica de checkout para reducir el tamano de app.py.
"""

from datetime import datetime
import hashlib
import json
import re
from typing import Mapping

import pandas as pd
from flask import flash, redirect, session, url_for


def asegurar_columnas_descuento_pagos(pagos):
    if "comprobante_url" not in pagos.columns:
        pagos["comprobante_url"] = ""
    if "id_promo" not in pagos.columns:
        pagos["id_promo"] = pd.Series(dtype="float")
    if "codigo_promo" not in pagos.columns:
        pagos["codigo_promo"] = ""
    if "tipo_descuento" not in pagos.columns:
        pagos["tipo_descuento"] = ""
    if "valor_descuento" not in pagos.columns:
        pagos["valor_descuento"] = 0.0
    if "monto_descuento" not in pagos.columns:
        pagos["monto_descuento"] = 0.0
    return pagos


def resolver_promocion_checkout(codigo_promo, promos, total, buscar_promocion_por_codigo, calcular_descuento_promocion, carrito=None):
    if not codigo_promo:
        return None, 0.0, None

    promo_aplicada = buscar_promocion_por_codigo(promos, codigo_promo, datetime.now().date())
    if promo_aplicada is None:
        return None, 0.0, ("El codigo promocional no es valido o no esta vigente.", "warning")

    id_producto_promo = pd.to_numeric(promo_aplicada.get("id_producto"), errors="coerce")
    subtotal_aplicable = 0.0
    if carrito is not None and pd.notna(id_producto_promo):
        id_producto_promo = int(id_producto_promo)
        for item in carrito if isinstance(carrito, list) else []:
            if int(pd.to_numeric(item.get("id_producto", 0), errors="coerce") or 0) != id_producto_promo:
                continue
            subtotal_aplicable += float(pd.to_numeric(item.get("subtotal", 0), errors="coerce") or 0)
    else:
        subtotal_aplicable = float(total)

    if subtotal_aplicable <= 0:
        return None, 0.0, ("El codigo promocional no aplica a los productos de tu carrito.", "warning")

    descuento_promo = calcular_descuento_promocion(subtotal_aplicable, promo_aplicada)
    return promo_aplicada, descuento_promo, None


def aplicar_promociones_carrito(
    carrito,
    productos,
    promos,
    obtener_mejor_promocion_por_producto_fn,
    calcular_descuento_promocion_fn,
    buscar_promocion_por_codigo_fn,
    codigo_promo="",
):
    carrito_base = carrito if isinstance(carrito, list) else []
    productos_ref = productos.copy() if isinstance(productos, pd.DataFrame) else pd.DataFrame()
    if productos_ref.empty or not carrito_base:
        return carrito_base, 0.0, 0.0, None, 0.0, None

    hoy = datetime.now().date()
    productos_ref["id_producto"] = pd.to_numeric(productos_ref.get("id_producto", 0), errors="coerce")
    productos_ref["precio"] = pd.to_numeric(productos_ref.get("precio", 0), errors="coerce").fillna(0.0)
    promos_ref = promos.copy() if isinstance(promos, pd.DataFrame) else pd.DataFrame()
    promo_codigo = None
    codigo_norm = str(codigo_promo or "").strip().upper()
    if codigo_norm:
        promo_codigo = buscar_promocion_por_codigo_fn(promos_ref, codigo_norm, hoy)
        if promo_codigo is None:
            return carrito_base, sum(float(pd.to_numeric(i.get("subtotal", 0), errors="coerce") or 0) for i in carrito_base), 0.0, None, 0.0, ("El codigo promocional no es valido o no esta vigente.", "warning")

    mejor_auto = obtener_mejor_promocion_por_producto_fn(productos_ref, promos_ref, hoy)
    total_bruto = 0.0
    total_descuento = 0.0
    promo_codigo_aplico = False
    carrito_actualizado = []

    for item in carrito_base:
        item_final = dict(item) if isinstance(item, dict) else {}
        cantidad = max(1, int(pd.to_numeric(item_final.get("cantidad", 1), errors="coerce") or 1))
        id_producto = int(pd.to_numeric(item_final.get("id_producto", 0), errors="coerce") or 0)

        if item_final.get("personalizado"):
            precio_unitario = float(pd.to_numeric(item_final.get("precio", 0), errors="coerce") or 0)
            subtotal_bruto = float(pd.to_numeric(item_final.get("subtotal", precio_unitario * cantidad), errors="coerce") or 0)
            item_final["precio"] = precio_unitario
            item_final["subtotal"] = subtotal_bruto
            item_final["subtotal_bruto"] = subtotal_bruto
            item_final["monto_descuento"] = 0.0
            carrito_actualizado.append(item_final)
            total_bruto += subtotal_bruto
            continue

        fila = productos_ref[productos_ref["id_producto"] == id_producto]
        precio_unitario = float(fila.iloc[0]["precio"]) if not fila.empty else float(pd.to_numeric(item_final.get("precio", 0), errors="coerce") or 0)
        subtotal_bruto = precio_unitario * cantidad

        promo = mejor_auto.get(id_producto)
        if promo_codigo is not None:
            id_producto_codigo = int(pd.to_numeric(promo_codigo.get("id_producto", 0), errors="coerce") or 0)
            if id_producto_codigo == id_producto:
                promo = promo_codigo
                promo_codigo_aplico = True

        descuento_unitario = calcular_descuento_promocion_fn(precio_unitario, promo) if promo else 0.0
        subtotal_descuento = min(subtotal_bruto, descuento_unitario * cantidad)
        subtotal_final = max(0.0, subtotal_bruto - subtotal_descuento)

        item_final["precio"] = precio_unitario
        item_final["subtotal"] = subtotal_final
        item_final["subtotal_bruto"] = subtotal_bruto
        item_final["monto_descuento"] = subtotal_descuento
        item_final["promo_id"] = promo.get("id_promo", "") if promo else ""
        item_final["promo_codigo"] = promo.get("codigo", "") if promo else ""
        item_final["promo_nombre"] = promo.get("nombre", "") if promo else ""
        item_final["promo_tipo_descuento"] = promo.get("tipo_descuento", "") if promo else ""
        item_final["promo_valor_descuento"] = float(pd.to_numeric(promo.get("valor_descuento", 0), errors="coerce") or 0) if promo else 0.0
        item_final["promo_fecha_fin"] = str(promo.get("fecha_fin", "") or "") if promo else ""

        carrito_actualizado.append(item_final)
        total_bruto += subtotal_bruto
        total_descuento += subtotal_descuento

    if promo_codigo is not None and not promo_codigo_aplico:
        return carrito_base, total_bruto, 0.0, None, 0.0, ("El codigo promocional no aplica a los productos de tu carrito.", "warning")

    total_final = max(0.0, total_bruto - total_descuento)
    return carrito_actualizado, total_final, total_descuento, promo_codigo, total_bruto, None


def obtener_contacto_checkout_predeterminado(normalizar_email, cargar_usuarios_df):
    telefono = str(session.get("checkout_cliente_telefono", "") or "").strip()
    direccion = str(session.get("checkout_cliente_direccion", "") or "").strip()
    usuario_email = normalizar_email(session.get("usuario", ""))

    if not usuario_email:
        return {"telefono": telefono, "direccion": direccion}

    usuarios = cargar_usuarios_df()
    if usuarios.empty:
        return {"telefono": telefono, "direccion": direccion}

    usuario = usuarios[usuarios["email"] == usuario_email]
    if usuario.empty:
        return {"telefono": telefono, "direccion": direccion}

    usuario_dict = usuario.iloc[0].to_dict()
    if not telefono:
        telefono = str(usuario_dict.get("telefono", "") or "").strip()
    if not direccion:
        direccion = str(usuario_dict.get("direccion", "") or "").strip()

    return {"telefono": telefono, "direccion": direccion}


def validar_datos_cliente_checkout(telefono, direccion):
    telefono_limpio = re.sub(r"\D", "", str(telefono or ""))
    direccion_limpia = re.sub(r"\s+", " ", str(direccion or "")).strip()

    if not telefono_limpio or not direccion_limpia:
        return None, None, (
            "Antes de finalizar tu compra debes registrar el telefono y la direccion de entrega.",
            "warning",
        )

    if len(telefono_limpio) != 10:
        return None, None, (
            "El telefono debe contener solo numeros y tener exactamente 10 digitos.",
            "warning",
        )

    return telefono_limpio, direccion_limpia, None


def guardar_contacto_checkout_usuario(telefono, direccion, normalizar_email, cargar_usuarios_df, guardar_usuarios_df):
    usuario_email = normalizar_email(session.get("usuario", ""))
    if not usuario_email:
        return

    usuarios = cargar_usuarios_df()
    if "telefono" not in usuarios.columns:
        usuarios["telefono"] = ""
    if "direccion" not in usuarios.columns:
        usuarios["direccion"] = ""

    idx = usuarios[usuarios["email"] == usuario_email].index
    if idx.empty:
        return

    usuarios.loc[idx, "telefono"] = str(telefono or "").strip()
    usuarios.loc[idx, "direccion"] = str(direccion or "").strip()
    guardar_usuarios_df(usuarios)


def validar_stock_checkout(productos, carrito):
    for item in carrito:
        if item.get("personalizado"):
            continue
        id_producto = int(item.get("id_producto", 0))
        cantidad = int(item.get("cantidad", 0))
        fila = productos[(productos["id_producto"] == id_producto) & (productos["eliminado"] == False)]
        if fila.empty:
            return (
                f'El producto "{item.get("nombre", id_producto)}" ya no esta disponible o fue retirado del catalogo.',
                "warning",
            )
        stock_actual = int(fila.iloc[0].get("stock", 0))
        if stock_actual <= 0:
            nombre = str(fila.iloc[0].get("nombre", item.get("nombre", id_producto)))
            return (f'El producto "{nombre}" esta agotado y no se puede procesar el pedido.', "warning")
        if cantidad > stock_actual:
            nombre = str(fila.iloc[0].get("nombre", item.get("nombre", id_producto)))
            return (
                f'Stock insuficiente para "{nombre}". Disponible: {stock_actual}. Ajusta la cantidad para continuar.',
                "warning",
            )
    return None


def descontar_stock_checkout(productos, carrito):
    agotados_en_compra = []
    for item in carrito:
        if item.get("personalizado"):
            continue
        id_producto = int(item.get("id_producto", 0))
        cantidad = int(item.get("cantidad", 0))
        idx = productos[productos["id_producto"] == id_producto].index[0]
        stock_anterior = int(productos.at[idx, "stock"])
        nuevo_stock = stock_anterior - cantidad
        productos.at[idx, "stock"] = nuevo_stock
        if stock_anterior > 0 and nuevo_stock == 0:
            agotados_en_compra.append(str(productos.at[idx, "nombre"]))
    return agotados_en_compra


def registrar_compra_checkout_usuario(
    carrito,
    pedidos,
    detalle_pedido,
    pagos,
    metodo_pago,
    total_final,
    promo_aplicada,
    descuento_promo,
    construir_items_detalle_desde_carrito,
    crear_pedido_y_detalle,
    resumen_promocion_desde_promo_aplicada,
    crear_pago_para_pedido,
    estado_pedido="confirmado",
    cliente_telefono="",
    cliente_direccion="",
):
    items_detalle = construir_items_detalle_desde_carrito(carrito)
    nuevo_id_pedido = crear_pedido_y_detalle(
        pedidos=pedidos,
        detalle_pedido=detalle_pedido,
        id_usuario=session.get("id_usuario", session["usuario"]),
        estado_pedido=estado_pedido,
        items_detalle=items_detalle,
        cliente_telefono=cliente_telefono,
        cliente_direccion=cliente_direccion,
    )

    resumen_promos = resumen_promocion_desde_promo_aplicada(promo_aplicada)
    if not promo_aplicada and float(descuento_promo or 0) > 0:
        resumen_promos = resumen_promocion_pago_desde_carrito(carrito)
    crear_pago_para_pedido(
        pagos=pagos,
        id_pedido=nuevo_id_pedido,
        monto=total_final,
        metodo_pago=metodo_pago,
        resumen_promos=resumen_promos,
        monto_descuento=float(descuento_promo),
        estado_pago="pendiente_comprobante" if str(metodo_pago).strip().lower() == "transferencia" else "aprobado",
    )
    return nuevo_id_pedido


def iniciar_pago_stripe_desde_carrito(
    carrito,
    codigo_promo,
    total_final,
    hash_carrito_checkout,
    stripe_estado_configuracion,
    crear_checkout_sesion_tarjeta,
    stripe_obj_get,
    stripe_checkout_guardar_creado,
    logger,
):
    ok_stripe, msg_stripe = stripe_estado_configuracion()
    if not ok_stripe:
        flash(f"El pago con tarjeta no esta disponible en este momento. Detalle: {msg_stripe}", "warning")
        return redirect(url_for("cart", metodo_pago="tarjeta", codigo_promo=codigo_promo))

    cart_hash = hash_carrito_checkout(carrito)

    try:
        stripe_session = crear_checkout_sesion_tarjeta(
            amount_total=total_final,
            success_url=url_for("pay_stripe_success", _external=True),
            cancel_url=url_for("pay_stripe_cancel", _external=True),
            customer_email=session.get("usuario", ""),
            descripcion=f"Compra NACHOHERS ({len(carrito)} item(s))",
            metadata={
                "usuario": session.get("usuario", ""),
                "codigo_promo": codigo_promo,
                "cart_hash": cart_hash,
                "total_esperado": f"{total_final:.2f}",
            },
        )
    except Exception as exc:
        logger.exception("Error creando sesion Stripe Checkout: %s", exc)
        flash("No fue posible iniciar el pago con tarjeta. Intenta de nuevo.", "danger")
        return redirect(url_for("cart", metodo_pago="tarjeta", codigo_promo=codigo_promo))

    stripe_session_id = str(stripe_obj_get(stripe_session, "id", "") or "").strip()
    stripe_session_url = str(stripe_obj_get(stripe_session, "url", "") or "").strip()
    if not stripe_session_id or not stripe_session_url:
        flash("Stripe no devolvio una sesion valida para continuar el pago.", "danger")
        return redirect(url_for("cart", metodo_pago="tarjeta", codigo_promo=codigo_promo))

    stripe_checkout_guardar_creado(
        session_id=stripe_session_id,
        usuario_email=session.get("usuario", ""),
        codigo_promo=codigo_promo,
        carrito=carrito,
        cart_hash=cart_hash,
        total_esperado=total_final,
    )
    return redirect(stripe_session_url, code=303)


def obtener_productos_agotados(productos):
    if productos.empty:
        return []

    agotados = productos[(productos["eliminado"] == False) & (productos["stock"] <= 0)].copy()
    if agotados.empty:
        return []

    agotados = agotados.sort_values(by="nombre", na_position="last")
    return agotados[["id_producto", "nombre", "stock"]].to_dict(orient="records")


def normalizar_carrito_por_stock(carrito, cargar_productos_df_fn):
    if not carrito:
        return [], []

    productos = cargar_productos_df_fn()
    if "id_producto" not in productos.columns:
        return carrito, []

    inventario = {}
    for _, row in productos.iterrows():
        if pd.isna(row["id_producto"]):
            continue
        inventario[int(row["id_producto"])] = {
            "nombre": str(row.get("nombre", "")).strip(),
            "precio": float(row.get("precio", 0.0)),
            "stock": int(row.get("stock", 0)),
            "eliminado": bool(row.get("eliminado", False)),
        }

    carrito_limpio = []
    cambios = []

    for item in carrito:
        if item.get("personalizado"):
            cantidad = max(1, int(pd.to_numeric(item.get("cantidad", 1), errors="coerce") or 1))
            precio = float(pd.to_numeric(item.get("precio", 0), errors="coerce") or 0)
            item_personalizado = item.copy()
            item_personalizado["id_producto"] = 0
            item_personalizado["cantidad"] = cantidad
            item_personalizado["precio"] = precio
            item_personalizado["subtotal"] = float(precio) * cantidad
            carrito_limpio.append(item_personalizado)
            continue

        id_producto = pd.to_numeric(item.get("id_producto"), errors="coerce")
        cantidad_item = pd.to_numeric(item.get("cantidad", 0), errors="coerce")
        if pd.isna(id_producto) or pd.isna(cantidad_item):
            continue

        id_producto = int(id_producto)
        cantidad = max(0, int(cantidad_item))
        if cantidad <= 0:
            continue

        referencia = inventario.get(id_producto)
        nombre_item = str(item.get("nombre", f"ID {id_producto}"))
        if referencia is None or referencia["eliminado"] or referencia["stock"] <= 0:
            cambios.append(f'Se removio "{nombre_item}" porque ya no tiene stock.')
            continue

        stock_actual = int(referencia["stock"])
        cantidad_final = min(cantidad, stock_actual)
        if cantidad_final < cantidad:
            cambios.append(f'Se ajusto "{nombre_item}" de {cantidad} a {cantidad_final} por stock disponible.')

        precio_final = float(referencia["precio"]) if referencia["precio"] > 0 else float(item.get("precio", 0))
        talla_item = str(item.get("talla", "")).strip()
        carrito_limpio.append(
            {
                "id_producto": id_producto,
                "nombre": referencia["nombre"] or nombre_item,
                "cantidad": cantidad_final,
                "precio": precio_final,
                "subtotal": float(precio_final) * cantidad_final,
                "talla": talla_item,
            }
        )

    return carrito_limpio, cambios


def obtener_carrito_guardado_usuario(email, normalizar_email_fn, engine, sa_module, logger=print):
    email_norm = normalizar_email_fn(email)
    if not email_norm:
        return []

    try:
        with engine.connect() as conn:
            row = conn.execute(
                sa_module.text("SELECT carrito_json FROM carrito_usuario WHERE email = :email"),
                {"email": email_norm},
            ).fetchone()
        if not row:
            return []

        carrito = json.loads(str(row[0] or "[]"))
        if isinstance(carrito, list):
            return carrito
        return []
    except Exception as exc:
        logger(f"No se pudo cargar carrito guardado para {email_norm}: {exc}")
        return []


def guardar_carrito_guardado_usuario(email, carrito, normalizar_email_fn, engine, sa_module, logger=print):
    email_norm = normalizar_email_fn(email)
    if not email_norm:
        return

    payload = carrito if isinstance(carrito, list) else []
    try:
        with engine.begin() as conn:
            conn.execute(
                sa_module.text(
                    """
                    INSERT INTO carrito_usuario (email, carrito_json, updated_at)
                    VALUES (:email, :carrito_json, NOW())
                    ON CONFLICT (email)
                    DO UPDATE SET
                        carrito_json = EXCLUDED.carrito_json,
                        updated_at = NOW()
                    """
                ),
                {
                    "email": email_norm,
                    "carrito_json": json.dumps(payload, ensure_ascii=False),
                },
            )
    except Exception as exc:
        logger(f"No se pudo guardar carrito para {email_norm}: {exc}")


def sincronizar_carrito_usuario_desde_sesion(session_obj, guardar_carrito_guardado_usuario_fn):
    if session_obj.get("rol") != "normal":
        return
    guardar_carrito_guardado_usuario_fn(session_obj.get("usuario", ""), session_obj.get("carrito", []))


def obtener_carrito_sesion_usuario(session_obj, obtener_carrito_guardado_usuario_fn):
    if session_obj.get("rol") != "normal":
        return []

    carrito_actual = session_obj.get("carrito", None)
    if not isinstance(carrito_actual, list):
        carrito_actual = obtener_carrito_guardado_usuario_fn(session_obj.get("usuario", ""))
        session_obj["carrito"] = carrito_actual
        session_obj.modified = True

    return carrito_actual


def enriquecer_carrito_con_imagenes(
    carrito,
    cargar_productos_df_fn,
    obtener_galeria_producto_fn,
    normalizar_imagen_url_fn,
):
    if not isinstance(carrito, list) or not carrito:
        return []

    productos = cargar_productos_df_fn()
    referencias = {}
    if not productos.empty:
        for _, row in productos.iterrows():
            id_producto = pd.to_numeric(row.get("id_producto"), errors="coerce")
            if pd.isna(id_producto):
                continue
            referencias[int(id_producto)] = {
                "imagen_url": str(row.get("imagen_url", "") or "").strip(),
                "descripcion": str(row.get("descripcion", "") or "").strip(),
            }

    carrito_enriquecido = []
    for item in carrito:
        item_enriquecido = dict(item) if isinstance(item, dict) else {}
        id_producto = pd.to_numeric(item_enriquecido.get("id_producto"), errors="coerce")
        if pd.isna(id_producto):
            item_enriquecido["imagen_url"] = normalizar_imagen_url_fn(item_enriquecido.get("imagen_url", ""))
            carrito_enriquecido.append(item_enriquecido)
            continue

        id_producto = int(id_producto)
        ref = referencias.get(id_producto, {})
        imagen_actual = str(item_enriquecido.get("imagen_url", "") or "").strip()
        imagen_principal = str(ref.get("imagen_url", "") or "").strip()
        galeria = obtener_galeria_producto_fn(id_producto, imagen_principal)
        imagen_final = ""
        if galeria:
            imagen_final = normalizar_imagen_url_fn(galeria[0])
        elif imagen_actual:
            imagen_final = normalizar_imagen_url_fn(imagen_actual)

        item_enriquecido["imagen_url"] = imagen_final
        if not str(item_enriquecido.get("descripcion", "") or "").strip() and ref.get("descripcion"):
            item_enriquecido["descripcion"] = ref.get("descripcion")
        carrito_enriquecido.append(item_enriquecido)

    return carrito_enriquecido


def hash_carrito_checkout(carrito):
    payload = carrito if isinstance(carrito, list) else []
    texto = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def stripe_checkout_guardar_creado(
    session_id,
    usuario_email,
    codigo_promo,
    carrito,
    cart_hash,
    total_esperado,
    normalizar_email_fn,
    engine,
    sa_module,
):
    carrito_json = "[]"
    if isinstance(carrito, list):
        carrito_json = json.dumps(carrito, ensure_ascii=False)
    with engine.begin() as conn:
        conn.execute(
            sa_module.text(
                """
                INSERT INTO stripe_checkout (
                    session_id, usuario_email, codigo_promo, carrito_json, cart_hash, total_esperado,
                    estado, id_pedido, created_at, updated_at
                )
                VALUES (
                    :session_id, :usuario_email, :codigo_promo, :carrito_json, :cart_hash, :total_esperado,
                    'creado', NULL, NOW(), NOW()
                )
                ON CONFLICT (session_id)
                DO UPDATE SET
                    usuario_email = EXCLUDED.usuario_email,
                    codigo_promo = EXCLUDED.codigo_promo,
                    carrito_json = EXCLUDED.carrito_json,
                    cart_hash = EXCLUDED.cart_hash,
                    total_esperado = EXCLUDED.total_esperado,
                    estado = 'creado',
                    id_pedido = NULL,
                    updated_at = NOW()
                """
            ),
            {
                "session_id": str(session_id or "").strip(),
                "usuario_email": normalizar_email_fn(usuario_email),
                "codigo_promo": str(codigo_promo or "").strip().upper(),
                "carrito_json": carrito_json,
                "cart_hash": str(cart_hash or "").strip(),
                "total_esperado": float(total_esperado or 0.0),
            },
        )


def stripe_checkout_obtener(session_id, engine, sa_module):
    sid = str(session_id or "").strip()
    if not sid:
        return None
    with engine.connect() as conn:
        row = conn.execute(
            sa_module.text(
                """
                SELECT session_id, usuario_email, codigo_promo, carrito_json, cart_hash,
                       total_esperado, estado, id_pedido
                FROM stripe_checkout
                WHERE session_id = :session_id
                """
            ),
            {"session_id": sid},
        ).mappings().first()
    return dict(row) if row else None


def stripe_checkout_marcar_estado(session_id, estado, engine, sa_module, id_pedido=None):
    sid = str(session_id or "").strip()
    if not sid:
        return
    with engine.begin() as conn:
        conn.execute(
            sa_module.text(
                """
                UPDATE stripe_checkout
                SET estado = :estado,
                    id_pedido = :id_pedido,
                    updated_at = NOW()
                WHERE session_id = :session_id
                """
            ),
            {
                "session_id": sid,
                "estado": str(estado or "").strip() or "creado",
                "id_pedido": id_pedido,
            },
        )


def stripe_obj_get(data, key, default=None):
    if isinstance(data, Mapping):
        return data.get(key, default)
    try:
        return data.get(key, default)
    except Exception:
        return getattr(data, key, default)


def stripe_checkout_cargar_carrito(registro_checkout):
    raw = str((registro_checkout or {}).get("carrito_json", "") or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


def obtener_usuario_por_email(email, normalizar_email_fn, cargar_usuarios_df_fn):
    email_norm = normalizar_email_fn(email)
    if not email_norm:
        return None
    usuarios = cargar_usuarios_df_fn()
    usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()
    candidatos = usuarios[usuarios["email"] == email_norm]
    if candidatos.empty:
        return None
    return candidatos.iloc[0].to_dict()


def normalizar_dataframes_admin_pedidos(pedidos, pagos, detalle, productos):
    if "id_pedido" not in pedidos.columns:
        pedidos["id_pedido"] = pd.Series(dtype="int")
    if "id_usuario" not in pedidos.columns:
        pedidos["id_usuario"] = ""
    if "fecha_pedido" not in pedidos.columns:
        pedidos["fecha_pedido"] = ""
    if "estado" not in pedidos.columns:
        pedidos["estado"] = "confirmado"
    if "cliente_telefono" not in pedidos.columns:
        pedidos["cliente_telefono"] = ""
    if "cliente_direccion" not in pedidos.columns:
        pedidos["cliente_direccion"] = ""

    if "id_pago" not in pagos.columns:
        pagos["id_pago"] = pd.Series(dtype="int")
    if "id_pedido" not in pagos.columns:
        pagos["id_pedido"] = pd.Series(dtype="int")
    if "monto" not in pagos.columns:
        pagos["monto"] = 0.0
    if "metodo_pago" not in pagos.columns:
        pagos["metodo_pago"] = ""
    if "fecha_pago" not in pagos.columns:
        pagos["fecha_pago"] = ""
    if "estado_pago" not in pagos.columns:
        pagos["estado_pago"] = ""
    if "comprobante_url" not in pagos.columns:
        pagos["comprobante_url"] = ""

    if "id_pedido" not in detalle.columns:
        detalle["id_pedido"] = pd.Series(dtype="int")
    if "id_producto" not in detalle.columns:
        detalle["id_producto"] = pd.Series(dtype="int")
    if "cantidad" not in detalle.columns:
        detalle["cantidad"] = 0
    if "subtotal" not in detalle.columns:
        detalle["subtotal"] = 0.0
    if "talla" not in detalle.columns:
        detalle["talla"] = ""

    if "id_producto" not in productos.columns:
        productos["id_producto"] = pd.Series(dtype="int")
    if "nombre" not in productos.columns:
        productos["nombre"] = ""

    pedidos["id_pedido"] = pd.to_numeric(pedidos["id_pedido"], errors="coerce")
    pagos["id_pedido"] = pd.to_numeric(pagos["id_pedido"], errors="coerce")
    pagos["id_pago"] = pd.to_numeric(pagos["id_pago"], errors="coerce")
    pagos["monto"] = pd.to_numeric(pagos["monto"], errors="coerce").fillna(0)
    detalle["id_pedido"] = pd.to_numeric(detalle["id_pedido"], errors="coerce")
    detalle["id_producto"] = pd.to_numeric(detalle["id_producto"], errors="coerce")
    detalle["cantidad"] = pd.to_numeric(detalle["cantidad"], errors="coerce").fillna(0)
    detalle["subtotal"] = pd.to_numeric(detalle["subtotal"], errors="coerce").fillna(0)
    detalle["talla"] = detalle["talla"].fillna("").astype(str).str.strip().str.upper()
    productos["id_producto"] = pd.to_numeric(productos["id_producto"], errors="coerce")

    return pedidos, pagos, detalle, productos[["id_producto", "nombre"]].copy()


def construir_mapa_usuarios(usuarios):
    usuarios_map = {}
    for _, usuario in usuarios.iterrows():
        uid = pd.to_numeric(usuario.get("id_usuario"), errors="coerce")
        if pd.notna(uid):
            usuarios_map[int(uid)] = str(usuario.get("nombre", "")).strip()
    return usuarios_map


def resolver_nombre_usuario(valor, usuarios_map):
    uid = pd.to_numeric(valor, errors="coerce")
    if pd.notna(uid):
        uid = int(uid)
        if uid in usuarios_map and usuarios_map[uid]:
            return usuarios_map[uid]
        return f"Usuario #{uid}"
    return str(valor) if str(valor).strip() else "N/A"


def construir_mapa_productos(productos):
    productos_map = {}
    for _, producto in productos.iterrows():
        pid = pd.to_numeric(producto.get("id_producto"), errors="coerce")
        if pd.notna(pid):
            productos_map[int(pid)] = str(producto.get("nombre", "")).strip()
    return productos_map


def construir_productos_por_pedido(detalle, productos_map):
    productos_por_pedido = {}

    for id_pedido, grupo in detalle.groupby("id_pedido"):
        if pd.isna(id_pedido):
            continue

        items = []
        for _, item in grupo.iterrows():
            pid = pd.to_numeric(item.get("id_producto"), errors="coerce")
            cantidad = pd.to_numeric(item.get("cantidad"), errors="coerce")
            talla = str(item.get("talla", "") or "").strip().upper()
            nombre_producto = ""

            if pd.notna(pid):
                nombre_producto = productos_map.get(int(pid), f"Producto #{int(pid)}")
            if not nombre_producto:
                nombre_producto = "Producto sin nombre"

            etiqueta_talla = f" ({talla})" if talla else ""
            nombre_con_talla = f"{nombre_producto}{etiqueta_talla}"

            if pd.notna(cantidad) and int(cantidad) > 1:
                items.append(f"{nombre_con_talla} x{int(cantidad)}")
            else:
                items.append(nombre_con_talla)

        vistos = []
        for item in items:
            if item not in vistos:
                vistos.append(item)
        productos_por_pedido[int(id_pedido)] = ", ".join(vistos) if vistos else "Sin productos"

    return productos_por_pedido


def etiqueta_metodo_pago(valor):
    metodo = str(valor or "").strip().lower()
    etiquetas = {
        "tarjeta": "Tarjeta",
        "transferencia": "Transferencia por QR",
        "efectivo": "Efectivo",
        "qr": "QR",
    }
    return etiquetas.get(metodo, metodo.replace("_", " ").title() if metodo else "")


def etiqueta_estado_pago(valor, pago_status_labels):
    estado = str(valor or "").strip().lower()
    return pago_status_labels.get(estado, estado.replace("_", " ").capitalize() if estado else "")


def construir_vista_pedidos(
    pedidos,
    pagos,
    detalle,
    usuarios,
    productos,
    etiqueta_metodo_pago_fn,
    etiqueta_estado_pago_fn,
    construir_mapa_usuarios_fn,
    construir_mapa_productos_fn,
    construir_productos_por_pedido_fn,
    resolver_nombre_usuario_fn,
):
    totales_pedido = detalle.groupby("id_pedido", as_index=False)["subtotal"].sum()
    totales_pedido = totales_pedido.rename(columns={"subtotal": "total_productos"})

    pagos_ultimos = pagos.sort_values(by="id_pago", ascending=False).drop_duplicates(subset=["id_pedido"], keep="first")
    pagos_ultimos = pagos_ultimos[["id_pedido", "monto", "metodo_pago", "fecha_pago", "estado_pago", "comprobante_url"]]

    pedidos_view = pedidos.merge(totales_pedido, on="id_pedido", how="left")
    pedidos_view = pedidos_view.merge(pagos_ultimos, on="id_pedido", how="left")
    pedidos_view["total_productos"] = pedidos_view["total_productos"].fillna(0)
    pedidos_view["monto"] = pedidos_view["monto"].fillna(0)
    pedidos_view["metodo_pago"] = pedidos_view["metodo_pago"].fillna("").astype(str).str.strip().str.lower()
    pedidos_view["estado_pago"] = pedidos_view["estado_pago"].fillna("").astype(str).str.strip().str.lower()
    pedidos_view["comprobante_url"] = pedidos_view["comprobante_url"].fillna("").astype(str).str.strip()
    pedidos_view["metodo_pago_label"] = pedidos_view["metodo_pago"].apply(etiqueta_metodo_pago_fn)
    pedidos_view["estado_pago_label"] = pedidos_view["estado_pago"].apply(etiqueta_estado_pago_fn)

    usuarios_map = construir_mapa_usuarios_fn(usuarios)
    productos_map = construir_mapa_productos_fn(productos)
    productos_por_pedido = construir_productos_por_pedido_fn(detalle, productos_map)

    pedidos_view["usuario_nombre"] = pedidos_view["id_usuario"].apply(lambda valor: resolver_nombre_usuario_fn(valor, usuarios_map))
    pedidos_view["productos_pedido"] = pedidos_view["id_pedido"].apply(
        lambda valor: productos_por_pedido.get(int(valor), "Sin productos") if pd.notna(valor) else "Sin productos"
    )
    return pedidos_view


def leer_filtros_admin_pedidos(args):
    filtros = {
        "q": str(args.get("q", "")).strip(),
        "estado": str(args.get("estado", "todos")).strip().lower(),
        "estado_pago": str(args.get("estado_pago", "todos")).strip().lower(),
        "fecha_desde": str(args.get("fecha_desde", "")).strip(),
        "fecha_hasta": str(args.get("fecha_hasta", "")).strip(),
        "page": str(args.get("page", "1")).strip(),
    }
    pago_filtros = {
        "q": str(args.get("pago_q", "")).strip(),
        "metodo": str(args.get("pago_metodo", "todos")).strip().lower(),
        "estado": str(args.get("pago_estado", "todos")).strip().lower(),
        "fecha_desde": str(args.get("pago_fecha_desde", "")).strip(),
        "fecha_hasta": str(args.get("pago_fecha_hasta", "")).strip(),
        "page": str(args.get("pago_page", "1")).strip(),
    }
    return filtros, pago_filtros


def parse_positive_int(value, default=1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, parsed)


def build_pagination_buttons(total_paginas, pagina_actual):
    if total_paginas <= 7:
        return list(range(1, total_paginas + 1))

    botones = [1]
    inicio = max(2, pagina_actual - 1)
    fin = min(total_paginas - 1, pagina_actual + 1)
    if inicio > 2:
        botones.append("...")
    botones.extend(range(inicio, fin + 1))
    if fin < total_paginas - 1:
        botones.append("...")
    botones.append(total_paginas)
    return botones


def paginar_lista(items, pagina_actual, per_page=5):
    total = len(items)
    total_paginas = max(1, (total + per_page - 1) // per_page)
    pagina_actual = min(max(1, pagina_actual), total_paginas)

    inicio = (pagina_actual - 1) * per_page
    fin = inicio + per_page
    vista = items[inicio:fin]

    paginacion = {
        "page": pagina_actual,
        "per_page": per_page,
        "total": total,
        "total_paginas": total_paginas,
        "desde": inicio + 1 if total else 0,
        "hasta": min(fin, total),
        "botones": build_pagination_buttons(total_paginas, pagina_actual),
    }
    return vista, paginacion


def estado_pedido_ui(estado, pedido_status_alias):
    estado_normalizado = str(estado or "").strip().lower() or "confirmado"
    return pedido_status_alias.get(estado_normalizado, estado_normalizado)


def etiqueta_estado_pedido(estado, pedido_status_alias, pedido_status_labels):
    estado_normalizado = str(estado or "").strip().lower() or "confirmado"
    if estado_normalizado in pedido_status_alias:
        estado_ui = pedido_status_alias[estado_normalizado]
        return pedido_status_labels.get(estado_ui, estado_ui.replace("_", " ").capitalize())
    return pedido_status_labels.get(estado_normalizado, estado_normalizado.replace("_", " ").capitalize())


def construir_pasos_estado_pedido(estado, pedido_status_alias, pedido_status_flow):
    estado_ui = estado_pedido_ui(estado, pedido_status_alias)
    flujo = [clave for clave, _ in pedido_status_flow]

    if estado_ui in {"cancelado", "pago_en_revision"}:
        return []

    try:
        indice_actual = flujo.index(estado_ui)
    except ValueError:
        indice_actual = 0

    pasos = []
    for indice, (clave, etiqueta) in enumerate(pedido_status_flow):
        if indice < indice_actual:
            estado_paso = "done"
        elif indice == indice_actual:
            estado_paso = "current"
        else:
            estado_paso = "upcoming"
        pasos.append({"key": clave, "label": etiqueta, "state": estado_paso})
    return pasos


def enriquecer_pedidos_con_tracking(
    registros,
    pedido_status_alias,
    pedido_status_labels,
    pedido_status_flow,
    pago_status_labels,
):
    pedidos_enriquecidos = []
    for pedido in registros:
        pedido_item = dict(pedido)
        estado_valor = pedido_item.get("estado", "")
        estado_pago_valor = pedido_item.get("estado_pago", "")
        metodo_pago_valor = pedido_item.get("metodo_pago", "")
        estado_original = "" if pd.isna(estado_valor) else str(estado_valor).strip().lower()
        estado_pago_original = "" if pd.isna(estado_pago_valor) else str(estado_pago_valor).strip().lower()
        metodo_pago_original = "" if pd.isna(metodo_pago_valor) else str(metodo_pago_valor).strip().lower()
        estado_original = estado_original or "confirmado"
        estado_ui = estado_pedido_ui(estado_original, pedido_status_alias)
        pedido_item["estado"] = estado_original
        pedido_item["estado_ui"] = estado_ui
        pedido_item["estado_label"] = etiqueta_estado_pedido(estado_original, pedido_status_alias, pedido_status_labels)
        pedido_item["metodo_pago"] = metodo_pago_original
        pedido_item["metodo_pago_label"] = etiqueta_metodo_pago(metodo_pago_original)
        pedido_item["estado_pago"] = estado_pago_original
        pedido_item["estado_pago_ui"] = estado_pago_original
        pedido_item["estado_pago_label"] = etiqueta_estado_pago(estado_pago_original, pago_status_labels)
        pedido_item["comprobante_url"] = (
            "" if pd.isna(pedido_item.get("comprobante_url", "")) else str(pedido_item.get("comprobante_url", "") or "").strip()
        )
        pedido_item["estado_activo"] = estado_ui not in {"entregado", "cancelado"}
        pedido_item["tracking_steps"] = construir_pasos_estado_pedido(estado_original, pedido_status_alias, pedido_status_flow)
        pedidos_enriquecidos.append(pedido_item)
    return pedidos_enriquecidos


def filtrar_y_paginar_pedidos(
    pedidos_view,
    filtros,
    pedido_status_flow,
    pedido_status_alias,
    pago_status_labels,
    per_page=10,
):
    filtros = dict(filtros)
    estados_validos = {clave for clave, _ in pedido_status_flow} | {"cancelado", "pago_en_revision"}
    estados_pago_validos = set(pago_status_labels.keys())
    if filtros.get("estado") not in estados_validos:
        filtros["estado"] = "todos"
    if filtros.get("estado_pago") not in estados_pago_validos:
        filtros["estado_pago"] = "todos"

    vista = pedidos_view.copy()
    vista["estado"] = vista["estado"].fillna("confirmado").astype(str).str.strip().str.lower()
    vista["estado_ui"] = vista["estado"].apply(lambda x: estado_pedido_ui(x, pedido_status_alias))
    vista["estado_pago"] = vista["estado_pago"].fillna("").astype(str).str.strip().str.lower()
    vista["fecha_pedido"] = vista["fecha_pedido"].fillna("").astype(str)
    vista["fecha_pedido_dt"] = pd.to_datetime(vista["fecha_pedido"], errors="coerce")
    vista["id_pedido_txt"] = vista["id_pedido"].apply(lambda valor: str(int(valor)) if pd.notna(valor) else "")

    if filtros["estado"] != "todos":
        vista = vista[vista["estado_ui"] == filtros["estado"]]
    if filtros["estado_pago"] != "todos":
        vista = vista[vista["estado_pago"] == filtros["estado_pago"]]

    fecha_desde_dt = pd.to_datetime(filtros.get("fecha_desde", ""), errors="coerce")
    if pd.notna(fecha_desde_dt):
        vista = vista[vista["fecha_pedido_dt"].dt.date >= fecha_desde_dt.date()]
    else:
        filtros["fecha_desde"] = ""

    fecha_hasta_dt = pd.to_datetime(filtros.get("fecha_hasta", ""), errors="coerce")
    if pd.notna(fecha_hasta_dt):
        vista = vista[vista["fecha_pedido_dt"].dt.date <= fecha_hasta_dt.date()]
    else:
        filtros["fecha_hasta"] = ""

    filtro_q = filtros.get("q", "")
    if filtro_q:
        texto = filtro_q.lower()
        vista = vista[
            vista["id_pedido_txt"].str.contains(texto, na=False)
            | vista["usuario_nombre"].fillna("").astype(str).str.lower().str.contains(texto, na=False)
            | vista["productos_pedido"].fillna("").astype(str).str.lower().str.contains(texto, na=False)
            | vista["fecha_pedido"].str.lower().str.contains(texto, na=False)
        ]

    vista = vista.sort_values(by="id_pedido", ascending=False, na_position="last")
    pagina_actual = parse_positive_int(filtros.get("page", 1), default=1)
    total_filtrados = int(len(vista.index))
    total_paginas = max(1, (total_filtrados + per_page - 1) // per_page)
    if pagina_actual > total_paginas:
        pagina_actual = total_paginas

    inicio = (pagina_actual - 1) * per_page
    fin = inicio + per_page
    vista = vista.iloc[inicio:fin].copy()

    filtros["page"] = pagina_actual
    paginacion = {
        "page": pagina_actual,
        "per_page": per_page,
        "total": total_filtrados,
        "total_paginas": total_paginas,
        "desde": (inicio + 1) if total_filtrados > 0 else 0,
        "hasta": min(fin, total_filtrados),
        "opciones": list(range(1, total_paginas + 1)),
        "botones": build_pagination_buttons(total_paginas, pagina_actual),
    }
    hay_filtros_activos = bool(
        filtros.get("q")
        or filtros.get("fecha_desde")
        or filtros.get("fecha_hasta")
        or filtros.get("estado") != "todos"
        or filtros.get("estado_pago") != "todos"
    )
    return vista, filtros, paginacion, hay_filtros_activos


def filtrar_y_paginar_pagos(pagos, pago_filtros, per_page=10):
    filtros = dict(pago_filtros)

    vista = pagos.copy()
    vista["metodo_pago"] = vista["metodo_pago"].fillna("").astype(str).str.strip().str.lower()
    vista["estado_pago"] = vista["estado_pago"].fillna("").astype(str).str.strip().str.lower()
    vista["fecha_pago"] = vista["fecha_pago"].fillna("").astype(str)
    vista["fecha_pago_dt"] = pd.to_datetime(vista["fecha_pago"], errors="coerce")
    vista["id_pago_txt"] = vista["id_pago"].apply(lambda valor: str(int(valor)) if pd.notna(valor) else "")
    vista["id_pedido_txt"] = vista["id_pedido"].apply(lambda valor: str(int(valor)) if pd.notna(valor) else "")
    vista["monto_txt"] = vista["monto"].apply(lambda valor: f"{float(valor):.2f}" if pd.notna(valor) else "")

    metodos_pago_opciones = sorted([m for m in vista["metodo_pago"].unique().tolist() if m])
    estados_pago_opciones = sorted([e for e in vista["estado_pago"].unique().tolist() if e])

    if filtros.get("metodo") != "todos" and filtros.get("metodo") not in metodos_pago_opciones:
        filtros["metodo"] = "todos"
    if filtros.get("estado") != "todos" and filtros.get("estado") not in estados_pago_opciones:
        filtros["estado"] = "todos"

    if filtros.get("metodo") != "todos":
        vista = vista[vista["metodo_pago"] == filtros["metodo"]]
    if filtros.get("estado") != "todos":
        vista = vista[vista["estado_pago"] == filtros["estado"]]

    pago_fecha_desde_dt = pd.to_datetime(filtros.get("fecha_desde", ""), errors="coerce")
    if pd.notna(pago_fecha_desde_dt):
        vista = vista[vista["fecha_pago_dt"].dt.date >= pago_fecha_desde_dt.date()]
    else:
        filtros["fecha_desde"] = ""

    pago_fecha_hasta_dt = pd.to_datetime(filtros.get("fecha_hasta", ""), errors="coerce")
    if pd.notna(pago_fecha_hasta_dt):
        vista = vista[vista["fecha_pago_dt"].dt.date <= pago_fecha_hasta_dt.date()]
    else:
        filtros["fecha_hasta"] = ""

    filtro_q = filtros.get("q", "")
    if filtro_q:
        pago_texto = filtro_q.lower()
        vista = vista[
            vista["id_pago_txt"].str.contains(pago_texto, na=False)
            | vista["id_pedido_txt"].str.contains(pago_texto, na=False)
            | vista["metodo_pago"].str.contains(pago_texto, na=False)
            | vista["estado_pago"].str.contains(pago_texto, na=False)
            | vista["fecha_pago"].str.lower().str.contains(pago_texto, na=False)
            | vista["monto_txt"].str.contains(pago_texto, na=False)
        ]

    vista = vista.sort_values(by="id_pago", ascending=False, na_position="last")
    pagina_actual = parse_positive_int(filtros.get("page", 1), default=1)
    total_filtrados = int(len(vista.index))
    total_paginas = max(1, (total_filtrados + per_page - 1) // per_page)
    if pagina_actual > total_paginas:
        pagina_actual = total_paginas

    inicio = (pagina_actual - 1) * per_page
    fin = inicio + per_page
    vista = vista.iloc[inicio:fin].copy()

    filtros["page"] = pagina_actual
    paginacion = {
        "page": pagina_actual,
        "per_page": per_page,
        "total": total_filtrados,
        "total_paginas": total_paginas,
        "desde": (inicio + 1) if total_filtrados > 0 else 0,
        "hasta": min(fin, total_filtrados),
        "botones": build_pagination_buttons(total_paginas, pagina_actual),
    }
    hay_filtros_activos = bool(
        filtros.get("q")
        or filtros.get("fecha_desde")
        or filtros.get("fecha_hasta")
        or filtros.get("metodo") != "todos"
        or filtros.get("estado") != "todos"
    )
    return vista, filtros, paginacion, metodos_pago_opciones, estados_pago_opciones, hay_filtros_activos


def serializar_pedidos_admin(pedidos_view):
    lista_pedidos = pedidos_view.fillna("").to_dict(orient="records")
    for pedido in lista_pedidos:
        if pedido.get("id_pedido") != "":
            pedido["id_pedido"] = int(pedido["id_pedido"])
        pedido["estado"] = str(pedido.get("estado", "confirmado")).strip().lower() or "confirmado"
        pedido["estado_pago"] = str(pedido.get("estado_pago", "")).strip().lower()
        pedido["metodo_pago"] = str(pedido.get("metodo_pago", "")).strip().lower()
        pedido["comprobante_url"] = str(pedido.get("comprobante_url", "") or "").strip()
    return lista_pedidos


def serializar_pagos_admin(pagos_view):
    lista_pagos = pagos_view.fillna("").to_dict(orient="records")
    for pago in lista_pagos:
        if pago.get("id_pago") != "":
            pago["id_pago"] = int(pago["id_pago"])
        if pago.get("id_pedido") != "":
            pago["id_pedido"] = int(pago["id_pedido"])
        pago["metodo_pago"] = str(pago.get("metodo_pago", "")).strip().lower()
        pago["estado_pago"] = str(pago.get("estado_pago", "")).strip().lower()
    return lista_pagos


def construir_params_redireccion_admin_pedidos(filtros, pago_filtros):
    params = {}

    if filtros.get("q"):
        params["q"] = filtros["q"]
    if filtros.get("estado") and filtros["estado"] != "todos":
        params["estado"] = filtros["estado"]
    if filtros.get("estado_pago") and filtros["estado_pago"] != "todos":
        params["estado_pago"] = filtros["estado_pago"]
    if filtros.get("fecha_desde"):
        params["fecha_desde"] = filtros["fecha_desde"]
    if filtros.get("fecha_hasta"):
        params["fecha_hasta"] = filtros["fecha_hasta"]

    page = parse_positive_int(filtros.get("page", 1), default=1)
    if page > 1:
        params["page"] = page

    if pago_filtros.get("q"):
        params["pago_q"] = pago_filtros["q"]
    if pago_filtros.get("metodo") and pago_filtros["metodo"] != "todos":
        params["pago_metodo"] = pago_filtros["metodo"]
    if pago_filtros.get("estado") and pago_filtros["estado"] != "todos":
        params["pago_estado"] = pago_filtros["estado"]
    if pago_filtros.get("fecha_desde"):
        params["pago_fecha_desde"] = pago_filtros["fecha_desde"]
    if pago_filtros.get("fecha_hasta"):
        params["pago_fecha_hasta"] = pago_filtros["fecha_hasta"]

    pago_page = parse_positive_int(pago_filtros.get("page", 1), default=1)
    if pago_page > 1:
        params["pago_page"] = pago_page

    return params


def redirigir_admin_pedidos_con_filtros(filtros, pago_filtros, construir_params_fn):
    params = construir_params_fn(filtros, pago_filtros)
    return redirect(url_for("admin_pedidos", **params))


def redirigir_admin_pedidos_por_origen(
    origen,
    filtros,
    pago_filtros,
    construir_params_fn,
    redirigir_con_filtros_fn,
    ajustes_page=1,
    curso_page=1,
):
    if origen == "ajustes":
        return redirect(url_for("admin_ajustes", ajustes_page=ajustes_page))
    if origen == "pedidos":
        params = construir_params_fn(filtros, pago_filtros)
        if curso_page > 1:
            params["curso_page"] = curso_page
        return redirect(url_for("admin_pedidos", **params))
    return redirigir_con_filtros_fn(filtros, pago_filtros)


def validar_cliente_pos(cliente_nombre, cliente_correo, cliente_documento, cliente_telefono, normalizar_email_fn):
    cliente_nombre = str(cliente_nombre or "").strip()
    cliente_correo = normalizar_email_fn(cliente_correo)
    cliente_documento = str(cliente_documento or "").strip()
    cliente_telefono = str(cliente_telefono or "").strip()

    if not cliente_nombre or not cliente_correo or not cliente_documento or not cliente_telefono:
        return ("Debes completar todos los datos del cliente para registrar la venta.", "warning")
    if any(not (caracter.isalpha() or caracter.isspace()) for caracter in cliente_nombre):
        return ("El nombre del cliente solo puede contener letras y espacios.", "warning")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", cliente_correo):
        return ("Debes ingresar un correo electronico valido.", "warning")
    if not cliente_documento.isdigit():
        return ("La cedula solo puede contener numeros.", "warning")
    if not cliente_telefono.isdigit() or len(cliente_telefono) > 10:
        return ("El telefono solo puede contener numeros y maximo 10 digitos.", "warning")
    return None


def normalizar_metodo_pago_pos(metodo_pago):
    metodo = str(metodo_pago or "efectivo").strip().lower()
    metodos_validos = {"efectivo", "tarjeta", "transferencia", "qr"}
    if metodo not in metodos_validos:
        return "efectivo"
    return metodo


def parsear_items_checkout_pos(items_raw):
    try:
        items = json.loads(items_raw)
    except json.JSONDecodeError:
        return None, ("No se pudo procesar el carrito POS.", "danger")

    if not isinstance(items, list) or not items:
        return None, ("Agrega al menos un producto para cobrar.", "warning")

    return items, None


def validar_y_preparar_carrito_pos(
    items,
    productos,
    mejor_promo_por_producto,
    producto_requiere_talla_fn,
    tallas_opciones,
    calcular_descuento_promocion_fn,
):
    carrito_validado = []
    total_bruto = 0.0
    total_descuento = 0.0
    total = 0.0

    for item in items:
        try:
            id_producto = int(item.get("id_producto", 0))
            cantidad = int(item.get("cantidad", 0))
        except (TypeError, ValueError):
            return None, ("Hay productos invalidos en el carrito POS.", "danger")

        if cantidad <= 0:
            return None, ("La cantidad debe ser mayor a cero.", "danger")

        idx = productos[productos["id_producto"] == id_producto].index
        if idx.empty:
            return None, (f"El producto con ID {id_producto} ya no existe.", "danger")

        row_idx = idx[0]
        if bool(productos.at[row_idx, "eliminado"]):
            return None, (f"El producto ID {id_producto} esta eliminado.", "danger")

        requiere_talla = producto_requiere_talla_fn(productos.at[row_idx, "intendencia"])
        talla = str(item.get("talla", "")).strip().upper()
        if requiere_talla:
            if talla not in tallas_opciones:
                nombre = str(productos.at[row_idx, "nombre"])
                return None, (f'Selecciona una talla valida para "{nombre}".', "warning")
        else:
            talla = ""

        stock_actual = int(pd.to_numeric(productos.at[row_idx, "stock"], errors="coerce") or 0)
        if cantidad > stock_actual:
            nombre = str(productos.at[row_idx, "nombre"])
            return None, (f'Stock insuficiente para "{nombre}". Disponible: {stock_actual}.', "warning")

        precio_base = float(pd.to_numeric(productos.at[row_idx, "precio"], errors="coerce") or 0)
        promo = mejor_promo_por_producto.get(id_producto)
        descuento_unitario = calcular_descuento_promocion_fn(precio_base, promo) if promo else 0.0

        subtotal_bruto = precio_base * cantidad
        subtotal_descuento = descuento_unitario * cantidad
        subtotal_final = max(0.0, subtotal_bruto - subtotal_descuento)

        total_bruto += subtotal_bruto
        total_descuento += subtotal_descuento
        total += subtotal_final

        productos.at[row_idx, "stock"] = stock_actual - cantidad
        carrito_validado.append(
            {
                "id_producto": id_producto,
                "cantidad": cantidad,
                "talla": talla,
                "subtotal": subtotal_final,
                "subtotal_bruto": subtotal_bruto,
                "monto_descuento": subtotal_descuento,
                "promo_id": promo.get("id_promo", "") if promo else "",
                "promo_codigo": promo.get("codigo", "") if promo else "",
                "promo_tipo_descuento": promo.get("tipo_descuento", "") if promo else "",
                "promo_valor_descuento": float(pd.to_numeric(promo.get("valor_descuento", 0), errors="coerce") or 0) if promo else 0.0,
            }
        )

    return {
        "carrito_validado": carrito_validado,
        "productos": productos,
        "total_bruto": total_bruto,
        "total_descuento": total_descuento,
        "total": total,
    }, None


def resumen_promocion_pago_desde_carrito(carrito_validado):
    promo_ids = []
    promo_codigos = []
    promo_tipos = []
    promo_valores = []
    for item in carrito_validado:
        promo_id = str(item.get("promo_id", "")).strip()
        promo_codigo = str(item.get("promo_codigo", "")).strip()
        promo_tipo = str(item.get("promo_tipo_descuento", "")).strip()
        promo_valor = float(pd.to_numeric(item.get("promo_valor_descuento", 0), errors="coerce") or 0)

        if promo_id and promo_id not in promo_ids:
            promo_ids.append(promo_id)
        if promo_codigo and promo_codigo not in promo_codigos:
            promo_codigos.append(promo_codigo)
        if promo_tipo and promo_tipo not in promo_tipos:
            promo_tipos.append(promo_tipo)
        if promo_valor and promo_valor not in promo_valores:
            promo_valores.append(promo_valor)

    if not promo_ids:
        return {"id_promo": "", "codigo_promo": "", "tipo_descuento": "", "valor_descuento": 0.0}
    if len(promo_ids) == 1:
        return {
            "id_promo": promo_ids[0],
            "codigo_promo": promo_codigos[0] if promo_codigos else "",
            "tipo_descuento": promo_tipos[0] if promo_tipos else "",
            "valor_descuento": float(promo_valores[0]) if promo_valores else 0.0,
        }
    return {"id_promo": "multi", "codigo_promo": ",".join(promo_codigos), "tipo_descuento": "multi", "valor_descuento": 0.0}


def resumen_promocion_desde_promo_aplicada(promo_aplicada):
    if not promo_aplicada:
        return {"id_promo": "", "codigo_promo": "", "tipo_descuento": "", "valor_descuento": 0.0}

    id_promo_num = pd.to_numeric(promo_aplicada.get("id_promo"), errors="coerce")
    id_promo = int(id_promo_num) if pd.notna(id_promo_num) else ""
    return {
        "id_promo": id_promo,
        "codigo_promo": promo_aplicada.get("codigo", ""),
        "tipo_descuento": promo_aplicada.get("tipo_descuento", ""),
        "valor_descuento": float(pd.to_numeric(promo_aplicada.get("valor_descuento", 0), errors="coerce") or 0.0),
    }


def construir_items_detalle_desde_carrito(carrito):
    items_detalle = []
    for item in carrito:
        items_detalle.append(
            {
                "id_producto": int(pd.to_numeric(item.get("id_producto", 0), errors="coerce") or 0),
                "cantidad": int(pd.to_numeric(item.get("cantidad", 1), errors="coerce") or 1),
                "subtotal": float(pd.to_numeric(item.get("subtotal", 0), errors="coerce") or 0),
                "talla": str(item.get("talla", "")).strip(),
            }
        )
    return items_detalle


def crear_pedido_y_detalle(
    pedidos,
    detalle_pedido,
    id_usuario,
    estado_pedido,
    items_detalle,
    next_id_fn,
    guardar_pedidos_df_fn,
    guardar_detalle_pedido_df_fn,
    cliente_telefono="",
    cliente_direccion="",
):
    nuevo_id_pedido = next_id_fn("pedidos", "id_pedido")
    nuevo_pedido = {
        "id_pedido": nuevo_id_pedido,
        "id_usuario": id_usuario,
        "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": estado_pedido,
        "cliente_telefono": str(cliente_telefono or "").strip(),
        "cliente_direccion": str(cliente_direccion or "").strip(),
    }
    pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
    guardar_pedidos_df_fn(pedidos)

    next_detalle_id = next_id_fn("detalle_pedido", "id_detalle")
    nuevos_detalles = []
    for item in items_detalle:
        nuevos_detalles.append(
            {
                "id_detalle": next_detalle_id,
                "id_pedido": nuevo_id_pedido,
                "id_producto": item["id_producto"],
                "cantidad": item["cantidad"],
                "subtotal": item["subtotal"],
                "talla": str(item.get("talla", "")).strip(),
            }
        )
        next_detalle_id += 1
    detalle_pedido = pd.concat([detalle_pedido, pd.DataFrame(nuevos_detalles)], ignore_index=True)
    guardar_detalle_pedido_df_fn(detalle_pedido)
    return nuevo_id_pedido


def crear_pago_para_pedido(
    pagos,
    id_pedido,
    monto,
    metodo_pago,
    resumen_promos,
    monto_descuento,
    next_id_fn,
    guardar_pagos_df_fn,
    estado_pago="aprobado",
):
    resumen = resumen_promos or {"id_promo": "", "codigo_promo": "", "tipo_descuento": "", "valor_descuento": 0.0}

    nuevo_id_pago = next_id_fn("pagos", "id_pago")
    nuevo_pago = {
        "id_pago": nuevo_id_pago,
        "id_pedido": id_pedido,
        "monto": monto,
        "metodo_pago": metodo_pago,
        "fecha_pago": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado_pago": str(estado_pago or "aprobado").strip().lower() or "aprobado",
        "id_promo": resumen.get("id_promo", ""),
        "codigo_promo": resumen.get("codigo_promo", ""),
        "tipo_descuento": resumen.get("tipo_descuento", ""),
        "valor_descuento": resumen.get("valor_descuento", 0.0),
        "monto_descuento": monto_descuento,
    }
    pagos = pd.concat([pagos, pd.DataFrame([nuevo_pago])], ignore_index=True)
    guardar_pagos_df_fn(pagos)
    return nuevo_id_pago


def registrar_venta_pos_admin(
    carrito_validado,
    metodo_pago,
    total,
    total_descuento,
    cargar_pedidos_df_fn,
    cargar_detalle_pedido_df_fn,
    cargar_pagos_df_fn,
    session_usuario,
    construir_items_detalle_fn,
    crear_pedido_y_detalle_fn,
    resumen_promocion_pago_fn,
    crear_pago_para_pedido_fn,
):
    pedidos = cargar_pedidos_df_fn()
    detalle_pedido = cargar_detalle_pedido_df_fn()
    pagos = cargar_pagos_df_fn()
    items_detalle = construir_items_detalle_fn(carrito_validado)
    next_pedido_id = crear_pedido_y_detalle_fn(
        pedidos=pedidos,
        detalle_pedido=detalle_pedido,
        id_usuario=session_usuario,
        estado_pedido="completado",
        items_detalle=items_detalle,
    )

    resumen_promos = resumen_promocion_pago_fn(carrito_validado)
    crear_pago_para_pedido_fn(
        pagos=pagos,
        id_pedido=next_pedido_id,
        monto=round(total, 2),
        metodo_pago=metodo_pago,
        resumen_promos={
            "id_promo": resumen_promos["id_promo"],
            "codigo_promo": resumen_promos["codigo_promo"],
            "tipo_descuento": resumen_promos["tipo_descuento"],
            "valor_descuento": round(float(pd.to_numeric(resumen_promos["valor_descuento"], errors="coerce") or 0.0), 2),
        },
        monto_descuento=round(total_descuento, 2),
    )
    return next_pedido_id
