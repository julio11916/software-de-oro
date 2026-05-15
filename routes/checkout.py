from datetime import datetime

import pandas as pd
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout")


def register_checkout_legacy_routes(app, legacy):
    """Registro incremental de rutas legacy de carrito y checkout."""

    def product_detail(id_producto):
        if session.get("rol") == "normal":
            productos = legacy.cargar_productos_activos_df()
            producto = productos[productos["id_producto"] == id_producto]

            if producto.empty:
                return "Producto no encontrado"

            producto_dict = producto.iloc[0].to_dict()
            galeria = legacy.obtener_galeria_producto(id_producto, producto_dict.get("imagen_url", ""))[: legacy.MAX_IMAGES_PER_PRODUCT]
            producto_dict["imagenes"] = galeria
            if galeria:
                producto_dict["imagen_url"] = galeria[0]
            producto_dict["requiere_talla"] = bool(legacy.producto_requiere_talla(producto_dict.get("intendencia", "")))

            carrito = legacy._obtener_carrito_sesion_usuario()
            cart_count = len(carrito)

            return render_template(
                "Usuarios/Detalle pedido/product_detail.html",
                producto=producto_dict,
                cart_count=cart_count,
                tallas_opciones=legacy.TALLAS_OPCIONES,
            )
        return "Acceso denegado"

    def add_to_cart(id_producto):
        if session.get("rol") != "normal":
            return "Acceso denegado"

        productos = legacy.cargar_productos_activos_df()

        try:
            cantidad = int(request.form.get("cantidad", 1))
        except (TypeError, ValueError):
            cantidad = 1

        if cantidad <= 0:
            flash("Cantidad inválida.", "warning")
            return redirect(url_for("user_dashboard"))

        producto_df = productos[productos["id_producto"] == id_producto]
        if producto_df.empty:
            flash("El producto no existe o ya no está disponible.", "warning")
            return redirect(url_for("user_dashboard"))

        producto = producto_df.iloc[0]
        stock_actual = int(producto.get("stock", 0))
        if stock_actual <= 0:
            flash(f'El producto "{producto["nombre"]}" está agotado.', "warning")
            return redirect(url_for("user_dashboard"))
        if cantidad > stock_actual:
            flash(f'Solo hay {stock_actual} unidad(es) disponibles de "{producto["nombre"]}".', "warning")
            return redirect(url_for("user_dashboard"))

        carrito = legacy._obtener_carrito_sesion_usuario()
        talla = str(request.form.get("talla", "")).strip().upper()
        requiere_talla = legacy.producto_requiere_talla(producto.get("intendencia", ""))
        if requiere_talla:
            if talla not in legacy.TALLAS_OPCIONES:
                flash("Selecciona una talla valida antes de agregar al carrito.", "warning")
                return redirect(url_for("product_detail", id_producto=id_producto))
        else:
            talla = ""

        galeria_producto = legacy.obtener_galeria_producto(id_producto, producto.get("imagen_url", ""))
        imagen_principal = legacy.normalizar_imagen_url(galeria_producto[0]) if galeria_producto else ""

        item_existente = next(
            (
                item
                for item in carrito
                if int(item.get("id_producto", 0)) == int(id_producto)
                and str(item.get("talla", "")).strip().upper() == talla
            ),
            None,
        )
        if item_existente:
            nueva_cantidad = int(item_existente.get("cantidad", 0)) + cantidad
            if nueva_cantidad > stock_actual:
                flash(f'No puedes agregar más de {stock_actual} unidad(es) de "{producto["nombre"]}".', "warning")
                return redirect(url_for("cart"))
            item_existente["cantidad"] = nueva_cantidad
            item_existente["subtotal"] = float(item_existente["precio"]) * nueva_cantidad
            if not str(item_existente.get("imagen_url", "") or "").strip() and imagen_principal:
                item_existente["imagen_url"] = imagen_principal
        else:
            item_carrito = {
                "id_producto": int(id_producto),
                "nombre": producto["nombre"],
                "descripcion": str(producto.get("descripcion", "") or "").strip(),
                "cantidad": cantidad,
                "precio": float(producto["precio"]),
                "subtotal": float(producto["precio"]) * cantidad,
                "talla": talla,
                "imagen_url": imagen_principal,
            }
            carrito.append(item_carrito)

        session["carrito"] = carrito
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()

        flash(f'{producto["nombre"]} agregado al carrito correctamente.', "success")

        referer = request.referrer
        if referer and "product" in referer:
            return redirect(url_for("product_detail", id_producto=id_producto))

        return redirect(url_for("user_dashboard"))

    def cart():
        if session.get("rol") == "normal":
            metodos_validos = {"tarjeta", "transferencia"}
            metodo_pago = str(request.args.get("metodo_pago", "") or "").strip().lower()
            if metodo_pago not in metodos_validos:
                metodo_pago = str(session.get("checkout_metodo_preferido", "") or "").strip().lower()
            if metodo_pago not in metodos_validos:
                metodo_pago = ""

            session["checkout_metodo_preferido"] = metodo_pago
            if "codigo_promo" in request.args:
                codigo_promo = str(request.args.get("codigo_promo", "") or "").strip().upper()
            else:
                codigo_promo = str(session.get("checkout_codigo_promo", "") or "").strip().upper()
            session["checkout_codigo_promo"] = codigo_promo

            carrito = legacy._obtener_carrito_sesion_usuario()
            carrito_enriquecido = legacy._enriquecer_carrito_con_imagenes(carrito)
            productos = legacy.cargar_productos_df()
            promos = legacy.cargar_promociones_df()
            carrito_enriquecido, total, total_descuento, _, total_bruto, error_promo = legacy._aplicar_promociones_carrito(
                carrito_enriquecido,
                productos,
                promos,
                codigo_promo,
            )
            if error_promo:
                flash(error_promo[0], error_promo[1])
                codigo_promo = ""
                session["checkout_codigo_promo"] = ""
                carrito_enriquecido, total, total_descuento, _, total_bruto, _ = legacy._aplicar_promociones_carrito(
                    carrito_enriquecido,
                    productos,
                    promos,
                    "",
                )
            if carrito_enriquecido != carrito:
                session["carrito"] = carrito_enriquecido
                session.modified = True
                legacy._sincronizar_carrito_usuario_desde_sesion()
            contacto_cliente = legacy._obtener_contacto_checkout_predeterminado()
            telefono_cliente = str(contacto_cliente.get("telefono", "") or "").strip()
            direccion_cliente = str(contacto_cliente.get("direccion", "") or "").strip()
            contacto_cliente_completo = bool(telefono_cliente and direccion_cliente)
            return render_template(
                "Usuarios/Carrito/cart.html",
                carrito=carrito_enriquecido,
                total=total,
                total_bruto=total_bruto,
                total_descuento=total_descuento,
                selected_metodo_pago=metodo_pago,
                selected_codigo_promo=codigo_promo,
                cliente_telefono=telefono_cliente,
                cliente_direccion=direccion_cliente,
                contacto_cliente_completo=contacto_cliente_completo,
            )
        return "Acceso denegado"

    def get_cart_count():
        carrito = legacy._obtener_carrito_sesion_usuario()
        count = len(carrito)
        return {"count": count}

    def remove_from_cart(index):
        if session.get("rol") == "normal":
            carrito = legacy._obtener_carrito_sesion_usuario()
            if 0 <= index < len(carrito):
                item_removido = carrito.pop(index)
                if item_removido.get("personalizado"):
                    legacy.actualizar_estado_ordenes_personalizadas_carrito([item_removido], "cancelada")
                session["carrito"] = carrito
                session.modified = True
                legacy._sincronizar_carrito_usuario_desde_sesion()
        return redirect(url_for("cart"))

    def checkout():
        if session.get("rol") == "normal":
            metodos_validos = {"transferencia"}
            metodo_pago = str(request.args.get("metodo_pago", "") or "").strip().lower()
            if metodo_pago not in metodos_validos:
                metodo_pago = "transferencia"
            if metodo_pago not in metodos_validos:
                metodo_pago = "transferencia"

            session["checkout_metodo_preferido"] = metodo_pago
            if "codigo_promo" in request.args:
                codigo_promo = str(request.args.get("codigo_promo", "") or "").strip().upper()
            else:
                codigo_promo = str(session.get("checkout_codigo_promo", "") or "").strip().upper()
            session["checkout_codigo_promo"] = codigo_promo

            carrito = legacy._obtener_carrito_sesion_usuario()
            if not carrito:
                flash("No hay productos en el carrito.", "warning")
                return redirect(url_for("cart"))

            total = sum(float(item.get("subtotal", 0)) for item in carrito)
            contacto_cliente = legacy._obtener_contacto_checkout_predeterminado()
            return render_template(
                "Usuarios/Carrito/checkout.html",
                carrito=carrito,
                total=total,
                selected_metodo_pago=metodo_pago,
                selected_codigo_promo=codigo_promo,
                cliente_telefono=contacto_cliente["telefono"],
                cliente_direccion=contacto_cliente["direccion"],
                transfer_support_email=legacy.app.config.get("TRANSFER_SUPPORT_EMAIL", ""),
                transfer_support_whatsapp=legacy.app.config.get("TRANSFER_SUPPORT_WHATSAPP", ""),
                transfer_qr_image=legacy.app.config.get("TRANSFER_QR_IMAGE", "img/qr/qr.jpeg"),
            )
        return "Acceso denegado"

    def checkout_select():
        if session.get("rol") != "normal":
            return "Acceso denegado"

        carrito = legacy._obtener_carrito_sesion_usuario()
        if not carrito:
            flash("No hay productos en el carrito.", "warning")
            return redirect(url_for("cart"))

        metodo_pago = str(request.form.get("metodo_pago", "") or "").strip().lower()
        codigo_promo = str(request.form.get("codigo_promo", "") or "").strip().upper()
        cliente_telefono_input = request.form.get("cliente_telefono", "")
        cliente_direccion_input = request.form.get("cliente_direccion", "")
        if not str(cliente_telefono_input or "").strip() or not str(cliente_direccion_input or "").strip():
            contacto_cliente = legacy._obtener_contacto_checkout_predeterminado()
            cliente_telefono_input = contacto_cliente.get("telefono", "")
            cliente_direccion_input = contacto_cliente.get("direccion", "")
        cliente_telefono, cliente_direccion, error_cliente = legacy._validar_datos_cliente_checkout(
            cliente_telefono_input,
            cliente_direccion_input,
        )
        session["checkout_cliente_telefono"] = str(cliente_telefono_input or "").strip()
        session["checkout_cliente_direccion"] = str(cliente_direccion_input or "").strip()
        metodos_validos = {"tarjeta", "transferencia"}
        if metodo_pago not in metodos_validos:
            flash("Selecciona un metodo de pago valido.", "warning")
            return redirect(url_for("cart", codigo_promo=codigo_promo))
        if error_cliente:
            flash(error_cliente[0], error_cliente[1])
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))

        session["checkout_metodo_preferido"] = metodo_pago
        session["checkout_codigo_promo"] = codigo_promo
        session["checkout_cliente_telefono"] = cliente_telefono
        session["checkout_cliente_direccion"] = cliente_direccion
        legacy._guardar_contacto_checkout_usuario(cliente_telefono, cliente_direccion)

        promos = legacy.cargar_promociones_df()
        productos = legacy.cargar_productos_df()
        if productos.empty:
            flash("No existe la base de productos.", "danger")
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))

        carrito_calculado, total_final, descuento_promo, promo_aplicada, _, error_promo = legacy._aplicar_promociones_carrito(
            carrito,
            productos,
            promos,
            codigo_promo,
        )
        if error_promo:
            flash(error_promo[0], error_promo[1])
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))
        session["carrito"] = carrito_calculado
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()

        error_stock = legacy._validar_stock_checkout(productos, carrito_calculado)
        if error_stock:
            flash(error_stock[0], error_stock[1])
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))

        if metodo_pago == "tarjeta":
            return legacy._iniciar_pago_stripe_desde_carrito(carrito_calculado, codigo_promo, total_final)

        return redirect(url_for("checkout", metodo_pago="transferencia", codigo_promo=codigo_promo))

    def pay():
        if session.get("rol") != "normal":
            return "Acceso denegado"

        carrito = legacy._obtener_carrito_sesion_usuario()
        if not carrito:
            flash("No hay productos en el carrito.", "warning")
            return redirect(url_for("cart"))

        codigo_promo = request.form.get("codigo_promo", "").strip().upper()
        metodo_pago = str(request.form.get("metodo_pago", "") or "").strip().lower()
        comprobante_transferencia = request.files.get("comprobante_transferencia")
        cliente_telefono_input = request.form.get("cliente_telefono", "")
        cliente_direccion_input = request.form.get("cliente_direccion", "")
        if not str(cliente_telefono_input or "").strip() or not str(cliente_direccion_input or "").strip():
            contacto_cliente = legacy._obtener_contacto_checkout_predeterminado()
            cliente_telefono_input = contacto_cliente.get("telefono", "")
            cliente_direccion_input = contacto_cliente.get("direccion", "")
        cliente_telefono, cliente_direccion, error_cliente = legacy._validar_datos_cliente_checkout(
            cliente_telefono_input,
            cliente_direccion_input,
        )
        metodos_validos = {"tarjeta", "transferencia", "efectivo"}
        session["checkout_metodo_preferido"] = metodo_pago if metodo_pago in metodos_validos else ""
        session["checkout_codigo_promo"] = codigo_promo
        session["checkout_cliente_telefono"] = str(cliente_telefono_input or "").strip()
        session["checkout_cliente_direccion"] = str(cliente_direccion_input or "").strip()
        if error_cliente:
            flash(error_cliente[0], error_cliente[1])
            return redirect(url_for("checkout", metodo_pago="transferencia", codigo_promo=codigo_promo))
        session["checkout_cliente_telefono"] = cliente_telefono
        session["checkout_cliente_direccion"] = cliente_direccion
        legacy._guardar_contacto_checkout_usuario(cliente_telefono, cliente_direccion)

        pagos = legacy.cargar_pagos_df()
        pagos = legacy._asegurar_columnas_descuento_pagos(pagos)
        pedidos = legacy.cargar_pedidos_df()
        detalle_pedido = legacy.cargar_detalle_pedido_df()

        productos = legacy.cargar_productos_df()
        if productos.empty:
            flash("No existe la base de productos.", "danger")
            return redirect(url_for("cart"))

        promos = legacy.cargar_promociones_df()
        carrito_calculado, total_final, descuento_promo, promo_aplicada, _, error_promo = legacy._aplicar_promociones_carrito(
            carrito,
            productos,
            promos,
            codigo_promo,
        )
        if error_promo:
            flash(error_promo[0], error_promo[1])
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))
        session["carrito"] = carrito_calculado
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()

        error_stock = legacy._validar_stock_checkout(productos, carrito_calculado)
        if error_stock:
            flash(error_stock[0], error_stock[1])
            return redirect(url_for("cart", metodo_pago=metodo_pago, codigo_promo=codigo_promo))

        if metodo_pago == "transferencia":
            if not comprobante_transferencia or not str(getattr(comprobante_transferencia, "filename", "")).strip():
                flash("Debes adjuntar una captura legible del comprobante para registrar la transferencia.", "warning")
                return redirect(url_for("checkout", metodo_pago="transferencia", codigo_promo=codigo_promo))

            error_comprobante = legacy.validar_archivo_imagen(comprobante_transferencia)
            if error_comprobante:
                flash(error_comprobante, "warning")
                return redirect(url_for("checkout", metodo_pago="transferencia", codigo_promo=codigo_promo))

        if metodo_pago == "tarjeta":
            return legacy._iniciar_pago_stripe_desde_carrito(carrito_calculado, codigo_promo, total_final)
        agotados_en_compra = legacy._descontar_stock_checkout(productos, carrito_calculado)
        legacy.guardar_productos_df(productos)

        nuevo_id_pedido = legacy._registrar_compra_checkout_usuario(
            carrito=carrito_calculado,
            pedidos=pedidos,
            detalle_pedido=detalle_pedido,
            pagos=pagos,
            metodo_pago=metodo_pago,
            total_final=total_final,
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
            estado_pedido="pago_en_revision" if metodo_pago == "transferencia" else "confirmado",
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
        )
        legacy.actualizar_estado_ordenes_personalizadas_carrito(
            carrito_calculado,
            "en_revision" if metodo_pago == "transferencia" else "pendiente",
        )

        legacy.registrar_actividad(
            f"Creo pedido #{nuevo_id_pedido} con {len(carrito)} producto(s) por {legacy.formatear_cop(total_final)}"
        )
        if agotados_en_compra:
            legacy.registrar_actividad("Stock agotado por pedido: " + ", ".join(agotados_en_compra))

        comprobante_adjunto = False
        if metodo_pago == "transferencia":
            comprobante_url, error_guardado = legacy.guardar_comprobante_transferencia(comprobante_transferencia, nuevo_id_pedido)
            if comprobante_url:
                pagos_actualizados = legacy.cargar_pagos_df()
                pagos_actualizados = legacy._asegurar_columnas_descuento_pagos(pagos_actualizados)
                pagos_actualizados["id_pedido_num"] = pd.to_numeric(pagos_actualizados["id_pedido"], errors="coerce")
                pagos_actualizados["id_pago_num"] = pd.to_numeric(pagos_actualizados["id_pago"], errors="coerce")
                idx_pago = pagos_actualizados[pagos_actualizados["id_pedido_num"] == nuevo_id_pedido].sort_values(
                    by="id_pago_num", ascending=False, na_position="last"
                ).index
                if not idx_pago.empty:
                    pagos_actualizados.at[idx_pago[0], "comprobante_url"] = comprobante_url
                    pagos_actualizados = pagos_actualizados.drop(columns=["id_pedido_num", "id_pago_num"])
                    legacy.guardar_pagos_df(pagos_actualizados)
                    comprobante_adjunto = True
                    notificacion_admin_ok = legacy._notificar_transferencia_admin(
                        id_pedido=nuevo_id_pedido,
                        carrito=carrito,
                        total_final=total_final,
                        cliente_telefono=cliente_telefono,
                        cliente_direccion=cliente_direccion,
                        comprobante_url=comprobante_url,
                        promo_aplicada=promo_aplicada,
                        descuento_promo=descuento_promo,
                    )
                    if notificacion_admin_ok:
                        legacy.registrar_actividad(
                            f"Notificacion de transferencia enviada al administrador para pedido #{nuevo_id_pedido}"
                        )
                    else:
                        legacy.app.logger.warning("No se pudo enviar notificacion de transferencia para pedido %s", nuevo_id_pedido)
            elif error_guardado:
                legacy.app.logger.warning("No se pudo guardar comprobante para pedido %s: %s", nuevo_id_pedido, error_guardado)
                flash(
                    "El pedido fue registrado, pero no se pudo guardar el comprobante. Contacta al administrador para completar la revision.",
                    "warning",
                )

        session["carrito"] = []
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()

        metodo_pago_nombres = {
            "tarjeta": "Tarjeta de Credito/Debito",
            "transferencia": "Transferencia por QR",
            "efectivo": "Efectivo",
            "paypal": "PayPal",
        }

        return render_template(
            "Usuarios/Carrito/order_confirmation.html",
            pedido_id=nuevo_id_pedido,
            metodo_pago=metodo_pago_nombres.get(metodo_pago, metodo_pago),
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
            total=total_final,
            promo_codigo=promo_aplicada.get("codigo", "") if promo_aplicada else None,
            descuento=descuento_promo if promo_aplicada else 0,
            confirmacion_manual=(metodo_pago == "transferencia"),
            transfer_support_email=legacy.app.config.get("TRANSFER_SUPPORT_EMAIL", ""),
            transfer_support_whatsapp=legacy.app.config.get("TRANSFER_SUPPORT_WHATSAPP", ""),
            comprobante_adjunto=comprobante_adjunto,
        )

    def pay_stripe_success():
        if session.get("rol") != "normal":
            return "Acceso denegado"

        session_id = str(request.args.get("session_id", "") or "").strip()
        if not session_id:
            flash("Stripe no envio el identificador de la sesion de pago.", "warning")
            return redirect(url_for("cart", metodo_pago="tarjeta"))

        registro = legacy._stripe_checkout_obtener(session_id)
        if not registro:
            flash("No se encontro el registro local del pago con tarjeta.", "warning")
            return redirect(url_for("cart", metodo_pago="tarjeta"))

        usuario_registro = legacy.normalizar_email(registro.get("usuario_email", ""))
        usuario_sesion = legacy.normalizar_email(session.get("usuario", ""))
        if usuario_registro and usuario_sesion and usuario_registro != usuario_sesion:
            flash("La sesion de pago no pertenece al usuario autenticado.", "danger")
            return redirect(url_for("cart", metodo_pago="tarjeta"))

        estado_actual = str(registro.get("estado", "") or "").strip().lower()
        id_pedido_existente = pd.to_numeric(registro.get("id_pedido"), errors="coerce")
        if estado_actual == "pagado" and pd.notna(id_pedido_existente):
            flash(f"El pago ya fue procesado en el pedido #{int(id_pedido_existente)}.", "info")
            return redirect(url_for("user_orders"))

        try:
            stripe_session = legacy.obtener_checkout_sesion(session_id)
        except Exception as exc:
            legacy.app.logger.exception("Error validando sesion Stripe %s: %s", session_id, exc)
            flash("No se pudo validar el pago con Stripe. Intenta nuevamente en unos segundos.", "danger")
            return redirect(url_for("cart", metodo_pago="tarjeta"))

        payment_status = str(legacy._stripe_obj_get(stripe_session, "payment_status", "") or "").strip().lower()
        if payment_status != "paid":
            legacy._stripe_checkout_marcar_estado(session_id, "pendiente")
            flash("El pago aun no aparece como confirmado por Stripe.", "warning")
            return redirect(url_for("cart", metodo_pago="tarjeta"))

        carrito_checkout = legacy._stripe_checkout_cargar_carrito(registro)
        if not carrito_checkout:
            carrito_checkout = legacy._obtener_carrito_sesion_usuario()
        if not carrito_checkout:
            legacy._stripe_checkout_marcar_estado(session_id, "pagado_sin_carrito")
            flash(
                "El pago se confirmo, pero no se encontro el carrito asociado. Contacta al administrador con el id de sesion.",
                "danger",
            )
            return redirect(url_for("user_orders"))

        hash_registrado = str(registro.get("cart_hash", "") or "").strip()
        hash_actual = legacy._hash_carrito_checkout(carrito_checkout)
        if hash_registrado and hash_registrado != hash_actual:
            legacy.app.logger.warning(
                "Diferencia de hash de carrito en Stripe session %s (registro=%s, actual=%s)",
                session_id,
                hash_registrado,
                hash_actual,
            )

        subtotal_checkout = sum(float(item.get("subtotal", 0)) for item in carrito_checkout)
        total_esperado = float(pd.to_numeric(registro.get("total_esperado", 0), errors="coerce") or 0.0)
        total_final = round(total_esperado if total_esperado > 0 else subtotal_checkout, 2)
        descuento_promo = round(max(0.0, float(subtotal_checkout) - float(total_final)), 2)
        contacto_cliente = legacy._obtener_contacto_checkout_predeterminado()
        cliente_telefono, cliente_direccion, error_cliente = legacy._validar_datos_cliente_checkout(
            contacto_cliente.get("telefono", ""),
            contacto_cliente.get("direccion", ""),
        )
        if error_cliente:
            legacy.app.logger.warning(
                "Pedido Stripe %s confirmado sin datos completos del cliente. telefono=%r direccion=%r",
                session_id,
                contacto_cliente.get("telefono", ""),
                contacto_cliente.get("direccion", ""),
            )
            cliente_telefono = str(contacto_cliente.get("telefono", "") or "").strip()
            cliente_direccion = str(contacto_cliente.get("direccion", "") or "").strip()

        codigo_promo = str(registro.get("codigo_promo", "") or "").strip().upper()
        promo_aplicada = None
        if codigo_promo:
            promos = legacy.cargar_promociones_df()
            promo_aplicada = legacy.buscar_promocion_por_codigo(promos, codigo_promo, datetime.now().date())
            if promo_aplicada is None:
                promo_aplicada = {
                    "id_promo": "",
                    "codigo": codigo_promo,
                    "tipo_descuento": "",
                    "valor_descuento": 0.0,
                }

        productos = legacy.cargar_productos_df()
        pedidos = legacy.cargar_pedidos_df()
        detalle_pedido = legacy.cargar_detalle_pedido_df()
        pagos = legacy._asegurar_columnas_descuento_pagos(legacy.cargar_pagos_df())

        estado_pedido = "confirmado"
        agotados_en_compra = []
        error_stock = legacy._validar_stock_checkout(productos, carrito_checkout)
        if error_stock:
            estado_pedido = "pendiente_revision"
            legacy.registrar_actividad(
                f"Pago Stripe {session_id} confirmado con stock en conflicto. Pedido quedo en revision."
            )
        else:
            agotados_en_compra = legacy._descontar_stock_checkout(productos, carrito_checkout)
            legacy.guardar_productos_df(productos)

        nuevo_id_pedido = legacy._registrar_compra_checkout_usuario(
            carrito=carrito_checkout,
            pedidos=pedidos,
            detalle_pedido=detalle_pedido,
            pagos=pagos,
            metodo_pago="tarjeta",
            total_final=total_final,
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
            estado_pedido=estado_pedido,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
        )
        legacy._stripe_checkout_marcar_estado(session_id, "pagado", nuevo_id_pedido)
        legacy.actualizar_estado_ordenes_personalizadas_carrito(carrito_checkout, "pendiente")
        notificacion_personalizado_ok = legacy._notificar_pago_personalizado_admin(
            id_pedido=nuevo_id_pedido,
            carrito=carrito_checkout,
            total_final=total_final,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
            metodo_pago="Tarjeta",
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
        )
        if notificacion_personalizado_ok:
            legacy.registrar_actividad(
                f"Notificacion de pago de prenda personalizada enviada al administrador para pedido #{nuevo_id_pedido}"
            )

        legacy.registrar_actividad(f"Stripe confirmado. Pedido #{nuevo_id_pedido} creado por {legacy.formatear_cop(total_final)}")
        if agotados_en_compra:
            legacy.registrar_actividad("Stock agotado por pedido: " + ", ".join(agotados_en_compra))

        session["carrito"] = []
        session.modified = True
        legacy._sincronizar_carrito_usuario_desde_sesion()

        if error_stock:
            flash(
                f"El pago se registro correctamente, pero hay cambios de stock. Tu pedido #{nuevo_id_pedido} quedo en revision.",
                "warning",
            )

        return render_template(
            "Usuarios/Carrito/order_confirmation.html",
            pedido_id=nuevo_id_pedido,
            metodo_pago="Tarjeta de Credito/Debito",
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
            total=total_final,
            promo_codigo=codigo_promo or None,
            descuento=descuento_promo if descuento_promo > 0 else 0,
            confirmacion_manual=False,
            transfer_support_email=legacy.app.config.get("TRANSFER_SUPPORT_EMAIL", ""),
            transfer_support_whatsapp=legacy.app.config.get("TRANSFER_SUPPORT_WHATSAPP", ""),
        )

    def pay_stripe_cancel():
        if session.get("rol") != "normal":
            return "Acceso denegado"
        flash("Pago con tarjeta cancelado. Tu carrito sigue guardado.", "info")
        return redirect(url_for("cart", metodo_pago="tarjeta"))

    app.add_url_rule("/product/<int:id_producto>", endpoint="product_detail", view_func=product_detail)
    app.add_url_rule("/add_to_cart/<int:id_producto>", endpoint="add_to_cart", view_func=add_to_cart, methods=["POST"])
    app.add_url_rule("/cart", endpoint="cart", view_func=cart)
    app.add_url_rule("/get_cart_count", endpoint="get_cart_count", view_func=get_cart_count)
    app.add_url_rule("/cart/remove/<int:index>", endpoint="remove_from_cart", view_func=remove_from_cart, methods=["POST"])
    app.add_url_rule("/checkout", endpoint="checkout", view_func=checkout)
    app.add_url_rule("/checkout/select", endpoint="checkout_select", view_func=checkout_select, methods=["POST"])
    app.add_url_rule("/pay", endpoint="pay", view_func=pay, methods=["POST"])
    app.add_url_rule("/pay/stripe/success", endpoint="pay_stripe_success", view_func=pay_stripe_success)
    app.add_url_rule("/pay/stripe/cancel", endpoint="pay_stripe_cancel", view_func=pay_stripe_cancel)
