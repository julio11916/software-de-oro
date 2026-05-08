"""Servicio de promociones y descuentos."""

from datetime import date, datetime
from typing import Any, Mapping, Optional

import pandas as pd


def parsear_fecha_promocion(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor

    convertido = pd.to_datetime(valor, errors='coerce')
    if pd.isna(convertido):
        return None
    try:
        return convertido.date()
    except Exception:
        return None


def estado_vigencia_promocion(promo: Mapping[str, Any], fecha_ref: Optional[date] = None) -> str:
    if fecha_ref is None:
        fecha_ref = datetime.now().date()
    inicio = parsear_fecha_promocion(promo.get('fecha_inicio', ''))
    fin = parsear_fecha_promocion(promo.get('fecha_fin', ''))
    if inicio is not None and fecha_ref < inicio:
        return 'programada'
    if fin is not None and fecha_ref > fin:
        return 'vencida'
    return 'vigente'


def promocion_esta_aplicable(promo: Mapping[str, Any], fecha_ref: Optional[date] = None) -> bool:
    return bool(promo.get('activo', False)) and estado_vigencia_promocion(promo, fecha_ref) == 'vigente'


def calcular_descuento_promocion(subtotal, promo):
    subtotal = max(0.0, float(subtotal))
    tipo = str(promo.get('tipo_descuento', 'porcentaje')).strip().lower()
    valor = float(pd.to_numeric(promo.get('valor_descuento', 0), errors='coerce') or 0)

    if tipo == 'valor_fijo':
        descuento = max(0.0, valor)
    else:
        descuento = subtotal * max(0.0, valor) / 100.0

    return min(descuento, subtotal)


def obtener_mejor_promocion_por_producto(
    productos_df: pd.DataFrame,
    promos_df: pd.DataFrame,
    fecha_ref: Optional[date] = None,
):
    if fecha_ref is None:
        fecha_ref = datetime.now().date()

    productos_ref = productos_df.copy()
    if 'id_producto' not in productos_ref.columns:
        productos_ref['id_producto'] = pd.Series(dtype='int')
    if 'precio' not in productos_ref.columns:
        productos_ref['precio'] = 0.0

    productos_ref['id_producto'] = pd.to_numeric(productos_ref['id_producto'], errors='coerce')
    productos_ref['precio'] = pd.to_numeric(productos_ref['precio'], errors='coerce').fillna(0.0)

    precio_por_producto = {}
    for _, producto in productos_ref.iterrows():
        pid = pd.to_numeric(producto.get('id_producto'), errors='coerce')
        if pd.notna(pid):
            precio_por_producto[int(pid)] = float(pd.to_numeric(producto.get('precio', 0), errors='coerce') or 0.0)

    mejor_promo_por_producto = {}
    mejor_descuento_por_producto = {}
    for _, row in promos_df.iterrows():
        promo = row.to_dict()
        if not promocion_esta_aplicable(promo, fecha_ref):
            continue

        id_producto_promo = pd.to_numeric(promo.get('id_producto'), errors='coerce')
        if pd.isna(id_producto_promo):
            continue

        id_prod_int = int(id_producto_promo)
        if id_prod_int not in precio_por_producto:
            continue

        precio_ref = precio_por_producto.get(id_prod_int, 0.0)
        descuento_actual = calcular_descuento_promocion(precio_ref, promo)
        if descuento_actual > mejor_descuento_por_producto.get(id_prod_int, -1):
            mejor_descuento_por_producto[id_prod_int] = descuento_actual
            mejor_promo_por_producto[id_prod_int] = promo

    return mejor_promo_por_producto


def buscar_promocion_por_codigo(promos_df, codigo, fecha_ref=None):
    codigo_norm = str(codigo).strip().upper()
    if not codigo_norm:
        return None

    candidatos = promos_df[promos_df['codigo'].astype(str).str.upper() == codigo_norm]
    if candidatos.empty:
        return None

    for _, row in candidatos.iterrows():
        promo = row.to_dict()
        if promocion_esta_aplicable(promo, fecha_ref):
            return promo
    return None
