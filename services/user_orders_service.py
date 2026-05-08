"""Servicio de lectura de pedidos del usuario autenticado."""

import pandas as pd


def obtener_pedidos_usuario_actual(
    *,
    session_obj,
    cargar_pedidos_df_fn,
    cargar_pagos_df_fn,
    pedido_columns,
    enriquecer_pedidos_con_tracking_fn,
):
    pedidos = cargar_pedidos_df_fn()
    id_usuario = pd.to_numeric(session_obj.get('id_usuario'), errors='coerce')
    pedidos_usuario = pd.DataFrame(columns=pedido_columns)
    if not pedidos.empty and pd.notna(id_usuario):
        pedidos = pedidos.copy()
        pedidos['id_usuario_num'] = pd.to_numeric(pedidos['id_usuario'], errors='coerce')
        pedidos_usuario = pedidos[pedidos['id_usuario_num'] == id_usuario].copy()

    def asignar_numero_pedido_usuario(df):
        if df.empty or 'id_pedido' not in df.columns:
            return df

        df = df.copy()
        df['id_pedido_num'] = pd.to_numeric(df['id_pedido'], errors='coerce')
        orden_base = df.sort_values(by='id_pedido_num', ascending=True, na_position='last').reset_index()
        orden_base['numero_pedido_usuario'] = range(1, len(orden_base) + 1)
        mapa_numeros = dict(zip(orden_base['index'], orden_base['numero_pedido_usuario']))
        df['numero_pedido_usuario'] = df.index.map(mapa_numeros).fillna(0).astype(int)
        return df

    if not pedidos_usuario.empty:
        pagos = cargar_pagos_df_fn()
        if not pagos.empty:
            pagos = pagos.copy()
            pagos['id_pago_num'] = pd.to_numeric(pagos['id_pago'], errors='coerce')
            pagos = pagos.sort_values(by='id_pago_num', ascending=False, na_position='last').drop_duplicates(
                subset=['id_pedido'],
                keep='first',
            )
            columnas_pago = [
                col
                for col in ['id_pedido', 'monto', 'metodo_pago', 'estado_pago', 'comprobante_url']
                if col in pagos.columns
            ]
            pedidos_usuario = pd.merge(
                pedidos_usuario,
                pagos[columnas_pago],
                on='id_pedido',
                how='left',
            )
        pedidos_usuario = asignar_numero_pedido_usuario(pedidos_usuario)
        pedidos_usuario = pedidos_usuario.sort_values(by='id_pedido', ascending=False, na_position='last')
        pedidos_usuario['id_pedido'] = pd.to_numeric(pedidos_usuario['id_pedido'], errors='coerce').fillna(0).astype(int)

    return enriquecer_pedidos_con_tracking_fn(pedidos_usuario.fillna('').to_dict(orient='records'))
