"""
Servicios de almacenamiento y normalizacion de tablas.
"""

import re
from typing import Any

import pandas as pd
import sqlalchemy as sa

from core.db_utils import engine, read_table_df, replace_table_df
from models.constants import *
from services import image_service as app_image_service


def asegurar_columnas_usuarios():
    with engine.begin() as conn:
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS terminos_identidad_aceptados BOOLEAN NOT NULL DEFAULT FALSE"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS terminos_identidad_fecha TIMESTAMPTZ"))


def normalizar_intendencia(valor):
    texto = str(valor or "").strip().lower()
    return re.sub(r"\s+", " ", texto)

def producto_requiere_talla(intendencia):
    return normalizar_intendencia(intendencia) not in INTENDENCIAS_SIN_TALLA

def cargar_usuarios_df():
    asegurar_columnas_usuarios()
    usuarios = read_table_df('usuarios')
    if usuarios.empty:
        usuarios = pd.DataFrame(columns=USUARIO_COLUMNS)

    for col in USUARIO_COLUMNS:
        if col not in usuarios.columns:
            if col == 'estado':
                usuarios[col] = 'activo'
            elif col in {'email_verified', 'terminos_identidad_aceptados'}:
                usuarios[col] = False
            else:
                usuarios[col] = ''
    
    # Asegurar que las columnas de tokens sean tipo string
    if 'verification_code' in usuarios.columns:
        usuarios['verification_code'] = usuarios['verification_code'].fillna('').astype(str)
    if 'verification_code_expiry' in usuarios.columns:
        usuarios['verification_code_expiry'] = usuarios['verification_code_expiry'].fillna('').astype(str)
    if 'reset_token' in usuarios.columns:
        usuarios['reset_token'] = usuarios['reset_token'].fillna('').astype(str)
    if 'reset_token_expiry' in usuarios.columns:
        usuarios['reset_token_expiry'] = usuarios['reset_token_expiry'].fillna('').astype(str)
    if 'password_change_code' in usuarios.columns:
        usuarios['password_change_code'] = usuarios['password_change_code'].fillna('').astype(str)
    if 'password_change_code_expiry' in usuarios.columns:
        usuarios['password_change_code_expiry'] = usuarios['password_change_code_expiry'].fillna('').astype(str)
    if 'email_verified' in usuarios.columns:
        usuarios['email_verified'] = usuarios['email_verified'].fillna(False).astype(bool)
    if 'terminos_identidad_aceptados' in usuarios.columns:
        usuarios['terminos_identidad_aceptados'] = usuarios['terminos_identidad_aceptados'].fillna(False).astype(bool)
    if 'terminos_identidad_fecha' in usuarios.columns:
        usuarios['terminos_identidad_fecha'] = usuarios['terminos_identidad_fecha'].fillna('').astype(str)
    
    usuarios['estado'] = usuarios['estado'].fillna('activo').astype(str).str.strip().str.lower()
    usuarios.loc[~usuarios['estado'].isin(['activo', 'inactivo']), 'estado'] = 'activo'
    return usuarios[USUARIO_COLUMNS]

def guardar_usuarios_df(usuarios):
    """
    Persiste el DataFrame de usuarios en PostgreSQL manteniendo tipos correctos
    para fechas y booleanos, y normalizando los tokens a texto.
    """
    asegurar_columnas_usuarios()
    df = usuarios.copy()

    # Normalizar columnas de texto
    for col in ['verification_code', 'reset_token', 'password_change_code']:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str)

    # Convertir columnas de fecha/hora a datetime o None
    for col in ['fecha_registro', 'verification_code_expiry', 'reset_token_expiry', 'password_change_code_expiry', 'terminos_identidad_fecha']:
        if col in df.columns:
            col_series = df[col].replace('', pd.NA)
            parsed = pd.to_datetime(col_series, errors='coerce')
            df[col] = parsed.where(parsed.notna(), None)

    # Asegurar booleanos
    if 'email_verified' in df.columns:
        df['email_verified'] = df['email_verified'].fillna(False).astype(bool)
    if 'terminos_identidad_aceptados' in df.columns:
        df['terminos_identidad_aceptados'] = df['terminos_identidad_aceptados'].fillna(False).astype(bool)

    replace_table_df('usuarios', df[USUARIO_COLUMNS])

def cargar_registros_df():
    registros = read_table_df('registros')
    if registros.empty:
        registros = pd.DataFrame(columns=REGISTRO_COLUMNS)

    for col in REGISTRO_COLUMNS:
        if col not in registros.columns:
            registros[col] = ''
    registros['id_registro'] = pd.to_numeric(registros['id_registro'], errors='coerce')
    registros['id_usuario'] = registros['id_usuario'].fillna('')
    registros['accion'] = registros['accion'].fillna('')
    registros['fecha_accion'] = registros['fecha_accion'].fillna('')
    return registros[REGISTRO_COLUMNS]

def guardar_registros_df(registros):
    replace_table_df('registros', registros[REGISTRO_COLUMNS])

def cargar_promociones_df():
    """Carga el DataFrame de promociones desde la tabla SQL."""
    promos = read_table_df('promociones')
    if promos.empty:
        promos = pd.DataFrame(columns=PROMO_COLUMNS)

    for col in PROMO_COLUMNS:
        if col not in promos.columns:
            promos[col] = ''

    # compatibilidad con estructura anterior
    if 'valor_descuento' not in promos.columns and 'descuento' in promos.columns:
        promos['valor_descuento'] = promos['descuento']
    if 'tipo_descuento' not in promos.columns:
        promos['tipo_descuento'] = 'porcentaje'
    if 'codigo' not in promos.columns:
        promos['codigo'] = ''
    if 'id_producto' not in promos.columns:
        promos['id_producto'] = pd.Series(dtype='float')

    # asegurar tipos
    promos['valor_descuento'] = pd.to_numeric(promos['valor_descuento'], errors='coerce').fillna(0)
    promos['tipo_descuento'] = promos['tipo_descuento'].astype(str).str.strip().str.lower()
    promos.loc[~promos['tipo_descuento'].isin(['porcentaje', 'valor_fijo']), 'tipo_descuento'] = 'porcentaje'
    promos['id_producto'] = pd.to_numeric(promos['id_producto'], errors='coerce')
    promos['codigo'] = promos['codigo'].fillna('').astype(str).str.strip().str.upper()
    promos['activo'] = promos['activo'].astype(bool)
    return promos[PROMO_COLUMNS]

def guardar_promociones_df(promos):
    """Guarda las promociones en la tabla SQL."""
    replace_table_df('promociones', promos[PROMO_COLUMNS])

def normalizar_producto_personalizado(valor):
    return re.sub(r"\s+", " ", str(valor or "").strip().lower())

def producto_personalizado_canonico(valor):
    producto = normalizar_producto_personalizado(valor)
    return ORDEN_PERSONALIZADA_PRODUCTO_ALIAS.get(producto, producto)

def asegurar_tablas_orden_personalizada():
    ddl = """
    CREATE TABLE IF NOT EXISTS orden_personalizada (
        id_orden_personalizada BIGSERIAL PRIMARY KEY,
        usuario_email TEXT,
        cliente_nombre TEXT,
        cliente_correo TEXT,
        cliente_telefono TEXT,
        cliente_direccion TEXT,
        rango TEXT,
        fecha_contingencia TEXT,
        identidad TEXT,
        producto TEXT,
        tecnica TEXT,
        color TEXT,
        estampado TEXT,
        talla TEXT,
        modelo_rh TEXT,
        modelo_presilla TEXT,
        cantidad INTEGER NOT NULL DEFAULT 1,
        imagen_url TEXT,
        precio NUMERIC(12,2) NOT NULL DEFAULT 0,
        estado TEXT NOT NULL DEFAULT 'pendiente',
        datos_json TEXT NOT NULL DEFAULT '{}',
        fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS orden_personalizada_precio (
        producto TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio NUMERIC(12,2) NOT NULL DEFAULT 0
    );
    """
    with engine.begin() as conn:
        conn.execute(sa.text(ddl))
        for col in ORDEN_PERSONALIZADA_COLUMNS:
            if col == 'id_orden_personalizada':
                continue
            column_type = (
                'NUMERIC(12,2)' if col == 'precio'
                else 'INTEGER' if col == 'cantidad'
                else 'TIMESTAMPTZ' if col == 'fecha_creacion'
                else 'TEXT'
            )
            default_sql = " DEFAULT NOW()" if col == 'fecha_creacion' else ""
            if col == 'estado':
                default_sql = " DEFAULT 'pendiente'"
            if col == 'datos_json':
                default_sql = " DEFAULT '{}'"
            if col == 'cantidad':
                default_sql = " DEFAULT 1"
            conn.execute(sa.text(f'ALTER TABLE orden_personalizada ADD COLUMN IF NOT EXISTS "{col}" {column_type}{default_sql}'))
        for item in ORDEN_PERSONALIZADA_PRECIOS_DEFAULT:
            conn.execute(
                sa.text("""
                    INSERT INTO orden_personalizada_precio (producto, nombre, precio)
                    VALUES (:producto, :nombre, :precio)
                    ON CONFLICT (producto) DO NOTHING
                """),
                item
            )

def cargar_precios_orden_personalizada_df():
    asegurar_tablas_orden_personalizada()
    precios = read_table_df('orden_personalizada_precio')
    if precios.empty:
        precios = pd.DataFrame(ORDEN_PERSONALIZADA_PRECIOS_DEFAULT)
    for col in ORDEN_PERSONALIZADA_PRECIO_COLUMNS:
        if col not in precios.columns:
            precios[col] = 0 if col == 'precio' else ''
    precios['precio'] = pd.to_numeric(precios['precio'], errors='coerce').fillna(0.0)
    nombres_ref = {
        producto_personalizado_canonico(item['producto']): item['nombre']
        for item in ORDEN_PERSONALIZADA_PRECIOS_DEFAULT
    }
    precios['producto'] = precios['producto'].apply(producto_personalizado_canonico)
    precios = precios[precios['producto'].isin(nombres_ref.keys())].copy()
    precios['nombre'] = precios['producto'].map(nombres_ref).fillna(precios['nombre'])
    precios = precios.drop_duplicates(subset=['producto'], keep='first')
    return precios[ORDEN_PERSONALIZADA_PRECIO_COLUMNS]

def precios_orden_personalizada_mapa():
    precios = cargar_precios_orden_personalizada_df()
    mapa = {
        normalizar_producto_personalizado(row.get('producto')): float(row.get('precio', 0) or 0)
        for _, row in precios.iterrows()
    }
    for alias, canonico in ORDEN_PERSONALIZADA_PRODUCTO_ALIAS.items():
        if canonico in mapa:
            mapa[alias] = mapa[canonico]
    return mapa

def cargar_ordenes_personalizadas_df():
    asegurar_tablas_orden_personalizada()
    ordenes = read_table_df('orden_personalizada')
    if ordenes.empty:
        ordenes = pd.DataFrame(columns=ORDEN_PERSONALIZADA_COLUMNS)
    for col in ORDEN_PERSONALIZADA_COLUMNS:
        if col not in ordenes.columns:
            ordenes[col] = 0 if col in {'id_orden_personalizada', 'precio'} else 1 if col == 'cantidad' else ''
    ordenes['precio'] = pd.to_numeric(ordenes['precio'], errors='coerce').fillna(0.0)
    ordenes['cantidad'] = pd.to_numeric(ordenes['cantidad'], errors='coerce').fillna(1).astype(int)
    return ordenes[ORDEN_PERSONALIZADA_COLUMNS]

def actualizar_precio_orden_personalizada(producto, precio):
    producto_key = producto_personalizado_canonico(producto)
    if not producto_key:
        return False
    precios_ref = {
        producto_personalizado_canonico(item['producto']): item['nombre']
        for item in ORDEN_PERSONALIZADA_PRECIOS_DEFAULT
    }
    if producto_key not in precios_ref:
        return False
    nombre = precios_ref.get(producto_key, producto_key.replace('_', ' ').title())
    asegurar_tablas_orden_personalizada()
    with engine.begin() as conn:
        conn.execute(
            sa.text("""
                INSERT INTO orden_personalizada_precio (producto, nombre, precio)
                VALUES (:producto, :nombre, :precio)
                ON CONFLICT (producto)
                DO UPDATE SET precio = EXCLUDED.precio, nombre = EXCLUDED.nombre
            """),
            {'producto': producto_key, 'nombre': nombre, 'precio': float(precio)}
        )
    return True

def actualizar_estado_ordenes_personalizadas_carrito(carrito, estado):
    if estado not in ORDEN_PERSONALIZADA_ESTADOS_PAGO:
        return
    ids_orden = []
    for item in carrito or []:
        if not item.get('personalizado'):
            continue
        id_orden = pd.to_numeric(item.get('id_orden_personalizada'), errors='coerce')
        if pd.notna(id_orden):
            ids_orden.append(int(id_orden))
    if not ids_orden:
        return
    asegurar_tablas_orden_personalizada()
    with engine.begin() as conn:
        stmt = sa.text("""
                UPDATE orden_personalizada
                SET estado = :estado
                WHERE id_orden_personalizada IN :ids_orden
            """).bindparams(sa.bindparam("ids_orden", expanding=True))
        conn.execute(
            stmt,
            {'estado': estado, 'ids_orden': ids_orden}
        )


def cargar_productos_df():
    productos = read_table_df('producto')
    for column in PRODUCTO_COLUMNS:
        if column not in productos.columns:
            if column in {'eliminado', 'destacado_dashboard'}:
                productos[column] = False
            elif column in {'precio'}:
                productos[column] = 0.0
            elif column in {'stock', 'id_categoria'}:
                productos[column] = 0
            else:
                productos[column] = ''

    productos = app_image_service.normalizar_imagenes_productos(productos)
    productos['id_producto'] = pd.to_numeric(productos['id_producto'], errors='coerce')
    productos['precio'] = pd.to_numeric(productos['precio'], errors='coerce').fillna(0.0).astype(float)
    productos['stock'] = pd.to_numeric(productos['stock'], errors='coerce').fillna(0).astype(int)
    productos['id_categoria'] = pd.to_numeric(productos['id_categoria'], errors='coerce').fillna(0).astype(int)
    # Normalizar bandera eliminado aun si viene como texto ('t','f','true','false') o nulos.
    def _to_bool(valor: Any) -> bool:
        if pd.isna(valor):
            return False
        if isinstance(valor, (int, float, bool)):
            return bool(valor)
        if isinstance(valor, str):
            return valor.strip().lower() in {'true', 't', '1', 'yes', 'si', 'y'}
        return bool(valor)

    productos['eliminado'] = productos['eliminado'].apply(_to_bool)
    if 'destacado_dashboard' in productos.columns:
        productos['destacado_dashboard'] = productos['destacado_dashboard'].apply(_to_bool)
    else:
        productos['destacado_dashboard'] = False
    productos['fuerza'] = productos['fuerza'].fillna('').astype(str)
    productos['intendencia'] = productos['intendencia'].fillna('').astype(str)
    productos['nombre'] = productos['nombre'].fillna('').astype(str)
    productos['descripcion'] = productos['descripcion'].fillna('').astype(str)
    productos['imagen_url'] = productos['imagen_url'].fillna('').astype(str)
    return productos[PRODUCTO_COLUMNS]

def guardar_productos_df(productos):
    productos = productos.copy()
    for column in PRODUCTO_COLUMNS:
        if column not in productos.columns:
            if column in {'eliminado', 'destacado_dashboard'}:
                productos[column] = False
            elif column in {'precio'}:
                productos[column] = 0.0
            elif column in {'stock', 'id_categoria'}:
                productos[column] = 0
            else:
                productos[column] = ''

    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos['destacado_dashboard'] = productos['destacado_dashboard'].fillna(False).astype(bool)
    replace_table_df('producto', productos[PRODUCTO_COLUMNS])

def cargar_productos_activos_df():
    productos = cargar_productos_df()
    return productos[productos['eliminado'] == False].copy()

def cargar_pedidos_df():
    pedidos = read_table_df('pedidos')
    for column in PEDIDO_COLUMNS:
        if column not in pedidos.columns:
            pedidos[column] = '' if column in {'id_usuario', 'fecha_pedido', 'estado', 'cliente_telefono', 'cliente_direccion'} else 0
    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    pedidos['id_usuario'] = pedidos['id_usuario'].fillna('')
    pedidos['fecha_pedido'] = pedidos['fecha_pedido'].fillna('')
    pedidos['estado'] = pedidos['estado'].fillna('confirmado')
    pedidos['cliente_telefono'] = pedidos['cliente_telefono'].fillna('').astype(str)
    pedidos['cliente_direccion'] = pedidos['cliente_direccion'].fillna('').astype(str)
    return pedidos[PEDIDO_COLUMNS]

def guardar_pedidos_df(pedidos):
    pedidos = pedidos.copy()
    for column in PEDIDO_COLUMNS:
        if column not in pedidos.columns:
            pedidos[column] = '' if column in {'id_usuario', 'fecha_pedido', 'estado', 'cliente_telefono', 'cliente_direccion'} else 0
    replace_table_df('pedidos', pedidos[PEDIDO_COLUMNS])

def cargar_detalle_pedido_df():
    detalle = read_table_df('detalle_pedido')
    for column in DETALLE_PEDIDO_COLUMNS:
        if column not in detalle.columns:
            detalle[column] = '' if column == 'talla' else 0
    detalle['id_detalle'] = pd.to_numeric(detalle['id_detalle'], errors='coerce')
    detalle['id_pedido'] = pd.to_numeric(detalle['id_pedido'], errors='coerce')
    detalle['id_producto'] = pd.to_numeric(detalle['id_producto'], errors='coerce')
    detalle['cantidad'] = pd.to_numeric(detalle['cantidad'], errors='coerce').fillna(0)
    detalle['subtotal'] = pd.to_numeric(detalle['subtotal'], errors='coerce').fillna(0.0)
    if 'talla' in detalle.columns:
        detalle['talla'] = detalle['talla'].fillna('').astype(str)
    return detalle[DETALLE_PEDIDO_COLUMNS]

def guardar_detalle_pedido_df(detalle):
    detalle = detalle.copy()
    for column in DETALLE_PEDIDO_COLUMNS:
        if column not in detalle.columns:
            detalle[column] = '' if column == 'talla' else 0
    replace_table_df('detalle_pedido', detalle[DETALLE_PEDIDO_COLUMNS])

def cargar_pagos_df():
    pagos = read_table_df('pagos')
    defaults = {
        'id_pago': 0,
        'id_pedido': 0,
        'monto': 0.0,
        'metodo_pago': '',
        'fecha_pago': '',
        'estado_pago': '',
        'comprobante_url': '',
        'id_promo': '',
        'codigo_promo': '',
        'tipo_descuento': '',
        'valor_descuento': 0.0,
        'monto_descuento': 0.0,
    }
    for column, default_value in defaults.items():
        if column not in pagos.columns:
            pagos[column] = default_value
    pagos['id_pago'] = pd.to_numeric(pagos['id_pago'], errors='coerce')
    pagos['id_pedido'] = pd.to_numeric(pagos['id_pedido'], errors='coerce')
    pagos['monto'] = pd.to_numeric(pagos['monto'], errors='coerce').fillna(0.0)
    pagos['valor_descuento'] = pd.to_numeric(pagos['valor_descuento'], errors='coerce').fillna(0.0)
    pagos['monto_descuento'] = pd.to_numeric(pagos['monto_descuento'], errors='coerce').fillna(0.0)
    pagos['metodo_pago'] = pagos['metodo_pago'].fillna('')
    pagos['fecha_pago'] = pagos['fecha_pago'].fillna('')
    pagos['estado_pago'] = pagos['estado_pago'].fillna('')
    pagos['comprobante_url'] = pagos['comprobante_url'].fillna('')
    pagos['codigo_promo'] = pagos['codigo_promo'].fillna('')
    pagos['tipo_descuento'] = pagos['tipo_descuento'].fillna('')
    return pagos[PAGO_COLUMNS]

def guardar_pagos_df(pagos):
    pagos = pagos.copy()
    defaults = {
        'id_pago': 0,
        'id_pedido': 0,
        'monto': 0.0,
        'metodo_pago': '',
        'fecha_pago': '',
        'estado_pago': '',
        'comprobante_url': '',
        'id_promo': '',
        'codigo_promo': '',
        'tipo_descuento': '',
        'valor_descuento': 0.0,
        'monto_descuento': 0.0,
    }
    for column, default_value in defaults.items():
        if column not in pagos.columns:
            pagos[column] = default_value
    replace_table_df('pagos', pagos[PAGO_COLUMNS])

def cargar_productos_por_fuerza(fuerza):
    productos = cargar_productos_activos_df()
    fuerza_norm = fuerza.strip().lower()
    productos = productos[productos['fuerza'].str.strip().str.lower() == fuerza_norm]
    return productos.to_dict(orient='records')

def cargar_productos_por_intendencia(intendencia):
    productos = cargar_productos_activos_df()
    intendencia_norm = intendencia.strip().lower()
    productos = productos[productos['intendencia'].str.strip().str.lower() == intendencia_norm]
    return productos.to_dict(orient='records')

