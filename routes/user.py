import re
from datetime import datetime, timedelta

import pandas as pd
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

user_bp = Blueprint("user", __name__, url_prefix="/user")


def register_user_legacy_routes(app, legacy):
    """Registro incremental de rutas legacy del area de usuario."""

    def user_orders():
        if session.get("rol") != "normal":
            return "Acceso denegado"

        lista_pedidos = legacy._obtener_pedidos_usuario_actual()
        return render_template("Usuarios/Carrito/user_orders.html", pedidos=lista_pedidos)

    def user_order_details(id_pedido):
        if session.get("rol") != "normal":
            return "Acceso denegado"

        pedidos = legacy.cargar_pedidos_df().copy()
        pedidos["id_pedido_num"] = pd.to_numeric(pedidos["id_pedido"], errors="coerce")
        pedidos["id_usuario_num"] = pd.to_numeric(pedidos["id_usuario"], errors="coerce")
        id_usuario = pd.to_numeric(session.get("id_usuario"), errors="coerce")
        pedido = pedidos[(pedidos["id_pedido_num"] == id_pedido) & (pedidos["id_usuario_num"] == id_usuario)]

        if pedido.empty:
            return "Pedido no encontrado o no tienes permiso para verlo"

        pedidos_usuario = pedidos[pedidos["id_usuario_num"] == id_usuario].copy()
        pedidos_usuario = pedidos_usuario.sort_values(by="id_pedido_num", ascending=True, na_position="last").reset_index(drop=True)
        pedidos_usuario["numero_pedido_usuario"] = range(1, len(pedidos_usuario) + 1)
        pedido_numero_usuario = pedidos_usuario.loc[pedidos_usuario["id_pedido_num"] == id_pedido, "numero_pedido_usuario"]

        detalle_pedido = legacy.cargar_detalle_pedido_df()
        detalles = detalle_pedido[detalle_pedido["id_pedido"] == id_pedido]

        productos = legacy.cargar_productos_df()
        detalles = pd.merge(detalles, productos[["id_producto", "nombre", "precio"]], on="id_producto")
        if "talla" not in detalles.columns:
            detalles["talla"] = ""

        pedido_dict = pedido.iloc[0].to_dict()
        pedido_dict["numero_pedido_usuario"] = int(pedido_numero_usuario.iloc[0]) if not pedido_numero_usuario.empty else ""
        pagos = legacy.cargar_pagos_df()
        if not pagos.empty:
            pagos = pagos.copy()
            pagos["id_pedido_num"] = pd.to_numeric(pagos["id_pedido"], errors="coerce")
            pagos["id_pago_num"] = pd.to_numeric(pagos["id_pago"], errors="coerce")
            pago_pedido = pagos[pagos["id_pedido_num"] == id_pedido].sort_values(by="id_pago_num", ascending=False, na_position="last")
            if not pago_pedido.empty:
                pago_info = pago_pedido.iloc[0].to_dict()
                pedido_dict["monto"] = pago_info.get("monto", "")
                pedido_dict["metodo_pago"] = pago_info.get("metodo_pago", "")
                pedido_dict["estado_pago"] = pago_info.get("estado_pago", "")
                pedido_dict["comprobante_url"] = pago_info.get("comprobante_url", "")

        pedido_info = legacy._enriquecer_pedidos_con_tracking([pedido_dict])[0]

        return render_template(
            "Usuarios/Informacion compras pedido/user_order_details.html",
            pedido=pedido_info,
            detalles=detalles.to_dict(orient="records"),
        )

    def user_profile():
        if session.get("rol") != "normal":
            return "Acceso denegado"

        usuarios = legacy.cargar_usuarios_df()
        usuario_email = session.get("usuario")
        usuario = usuarios[usuarios["email"] == usuario_email]

        if usuario.empty:
            return "Usuario no encontrado"

        usuario_dict = usuario.iloc[0].to_dict()
        if "telefono" not in usuario_dict:
            usuario_dict["telefono"] = ""
        if "direccion" not in usuario_dict:
            usuario_dict["direccion"] = ""
        if "email_verified" not in usuario_dict:
            usuario_dict["email_verified"] = False

        config_defaults = {
            "notif_email": True,
            "notif_pedidos": True,
            "notif_promociones": True,
            "idioma": "es",
            "moneda": "COP",
        }
        for key, default_value in config_defaults.items():
            if key not in usuario_dict or pd.isna(usuario_dict[key]):
                usuario_dict[key] = default_value

        pedidos_usuario = legacy._obtener_pedidos_usuario_actual()
        pedidos_total = len(pedidos_usuario)
        montos_usuario = pd.to_numeric(pd.Series([pedido.get("monto", 0) for pedido in pedidos_usuario]), errors="coerce").fillna(0)
        gasto_total = float(montos_usuario.sum()) if not montos_usuario.empty else 0.0
        pedidos_recientes = pedidos_usuario[:3]
        ultimo_pedido = pedidos_recientes[0] if pedidos_recientes else None
        pedidos_activos = sum(1 for pedido in pedidos_usuario if pedido.get("estado_activo"))

        return render_template(
            "Usuarios/Ajustes/user_profile.html",
            usuario=usuario_dict,
            pedidos_total=pedidos_total,
            gasto_total=gasto_total,
            pedidos_recientes=pedidos_recientes,
            ultimo_pedido=ultimo_pedido,
            pedidos_activos=pedidos_activos,
            PASSWORD_CHANGE_CODE_EXP_MINUTES=legacy.PASSWORD_CHANGE_CODE_EXP_MINUTES,
        )

    def update_profile():
        if session.get("rol") != "normal":
            flash("Acceso denegado", "danger")
            return redirect(url_for("home"))

        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono", "")
        direccion = request.form.get("direccion", "")

        usuarios = legacy.cargar_usuarios_df()
        usuario_email = session.get("usuario")
        if "telefono" not in usuarios.columns:
            usuarios["telefono"] = ""
        if "direccion" not in usuarios.columns:
            usuarios["direccion"] = ""

        idx = usuarios[usuarios["email"] == usuario_email].index
        if not idx.empty:
            usuarios.loc[idx, "nombre"] = nombre
            usuarios.loc[idx, "telefono"] = telefono
            usuarios.loc[idx, "direccion"] = direccion
            legacy.guardar_usuarios_df(usuarios)
            legacy.registrar_actividad(f"Usuario {usuario_email} actualizo su perfil")
            flash("Perfil actualizado correctamente", "success")
        else:
            flash("Error al actualizar el perfil", "danger")

        return redirect(url_for("user_profile"))

    def send_password_change_code():
        if session.get("rol") != "normal":
            return jsonify({"success": False, "message": "Acceso denegado"}), 403

        try:
            usuarios = legacy.cargar_usuarios_df()
            usuarios = legacy.asegurar_columnas_cambio_password(usuarios)
            usuario_email = legacy.normalizar_email(session.get("usuario", ""))
            usuario_idx = usuarios[usuarios["email"] == usuario_email].index
            if usuario_idx.empty:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

            codigo = legacy.generar_codigo_verificacion()
            expiry = datetime.now() + timedelta(minutes=legacy.PASSWORD_CHANGE_CODE_EXP_MINUTES)
            usuarios.loc[usuario_idx, "password_change_code"] = str(codigo)
            usuarios.loc[usuario_idx, "password_change_code_expiry"] = expiry.strftime("%Y-%m-%d %H:%M:%S")
            legacy.guardar_usuarios_df(usuarios)

            envio_ok = legacy.enviar_codigo_verificacion(
                usuario_email,
                codigo,
                tipo="autenticacion",
                minutos_expiracion=legacy.PASSWORD_CHANGE_CODE_EXP_MINUTES,
            )
            if not envio_ok:
                legacy.limpiar_codigo_cambio_password(usuarios, usuario_idx[0])
                legacy.guardar_usuarios_df(usuarios)
                return jsonify({"success": False, "message": "No fue posible enviar el código al correo. Intenta nuevamente."}), 500

            legacy.registrar_actividad(f"Código de cambio de contraseña enviado a {usuario_email}")
            return jsonify(
                {
                    "success": True,
                    "message": f"Código enviado a {usuario_email}. Es válido por {legacy.PASSWORD_CHANGE_CODE_EXP_MINUTES} minutos.",
                }
            )
        except Exception:
            app.logger.exception("Error enviando código de cambio de contraseña")
            return jsonify({"success": False, "message": "Error interno enviando el código."}), 500

    def verify_password_change_code():
        if session.get("rol") != "normal":
            return jsonify({"success": False, "message": "Acceso denegado"}), 403

        try:
            payload = request.get_json(silent=True) or {}
            codigo_ingresado = str(payload.get("code", "") or "").strip()
            if not re.fullmatch(r"\d{6}", codigo_ingresado):
                return jsonify({"success": False, "message": "El código debe tener 6 dígitos numéricos."}), 400

            usuarios = legacy.cargar_usuarios_df()
            usuarios = legacy.asegurar_columnas_cambio_password(usuarios)
            usuario_email = legacy.normalizar_email(session.get("usuario", ""))
            usuario_idx = usuarios[usuarios["email"] == usuario_email].index
            if usuario_idx.empty:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

            idx = usuario_idx[0]
            usuario = usuarios.loc[idx]
            codigo_guardado = str(usuario.get("password_change_code", "") or "").replace(".0", "").strip()
            if not codigo_guardado:
                return jsonify({"success": False, "message": "No hay un código activo. Solicita uno nuevo."}), 400

            if legacy.codigo_cambio_password_expirado(usuario):
                legacy.limpiar_codigo_cambio_password(usuarios, idx)
                legacy.guardar_usuarios_df(usuarios)
                return jsonify({"success": False, "message": "El código expiró. Solicita uno nuevo."}), 400

            if codigo_guardado != codigo_ingresado:
                return jsonify({"success": False, "message": "El código es incorrecto. Verifica e intenta nuevamente."}), 400

            return jsonify({"success": True, "message": "Código validado. Ya puedes continuar con el cambio de contraseña."})
        except Exception:
            app.logger.exception("Error verificando código de cambio de contraseña")
            return jsonify({"success": False, "message": "Error interno verificando el código."}), 500

    def change_password():
        if session.get("rol") != "normal":
            flash("Acceso denegado", "danger")
            return redirect(url_for("home"))

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        password_change_code = request.form.get("password_change_code", "").strip()

        if not password_change_code:
            flash("Debes ingresar el código de seguridad enviado a tu correo.", "danger")
            return redirect(url_for("user_profile"))
        if not re.fullmatch(r"\d{6}", password_change_code):
            flash("El código de seguridad debe tener 6 dígitos numéricos.", "danger")
            return redirect(url_for("user_profile"))
        if not current_password or not new_password:
            flash("Debes completar todos los campos para cambiar la contraseña.", "danger")
            return redirect(url_for("user_profile"))
        if not legacy.password_cumple_estandares(new_password):
            flash(
                "La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial.",
                "danger",
            )
            return redirect(url_for("user_profile"))
        if current_password == new_password:
            flash("La nueva contraseña debe ser diferente a la actual.", "warning")
            return redirect(url_for("user_profile"))

        usuarios = legacy.cargar_usuarios_df()
        usuarios = legacy.asegurar_columnas_cambio_password(usuarios)
        usuario_email = legacy.normalizar_email(session.get("usuario", ""))
        usuario_idx = usuarios[usuarios["email"] == usuario_email].index
        if usuario_idx.empty:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("user_profile"))

        idx = usuario_idx[0]
        usuario = usuarios.loc[idx]
        codigo_guardado = str(usuario.get("password_change_code", "") or "").replace(".0", "").strip()
        if not codigo_guardado:
            flash("No hay un código activo. Solicita uno nuevo antes de cambiar la contraseña.", "warning")
            return redirect(url_for("user_profile"))
        if legacy.codigo_cambio_password_expirado(usuario):
            legacy.limpiar_codigo_cambio_password(usuarios, idx)
            legacy.guardar_usuarios_df(usuarios)
            flash("El código de seguridad expiró. Solicita uno nuevo.", "warning")
            return redirect(url_for("user_profile"))
        if codigo_guardado != password_change_code:
            flash("El código de seguridad es incorrecto.", "danger")
            return redirect(url_for("user_profile"))
        if not legacy.password_coincide(usuario.get("password_hash", ""), current_password):
            flash("La contraseña actual es incorrecta.", "danger")
            return redirect(url_for("user_profile"))

        usuarios.at[idx, "password_hash"] = legacy.crear_hash_password(new_password)
        usuarios.at[idx, "reset_token"] = ""
        usuarios.at[idx, "reset_token_expiry"] = ""
        legacy.limpiar_codigo_cambio_password(usuarios, idx)
        legacy.guardar_usuarios_df(usuarios)
        legacy.registrar_actividad(f"Usuario {usuario_email} cambio su contraseña con código de seguridad")
        flash("Contraseña cambiada correctamente.", "success")
        return redirect(url_for("user_profile"))

    def update_settings():
        if session.get("rol") != "normal":
            flash("Acceso denegado", "danger")
            return redirect(url_for("home"))

        notif_email = request.form.get("notif_email") == "on"
        notif_pedidos = request.form.get("notif_pedidos") == "on"
        notif_promociones = request.form.get("notif_promociones") == "on"
        idioma = request.form.get("idioma", "es")
        moneda = request.form.get("moneda", "COP")

        usuarios = legacy.cargar_usuarios_df()
        usuario_email = session.get("usuario")
        columnas_config = ["notif_email", "notif_pedidos", "notif_promociones", "idioma", "moneda"]
        for col in columnas_config:
            if col not in usuarios.columns:
                usuarios[col] = "" if col in ["idioma", "moneda"] else False

        idx = usuarios[usuarios["email"] == usuario_email].index
        if not idx.empty:
            usuarios.loc[idx, "notif_email"] = notif_email
            usuarios.loc[idx, "notif_pedidos"] = notif_pedidos
            usuarios.loc[idx, "notif_promociones"] = notif_promociones
            usuarios.loc[idx, "idioma"] = idioma
            usuarios.loc[idx, "moneda"] = moneda
            legacy.guardar_usuarios_df(usuarios)
            legacy.registrar_actividad(f"Usuario {usuario_email} actualizo sus ajustes")
            flash("Ajustes guardados correctamente", "success")
        else:
            flash("Error al guardar los ajustes", "danger")

        return redirect(url_for("user_profile"))

    def send_verification_code():
        if session.get("rol") != "normal":
            return jsonify({"success": False, "message": "Acceso denegado"}), 403
        try:
            usuarios = legacy.cargar_usuarios_df()
            usuario_email = session.get("usuario")

            if "email_verified" not in usuarios.columns:
                usuarios["email_verified"] = False
            if "verification_code" not in usuarios.columns:
                usuarios["verification_code"] = ""
            if "verification_code_expiry" not in usuarios.columns:
                usuarios["verification_code_expiry"] = ""

            usuario_idx = usuarios[usuarios["email"] == usuario_email].index
            if usuario_idx.empty:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

            codigo = legacy.generar_codigo_verificacion()
            expiry = datetime.now() + timedelta(minutes=legacy.REGISTER_CODE_EXP_MINUTES)
            usuarios.loc[usuario_idx, "verification_code"] = str(codigo)
            usuarios.loc[usuario_idx, "verification_code_expiry"] = expiry.strftime("%Y-%m-%d %H:%M:%S")
            usuarios["verification_code"] = usuarios["verification_code"].astype(str).str.replace(".0", "", regex=False).replace("nan", "")
            legacy.guardar_usuarios_df(usuarios)

            if legacy.enviar_codigo_verificacion(
                usuario_email,
                codigo,
                tipo="autenticacion",
                minutos_expiracion=legacy.REGISTER_CODE_EXP_MINUTES,
            ):
                legacy.registrar_actividad(f"Código de autenticación enviado a {usuario_email}")
                return jsonify({"success": True, "message": "Código enviado correctamente. Revisa tu correo."})

            usuarios.loc[usuario_idx, "verification_code"] = ""
            usuarios.loc[usuario_idx, "verification_code_expiry"] = ""
            legacy.guardar_usuarios_df(usuarios)
            return jsonify(
                {
                    "success": False,
                    "message": "No fue posible enviar el código de verificación al correo indicado. Verifica la configuración SMTP del sistema e intenta nuevamente.",
                }
            ), 500
        except Exception:
            app.logger.exception("Error al enviar código de verificación de correo")
            return jsonify({"success": False, "message": "Error interno enviando el código."}), 500

    def verify_email():
        if session.get("rol") != "normal":
            return jsonify({"success": False, "message": "Acceso denegado"}), 403
        try:
            payload = request.get_json(silent=True) or {}
            codigo_ingresado = str(payload.get("code", "") or "").strip()
            if not codigo_ingresado:
                return jsonify({"success": False, "message": "Debe ingresar un código"}), 400

            usuarios = legacy.cargar_usuarios_df()
            usuario_email = session.get("usuario")
            if "email_verified" not in usuarios.columns:
                usuarios["email_verified"] = False
            if "verification_code" not in usuarios.columns:
                usuarios["verification_code"] = ""
            if "verification_code_expiry" not in usuarios.columns:
                usuarios["verification_code_expiry"] = ""

            usuario_idx = usuarios[usuarios["email"] == usuario_email].index
            if usuario_idx.empty:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

            usuario = usuarios.loc[usuario_idx[0]]
            if not usuario["verification_code"]:
                return jsonify({"success": False, "message": "No hay código de verificación. Solicita uno nuevo."}), 400
            if legacy.timestamp_expirado(usuario.get("verification_code_expiry", "")):
                return jsonify({"success": False, "message": "El código ha expirado. Solicita uno nuevo."}), 400

            codigo_guardado = str(usuario["verification_code"]).replace(".0", "").strip()
            if codigo_guardado == str(codigo_ingresado):
                if not usuario["email_verified"]:
                    usuarios.loc[usuario_idx, "email_verified"] = True
                    mensaje_exito = "¡Correo verificado exitosamente!"
                    actividad = f"Usuario {usuario_email} verifico su correo electronico"
                else:
                    mensaje_exito = "¡Autenticacion exitosa!"
                    actividad = f"Usuario {usuario_email} se autentico correctamente"

                usuarios.loc[usuario_idx, "verification_code"] = ""
                usuarios.loc[usuario_idx, "verification_code_expiry"] = ""
                legacy.guardar_usuarios_df(usuarios)
                legacy.registrar_actividad(actividad)
                return jsonify({"success": True, "message": mensaje_exito})

            return jsonify({"success": False, "message": "Código incorrecto. Verifica e intenta nuevamente."}), 400
        except Exception:
            app.logger.exception("Error al verificar código de correo")
            return jsonify({"success": False, "message": "Error interno del servidor"}), 500

    def _productos_catalogo_con_promos(fuerza):
        productos = legacy.cargar_productos_activos_df()
        if productos.empty:
            return []

        productos = productos.copy()
        if "fuerza" not in productos.columns:
            productos["fuerza"] = ""
        productos["fuerza_norm"] = productos["fuerza"].astype(str).str.strip().str.lower()
        if fuerza.lower() == "accesorios":
            if "intendencia" not in productos.columns:
                productos["intendencia"] = ""
            intendencia_norm = productos["intendencia"].astype(str).str.strip().str.lower()
            productos_fuerza = productos[
                (productos["fuerza_norm"] == "accesorios") | (intendencia_norm == "accesorios")
            ].copy()
        else:
            productos_fuerza = productos[productos["fuerza_norm"] == fuerza.lower()].copy()
        if productos_fuerza.empty:
            return []

        hoy = datetime.now().date()
        promos = legacy.cargar_promociones_df()
        mejor_promo = legacy.obtener_mejor_promocion_por_producto(productos_fuerza, promos, hoy)
        lista_productos = productos_fuerza.drop(columns=["fuerza_norm"], errors="ignore").to_dict(orient="records")

        for producto in lista_productos:
            id_producto_raw = pd.to_numeric(producto.get("id_producto", 0), errors="coerce")
            id_producto = int(id_producto_raw) if pd.notna(id_producto_raw) else 0
            precio_base_raw = pd.to_numeric(producto.get("precio", 0), errors="coerce")
            precio_base = float(precio_base_raw) if pd.notna(precio_base_raw) else 0.0
            promo = mejor_promo.get(id_producto)
            producto["precio_original"] = precio_base
            producto["precio_con_descuento"] = precio_base
            producto["promo_activa"] = False
            producto["promo_nombre"] = ""
            producto["promo_etiqueta"] = ""
            producto["promo_fecha_fin"] = ""

            if promo:
                descuento = legacy.calcular_descuento_promocion(precio_base, promo)
                producto["precio_con_descuento"] = max(0.0, precio_base - descuento)
                producto["promo_activa"] = True
                producto["promo_nombre"] = str(promo.get("nombre", "") or "").strip()
                producto["promo_fecha_fin"] = str(promo.get("fecha_fin", "") or "").strip()
                if str(promo.get("tipo_descuento", "")).strip().lower() == "valor_fijo":
                    producto["promo_etiqueta"] = f"-{legacy.formatear_cop(promo.get('valor_descuento', 0))}"
                else:
                    valor_pct_raw = pd.to_numeric(promo.get("valor_descuento", 0), errors="coerce")
                    valor_pct = float(valor_pct_raw) if pd.notna(valor_pct_raw) else 0.0
                    producto["promo_etiqueta"] = f"-{valor_pct:g}%"

            galeria = legacy.obtener_galeria_producto(id_producto, producto.get("imagen_url", ""))
            if galeria:
                producto["imagen_url"] = galeria[0]

        return lista_productos

    def armada():
        productos = _productos_catalogo_con_promos("Armada")
        return render_template("Usuarios/catalogo/armada.html", productos=productos)

    def policia():
        productos = _productos_catalogo_con_promos("Policia")
        return render_template("Usuarios/catalogo/policia.html", productos=productos)

    def gaula():
        productos = _productos_catalogo_con_promos("Gaula")
        return render_template("Usuarios/catalogo/gaula.html", productos=productos)

    def variado():
        productos = _productos_catalogo_con_promos("Variado")
        return render_template("Usuarios/catalogo/variado.html", productos=productos)

    def ejercito():
        productos = _productos_catalogo_con_promos("Ejercito")
        return render_template("Usuarios/catalogo/ejercito.html", productos=productos)

    def producto_detalle(id_producto):
        productos = legacy.cargar_productos_activos_df()
        producto = productos[productos["id_producto"] == id_producto]
        if producto.empty:
            return "Producto no encontrado"

        producto_dict = producto.iloc[0].to_dict()
        promos = legacy.cargar_promociones_df()
        mejor_promo = legacy.obtener_mejor_promocion_por_producto(producto, promos, datetime.now().date())
        promo = mejor_promo.get(int(producto_dict.get("id_producto", id_producto)))
        precio_base_raw = pd.to_numeric(producto_dict.get("precio", 0), errors="coerce")
        precio_base = float(precio_base_raw) if pd.notna(precio_base_raw) else 0.0
        producto_dict["precio_original"] = precio_base
        producto_dict["precio_con_descuento"] = precio_base
        producto_dict["promo_activa"] = False
        producto_dict["promo_nombre"] = ""
        producto_dict["promo_etiqueta"] = ""
        producto_dict["promo_fecha_fin"] = ""
        if promo:
            descuento = legacy.calcular_descuento_promocion(precio_base, promo)
            producto_dict["precio_con_descuento"] = max(0.0, precio_base - descuento)
            producto_dict["promo_activa"] = True
            producto_dict["promo_nombre"] = str(promo.get("nombre", "") or "").strip()
            producto_dict["promo_fecha_fin"] = str(promo.get("fecha_fin", "") or "").strip()
            if str(promo.get("tipo_descuento", "")).strip().lower() == "valor_fijo":
                producto_dict["promo_etiqueta"] = f"-{legacy.formatear_cop(promo.get('valor_descuento', 0))}"
            else:
                valor_pct_raw = pd.to_numeric(promo.get("valor_descuento", 0), errors="coerce")
                valor_pct = float(valor_pct_raw) if pd.notna(valor_pct_raw) else 0.0
                producto_dict["promo_etiqueta"] = f"-{valor_pct:g}%"
        galeria = legacy.obtener_galeria_producto(id_producto, producto_dict.get("imagen_url", ""))[: legacy.MAX_IMAGES_PER_PRODUCT]
        producto_dict["imagenes"] = galeria
        if galeria:
            producto_dict["imagen_url"] = galeria[0]
        producto_dict["requiere_talla"] = bool(legacy.producto_requiere_talla(producto_dict.get("intendencia", "")))

        carrito = legacy._obtener_carrito_sesion_usuario() if session.get("rol") == "normal" else []
        cart_count = len(carrito)
        return render_template(
            "Usuarios/Detalle pedido/product_detail.html",
            producto=producto_dict,
            cart_count=cart_count,
            tallas_opciones=legacy.TALLAS_OPCIONES,
        )

    def accesorios():
        productos = _productos_catalogo_con_promos("Accesorios")
        return render_template("Usuarios/catalogo/accesorios.html", productos=productos)

    def sobre_nosotros():
        return render_template("Usuarios/Informacion empresa/sobre_nosotros.html")

    def home():
        contexto = legacy._construir_contexto_home()
        return render_template(
            "Usuarios/Autenticacion/login.html",
            productos=contexto["productos"],
            productos_destacados_ejercito=contexto["productos_destacados_ejercito"],
            productos_destacados_policia=contexto["productos_destacados_policia"],
            productos_destacados_armada=contexto["productos_destacados_armada"],
            productos_destacados_gaula=contexto["productos_destacados_gaula"],
            productos_destacados_variado=contexto["productos_destacados_variado"],
            productos_destacados_accesorios=contexto["productos_destacados_accesorios"],
        )

    def user_dashboard():
        if session.get("rol") != "normal":
            flash("Debes iniciar sesion como usuario para acceder al catalogo.", "warning")
            return redirect(url_for("login"))

        contexto = legacy._construir_contexto_home()
        carrito = legacy._obtener_carrito_sesion_usuario()
        cart_count = len(carrito)

        return render_template(
            "Usuarios/user_dashboard.html",
            productos=contexto["productos"],
            productos_destacados_ejercito=contexto["productos_destacados_ejercito"],
            productos_destacados_policia=contexto["productos_destacados_policia"],
            productos_destacados_armada=contexto["productos_destacados_armada"],
            productos_destacados_gaula=contexto["productos_destacados_gaula"],
            productos_destacados_variado=contexto["productos_destacados_variado"],
            productos_destacados_accesorios=contexto["productos_destacados_accesorios"],
            cart_count=cart_count,
        )

    app.add_url_rule("/", endpoint="home", view_func=home)
    app.add_url_rule("/user", endpoint="user_dashboard", view_func=user_dashboard)
    app.add_url_rule("/user/orders", endpoint="user_orders", view_func=user_orders)
    app.add_url_rule("/user/orders/details/<int:id_pedido>", endpoint="user_order_details", view_func=user_order_details)
    app.add_url_rule("/user/profile", endpoint="user_profile", view_func=user_profile)
    app.add_url_rule("/user/profile/update", endpoint="update_profile", view_func=update_profile, methods=["POST"])
    app.add_url_rule(
        "/user/profile/send-password-change-code",
        endpoint="send_password_change_code",
        view_func=send_password_change_code,
        methods=["POST"],
    )
    app.add_url_rule(
        "/user/profile/verify-password-change-code",
        endpoint="verify_password_change_code",
        view_func=verify_password_change_code,
        methods=["POST"],
    )
    app.add_url_rule("/user/profile/change-password", endpoint="change_password", view_func=change_password, methods=["POST"])
    app.add_url_rule("/user/profile/settings", endpoint="update_settings", view_func=update_settings, methods=["POST"])
    app.add_url_rule("/user/send-verification-code", endpoint="send_verification_code", view_func=send_verification_code, methods=["POST"])
    app.add_url_rule("/user/verify-email", endpoint="verify_email", view_func=verify_email, methods=["POST"])
    app.add_url_rule("/armada", endpoint="armada", view_func=armada)
    app.add_url_rule("/policia", endpoint="policia", view_func=policia)
    app.add_url_rule("/gaula", endpoint="gaula", view_func=gaula)
    app.add_url_rule("/variado", endpoint="variado", view_func=variado)
    app.add_url_rule("/ejercito", endpoint="ejercito", view_func=ejercito)
    app.add_url_rule("/producto/<int:id_producto>", endpoint="producto_detalle", view_func=producto_detalle)
    app.add_url_rule("/accesorios", endpoint="accesorios", view_func=accesorios)
    app.add_url_rule("/sobre-nosotros", endpoint="sobre_nosotros", view_func=sobre_nosotros)
