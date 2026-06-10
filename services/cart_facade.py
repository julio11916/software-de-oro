"""Fachada de wrappers legacy para carrito y Stripe checkout."""


def build_cart_legacy_bindings(
    *,
    order_service,
    session_obj,
    cargar_productos_df_fn,
    obtener_galeria_producto_fn,
    normalizar_imagen_url_fn,
    normalizar_email_fn,
    engine,
    sa_module,
):
    def obtener_productos_agotados():
        return order_service.obtener_productos_agotados(cargar_productos_df_fn())

    def normalizar_carrito_por_stock(carrito):
        return order_service.normalizar_carrito_por_stock(carrito, cargar_productos_df_fn=cargar_productos_df_fn)

    def _obtener_carrito_guardado_usuario(email):
        return order_service.obtener_carrito_guardado_usuario(
            email,
            normalizar_email_fn=normalizar_email_fn,
            engine=engine,
            sa_module=sa_module,
        )

    def _guardar_carrito_guardado_usuario(email, carrito):
        return order_service.guardar_carrito_guardado_usuario(
            email,
            carrito,
            normalizar_email_fn=normalizar_email_fn,
            engine=engine,
            sa_module=sa_module,
        )

    def _sincronizar_carrito_usuario_desde_sesion():
        return order_service.sincronizar_carrito_usuario_desde_sesion(
            session_obj=session_obj,
            guardar_carrito_guardado_usuario_fn=_guardar_carrito_guardado_usuario,
        )

    def _obtener_carrito_sesion_usuario():
        return order_service.obtener_carrito_sesion_usuario(
            session_obj=session_obj,
            obtener_carrito_guardado_usuario_fn=_obtener_carrito_guardado_usuario,
        )

    def _enriquecer_carrito_con_imagenes(carrito):
        return order_service.enriquecer_carrito_con_imagenes(
            carrito,
            cargar_productos_df_fn=cargar_productos_df_fn,
            obtener_galeria_producto_fn=obtener_galeria_producto_fn,
            normalizar_imagen_url_fn=normalizar_imagen_url_fn,
        )

    _hash_carrito_checkout = order_service.hash_carrito_checkout

    def _stripe_checkout_guardar_creado(session_id, usuario_email, codigo_promo, carrito, cart_hash, total_esperado):
        return order_service.stripe_checkout_guardar_creado(
            session_id=session_id,
            usuario_email=usuario_email,
            codigo_promo=codigo_promo,
            carrito=carrito,
            cart_hash=cart_hash,
            total_esperado=total_esperado,
            normalizar_email_fn=normalizar_email_fn,
            engine=engine,
            sa_module=sa_module,
        )

    def _stripe_checkout_obtener(session_id):
        return order_service.stripe_checkout_obtener(
            session_id=session_id,
            engine=engine,
            sa_module=sa_module,
        )

    def _stripe_checkout_marcar_estado(session_id, estado, id_pedido=None):
        return order_service.stripe_checkout_marcar_estado(
            session_id=session_id,
            estado=estado,
            id_pedido=id_pedido,
            engine=engine,
            sa_module=sa_module,
        )

    _stripe_obj_get = order_service.stripe_obj_get
    _stripe_checkout_cargar_carrito = order_service.stripe_checkout_cargar_carrito

    return {
        'obtener_productos_agotados': obtener_productos_agotados,
        'normalizar_carrito_por_stock': normalizar_carrito_por_stock,
        '_obtener_carrito_guardado_usuario': _obtener_carrito_guardado_usuario,
        '_guardar_carrito_guardado_usuario': _guardar_carrito_guardado_usuario,
        '_sincronizar_carrito_usuario_desde_sesion': _sincronizar_carrito_usuario_desde_sesion,
        '_obtener_carrito_sesion_usuario': _obtener_carrito_sesion_usuario,
        '_enriquecer_carrito_con_imagenes': _enriquecer_carrito_con_imagenes,
        '_hash_carrito_checkout': _hash_carrito_checkout,
        '_stripe_checkout_guardar_creado': _stripe_checkout_guardar_creado,
        '_stripe_checkout_obtener': _stripe_checkout_obtener,
        '_stripe_checkout_marcar_estado': _stripe_checkout_marcar_estado,
        '_stripe_obj_get': _stripe_obj_get,
        '_stripe_checkout_cargar_carrito': _stripe_checkout_cargar_carrito,
    }
