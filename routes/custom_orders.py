import json
import re

from flask import Blueprint, jsonify, render_template, request, session, url_for

custom_orders_bp = Blueprint("custom_orders", __name__, url_prefix="/orden-personalizada")


def register_custom_orders_legacy_routes(app, legacy):
    """Registro incremental de rutas legacy de orden personalizada."""

    def orden_personalizada():
        precios = legacy.precios_orden_personalizada_mapa()
        return render_template("Usuarios/orden_personalizada/orden.html", precios_personalizados=precios)

    def enviar_orden_personalizada():
        if session.get("rol") != "normal":
            return jsonify({"success": False, "message": "Debes iniciar sesión para pagar una prenda personalizada."}), 403

        payload = request.get_json(silent=True) or {}
        cliente = payload.get("cliente") or {}
        detalle = payload.get("detalle") or {}

        nombre = str(cliente.get("nombre", "")).strip()
        correo = str(cliente.get("correo", "")).strip().lower()
        telefono = re.sub(r"\D", "", str(cliente.get("telefono", "")))[:10]
        direccion = str(cliente.get("direccion", "")).strip()
        producto = legacy.producto_personalizado_canonico(detalle.get("producto", ""))
        identidad = str(detalle.get("identidad", "")).strip()
        try:
            cantidad = int(detalle.get("cantidad", 1) or 1)
        except (TypeError, ValueError):
            cantidad = 1
        cantidad = max(1, min(cantidad, 99))
        imagen_url = str(detalle.get("imagen_url", "")).strip()
        if imagen_url.startswith("data:image/"):
            imagen_guardada, error_imagen = legacy.guardar_preview_personalizado_desde_data_url(
                imagen_url,
                prefijo="gafete_preview",
            )
            if error_imagen:
                return jsonify({"success": False, "message": error_imagen}), 400
            imagen_url = imagen_guardada
        elif imagen_url and not imagen_url.startswith("/static/img/"):
            imagen_url = ""

        if not nombre or not correo or not telefono or not direccion or not producto or not identidad:
            return jsonify({"success": False, "message": "Faltan datos obligatorios para enviar la solicitud."}), 400
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            return jsonify({"success": False, "message": "El correo electrónico no es válido."}), 400
        if not re.fullmatch(r"[0-9]{10}", telefono):
            return jsonify({"success": False, "message": "El teléfono debe tener 10 dígitos."}), 400

        precios = legacy.precios_orden_personalizada_mapa()
        precio_unitario = float(precios.get(producto, 0) or 0)
        if precio_unitario <= 0:
            precio_unitario = 45000.0
        precio = precio_unitario * cantidad

        legacy.asegurar_tablas_orden_personalizada()
        datos_json = json.dumps(payload, ensure_ascii=False)
        with legacy.engine.begin() as conn:
            id_orden = conn.execute(
                legacy.sa.text(
                    """
                INSERT INTO orden_personalizada (
                    usuario_email, cliente_nombre, cliente_correo, cliente_telefono,
                    cliente_direccion, rango, fecha_contingencia, identidad, producto,
                    tecnica, color, estampado, talla, modelo_rh, modelo_presilla,
                    cantidad, imagen_url, precio, estado, datos_json
                )
                VALUES (
                    :usuario_email, :cliente_nombre, :cliente_correo, :cliente_telefono,
                    :cliente_direccion, :rango, :fecha_contingencia, :identidad, :producto,
                    :tecnica, :color, :estampado, :talla, :modelo_rh, :modelo_presilla,
                    :cantidad, :imagen_url, :precio, 'pendiente_pago', :datos_json
                )
                RETURNING id_orden_personalizada
                """
                ),
                {
                    "usuario_email": session.get("usuario", ""),
                    "cliente_nombre": nombre,
                    "cliente_correo": correo,
                    "cliente_telefono": telefono,
                    "cliente_direccion": direccion,
                    "rango": str(cliente.get("rango", "")).strip(),
                    "fecha_contingencia": str(cliente.get("fecha_contingencia", "")).strip(),
                    "identidad": identidad,
                    "producto": producto,
                    "tecnica": str(detalle.get("tecnica", "")).strip(),
                    "color": str(detalle.get("color", "")).strip(),
                    "estampado": str(detalle.get("estampado", "")).strip(),
                    "talla": str(detalle.get("talla", "")).strip(),
                    "modelo_rh": str(detalle.get("modelo_rh", "")).strip(),
                    "modelo_presilla": str(detalle.get("modelo_presilla", "")).strip(),
                    "cantidad": cantidad,
                    "imagen_url": imagen_url,
                    "precio": precio,
                    "datos_json": datos_json,
                },
            ).scalar_one()

        nombre_producto = str(detalle.get("producto_label", "") or "").strip() or producto.replace("_", " ").title()
        descripcion = " | ".join(
            parte
            for parte in [
                f"Identidad: {identidad}",
                f"Color: {str(detalle.get('color', '')).strip()}",
                f"Técnica: {str(detalle.get('tecnica', '')).strip()}",
                f"Estampado: {str(detalle.get('estampado', '')).strip()}",
                f"Rango: {str(cliente.get('rango', '')).strip()}",
                f"Fecha contingencia: {str(cliente.get('fecha_contingencia', '')).strip()}",
            ]
            if parte.split(": ", 1)[-1].strip()
        )
        imagen_carrito = imagen_url[8:] if imagen_url.startswith("/static/") else imagen_url
        carrito = legacy._obtener_carrito_sesion_usuario()
        carrito.append(
            {
                "id_producto": 0,
                "id_orden_personalizada": int(id_orden),
                "personalizado": True,
                "nombre": f"Prenda personalizada - {nombre_producto}",
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio": precio_unitario,
                "subtotal": precio,
                "talla": str(detalle.get("talla", "")).strip(),
                "imagen_url": imagen_carrito,
            }
        )
        session["carrito"] = carrito
        session["checkout_cliente_telefono"] = telefono
        session["checkout_cliente_direccion"] = direccion
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()
        legacy._guardar_contacto_checkout_usuario(telefono, direccion)

        legacy.registrar_actividad(f"Solicitud personalizada #{id_orden} agregada al carrito por {correo}")
        return jsonify(
            {
                "success": True,
                "message": "Prenda personalizada agregada al carrito.",
                "id_orden": int(id_orden),
                "redirect_url": url_for("cart"),
            }
        )

    app.add_url_rule("/orden-personalizada", endpoint="orden_personalizada", view_func=orden_personalizada)
    app.add_url_rule(
        "/orden-personalizada/enviar",
        endpoint="enviar_orden_personalizada",
        view_func=enviar_orden_personalizada,
        methods=["POST"],
    )
