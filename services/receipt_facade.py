"""Fachada de wrappers legacy para recibos POS."""


def build_receipt_legacy_bindings(
    *,
    app_receipt_service,
    session_obj,
    cargar_detalle_pedido_df_fn,
    cargar_productos_df_fn,
    cargar_pagos_df_fn,
    cargar_pedidos_df_fn,
    tallas_opciones,
    formatear_cop_fn,
    app_root_path,
    render_template_fn,
    edge_path_env,
):
    def _construir_datos_recibo_pos(id_pedido):
        return app_receipt_service.construir_datos_recibo_pos(
            id_pedido,
            cargar_detalle_pedido_df_fn=cargar_detalle_pedido_df_fn,
            cargar_productos_df_fn=cargar_productos_df_fn,
            cargar_pagos_df_fn=cargar_pagos_df_fn,
            cargar_pedidos_df_fn=cargar_pedidos_df_fn,
            tallas_opciones=tallas_opciones,
            ultimo_recibo_pos=session_obj.get('ultimo_recibo_pos', {}),
        )

    def _particionar_items_recibo(items, max_items_por_pagina=8):
        return app_receipt_service.particionar_items_recibo(items, max_items_por_pagina=max_items_por_pagina)

    def _construir_contexto_recibo_pos(id_pedido):
        return app_receipt_service.construir_contexto_recibo_pos(
            id_pedido,
            construir_datos_recibo_pos_fn=_construir_datos_recibo_pos,
            formatear_cop_fn=formatear_cop_fn,
            particionar_items_recibo_fn=_particionar_items_recibo,
        )

    def _cargar_css_recibo_pos():
        return app_receipt_service.cargar_css_recibo_pos(app_root_path)

    def _cargar_marca_agua_recibo_src():
        return app_receipt_service.cargar_marca_agua_recibo_src(app_root_path)

    def render_html_recibo_pos(id_pedido):
        return app_receipt_service.render_html_recibo_pos(
            id_pedido,
            construir_contexto_recibo_pos_fn=_construir_contexto_recibo_pos,
            cargar_css_recibo_pos_fn=_cargar_css_recibo_pos,
            cargar_marca_agua_recibo_src_fn=_cargar_marca_agua_recibo_src,
            render_template_fn=render_template_fn,
        )

    def _buscar_msedge():
        return app_receipt_service.buscar_msedge(edge_path_env=edge_path_env)

    def generar_pdf_recibo_pos(id_pedido):
        return app_receipt_service.generar_pdf_recibo_pos(
            id_pedido,
            render_html_recibo_pos_fn=render_html_recibo_pos,
            buscar_msedge_fn=_buscar_msedge,
            app_root_path=app_root_path,
        )

    return {
        '_construir_datos_recibo_pos': _construir_datos_recibo_pos,
        '_particionar_items_recibo': _particionar_items_recibo,
        '_construir_contexto_recibo_pos': _construir_contexto_recibo_pos,
        '_cargar_css_recibo_pos': _cargar_css_recibo_pos,
        '_cargar_marca_agua_recibo_src': _cargar_marca_agua_recibo_src,
        'render_html_recibo_pos': render_html_recibo_pos,
        '_buscar_msedge': _buscar_msedge,
        'generar_pdf_recibo_pos': generar_pdf_recibo_pos,
    }
