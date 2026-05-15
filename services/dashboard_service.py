"""
Servicios para construir contexto de dashboard y listados de productos.
"""

from datetime import datetime, timedelta

import pandas as pd


def construir_contexto_home(
    productos_activos,
    promos,
    *,
    obtener_mejor_promocion_por_producto_fn,
    calcular_descuento_promocion_fn,
    formatear_cop_fn,
    obtener_galeria_producto_fn,
):
    lista_productos = productos_activos.to_dict(orient="records")
    hoy = datetime.now().date()
    mejor_promo_por_producto = obtener_mejor_promocion_por_producto_fn(productos_activos, promos, hoy)

    for producto in lista_productos:
        precio_base = float(pd.to_numeric(producto.get("precio", 0), errors="coerce") or 0)
        promo = mejor_promo_por_producto.get(int(producto.get("id_producto", 0)))
        if promo:
            descuento = calcular_descuento_promocion_fn(precio_base, promo)
            producto["precio_original"] = precio_base
            producto["precio_con_descuento"] = max(0.0, precio_base - descuento)
            producto["promo_activa"] = True
            producto["promo_nombre"] = promo.get("nombre", "")
            if promo.get("tipo_descuento") == "valor_fijo":
                producto["promo_etiqueta"] = f"-{formatear_cop_fn(promo.get('valor_descuento', 0))}"
            else:
                valor_pct = float(pd.to_numeric(promo.get("valor_descuento", 0), errors="coerce") or 0)
                producto["promo_etiqueta"] = f"-{valor_pct:g}%"
        else:
            producto["precio_original"] = precio_base
            producto["precio_con_descuento"] = precio_base
            producto["promo_activa"] = False
            producto["promo_nombre"] = ""
            producto["promo_etiqueta"] = ""

        galeria = obtener_galeria_producto_fn(
            int(producto.get("id_producto", 0)),
            producto.get("imagen_url", ""),
        )
        if not galeria:
            galeria = [producto.get("imagen_url", "")]
        while len(galeria) < 5:
            galeria.append(galeria[0])
        producto["galeria_dashboard"] = galeria[:5]

    productos_destacados_ejercito = [
        p for p in lista_productos if bool(p.get("destacado_dashboard", False)) and p.get("fuerza") == "Ejercito"
    ]
    productos_destacados_policia = [
        p for p in lista_productos if bool(p.get("destacado_dashboard", False)) and p.get("fuerza") == "Policia"
    ]
    productos_destacados_armada = [
        p for p in lista_productos if bool(p.get("destacado_dashboard", False)) and p.get("fuerza") == "Armada"
    ]
    productos_destacados_gaula = [
        p for p in lista_productos if bool(p.get("destacado_dashboard", False)) and p.get("fuerza") == "Gaula"
    ]
    productos_destacados_variado = [
        p for p in lista_productos if bool(p.get("destacado_dashboard", False)) and p.get("fuerza") == "Variado"
    ]

    return {
        "productos": lista_productos,
        "productos_destacados_ejercito": productos_destacados_ejercito,
        "productos_destacados_policia": productos_destacados_policia,
        "productos_destacados_armada": productos_destacados_armada,
        "productos_destacados_gaula": productos_destacados_gaula,
        "productos_destacados_variado": productos_destacados_variado,
    }


def construir_contexto_admin_dashboard(
    productos_activos,
    productos_agotados,
    admin_nombre,
    usuarios_df,
    pedidos_df,
    detalle_df,
):
    lista_productos = productos_activos.to_dict(orient="records")

    hoy = datetime.now()
    hace_30 = hoy - timedelta(days=30)

    if not usuarios_df.empty and "fecha_registro" in usuarios_df.columns:
        usuarios_df = usuarios_df.copy()
        usuarios_df["fecha_registro_dt"] = pd.to_datetime(usuarios_df["fecha_registro"], errors="coerce", utc=True).dt.tz_convert(
            None
        )
        usuarios_ult_mes = usuarios_df[usuarios_df["fecha_registro_dt"] >= hace_30]["id_usuario"].nunique()
    else:
        usuarios_ult_mes = 0

    usuarios_compraron_ult_mes = 0
    if not pedidos_df.empty:
        pedidos_df = pedidos_df.copy()
        pedidos_df["fecha_pedido_dt"] = pd.to_datetime(
            pedidos_df["fecha_pedido"], errors="coerce", utc=True
        ).dt.tz_convert(None)
        pedidos_ult_mes = pedidos_df[pedidos_df["fecha_pedido_dt"] >= hace_30]
        usuarios_compraron_ult_mes = pedidos_ult_mes["id_usuario"].nunique()

    top_productos = []
    if not detalle_df.empty:
        detalle_df = detalle_df.copy()
        detalle_df["cantidad"] = pd.to_numeric(detalle_df.get("cantidad", 0), errors="coerce").fillna(0)
        top_df = (
            detalle_df.groupby("id_producto", as_index=False)["cantidad"]
            .sum()
            .sort_values("cantidad", ascending=False)
            .head(5)
        )
        prod_ref = (
            productos_activos[["id_producto", "nombre"]]
            if not productos_activos.empty
            else pd.DataFrame(columns=["id_producto", "nombre"])
        )
        top_df = pd.merge(top_df, prod_ref, on="id_producto", how="left")
        top_productos = top_df.to_dict(orient="records")

    productos_destacables = []
    destacados_count = 0
    if not productos_activos.empty:
        productos_ordenados = productos_activos.sort_values(["fuerza", "intendencia", "nombre"], ascending=[True, True, True])
        productos_destacables = productos_ordenados.to_dict(orient="records")
        destacados_count = int(
            pd.to_numeric(productos_ordenados.get("destacado_dashboard", False), errors="coerce")
            .fillna(0)
            .astype(bool)
            .sum()
        )

    return {
        "productos": lista_productos,
        "admin_nombre": admin_nombre,
        "productos_agotados": productos_agotados,
        "usuarios_ult_mes": usuarios_ult_mes,
        "usuarios_compraron_ult_mes": usuarios_compraron_ult_mes,
        "top_productos": top_productos,
        "productos_destacables": productos_destacables,
        "destacados_count": destacados_count,
    }


def actualizar_destacados_productos(
    productos,
    ids_ejercito_raw,
    ids_policia_raw,
    ids_armada_raw,
    ids_gaula_raw,
    ids_variado_raw,
):
    productos = productos.copy()
    productos["id_producto"] = pd.to_numeric(productos["id_producto"], errors="coerce")
    ids_disponibles = set(productos.loc[productos["eliminado"] == False, "id_producto"].dropna().astype(int).tolist())

    def procesar_ids(ids_raw):
        ids_seleccionados = []
        for valor in ids_raw:
            try:
                valor_int = int(valor)
            except (TypeError, ValueError):
                continue
            if valor_int in ids_disponibles and valor_int not in ids_seleccionados:
                ids_seleccionados.append(valor_int)
        return ids_seleccionados

    ids_ejercito = procesar_ids(ids_ejercito_raw)
    ids_policia = procesar_ids(ids_policia_raw)
    ids_armada = procesar_ids(ids_armada_raw)
    ids_gaula = procesar_ids(ids_gaula_raw)
    ids_variado = procesar_ids(ids_variado_raw)

    productos["destacado_dashboard"] = False
    productos.loc[productos["eliminado"] == True, "destacado_dashboard"] = False
    productos.loc[productos["id_producto"].isin(ids_ejercito), "destacado_dashboard"] = True
    productos.loc[productos["id_producto"].isin(ids_policia), "destacado_dashboard"] = True
    productos.loc[productos["id_producto"].isin(ids_armada), "destacado_dashboard"] = True
    productos.loc[productos["id_producto"].isin(ids_gaula), "destacado_dashboard"] = True
    productos.loc[productos["id_producto"].isin(ids_variado), "destacado_dashboard"] = True

    return {
        "productos": productos,
        "ids_ejercito": ids_ejercito,
        "ids_policia": ids_policia,
        "ids_armada": ids_armada,
        "ids_gaula": ids_gaula,
        "ids_variado": ids_variado,
        "total_destacados": len(ids_ejercito)
        + len(ids_policia)
        + len(ids_armada)
        + len(ids_gaula)
        + len(ids_variado),
    }


def construir_contexto_admin_productos(
    productos_todos,
    productos_activos,
    busqueda,
    fuerza_filtro,
    intendencia_filtro,
    *,
    fuerzas_opciones,
    intendencias_opciones,
    obtener_galeria_producto_fn,
):
    total_eliminados = int(productos_todos["eliminado"].fillna(False).astype(bool).sum())
    total_productos = len(productos_activos)
    productos = productos_activos.copy()

    if fuerza_filtro and fuerza_filtro not in fuerzas_opciones:
        fuerza_filtro = ""
    if intendencia_filtro and intendencia_filtro not in intendencias_opciones:
        intendencia_filtro = ""

    if busqueda:
        filtros = [
            productos["nombre"].str.contains(busqueda, case=False, na=False, regex=False),
            productos["descripcion"].str.contains(busqueda, case=False, na=False, regex=False),
            productos["fuerza"].str.contains(busqueda, case=False, na=False, regex=False),
            productos["intendencia"].str.contains(busqueda, case=False, na=False, regex=False),
            productos["id_producto"].fillna("").astype(str).str.contains(busqueda, case=False, na=False, regex=False),
        ]
        mascara = filtros[0]
        for filtro in filtros[1:]:
            mascara = mascara | filtro
        productos = productos[mascara].copy()

    if fuerza_filtro:
        productos = productos[productos["fuerza"].str.strip() == fuerza_filtro].copy()

    if intendencia_filtro:
        productos = productos[productos["intendencia"].str.strip() == intendencia_filtro].copy()

    hay_filtros = bool(busqueda or fuerza_filtro or intendencia_filtro)
    lista_productos = productos.to_dict(orient="records")
    productos_por_fuerza = {fuerza: [] for fuerza in fuerzas_opciones}

    for producto in lista_productos:
        imagen_principal = str(producto.get("imagen_url", "")).strip()
        galeria = obtener_galeria_producto_fn(producto.get("id_producto"), imagen_principal)
        producto["imagenes"] = galeria
        if galeria:
            producto["imagen_url"] = galeria[0]

        fuerza_producto = str(producto.get("fuerza", "")).strip().lower()
        for fuerza in fuerzas_opciones:
            if fuerza_producto == fuerza.lower():
                productos_por_fuerza[fuerza].append(producto)
                break

    return {
        "productos": lista_productos,
        "productos_por_fuerza": productos_por_fuerza,
        "fuerzas": fuerzas_opciones,
        "intendencias": intendencias_opciones,
        "search_query": busqueda,
        "selected_fuerza": fuerza_filtro,
        "selected_intendencia": intendencia_filtro,
        "has_filters": hay_filtros,
        "total_productos": total_productos,
        "total_eliminados": total_eliminados,
    }
