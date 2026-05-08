"""Fachada de wrappers legacy para flujos de dashboard, pedidos, notificaciones y POS."""


def build_workflow_legacy_bindings(
    *,
    app_dashboard_service,
    app_mail_service,
    order_service,
    request_obj,
    session_obj,
    app_obj,
    stripe_estado_configuracion,
    crear_checkout_sesion_tarjeta,
    cargar_productos_activos_df_fn,
    cargar_promociones_df_fn,
    obtener_mejor_promocion_por_producto_fn,
    calcular_descuento_promocion_fn,
    formatear_cop_fn,
    obtener_galeria_producto_fn,
    cargar_productos_df_fn,
    guardar_productos_df_fn,
    fuerzas_opciones,
    intendencias_opciones,
    obtener_productos_agotados_fn,
    obtener_nombre_sesion_fn,
    cargar_usuarios_df_fn,
    guardar_usuarios_df_fn,
    cargar_pedidos_df_fn,
    cargar_detalle_pedido_df_fn,
    cargar_pagos_df_fn,
    pago_status_labels,
    pedido_status_alias,
    pedido_status_labels,
    pedido_status_flow,
    normalizar_email_fn,
    email_es_valido_fn,
    enviar_actualizacion_pedido_fn,
    enviar_notificacion_pago_personalizado_admin_fn,
    enviar_notificacion_transferencia_admin_fn,
    next_id_fn,
    guardar_pagos_df_fn,
    guardar_detalle_pedido_df_fn,
    guardar_pedidos_df_fn,
    tallas_opciones,
    producto_requiere_talla_fn,
    buscar_promocion_por_codigo_fn,
    hash_carrito_checkout_fn,
    stripe_obj_get_fn,
    stripe_checkout_guardar_creado_fn,
    logger_obj,
    obtener_items_personalizados_carrito_fn,
):
    def _construir_contexto_home():
        return app_dashboard_service.construir_contexto_home(
            cargar_productos_activos_df_fn(),
            cargar_promociones_df_fn(),
            obtener_mejor_promocion_por_producto_fn=obtener_mejor_promocion_por_producto_fn,
            calcular_descuento_promocion_fn=calcular_descuento_promocion_fn,
            formatear_cop_fn=formatear_cop_fn,
            obtener_galeria_producto_fn=obtener_galeria_producto_fn,
        )

    def _construir_contexto_admin_dashboard():
        return app_dashboard_service.construir_contexto_admin_dashboard(
            productos_activos=cargar_productos_activos_df_fn(),
            productos_agotados=obtener_productos_agotados_fn(),
            admin_nombre=obtener_nombre_sesion_fn(),
            usuarios_df=cargar_usuarios_df_fn(),
            pedidos_df=cargar_pedidos_df_fn(),
            detalle_df=cargar_detalle_pedido_df_fn(),
        )

    def _actualizar_destacados_dashboard():
        productos = cargar_productos_df_fn()
        if productos.empty:
            return None

        resultado = app_dashboard_service.actualizar_destacados_productos(
            productos=productos,
            ids_ejercito_raw=request_obj.form.getlist('destacados_ejercito'),
            ids_policia_raw=request_obj.form.getlist('destacados_policia'),
            ids_armada_raw=request_obj.form.getlist('destacados_armada'),
        )
        guardar_productos_df_fn(resultado['productos'])
        return resultado

    def _construir_contexto_admin_productos(busqueda, fuerza_filtro, intendencia_filtro):
        return app_dashboard_service.construir_contexto_admin_productos(
            productos_todos=cargar_productos_df_fn(),
            productos_activos=cargar_productos_activos_df_fn(),
            busqueda=busqueda,
            fuerza_filtro=fuerza_filtro,
            intendencia_filtro=intendencia_filtro,
            fuerzas_opciones=fuerzas_opciones,
            intendencias_opciones=intendencias_opciones,
            obtener_galeria_producto_fn=obtener_galeria_producto_fn,
        )

    _normalizar_dataframes_admin_pedidos = order_service.normalizar_dataframes_admin_pedidos
    _construir_mapa_usuarios = order_service.construir_mapa_usuarios
    _resolver_nombre_usuario = order_service.resolver_nombre_usuario
    _construir_mapa_productos = order_service.construir_mapa_productos
    _construir_productos_por_pedido = order_service.construir_productos_por_pedido
    _etiqueta_metodo_pago = order_service.etiqueta_metodo_pago

    def _etiqueta_estado_pago(valor):
        return order_service.etiqueta_estado_pago(valor, pago_status_labels)

    def _construir_vista_pedidos(pedidos, pagos, detalle, usuarios, productos):
        return order_service.construir_vista_pedidos(
            pedidos,
            pagos,
            detalle,
            usuarios,
            productos,
            etiqueta_metodo_pago_fn=_etiqueta_metodo_pago,
            etiqueta_estado_pago_fn=_etiqueta_estado_pago,
            construir_mapa_usuarios_fn=_construir_mapa_usuarios,
            construir_mapa_productos_fn=_construir_mapa_productos,
            construir_productos_por_pedido_fn=_construir_productos_por_pedido,
            resolver_nombre_usuario_fn=_resolver_nombre_usuario,
        )

    _leer_filtros_admin_pedidos = order_service.leer_filtros_admin_pedidos
    _parse_positive_int = order_service.parse_positive_int
    _paginar_lista = order_service.paginar_lista

    def _etiqueta_estado_pedido(estado):
        return order_service.etiqueta_estado_pedido(estado, pedido_status_alias, pedido_status_labels)

    def _enriquecer_pedidos_con_tracking(registros):
        return order_service.enriquecer_pedidos_con_tracking(
            registros,
            pedido_status_alias=pedido_status_alias,
            pedido_status_labels=pedido_status_labels,
            pedido_status_flow=pedido_status_flow,
            pago_status_labels=pago_status_labels,
        )

    def _filtrar_y_paginar_pedidos(pedidos_view, filtros, per_page=10):
        return order_service.filtrar_y_paginar_pedidos(
            pedidos_view,
            filtros,
            pedido_status_flow=pedido_status_flow,
            pedido_status_alias=pedido_status_alias,
            pago_status_labels=pago_status_labels,
            per_page=per_page,
        )

    _serializar_pedidos_admin = order_service.serializar_pedidos_admin
    _construir_params_redireccion_admin_pedidos = order_service.construir_params_redireccion_admin_pedidos

    def _redirigir_admin_pedidos_con_filtros(filtros, pago_filtros):
        return order_service.redirigir_admin_pedidos_con_filtros(
            filtros,
            pago_filtros,
            construir_params_fn=_construir_params_redireccion_admin_pedidos,
        )

    def _redirigir_admin_pedidos_por_origen(origen, filtros, pago_filtros, ajustes_page=1, curso_page=1):
        return order_service.redirigir_admin_pedidos_por_origen(
            origen=origen,
            filtros=filtros,
            pago_filtros=pago_filtros,
            construir_params_fn=_construir_params_redireccion_admin_pedidos,
            redirigir_con_filtros_fn=_redirigir_admin_pedidos_con_filtros,
            ajustes_page=ajustes_page,
            curso_page=curso_page,
        )

    def _obtener_contacto_notificacion_pedido(id_usuario):
        return app_mail_service.obtener_contacto_notificacion_pedido(
            id_usuario=id_usuario,
            cargar_usuarios_df=cargar_usuarios_df_fn,
            normalizar_email=normalizar_email_fn,
        )

    def _notificar_actualizacion_pedido_cliente(
        id_pedido,
        id_usuario,
        estado_pedido='',
        estado_pago='',
        tipo_actualizacion='pedido',
    ):
        return app_mail_service.notificar_actualizacion_pedido_cliente(
            id_pedido=id_pedido,
            id_usuario=id_usuario,
            obtener_contacto_notificacion_pedido_fn=_obtener_contacto_notificacion_pedido,
            normalizar_email=normalizar_email_fn,
            email_es_valido=email_es_valido_fn,
            enviar_actualizacion_pedido=enviar_actualizacion_pedido_fn,
            etiqueta_estado_pedido=_etiqueta_estado_pedido,
            etiqueta_estado_pago=_etiqueta_estado_pago,
            estado_pedido=estado_pedido,
            estado_pago=estado_pago,
            tipo_actualizacion=tipo_actualizacion,
        )

    _flash_resultado_notificacion_pedido = app_mail_service.flash_resultado_notificacion_pedido

    def _notificar_pago_personalizado_admin(
        id_pedido,
        carrito,
        total_final,
        cliente_telefono,
        cliente_direccion,
        metodo_pago,
        promo_aplicada=None,
        descuento_promo=0,
    ):
        return app_mail_service.notificar_pago_personalizado_admin(
            id_pedido=id_pedido,
            carrito=carrito,
            total_final=total_final,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
            metodo_pago=metodo_pago,
            app_config=app_obj.config,
            normalizar_email=normalizar_email_fn,
            email_es_valido=email_es_valido_fn,
            formatear_cop=formatear_cop_fn,
            enviar_notificacion_pago_personalizado_admin=enviar_notificacion_pago_personalizado_admin_fn,
            obtener_items_personalizados_carrito_fn=obtener_items_personalizados_carrito_fn,
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
        )

    def _notificar_transferencia_admin(
        id_pedido,
        carrito,
        total_final,
        cliente_telefono,
        cliente_direccion,
        comprobante_url,
        promo_aplicada=None,
        descuento_promo=0,
    ):
        return app_mail_service.notificar_transferencia_admin(
            id_pedido=id_pedido,
            carrito=carrito,
            total_final=total_final,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
            comprobante_url=comprobante_url,
            app_config=app_obj.config,
            app_root_path=app_obj.root_path,
            normalizar_email=normalizar_email_fn,
            email_es_valido=email_es_valido_fn,
            formatear_cop=formatear_cop_fn,
            enviar_notificacion_transferencia_admin=enviar_notificacion_transferencia_admin_fn,
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
        )

    def _validar_cliente_pos(cliente_nombre, cliente_correo, cliente_documento, cliente_telefono):
        return order_service.validar_cliente_pos(
            cliente_nombre,
            cliente_correo,
            cliente_documento,
            cliente_telefono,
            normalizar_email_fn=normalizar_email_fn,
        )

    _normalizar_metodo_pago_pos = order_service.normalizar_metodo_pago_pos
    _parsear_items_checkout_pos = order_service.parsear_items_checkout_pos

    def _validar_y_preparar_carrito_pos(items, productos, mejor_promo_por_producto):
        return order_service.validar_y_preparar_carrito_pos(
            items,
            productos,
            mejor_promo_por_producto,
            producto_requiere_talla_fn=producto_requiere_talla_fn,
            tallas_opciones=tallas_opciones,
            calcular_descuento_promocion_fn=calcular_descuento_promocion_fn,
        )

    _resumen_promocion_pago_desde_carrito = order_service.resumen_promocion_pago_desde_carrito
    _resumen_promocion_desde_promo_aplicada = order_service.resumen_promocion_desde_promo_aplicada
    _construir_items_detalle_desde_carrito = order_service.construir_items_detalle_desde_carrito

    def _crear_pedido_y_detalle(
        pedidos,
        detalle_pedido,
        id_usuario,
        estado_pedido,
        items_detalle,
        cliente_telefono='',
        cliente_direccion='',
    ):
        return order_service.crear_pedido_y_detalle(
            pedidos=pedidos,
            detalle_pedido=detalle_pedido,
            id_usuario=id_usuario,
            estado_pedido=estado_pedido,
            items_detalle=items_detalle,
            next_id_fn=next_id_fn,
            guardar_pedidos_df_fn=guardar_pedidos_df_fn,
            guardar_detalle_pedido_df_fn=guardar_detalle_pedido_df_fn,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
        )

    def _crear_pago_para_pedido(
        pagos,
        id_pedido,
        monto,
        metodo_pago,
        resumen_promos,
        monto_descuento,
        estado_pago='aprobado',
    ):
        return order_service.crear_pago_para_pedido(
            pagos=pagos,
            id_pedido=id_pedido,
            monto=monto,
            metodo_pago=metodo_pago,
            resumen_promos=resumen_promos,
            monto_descuento=monto_descuento,
            next_id_fn=next_id_fn,
            guardar_pagos_df_fn=guardar_pagos_df_fn,
            estado_pago=estado_pago,
        )

    def _registrar_venta_pos_admin(carrito_validado, metodo_pago, total, total_descuento):
        return order_service.registrar_venta_pos_admin(
            carrito_validado=carrito_validado,
            metodo_pago=metodo_pago,
            total=total,
            total_descuento=total_descuento,
            cargar_pedidos_df_fn=cargar_pedidos_df_fn,
            cargar_detalle_pedido_df_fn=cargar_detalle_pedido_df_fn,
            cargar_pagos_df_fn=cargar_pagos_df_fn,
            session_usuario=session_obj.get('usuario', 'admin_pos'),
            construir_items_detalle_fn=_construir_items_detalle_desde_carrito,
            crear_pedido_y_detalle_fn=_crear_pedido_y_detalle,
            resumen_promocion_pago_fn=_resumen_promocion_pago_desde_carrito,
            crear_pago_para_pedido_fn=_crear_pago_para_pedido,
        )

    _asegurar_columnas_descuento_pagos = order_service.asegurar_columnas_descuento_pagos

    def _resolver_promocion_checkout(codigo_promo, promos, total):
        return order_service.resolver_promocion_checkout(
            codigo_promo,
            promos,
            total,
            buscar_promocion_por_codigo=buscar_promocion_por_codigo_fn,
            calcular_descuento_promocion=calcular_descuento_promocion_fn,
        )

    def _obtener_contacto_checkout_predeterminado():
        return order_service.obtener_contacto_checkout_predeterminado(
            normalizar_email=normalizar_email_fn,
            cargar_usuarios_df=cargar_usuarios_df_fn,
        )

    _validar_datos_cliente_checkout = order_service.validar_datos_cliente_checkout

    def _guardar_contacto_checkout_usuario(telefono, direccion):
        return order_service.guardar_contacto_checkout_usuario(
            telefono,
            direccion,
            normalizar_email=normalizar_email_fn,
            cargar_usuarios_df=cargar_usuarios_df_fn,
            guardar_usuarios_df=guardar_usuarios_df_fn,
        )

    _validar_stock_checkout = order_service.validar_stock_checkout
    _descontar_stock_checkout = order_service.descontar_stock_checkout

    def _registrar_compra_checkout_usuario(
        carrito,
        pedidos,
        detalle_pedido,
        pagos,
        metodo_pago,
        total_final,
        promo_aplicada,
        descuento_promo,
        estado_pedido='confirmado',
        cliente_telefono='',
        cliente_direccion='',
    ):
        return order_service.registrar_compra_checkout_usuario(
            carrito=carrito,
            pedidos=pedidos,
            detalle_pedido=detalle_pedido,
            pagos=pagos,
            metodo_pago=metodo_pago,
            total_final=total_final,
            promo_aplicada=promo_aplicada,
            descuento_promo=descuento_promo,
            construir_items_detalle_desde_carrito=_construir_items_detalle_desde_carrito,
            crear_pedido_y_detalle=_crear_pedido_y_detalle,
            resumen_promocion_desde_promo_aplicada=_resumen_promocion_desde_promo_aplicada,
            crear_pago_para_pedido=_crear_pago_para_pedido,
            estado_pedido=estado_pedido,
            cliente_telefono=cliente_telefono,
            cliente_direccion=cliente_direccion,
        )

    def _iniciar_pago_stripe_desde_carrito(carrito, codigo_promo, total_final):
        return order_service.iniciar_pago_stripe_desde_carrito(
            carrito=carrito,
            codigo_promo=codigo_promo,
            total_final=total_final,
            hash_carrito_checkout=hash_carrito_checkout_fn,
            stripe_estado_configuracion=stripe_estado_configuracion,
            crear_checkout_sesion_tarjeta=crear_checkout_sesion_tarjeta,
            stripe_obj_get=stripe_obj_get_fn,
            stripe_checkout_guardar_creado=stripe_checkout_guardar_creado_fn,
            logger=logger_obj,
        )

    return {
        '_construir_contexto_home': _construir_contexto_home,
        '_construir_contexto_admin_dashboard': _construir_contexto_admin_dashboard,
        '_actualizar_destacados_dashboard': _actualizar_destacados_dashboard,
        '_construir_contexto_admin_productos': _construir_contexto_admin_productos,
        '_normalizar_dataframes_admin_pedidos': _normalizar_dataframes_admin_pedidos,
        '_construir_mapa_usuarios': _construir_mapa_usuarios,
        '_resolver_nombre_usuario': _resolver_nombre_usuario,
        '_construir_mapa_productos': _construir_mapa_productos,
        '_construir_productos_por_pedido': _construir_productos_por_pedido,
        '_etiqueta_metodo_pago': _etiqueta_metodo_pago,
        '_etiqueta_estado_pago': _etiqueta_estado_pago,
        '_construir_vista_pedidos': _construir_vista_pedidos,
        '_leer_filtros_admin_pedidos': _leer_filtros_admin_pedidos,
        '_parse_positive_int': _parse_positive_int,
        '_paginar_lista': _paginar_lista,
        '_etiqueta_estado_pedido': _etiqueta_estado_pedido,
        '_enriquecer_pedidos_con_tracking': _enriquecer_pedidos_con_tracking,
        '_filtrar_y_paginar_pedidos': _filtrar_y_paginar_pedidos,
        '_serializar_pedidos_admin': _serializar_pedidos_admin,
        '_construir_params_redireccion_admin_pedidos': _construir_params_redireccion_admin_pedidos,
        '_redirigir_admin_pedidos_con_filtros': _redirigir_admin_pedidos_con_filtros,
        '_redirigir_admin_pedidos_por_origen': _redirigir_admin_pedidos_por_origen,
        '_obtener_contacto_notificacion_pedido': _obtener_contacto_notificacion_pedido,
        '_notificar_actualizacion_pedido_cliente': _notificar_actualizacion_pedido_cliente,
        '_flash_resultado_notificacion_pedido': _flash_resultado_notificacion_pedido,
        '_notificar_pago_personalizado_admin': _notificar_pago_personalizado_admin,
        '_notificar_transferencia_admin': _notificar_transferencia_admin,
        '_validar_cliente_pos': _validar_cliente_pos,
        '_normalizar_metodo_pago_pos': _normalizar_metodo_pago_pos,
        '_parsear_items_checkout_pos': _parsear_items_checkout_pos,
        '_validar_y_preparar_carrito_pos': _validar_y_preparar_carrito_pos,
        '_resumen_promocion_pago_desde_carrito': _resumen_promocion_pago_desde_carrito,
        '_resumen_promocion_desde_promo_aplicada': _resumen_promocion_desde_promo_aplicada,
        '_construir_items_detalle_desde_carrito': _construir_items_detalle_desde_carrito,
        '_crear_pedido_y_detalle': _crear_pedido_y_detalle,
        '_crear_pago_para_pedido': _crear_pago_para_pedido,
        '_registrar_venta_pos_admin': _registrar_venta_pos_admin,
        '_asegurar_columnas_descuento_pagos': _asegurar_columnas_descuento_pagos,
        '_resolver_promocion_checkout': _resolver_promocion_checkout,
        '_obtener_contacto_checkout_predeterminado': _obtener_contacto_checkout_predeterminado,
        '_validar_datos_cliente_checkout': _validar_datos_cliente_checkout,
        '_guardar_contacto_checkout_usuario': _guardar_contacto_checkout_usuario,
        '_validar_stock_checkout': _validar_stock_checkout,
        '_descontar_stock_checkout': _descontar_stock_checkout,
        '_registrar_compra_checkout_usuario': _registrar_compra_checkout_usuario,
        '_iniciar_pago_stripe_desde_carrito': _iniciar_pago_stripe_desde_carrito,
    }
