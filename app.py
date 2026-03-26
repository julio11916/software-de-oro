import os, json, re, shutil, subprocess, base64, pandas as pd
from io import BytesIO
from pathlib import Path
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash, send_file, jsonify
from datetime import datetime, timedelta, date
from typing import Any, Mapping, Optional
from email_service import mail, generar_codigo_verificacion, enviar_codigo_verificacion
import config_email
from db_utils import engine, read_table_df, replace_table_df, next_id  # Inicializa DB y proxys al importar

app = Flask(__name__)
app.secret_key = "clave"  # Necesario para manejar sesiones

# Configuración de Flask-Mail para Gmail
app.config['MAIL_SERVER'] = config_email.MAIL_SERVER
app.config['MAIL_PORT'] = config_email.MAIL_PORT
app.config['MAIL_USE_TLS'] = config_email.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config_email.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config_email.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config_email.MAIL_DEFAULT_SENDER

# Inicializar Flask-Mail
mail.init_app(app)

CURRENCY_CODE = "COP"
CURRENCY_NAME = "Peso colombiano"

USUARIO_COLUMNS = ['id_usuario', 'nombre', 'email', 'password_hash', 'rol', 'estado', 'fecha_registro', 'email_verified', 'verification_code', 'verification_code_expiry']
REGISTRO_COLUMNS = ['id_registro', 'id_usuario', 'accion', 'fecha_accion']
PRODUCTO_COLUMNS = ['id_producto', 'nombre', 'descripcion', 'precio', 'stock', 'id_categoria', 'fuerza', 'intendencia', 'imagen_url', 'eliminado']
PEDIDO_COLUMNS = ['id_pedido', 'id_usuario', 'fecha_pedido', 'estado']
DETALLE_PEDIDO_COLUMNS = ['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal']
PAGO_COLUMNS = ['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago', 'id_promo', 'codigo_promo', 'tipo_descuento', 'valor_descuento', 'monto_descuento']

# Column definitions for promociones
PROMO_COLUMNS = [
    'id_promo', 'nombre', 'descripcion',
    'tipo_descuento', 'valor_descuento',
    'id_producto',
    'codigo',
    'fecha_inicio', 'fecha_fin',
    'activo'
]

FUERZAS_OPCIONES = ["Policia", "Ejercito", "Armada", "Gaula"]
INTENDENCIAS_OPCIONES = [
    "Busos", "Camibusos", "Gorras", "Panoletas", "Sudaderas",
    "Pantalonetas", "Colchas", "Tendidos", "Chuspas para ropa sucia",
    "Fundas para almohadas", "Camuflados", "Accesorios", "Presillas"
]
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_SIZE_BYTES = 3 * 1024 * 1024
MAX_IMAGES_PER_PRODUCT = 5

# DB init y proxys se hacen al importar db_utils


def cargar_usuarios_df():
    usuarios = read_table_df('usuarios')
    if usuarios.empty:
        usuarios = pd.DataFrame(columns=USUARIO_COLUMNS)

    for col in USUARIO_COLUMNS:
        if col not in usuarios.columns:
            if col == 'estado':
                usuarios[col] = 'activo'
            elif col == 'email_verified':
                usuarios[col] = False
            else:
                usuarios[col] = ''
    
    # Asegurar que las columnas de verificación sean tipo string
    if 'verification_code' in usuarios.columns:
        usuarios['verification_code'] = usuarios['verification_code'].fillna('').astype(str)
    if 'verification_code_expiry' in usuarios.columns:
        usuarios['verification_code_expiry'] = usuarios['verification_code_expiry'].fillna('').astype(str)
    if 'email_verified' in usuarios.columns:
        usuarios['email_verified'] = usuarios['email_verified'].fillna(False).astype(bool)
    
    usuarios['estado'] = usuarios['estado'].fillna('activo').astype(str).str.strip().str.lower()
    usuarios.loc[~usuarios['estado'].isin(['activo', 'inactivo']), 'estado'] = 'activo'
    return usuarios[USUARIO_COLUMNS]


def guardar_usuarios_df(usuarios):
    # Convertir columnas de verificación a string antes de guardar
    if 'verification_code' in usuarios.columns:
        usuarios['verification_code'] = usuarios['verification_code'].astype(str)
    if 'verification_code_expiry' in usuarios.columns:
        usuarios['verification_code_expiry'] = usuarios['verification_code_expiry'].astype(str)
    replace_table_df('usuarios', usuarios[USUARIO_COLUMNS])


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


def normalizar_imagen_url(valor):
    ruta = str(valor or '').strip().replace('\\', '/')
    if not ruta or ruta.lower() == 'nan':
        return ''
    if ruta.startswith('img/Empresa/') or ruta.startswith('img/Pagina/') or ruta.startswith('img/catalogo/'):
        return ruta
    if ruta.startswith('img/'):
        return f"img/Empresa/{ruta.split('/')[-1]}"
    return ruta


def normalizar_imagenes_productos(productos):
    if 'imagen_url' not in productos.columns:
        productos['imagen_url'] = ''
    productos['imagen_url'] = productos['imagen_url'].apply(normalizar_imagen_url)
    return productos


def extension_imagen(nombre_archivo):
    if not nombre_archivo or '.' not in nombre_archivo:
        return ''
    return nombre_archivo.rsplit('.', 1)[-1].lower()


def validar_archivo_imagen(archivo):
    extension = extension_imagen(getattr(archivo, 'filename', ''))
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return "Formato de imagen no permitido. Usa .jpg, .jpeg, .png, .gif o .webp."

    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > MAX_IMAGE_SIZE_BYTES:
        return "La imagen excede el tamaño máximo permitido (3MB)."
    return None


def ruta_imagen_producto_absoluta(ruta_relativa):
    ruta = str(ruta_relativa or '').strip().replace('\\', '/').lstrip('/')
    if not ruta.startswith('img/Empresa/'):
        return ''

    base = os.path.abspath(os.path.join('static', 'img', 'Empresa'))
    candidata = os.path.abspath(os.path.join('static', ruta))
    if os.path.commonpath([base, candidata]) != base:
        return ''
    return candidata


def listar_archivos_galeria_producto(id_producto):
    carpeta_destino = os.path.join('static', 'img', 'Empresa')
    prefijo = f'producto_{id_producto}_'
    resultados = []

    if not os.path.isdir(carpeta_destino):
        return resultados

    for nombre in os.listdir(carpeta_destino):
        if not nombre.lower().startswith(prefijo.lower()):
            continue
        if extension_imagen(nombre) not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        sufijo = nombre[len(prefijo):]
        posicion = sufijo.split('.', 1)[0]
        if not posicion.isdigit():
            continue
        resultados.append((int(posicion), nombre))

    resultados.sort(key=lambda item: item[0])
    return resultados


def migrar_legacy_a_galeria(id_producto):
    if listar_archivos_galeria_producto(id_producto):
        return

    carpeta_destino = os.path.join('static', 'img', 'Empresa')
    if not os.path.isdir(carpeta_destino):
        return

    for extension in sorted(ALLOWED_IMAGE_EXTENSIONS):
        legacy_name = f'producto_{id_producto}.{extension}'
        legacy_path = os.path.join(carpeta_destino, legacy_name)
        if not os.path.exists(legacy_path):
            continue
        nuevo_nombre = f'producto_{id_producto}_1.{extension}'
        nuevo_path = os.path.join(carpeta_destino, nuevo_nombre)
        os.replace(legacy_path, nuevo_path)
        break


def limpiar_imagenes_producto(id_producto):
    carpeta_destino = os.path.join('static', 'img', 'Empresa')
    if not os.path.isdir(carpeta_destino):
        return

    prefijo_galeria = f'producto_{id_producto}_'.lower()
    prefijo_legacy = f'producto_{id_producto}.'.lower()
    for nombre in os.listdir(carpeta_destino):
        nombre_lower = nombre.lower()
        if not (nombre_lower.startswith(prefijo_galeria) or nombre_lower.startswith(prefijo_legacy)):
            continue
        if extension_imagen(nombre_lower) not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        ruta = os.path.join(carpeta_destino, nombre)
        if os.path.isfile(ruta):
            os.remove(ruta)


def guardar_galeria_producto(id_producto, imagenes, reemplazar=True):
    carpeta_destino = os.path.join('static', 'img', 'Empresa')
    os.makedirs(carpeta_destino, exist_ok=True)

    imagenes_validas = [img for img in imagenes if img and str(getattr(img, 'filename', '')).strip()]
    if reemplazar:
        limpiar_imagenes_producto(id_producto)
        indice_inicial = 1
    else:
        migrar_legacy_a_galeria(id_producto)
        existentes = listar_archivos_galeria_producto(id_producto)
        indice_inicial = (existentes[-1][0] + 1) if existentes else 1

    rutas_guardadas = []
    for indice, imagen in enumerate(imagenes_validas, start=indice_inicial):
        extension = extension_imagen(imagen.filename)
        nombre_archivo = f'producto_{id_producto}_{indice}.{extension}'
        ruta_absoluta = os.path.join(carpeta_destino, nombre_archivo)
        imagen.save(ruta_absoluta)
        rutas_guardadas.append(f"img/Empresa/{nombre_archivo}".replace('\\', '/'))
    return rutas_guardadas


def obtener_galeria_producto(id_producto, imagen_principal=''):
    try:
        id_producto_int = int(float(id_producto))
    except (TypeError, ValueError):
        return [normalizar_imagen_url(imagen_principal)] if str(imagen_principal).strip() else []

    galeria = listar_archivos_galeria_producto(id_producto_int)
    rutas = [f"img/Empresa/{nombre}".replace('\\', '/') for _, nombre in galeria]

    if not rutas:
        carpeta_destino = os.path.join('static', 'img', 'Empresa')
        if str(imagen_principal).strip():
            rutas.append(normalizar_imagen_url(imagen_principal))
        else:
            for extension in sorted(ALLOWED_IMAGE_EXTENSIONS):
                legacy_name = f'producto_{id_producto_int}.{extension}'
                legacy_path = os.path.join(carpeta_destino, legacy_name)
                if os.path.exists(legacy_path):
                    rutas.append(f"img/Empresa/{legacy_name}")
                    break
    return rutas


def cargar_productos_df():
    productos = read_table_df('producto')
    for column in PRODUCTO_COLUMNS:
        if column not in productos.columns:
            if column == 'eliminado':
                productos[column] = False
            elif column in {'precio'}:
                productos[column] = 0.0
            elif column in {'stock', 'id_categoria'}:
                productos[column] = 0
            else:
                productos[column] = ''

    productos = normalizar_imagenes_productos(productos)
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
            if column == 'eliminado':
                productos[column] = False
            elif column in {'precio'}:
                productos[column] = 0.0
            elif column in {'stock', 'id_categoria'}:
                productos[column] = 0
            else:
                productos[column] = ''

    replace_table_df('producto', productos[PRODUCTO_COLUMNS])


def cargar_productos_activos_df():
    productos = cargar_productos_df()
    return productos[productos['eliminado'] == False].copy()


def cargar_pedidos_df():
    pedidos = read_table_df('pedidos')
    for column in PEDIDO_COLUMNS:
        if column not in pedidos.columns:
            pedidos[column] = '' if column in {'id_usuario', 'fecha_pedido', 'estado'} else 0
    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    pedidos['id_usuario'] = pedidos['id_usuario'].fillna('')
    pedidos['fecha_pedido'] = pedidos['fecha_pedido'].fillna('')
    pedidos['estado'] = pedidos['estado'].fillna('pendiente')
    return pedidos[PEDIDO_COLUMNS]


def guardar_pedidos_df(pedidos):
    pedidos = pedidos.copy()
    for column in PEDIDO_COLUMNS:
        if column not in pedidos.columns:
            pedidos[column] = '' if column in {'id_usuario', 'fecha_pedido', 'estado'} else 0
    replace_table_df('pedidos', pedidos[PEDIDO_COLUMNS])


def cargar_detalle_pedido_df():
    detalle = read_table_df('detalle_pedido')
    for column in DETALLE_PEDIDO_COLUMNS:
        if column not in detalle.columns:
            detalle[column] = 0
    detalle['id_detalle'] = pd.to_numeric(detalle['id_detalle'], errors='coerce')
    detalle['id_pedido'] = pd.to_numeric(detalle['id_pedido'], errors='coerce')
    detalle['id_producto'] = pd.to_numeric(detalle['id_producto'], errors='coerce')
    detalle['cantidad'] = pd.to_numeric(detalle['cantidad'], errors='coerce').fillna(0)
    detalle['subtotal'] = pd.to_numeric(detalle['subtotal'], errors='coerce').fillna(0.0)
    return detalle[DETALLE_PEDIDO_COLUMNS]


def guardar_detalle_pedido_df(detalle):
    detalle = detalle.copy()
    for column in DETALLE_PEDIDO_COLUMNS:
        if column not in detalle.columns:
            detalle[column] = 0
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


def registrar_actividad(accion):
    registros = cargar_registros_df()
    nuevo_id = int(pd.to_numeric(registros['id_registro'], errors='coerce').max() + 1) if not registros.empty else 1
    actor = session.get('usuario', 'admin')
    nuevo_registro = {
        'id_registro': nuevo_id,
        'id_usuario': actor,
        'accion': accion,
        'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
    guardar_registros_df(registros)


def obtener_nombre_sesion():
    nombre = str(session.get('nombre', '')).strip()
    if nombre:
        return nombre

    email = str(session.get('usuario', '')).strip()
    if not email:
        return 'Administrador'

    usuarios = cargar_usuarios_df()
    if {'email', 'nombre'}.issubset(usuarios.columns):
        coincidencia = usuarios[usuarios['email'].astype(str).str.lower() == email.lower()]
        if not coincidencia.empty:
            nombre_excel = str(coincidencia.iloc[0].get('nombre', '')).strip()
            if nombre_excel:
                session['nombre'] = nombre_excel
                return nombre_excel

    return email.split('@')[0] if '@' in email else email


def formatear_cop(valor):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        numero = 0.0
    valor_formateado = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{CURRENCY_CODE} {valor_formateado}"


def _construir_datos_recibo_pos(id_pedido):
    detalle = cargar_detalle_pedido_df()
    if detalle.empty:
        raise ValueError(f'No existe detalle para el pedido #{id_pedido}.')

    detalle = detalle.copy()
    detalle['id_pedido'] = pd.to_numeric(detalle['id_pedido'], errors='coerce')
    detalle = detalle[detalle['id_pedido'] == int(id_pedido)]
    if detalle.empty:
        raise ValueError(f'No existe detalle para el pedido #{id_pedido}.')

    if 'id_detalle' in detalle.columns:
        detalle = detalle.sort_values(by='id_detalle', ascending=True, na_position='last')

    productos_df = cargar_productos_df()
    productos_df['id_producto'] = pd.to_numeric(productos_df['id_producto'], errors='coerce')
    productos_map = {}
    for _, row in productos_df.iterrows():
        if pd.notna(row.get('id_producto')):
            productos_map[int(row['id_producto'])] = str(row.get('nombre', '')).strip()

    items = []
    for _, row in detalle.iterrows():
        id_producto = int(pd.to_numeric(row.get('id_producto'), errors='coerce') or 0)
        cantidad = int(pd.to_numeric(row.get('cantidad', 0), errors='coerce') or 0)
        subtotal = float(pd.to_numeric(row.get('subtotal', 0), errors='coerce') or 0)
        if cantidad <= 0:
            cantidad = 1
        valor_unitario = subtotal / cantidad if cantidad else subtotal
        descripcion = productos_map.get(id_producto, f"Producto #{id_producto}")
        items.append({
            'cantidad': cantidad,
            'descripcion': descripcion,
            'valor_unitario': float(valor_unitario),
            'total': float(subtotal)
        })

    pagos = cargar_pagos_df()
    pagos['id_pedido'] = pd.to_numeric(pagos['id_pedido'], errors='coerce')
    pago_pedido = pagos[pagos['id_pedido'] == int(id_pedido)].copy()
    pago_row = None
    if not pago_pedido.empty:
        pago_pedido['id_pago'] = pd.to_numeric(pago_pedido['id_pago'], errors='coerce')
        pago_pedido = pago_pedido.sort_values(by='id_pago', ascending=False, na_position='last')
        pago_row = pago_pedido.iloc[0]

    metodo_pago = ''
    monto_total = float(sum(item['total'] for item in items))
    descuento_total = 0.0
    if pago_row is not None:
        metodo_pago = str(pago_row.get('metodo_pago', '')).strip().lower()
        monto_total = float(pd.to_numeric(pago_row.get('monto', monto_total), errors='coerce') or monto_total)
        descuento_total = float(pd.to_numeric(pago_row.get('monto_descuento', 0), errors='coerce') or 0)

    metodo_label = {
        'efectivo': 'Efectivo',
        'tarjeta': 'Tarjeta',
        'transferencia': 'Transferencia',
        'qr': 'QR'
    }.get(metodo_pago, metodo_pago.title() if metodo_pago else 'No especificado')

    pedidos = cargar_pedidos_df()
    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    pedido_row = pedidos[pedidos['id_pedido'] == int(id_pedido)]
    fecha_compra = datetime.now()
    if not pedido_row.empty:
        fecha_raw = pedido_row.iloc[0].get('fecha_pedido', '')
        fecha_parseada = pd.to_datetime(fecha_raw, errors='coerce')
        if pd.notna(fecha_parseada):
            fecha_compra = fecha_parseada.to_pydatetime()

    cliente_nombre = ''
    cliente_correo = ''
    cliente_documento = ''
    cliente_telefono = ''
    ultimo_recibo = session.get('ultimo_recibo_pos', {})
    if str(ultimo_recibo.get('id_pedido', '')) == str(id_pedido):
        cliente_nombre = str(ultimo_recibo.get('cliente_nombre', '')).strip()
        cliente_correo = str(ultimo_recibo.get('cliente_correo', '')).strip()
        cliente_documento = str(ultimo_recibo.get('cliente_documento', '')).strip()
        cliente_telefono = str(ultimo_recibo.get('cliente_telefono', '')).strip()

    subtotal_bruto = max(0.0, monto_total + descuento_total)
    return {
        'id_pedido': int(id_pedido),
        'fecha_compra': fecha_compra,
        'metodo_pago': metodo_label,
        'items': items,
        'subtotal_bruto': float(subtotal_bruto),
        'descuento_total': float(descuento_total),
        'total': float(monto_total),
        'cliente_nombre': cliente_nombre,
        'cliente_correo': cliente_correo,
        'cliente_documento': cliente_documento,
        'cliente_telefono': cliente_telefono
    }


def _particionar_items_recibo(items, max_items_por_pagina=8):
    items = list(items or [])
    if not items:
        return [[]]
    return [items[i:i + max_items_por_pagina] for i in range(0, len(items), max_items_por_pagina)]


def _construir_contexto_recibo_pos(id_pedido):
    datos = _construir_datos_recibo_pos(id_pedido)
    fecha_txt = datos['fecha_compra'].strftime('%d / %m / %Y')
    hora_txt = datos['fecha_compra'].strftime('%H:%M:%S')

    items_formateados = []
    for item in datos.get('items', []):
        items_formateados.append({
            'cantidad': int(pd.to_numeric(item.get('cantidad', 0), errors='coerce') or 0),
            'descripcion': str(item.get('descripcion', '') or '').strip(),
            'valor_unitario': formatear_cop(item.get('valor_unitario', 0)),
            'total': formatear_cop(item.get('total', 0))
        })

    paginas_items = _particionar_items_recibo(items_formateados, max_items_por_pagina=8)
    total_paginas = len(paginas_items)
    paginas = []
    for i, items_pagina in enumerate(paginas_items, start=1):
        paginas.append({
            'numero': i,
            'detalle_items': items_pagina,
            'es_ultima': i == total_paginas
        })

    cliente_campos = []
    cliente_nombre = str(datos.get('cliente_nombre', '') or '').strip()
    cliente_doc = str(datos.get('cliente_documento', '') or '').strip()
    cliente_tel = str(datos.get('cliente_telefono', '') or '').strip()
    cliente_mail = str(datos.get('cliente_correo', '') or '').strip()
    if cliente_nombre:
        cliente_campos.append({'label': 'Nombre', 'valor': cliente_nombre})
    if cliente_doc:
        cliente_campos.append({'label': 'Documento', 'valor': cliente_doc})
    if cliente_tel:
        cliente_campos.append({'label': 'Telefono', 'valor': cliente_tel})
    if cliente_mail:
        cliente_campos.append({'label': 'Correo', 'valor': cliente_mail})

    return {
        'id_pedido': int(datos['id_pedido']),
        'codigo_recibo': f"POS-{int(datos['id_pedido']):06d}",
        'fecha_txt': fecha_txt,
        'hora_txt': hora_txt,
        'paginas': paginas,
        'total_paginas': total_paginas,
        'cliente_campos': cliente_campos,
        'cantidad_items': len(items_formateados),
        'metodo_pago': str(datos.get('metodo_pago', 'No especificado') or 'No especificado'),
        'subtotal_txt': formatear_cop(datos.get('subtotal_bruto', 0)),
        'descuento_txt': formatear_cop(datos.get('descuento_total', 0)),
        'total_txt': formatear_cop(datos.get('total', 0)),
        'observaciones': (
            "Prendas confeccionadas bajo estandares de resistencia, "
            "durabilidad y ergonomia para uso tactico y operativo."
        )
    }


def _cargar_css_recibo_pos():
    ruta_css = os.path.join(app.root_path, 'static', 'css', 'administrador', 'admin_pos_recibo.css')
    if not os.path.exists(ruta_css):
        return ''
    try:
        with open(ruta_css, 'r', encoding='utf-8') as f_css:
            return f_css.read()
    except UnicodeDecodeError:
        with open(ruta_css, 'r', encoding='latin-1') as f_css:
            return f_css.read()


def _cargar_marca_agua_recibo_src():
    carpeta = os.path.join(app.root_path, 'static', 'img', 'Pagina')
    candidatos = ('recibo.png', 'nachoher_fondo_logo.jpg', 'logo.jpeg')
    mime_por_ext = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }

    for nombre in candidatos:
        ruta = Path(carpeta) / nombre
        if not ruta.exists():
            continue
        try:
            return ruta.resolve().as_uri()
        except ValueError:
            pass

        ext = ruta.suffix.lower()
        mime = mime_por_ext.get(ext, 'application/octet-stream')
        with open(ruta, 'rb') as f_img:
            contenido_b64 = base64.b64encode(f_img.read()).decode('ascii')
        return f"data:{mime};base64,{contenido_b64}"
    return ''


def render_html_recibo_pos(id_pedido):
    contexto = _construir_contexto_recibo_pos(id_pedido)
    css_content = _cargar_css_recibo_pos()
    return render_template(
        'Administrador/Sistema POS/recibo_pos_pdf.html',
        css_content=css_content,
        watermark_image_src=_cargar_marca_agua_recibo_src(),
        **contexto
    )


def _buscar_msedge():
    candidatos = []

    edge_env = str(os.environ.get('EDGE_PATH', '')).strip()
    if edge_env:
        candidatos.append(edge_env)

    for exe in ('msedge.exe', 'msedge'):
        encontrado = shutil.which(exe)
        if encontrado:
            candidatos.append(encontrado)

    candidatos.extend([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ])

    for ruta in candidatos:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


def generar_pdf_recibo_pos(id_pedido):
    html = render_html_recibo_pos(id_pedido)
    ruta_edge = _buscar_msedge()
    if not ruta_edge:
        raise RuntimeError(
            "No se encontro Microsoft Edge para convertir el recibo a PDF. "
            "Configura EDGE_PATH o instala Edge."
        )

    tmp_path = Path(app.root_path) / f"recibo_pos_tmp_{id_pedido}_{os.getpid()}_{int(datetime.now().timestamp() * 1000)}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    try:
        html_path = tmp_path / f"recibo_pos_{id_pedido}.html"
        pdf_path = tmp_path / f"recibo_pos_{id_pedido}.pdf"
        user_data_dir = tmp_path

        html_path.write_text(html, encoding='utf-8')

        comando = [
            ruta_edge,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            "--no-sandbox",
            "--disable-breakpad",
            "--no-first-run",
            "--no-default-browser-check",
            "--allow-file-access-from-files",
            f"--user-data-dir={str(user_data_dir)}",
            f"--print-to-pdf={str(pdf_path)}",
            html_path.resolve().as_uri()
        ]

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=90
        )

        if resultado.returncode != 0 or not pdf_path.exists():
            detalle_error = (resultado.stderr or resultado.stdout or '').strip()
            if detalle_error:
                detalle_error = detalle_error.splitlines()[0]
            raise RuntimeError(f"No se pudo convertir el recibo a PDF. {detalle_error}")

        return pdf_path.read_bytes()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def obtener_productos_agotados():
    productos = cargar_productos_df()
    if productos.empty:
        return []

    agotados = productos[(productos['eliminado'] == False) & (productos['stock'] <= 0)].copy()
    if agotados.empty:
        return []

    agotados = agotados.sort_values(by='nombre', na_position='last')
    return agotados[['id_producto', 'nombre', 'stock']].to_dict(orient='records')


def normalizar_carrito_por_stock(carrito):
    if not carrito:
        return [], []

    productos = cargar_productos_df()
    if 'id_producto' not in productos.columns:
        return carrito, []

    inventario = {}
    for _, row in productos.iterrows():
        if pd.isna(row['id_producto']):
            continue
        inventario[int(row['id_producto'])] = {
            'nombre': str(row.get('nombre', '')).strip(),
            'precio': float(row.get('precio', 0.0)),
            'stock': int(row.get('stock', 0)),
            'eliminado': bool(row.get('eliminado', False))
        }

    carrito_limpio = []
    cambios = []

    for item in carrito:
        id_producto = pd.to_numeric(item.get('id_producto'), errors='coerce')
        cantidad_item = pd.to_numeric(item.get('cantidad', 0), errors='coerce')
        if pd.isna(id_producto) or pd.isna(cantidad_item):
            continue

        id_producto = int(id_producto)
        cantidad = max(0, int(cantidad_item))
        if cantidad <= 0:
            continue

        referencia = inventario.get(id_producto)
        nombre_item = str(item.get('nombre', f'ID {id_producto}'))
        if referencia is None or referencia['eliminado'] or referencia['stock'] <= 0:
            cambios.append(f'Se removio "{nombre_item}" porque ya no tiene stock.')
            continue

        stock_actual = int(referencia['stock'])
        cantidad_final = min(cantidad, stock_actual)
        if cantidad_final < cantidad:
            cambios.append(f'Se ajusto "{nombre_item}" de {cantidad} a {cantidad_final} por stock disponible.')

        precio_final = float(referencia['precio']) if referencia['precio'] > 0 else float(item.get('precio', 0))
        carrito_limpio.append({
            'id_producto': id_producto,
            'nombre': referencia['nombre'] or nombre_item,
            'cantidad': cantidad_final,
            'precio': precio_final,
            'subtotal': float(precio_final) * cantidad_final
        })

    return carrito_limpio, cambios


@app.template_filter('cop')
def cop_filter(valor):
    return formatear_cop(valor)


@app.context_processor
def inyectar_nombre_admin():
    admin_nombre = ''
    if session.get('rol') == 'admin':
        admin_nombre = obtener_nombre_sesion()
    return {
        'admin_nombre': admin_nombre,
        'currency_code': CURRENCY_CODE,
        'currency_name': CURRENCY_NAME
    }

@app.route('/')
def home():
    productos = cargar_productos_activos_df()
    lista_productos = productos.to_dict(orient='records')
    return render_template('Usuarios/Autenticacion/login.html', productos=lista_productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Usuarios/Autenticacion/login_form.html')
    usuarios = cargar_usuarios_df()  # leer cada vez
    email = request.form['email']
    password = request.form['password']

    usuario = usuarios[(usuarios['email'] == email) & (usuarios['password_hash'] == password)]

    if not usuario.empty:
        estado = str(usuario.iloc[0].get('estado', 'activo')).strip().lower()
        if estado != 'activo':
            return "Tu usuario está inactivo. Contacta al administrador."

        rol = usuario.iloc[0]['rol']
        id_usuario = usuario.iloc[0]['id_usuario']
        nombre = str(usuario.iloc[0].get('nombre', '')).strip()
        session['usuario'] = email
        session['id_usuario'] = int(id_usuario)
        session['rol'] = rol
        session['nombre'] = nombre

        registrar_actividad("Inicio de sesión exitoso")

        if rol == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    else:
        return "Credenciales inválidas. Intenta de nuevo."

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = 'normal'

        usuarios = cargar_usuarios_df()

        if email in usuarios['email'].values:
            return "Este correo ya está registrado."

        ultimo_id = pd.to_numeric(usuarios['id_usuario'], errors='coerce').max()
        nuevo_id = int(ultimo_id + 1) if pd.notna(ultimo_id) else 1
        nuevo_usuario = {
            'id_usuario': nuevo_id,
            'nombre': nombre,
            'email': email,
            'password_hash': password,
            'rol': rol,
            'estado': 'activo',
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        guardar_usuarios_df(usuarios)
        registrar_actividad(f"Nuevo usuario registrado: {nombre}")

        # Iniciar sesión automáticamente después del registro
        session['usuario'] = email
        session['id_usuario'] = int(nuevo_id)
        session['rol'] = rol
        session['nombre'] = nombre

        return redirect(url_for('user_dashboard'))

    return render_template('Usuarios/Autenticacion/registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if session.get('rol') == 'admin':
        productos = cargar_productos_activos_df()
        lista_productos = productos.to_dict(orient='records')
        productos_agotados = obtener_productos_agotados()
        admin_nombre = obtener_nombre_sesion()

        # Métricas de usuarios y ventas últimos 30 días
        hoy = datetime.now()
        hace_30 = hoy - timedelta(days=30)

        usuarios_df = cargar_usuarios_df()
        if not usuarios_df.empty and 'fecha_registro' in usuarios_df.columns:
            # Normaliza la zona horaria para evitar comparaciones entre tz-aware y tz-naive
            usuarios_df['fecha_registro_dt'] = (
                pd.to_datetime(usuarios_df['fecha_registro'], errors='coerce', utc=True)
                .dt.tz_convert(None)
            )
            usuarios_ult_mes = usuarios_df[usuarios_df['fecha_registro_dt'] >= hace_30]['id_usuario'].nunique()
        else:
            usuarios_ult_mes = 0

        pedidos_df = cargar_pedidos_df()
        usuarios_compraron_ult_mes = 0
        if not pedidos_df.empty:
            pedidos_df['fecha_pedido_dt'] = (
                pd.to_datetime(pedidos_df['fecha_pedido'], dayfirst=True, errors='coerce', utc=True)
                .dt.tz_convert(None)
            )
            pedidos_ult_mes = pedidos_df[pedidos_df['fecha_pedido_dt'] >= hace_30]
            usuarios_compraron_ult_mes = pedidos_ult_mes['id_usuario'].nunique()

        # Top productos vendidos (totales)
        detalle_df = cargar_detalle_pedido_df()
        top_productos = []
        if not detalle_df.empty:
            detalle_df['cantidad'] = pd.to_numeric(detalle_df.get('cantidad', 0), errors='coerce').fillna(0)
            top_df = detalle_df.groupby('id_producto', as_index=False)['cantidad'].sum().sort_values('cantidad', ascending=False).head(5)
            prod_ref = productos[['id_producto', 'nombre']] if not productos.empty else pd.DataFrame(columns=['id_producto', 'nombre'])
            top_df = pd.merge(top_df, prod_ref, on='id_producto', how='left')
            top_productos = top_df.to_dict(orient='records')

        # plantilla actual en el proyecto
        return render_template(
            'Administrador/admin_dashboard_principal.html',
            productos=lista_productos,
            admin_nombre=admin_nombre,
            productos_agotados=productos_agotados,
            usuarios_ult_mes=usuarios_ult_mes,
            usuarios_compraron_ult_mes=usuarios_compraron_ult_mes,
            top_productos=top_productos
        )
    return "Acceso denegado"


@app.route('/admin/productos')
def admin_productos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos_todos = cargar_productos_df()
    total_eliminados = int(productos_todos['eliminado'].fillna(False).astype(bool).sum())
    productos = cargar_productos_activos_df()
    total_productos = len(productos)
    busqueda = request.args.get('q', '').strip()
    fuerza_filtro = request.args.get('fuerza', '').strip()
    intendencia_filtro = request.args.get('intendencia', '').strip()

    if fuerza_filtro and fuerza_filtro not in FUERZAS_OPCIONES:
        fuerza_filtro = ''
    if intendencia_filtro and intendencia_filtro not in INTENDENCIAS_OPCIONES:
        intendencia_filtro = ''

    if busqueda:
        filtros = [
            productos['nombre'].str.contains(busqueda, case=False, na=False, regex=False),
            productos['descripcion'].str.contains(busqueda, case=False, na=False, regex=False),
            productos['fuerza'].str.contains(busqueda, case=False, na=False, regex=False),
            productos['intendencia'].str.contains(busqueda, case=False, na=False, regex=False),
            productos['id_producto'].fillna('').astype(str).str.contains(busqueda, case=False, na=False, regex=False),
        ]
        mascara = filtros[0]
        for filtro in filtros[1:]:
            mascara = mascara | filtro
        productos = productos[mascara].copy()

    if fuerza_filtro:
        productos = productos[productos['fuerza'].str.strip() == fuerza_filtro].copy()

    if intendencia_filtro:
        productos = productos[productos['intendencia'].str.strip() == intendencia_filtro].copy()

    hay_filtros = bool(busqueda or fuerza_filtro or intendencia_filtro)
    lista_productos = productos.to_dict(orient='records')
    productos_por_fuerza = {fuerza: [] for fuerza in FUERZAS_OPCIONES}

    for producto in lista_productos:
        imagen_principal = str(producto.get('imagen_url', '')).strip()
        galeria = obtener_galeria_producto(producto.get('id_producto'), imagen_principal)
        producto['imagenes'] = galeria
        if galeria:
            producto['imagen_url'] = galeria[0]

        fuerza_producto = str(producto.get('fuerza', '')).strip().lower()
        for fuerza in FUERZAS_OPCIONES:
            if fuerza_producto == fuerza.lower():
                productos_por_fuerza[fuerza].append(producto)
                break

    return render_template(
        'Administrador/Gestion productos/admin_prod_dashboard.html',
        productos=lista_productos,
        productos_por_fuerza=productos_por_fuerza,
        fuerzas=FUERZAS_OPCIONES,
        intendencias=INTENDENCIAS_OPCIONES,
        search_query=busqueda,
        selected_fuerza=fuerza_filtro,
        selected_intendencia=intendencia_filtro,
        has_filters=hay_filtros,
        total_productos=total_productos,
        total_eliminados=total_eliminados,
        max_images_per_product=MAX_IMAGES_PER_PRODUCT
    )


@app.route('/admin/agregar_producto', methods=['POST'])
def agregar_producto():
    if session.get('rol') == 'admin':
        productos = cargar_productos_df()
        nuevo_id = next_id('producto', 'id_producto')
        fuerza = request.form.get('fuerza', '').strip()
        intendencia = request.form.get('intendencia', '').strip()
        if fuerza not in FUERZAS_OPCIONES or intendencia not in INTENDENCIAS_OPCIONES:
            flash('Selecciona una fuerza e intendencia validas.', 'danger')
            return redirect(url_for('admin_productos'))

        imagenes = [
            archivo for archivo in request.files.getlist('imagenes')
            if archivo and str(getattr(archivo, 'filename', '')).strip()
        ]
        if not imagenes:
            imagen_unica = request.files.get('imagen')
            if imagen_unica and str(getattr(imagen_unica, 'filename', '')).strip():
                imagenes = [imagen_unica]

        if len(imagenes) > MAX_IMAGES_PER_PRODUCT:
            flash(f'Solo puedes subir hasta {MAX_IMAGES_PER_PRODUCT} imagenes por producto.', 'danger')
            return redirect(url_for('admin_productos'))

        for imagen in imagenes:
            error_validacion = validar_archivo_imagen(imagen)
            if error_validacion:
                flash(error_validacion, 'danger')
                return redirect(url_for('admin_productos'))

        galeria_guardada = guardar_galeria_producto(nuevo_id, imagenes, reemplazar=True)
        imagen_url = galeria_guardada[0] if galeria_guardada else ''

        nuevo_producto = {
            'id_producto': nuevo_id,
            'nombre': request.form['nombre'],
            'descripcion': request.form['descripcion'],
            'precio': float(request.form['precio']),
            'stock': int(request.form['stock']),
            'id_categoria': 1,  # Se conserva por compatibilidad
            'fuerza': fuerza,
            'intendencia': intendencia,
            'imagen_url': imagen_url,
            'eliminado': False
        }

        productos = pd.concat([productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
        guardar_productos_df(productos)

        registrar_actividad(
            f"Creo producto '{request.form['nombre']}' (ID {nuevo_id})\n"
            f"- precio: {formatear_cop(float(request.form['precio']))}\n"
            f"- stock: {int(request.form['stock'])}\n"
            f"- fuerza: {fuerza}\n"
            f"- intendencia: {intendencia}\n"
            f"- imagenes: {len(galeria_guardada)}"
        )

        return redirect(url_for('admin_productos'))
    return "Acceso denegado"

@app.route('/admin/sales/export')
def export_sales():
    if session.get('rol') != 'admin':
        return "Acceso denegado"
    
    pedidos = cargar_pedidos_df()
    pagos = cargar_pagos_df()
    detalle = cargar_detalle_pedido_df()
    
    # Combinar los datos
    informe = pd.merge(pedidos, pagos, on='id_pedido', how='left')
    
    # Agregar totales por pedido
    totales_pedido = detalle.groupby('id_pedido')['subtotal'].sum().reset_index()
    totales_pedido.columns = ['id_pedido', 'total_productos']
    informe = pd.merge(informe, totales_pedido, on='id_pedido', how='left')
    
    # Convertir a CSV
    csv_data = informe.to_csv(index=False)
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )


@app.route('/admin/imagen/<int:id_producto>', methods=['POST'])
def subir_imagen(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    imagenes = [
        archivo for archivo in request.files.getlist('imagenes')
        if archivo and str(getattr(archivo, 'filename', '')).strip()
    ]
    if not imagenes:
        imagen_unica = request.files.get('imagen')
        if imagen_unica and str(getattr(imagen_unica, 'filename', '')).strip():
            imagenes = [imagen_unica]

    if not imagenes:
        flash("No se seleccionó ninguna imagen.")
        return redirect(url_for('admin_productos'))

    if len(imagenes) > MAX_IMAGES_PER_PRODUCT:
        flash(f'Solo puedes subir hasta {MAX_IMAGES_PER_PRODUCT} imagenes por producto.', 'danger')
        return redirect(url_for('admin_productos'))

    for imagen in imagenes:
        error_validacion = validar_archivo_imagen(imagen)
        if error_validacion:
            flash(error_validacion, 'danger')
            return redirect(url_for('admin_productos'))

    galeria_guardada = guardar_galeria_producto(id_producto, imagenes, reemplazar=True)

    productos = cargar_productos_df()
    idx = productos[productos['id_producto'] == id_producto].index
    if not idx.empty:
        productos.at[idx[0], 'imagen_url'] = galeria_guardada[0] if galeria_guardada else ''
        guardar_productos_df(productos)
        flash(f"Galeria reemplazada ({len(galeria_guardada)} imagenes).", 'success')
    else:
        flash("Producto no encontrado.", 'danger')

    return redirect(url_for('admin_productos'))


@app.route('/admin/imagen/agregar/<int:id_producto>', methods=['POST'])
def agregar_imagenes_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    imagenes = [
        archivo for archivo in request.files.getlist('imagenes_agregar')
        if archivo and str(getattr(archivo, 'filename', '')).strip()
    ]
    if not imagenes:
        imagenes = [
            archivo for archivo in request.files.getlist('imagenes')
            if archivo and str(getattr(archivo, 'filename', '')).strip()
        ]

    if not imagenes:
        flash("No se seleccionaron imagenes para agregar.", 'warning')
        return redirect(url_for('admin_productos'))

    for imagen in imagenes:
        error_validacion = validar_archivo_imagen(imagen)
        if error_validacion:
            flash(error_validacion, 'danger')
            return redirect(url_for('admin_productos'))

    productos = cargar_productos_df()
    idx = productos[productos['id_producto'] == id_producto].index
    if idx.empty:
        flash("Producto no encontrado.", 'danger')
        return redirect(url_for('admin_productos'))

    imagen_principal = str(productos.at[idx[0], 'imagen_url']) if 'imagen_url' in productos.columns else ''
    galeria_actual = obtener_galeria_producto(id_producto, imagen_principal)
    if len(galeria_actual) + len(imagenes) > MAX_IMAGES_PER_PRODUCT:
        disponibles = max(0, MAX_IMAGES_PER_PRODUCT - len(galeria_actual))
        flash(
            f"Este producto ya tiene {len(galeria_actual)} imagen(es). "
            f"Solo puedes agregar {disponibles} más (máximo {MAX_IMAGES_PER_PRODUCT}).",
            'danger'
        )
        return redirect(url_for('admin_productos'))

    guardar_galeria_producto(id_producto, imagenes, reemplazar=False)
    galeria_actualizada = obtener_galeria_producto(id_producto, '')
    productos.at[idx[0], 'imagen_url'] = galeria_actualizada[0] if galeria_actualizada else ''
    guardar_productos_df(productos)

    flash(f"Se agregaron {len(imagenes)} imagen(es). Total: {len(galeria_actualizada)}.", 'success')
    return redirect(url_for('admin_productos'))


@app.route('/admin/imagen/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_imagen_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    imagen_a_eliminar = normalizar_imagen_url(request.form.get('imagen_a_eliminar', '').strip())
    if not imagen_a_eliminar:
        flash("Selecciona una imagen para eliminar.", 'warning')
        return redirect(url_for('admin_productos'))

    productos = cargar_productos_df()
    idx = productos[productos['id_producto'] == id_producto].index
    if idx.empty:
        flash("Producto no encontrado.", 'danger')
        return redirect(url_for('admin_productos'))

    imagen_principal = str(productos.at[idx[0], 'imagen_url']) if 'imagen_url' in productos.columns else ''
    galeria_actual = obtener_galeria_producto(id_producto, imagen_principal)
    if imagen_a_eliminar not in galeria_actual:
        flash("La imagen seleccionada no pertenece a este producto.", 'danger')
        return redirect(url_for('admin_productos'))

    ruta_absoluta = ruta_imagen_producto_absoluta(imagen_a_eliminar)
    if ruta_absoluta and os.path.exists(ruta_absoluta):
        os.remove(ruta_absoluta)

    galeria_actualizada = obtener_galeria_producto(id_producto, '')
    productos.at[idx[0], 'imagen_url'] = galeria_actualizada[0] if galeria_actualizada else ''
    guardar_productos_df(productos)

    flash(f"Imagen eliminada. Total actual: {len(galeria_actualizada)}.", 'success')
    return redirect(url_for('admin_productos'))



@app.route('/admin/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = cargar_productos_df()

    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        productos.at[idx[0], 'eliminado'] = True
        guardar_productos_df(productos)

        nombre = productos.at[idx[0], 'nombre']
        registrar_actividad(f"Elimino producto: {nombre} (ID {id_producto})")

    return redirect(url_for('admin_productos'))

@app.route('/admin/eliminar_definitivo/<int:id_producto>', methods=['POST'])
def eliminar_definitivo(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = cargar_productos_df()
    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        nombre = productos.at[idx[0], 'nombre']
        productos = productos.drop(index=idx)
        guardar_productos_df(productos)

        registrar_actividad(f"Elimino definitivamente el producto: {nombre} (ID {id_producto})")

    return redirect(url_for('admin_papelera'))

@app.route('/admin/restaurar/<int:id_producto>', methods=['POST'])
def restaurar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = cargar_productos_df()
    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        productos.at[idx[0], 'eliminado'] = False
        guardar_productos_df(productos)

        nombre = productos.at[idx[0], 'nombre']
        registrar_actividad(f"Restauro producto: {nombre} (ID {id_producto})")

    return redirect(url_for('admin_papelera'))


@app.route('/admin/papelera')
def admin_papelera():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = cargar_productos_df()
    eliminados = productos[productos['eliminado'] == True].to_dict(orient='records')
    return render_template('Administrador/Papelera/admin_papelera.html', productos=eliminados)


@app.route('/admin/usuarios')
def admin_usuarios():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    usuarios = cargar_usuarios_df()
    usuarios['id_usuario'] = pd.to_numeric(usuarios['id_usuario'], errors='coerce')

    buscar = request.args.get('buscar', '').strip()
    rol = request.args.get('rol', '').strip()
    estado = request.args.get('estado', '').strip().lower()
    orden = request.args.get('orden', 'reciente').strip()
    edit_id = request.args.get('edit_id', type=int)

    filtrados = usuarios.copy()
    if buscar:
        mask = (
            filtrados['nombre'].astype(str).str.contains(buscar, case=False, na=False) |
            filtrados['email'].astype(str).str.contains(buscar, case=False, na=False)
        )
        filtrados = filtrados[mask]

    if rol:
        filtrados = filtrados[filtrados['rol'].astype(str).str.lower() == rol.lower()]
    if estado in ['activo', 'inactivo']:
        filtrados = filtrados[filtrados['estado'].astype(str).str.lower() == estado]

    if orden == 'antiguo':
        filtrados = filtrados.sort_values(by='id_usuario', ascending=True, na_position='last')
    elif orden == 'nombre':
        filtrados = filtrados.sort_values(by='nombre', ascending=True, na_position='last')
    else:
        filtrados = filtrados.sort_values(by='id_usuario', ascending=False, na_position='last')

    usuario_editar = None
    if edit_id is not None:
        candidato = usuarios[usuarios['id_usuario'] == edit_id]
        if not candidato.empty:
            usuario_editar = candidato.iloc[0].to_dict()
            if pd.notna(usuario_editar.get('id_usuario')):
                usuario_editar['id_usuario'] = int(usuario_editar['id_usuario'])
            usuario_editar['estado'] = str(usuario_editar.get('estado', 'activo')).strip().lower()

    lista_usuarios = filtrados.fillna('').to_dict(orient='records')
    for usuario in lista_usuarios:
        if usuario.get('id_usuario') != '':
            usuario['id_usuario'] = int(usuario['id_usuario'])
        usuario['estado'] = str(usuario.get('estado', 'activo')).strip().lower()

    filtros = {'buscar': buscar, 'rol': rol, 'estado': estado, 'orden': orden}
    return render_template(
        'Administrador/Gestion usuarios/admin_usuario.html',
        usuarios=lista_usuarios,
        usuario_editar=usuario_editar,
        filtros=filtros
    )


@app.route('/admin/usuarios/guardar', methods=['POST'])
def admin_guardar_usuario():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    id_usuario_raw = request.form.get('id_usuario', '').strip()
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    rol = request.form.get('rol', 'normal').strip().lower()
    estado = request.form.get('estado', 'activo').strip().lower()

    if rol not in ['admin', 'normal']:
        rol = 'normal'
    if estado not in ['activo', 'inactivo']:
        estado = 'activo'

    if not nombre or not email:
        flash('Nombre y email son obligatorios.', 'danger')
        return redirect(url_for('admin_usuarios'))

    usuarios = cargar_usuarios_df()
    usuarios['id_usuario'] = pd.to_numeric(usuarios['id_usuario'], errors='coerce')
    usuarios['email'] = usuarios['email'].astype(str)

    edit_id = None
    if id_usuario_raw:
        try:
            edit_id = int(float(id_usuario_raw))
        except ValueError:
            flash('ID de usuario inválido.', 'danger')
            return redirect(url_for('admin_usuarios'))

    if edit_id is None and not password:
        flash('La contraseña es obligatoria para crear usuarios.', 'danger')
        return redirect(url_for('admin_usuarios'))

    existe_email = usuarios[usuarios['email'].str.lower() == email.lower()]
    if edit_id is not None:
        existe_email = existe_email[existe_email['id_usuario'] != edit_id]
    if not existe_email.empty:
        flash('Ese email ya está registrado por otro usuario.', 'danger')
        return redirect(url_for('admin_usuarios'))

    if edit_id is not None:
        idx = usuarios[usuarios['id_usuario'] == edit_id].index
        if idx.empty:
            flash('Usuario no encontrado para edicion.', 'danger')
            return redirect(url_for('admin_usuarios'))

        usuarios.at[idx[0], 'nombre'] = nombre
        usuarios.at[idx[0], 'email'] = email
        usuarios.at[idx[0], 'rol'] = rol
        usuarios.at[idx[0], 'estado'] = estado
        if password:
            usuarios.at[idx[0], 'password_hash'] = password

        guardar_usuarios_df(usuarios[USUARIO_COLUMNS])
        registrar_actividad(f"Actualizo usuario {email} (ID {edit_id})\n- rol: {rol}\n- estado: {estado}")
        flash('Usuario actualizado correctamente.', 'success')
    else:
        ultimo_id = pd.to_numeric(usuarios['id_usuario'], errors='coerce').max()
        nuevo_id = int(ultimo_id + 1) if pd.notna(ultimo_id) else 1

        nuevo_usuario = {
            'id_usuario': nuevo_id,
            'nombre': nombre,
            'email': email,
            'password_hash': password,
            'rol': rol,
            'estado': estado,
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        guardar_usuarios_df(usuarios[USUARIO_COLUMNS])
        registrar_actividad(f"Creo usuario {email} (ID {nuevo_id})\n- rol: {rol}\n- estado: {estado}")
        flash('Usuario creado correctamente.', 'success')

    return redirect(url_for('admin_usuarios'))


@app.route('/admin/registros')
def admin_registros():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    registros = cargar_registros_df()

    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_fecha = request.args.get('fecha', '').strip()

    if filtro_usuario:
        registros = registros[
            registros['id_usuario'].astype(str).str.contains(filtro_usuario, case=False, na=False) |
            registros['accion'].astype(str).str.contains(filtro_usuario, case=False, na=False)
        ]

    if filtro_fecha:
        registros = registros[registros['fecha_accion'].astype(str).str.startswith(filtro_fecha)]

    registros['id_registro'] = pd.to_numeric(registros['id_registro'], errors='coerce')
    registros = registros.sort_values(by='id_registro', ascending=False, na_position='last')

    lista_registros = registros.fillna('').to_dict(orient='records')
    for registro in lista_registros:
        if registro.get('id_registro') != '':
            registro['id_registro'] = int(registro['id_registro'])

    filtros = {'usuario': filtro_usuario, 'fecha': filtro_fecha}
    return render_template(
        'Administrador/Gestion usuarios/admin_registros.html',
        registros=lista_registros,
        filtros=filtros
    )


@app.route('/admin/registros/export_excel')
def admin_registros_export_excel():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    registros = cargar_registros_df()
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_fecha = request.args.get('fecha', '').strip()

    if filtro_usuario:
        registros = registros[
            registros['id_usuario'].astype(str).str.contains(filtro_usuario, case=False, na=False) |
            registros['accion'].astype(str).str.contains(filtro_usuario, case=False, na=False)
        ]
    if filtro_fecha:
        registros = registros[registros['fecha_accion'].astype(str).str.startswith(filtro_fecha)]

    buffer = BytesIO()
    registros.to_excel(buffer, index=False)
    buffer.seek(0)

    nombre_archivo = f"registros_bd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/admin/ajustes')
def admin_ajustes():
    if session.get('rol') != 'admin':
        return "Acceso denegado"
    return render_template('Administrador/Ajustes/admin_ajustes_dashboard.html')


@app.route('/admin/informes')
def admin_informes():
    if session.get('rol') != 'admin':
        return "Acceso denegado"
    return render_template('Administrador/Informes/admin_infor_dashboard.html')


@app.route('/admin/pos')
def admin_pos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    recibo_pedido_id = None
    descargar_recibo = request.args.get('descargar_recibo', '').strip()
    if descargar_recibo:
        try:
            recibo_pedido_id = int(descargar_recibo)
            if recibo_pedido_id <= 0:
                recibo_pedido_id = None
        except ValueError:
            recibo_pedido_id = None

    productos = cargar_productos_activos_df()
    promos = cargar_promociones_df()
    hoy = datetime.now().date()

    mejor_promo_por_producto = {}
    mejor_descuento_por_producto = {}
    for _, row in promos.iterrows():
        promo = row.to_dict()
        if not promocion_esta_aplicable(promo, hoy):
            continue

        id_producto_promo = pd.to_numeric(promo.get('id_producto'), errors='coerce')
        if pd.isna(id_producto_promo):
            continue
        id_prod_int = int(id_producto_promo)

        producto_df = productos[productos['id_producto'] == id_prod_int]
        if producto_df.empty:
            continue

        precio_ref = float(pd.to_numeric(producto_df.iloc[0].get('precio', 0), errors='coerce') or 0)
        descuento_actual = calcular_descuento_promocion(precio_ref, promo)
        if descuento_actual > mejor_descuento_por_producto.get(id_prod_int, -1):
            mejor_descuento_por_producto[id_prod_int] = descuento_actual
            mejor_promo_por_producto[id_prod_int] = promo

    lista_productos = productos.to_dict(orient='records')
    for producto in lista_productos:
        id_producto = int(pd.to_numeric(producto.get('id_producto', 0), errors='coerce') or 0)
        precio_base = float(pd.to_numeric(producto.get('precio', 0), errors='coerce') or 0)
        promo = mejor_promo_por_producto.get(id_producto)

        if promo:
            descuento_unitario = calcular_descuento_promocion(precio_base, promo)
            precio_venta = max(0.0, precio_base - descuento_unitario)
            producto['promo_activa'] = True
            producto['promo_id'] = promo.get('id_promo', '')
            producto['promo_codigo'] = promo.get('codigo', '')
            producto['promo_nombre'] = promo.get('nombre', '')
            producto['promo_tipo_descuento'] = promo.get('tipo_descuento', '')
            producto['promo_valor_descuento'] = float(pd.to_numeric(promo.get('valor_descuento', 0), errors='coerce') or 0)
            producto['promo_descuento_unitario'] = float(descuento_unitario)
            producto['precio_original'] = float(precio_base)
            producto['precio_con_descuento'] = float(precio_venta)
            producto['precio_venta'] = float(precio_venta)
        else:
            producto['promo_activa'] = False
            producto['promo_id'] = ''
            producto['promo_codigo'] = ''
            producto['promo_nombre'] = ''
            producto['promo_tipo_descuento'] = ''
            producto['promo_valor_descuento'] = 0.0
            producto['promo_descuento_unitario'] = 0.0
            producto['precio_original'] = float(precio_base)
            producto['precio_con_descuento'] = float(precio_base)
            producto['precio_venta'] = float(precio_base)

    return render_template(
        'Administrador/Sistema POS/admin_pos_dashboard.html',
        productos=lista_productos,
        fuerzas=FUERZAS_OPCIONES,
        recibo_pedido_id=recibo_pedido_id
    )


@app.route('/admin/pos/recibo/<int:id_pedido>.pdf')
def admin_pos_recibo_pdf(id_pedido):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    try:
        pdf_bytes = generar_pdf_recibo_pos(id_pedido)
    except ValueError as exc:
        return Response(str(exc), status=404, mimetype='text/plain; charset=utf-8')
    except Exception as exc:
        return Response(
            f'No se pudo generar el recibo PDF. {str(exc)}',
            status=500,
            mimetype='text/plain; charset=utf-8'
        )

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"recibo_pos_{id_pedido}.pdf"
    )


@app.route('/admin/pos/recibo/<int:id_pedido>/html')
def admin_pos_recibo_html(id_pedido):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    try:
        return render_html_recibo_pos(id_pedido)
    except ValueError as exc:
        return Response(str(exc), status=404, mimetype='text/plain; charset=utf-8')
    except Exception as exc:
        return Response(
            f'No se pudo generar la vista del recibo. {str(exc)}',
            status=500,
            mimetype='text/plain; charset=utf-8'
        )


@app.route('/admin/pedidos')
def admin_pedidos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    pedidos = cargar_pedidos_df()
    pagos = cargar_pagos_df()
    detalle = cargar_detalle_pedido_df()

    productos = cargar_productos_df()[['id_producto', 'nombre']]

    usuarios = cargar_usuarios_df()

    if 'id_pedido' not in pedidos.columns:
        pedidos['id_pedido'] = pd.Series(dtype='int')
    if 'id_usuario' not in pedidos.columns:
        pedidos['id_usuario'] = ''
    if 'fecha_pedido' not in pedidos.columns:
        pedidos['fecha_pedido'] = ''
    if 'estado' not in pedidos.columns:
        pedidos['estado'] = 'pendiente'

    if 'id_pedido' not in pagos.columns:
        pagos['id_pedido'] = pd.Series(dtype='int')
    if 'id_pago' not in pagos.columns:
        pagos['id_pago'] = pd.Series(dtype='int')
    if 'monto' not in pagos.columns:
        pagos['monto'] = 0
    if 'metodo_pago' not in pagos.columns:
        pagos['metodo_pago'] = ''
    if 'fecha_pago' not in pagos.columns:
        pagos['fecha_pago'] = ''
    if 'estado_pago' not in pagos.columns:
        pagos['estado_pago'] = ''

    if 'id_pedido' not in detalle.columns:
        detalle['id_pedido'] = pd.Series(dtype='int')
    if 'id_producto' not in detalle.columns:
        detalle['id_producto'] = pd.Series(dtype='int')
    if 'cantidad' not in detalle.columns:
        detalle['cantidad'] = 0
    if 'subtotal' not in detalle.columns:
        detalle['subtotal'] = 0

    if 'id_producto' not in productos.columns:
        productos['id_producto'] = pd.Series(dtype='int')
    if 'nombre' not in productos.columns:
        productos['nombre'] = ''

    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    pagos['id_pedido'] = pd.to_numeric(pagos['id_pedido'], errors='coerce')
    pagos['id_pago'] = pd.to_numeric(pagos['id_pago'], errors='coerce')
    pagos['monto'] = pd.to_numeric(pagos['monto'], errors='coerce').fillna(0)
    detalle['id_pedido'] = pd.to_numeric(detalle['id_pedido'], errors='coerce')
    detalle['id_producto'] = pd.to_numeric(detalle['id_producto'], errors='coerce')
    detalle['cantidad'] = pd.to_numeric(detalle['cantidad'], errors='coerce').fillna(0)
    detalle['subtotal'] = pd.to_numeric(detalle['subtotal'], errors='coerce').fillna(0)
    productos['id_producto'] = pd.to_numeric(productos['id_producto'], errors='coerce')

    totales_pedido = detalle.groupby('id_pedido', as_index=False)['subtotal'].sum()
    totales_pedido = totales_pedido.rename(columns={'subtotal': 'total_productos'})

    pagos_ultimos = pagos.sort_values(by='id_pago', ascending=False).drop_duplicates(subset=['id_pedido'], keep='first')
    pagos_ultimos = pagos_ultimos[['id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago']]

    pedidos_view = pedidos.merge(totales_pedido, on='id_pedido', how='left')
    pedidos_view = pedidos_view.merge(pagos_ultimos, on='id_pedido', how='left')
    pedidos_view['total_productos'] = pedidos_view['total_productos'].fillna(0)
    pedidos_view['monto'] = pedidos_view['monto'].fillna(0)

    usuarios_map = {}
    for _, u in usuarios.iterrows():
        uid = pd.to_numeric(u.get('id_usuario'), errors='coerce')
        if pd.notna(uid):
            usuarios_map[int(uid)] = str(u.get('nombre', '')).strip()

    def resolver_usuario(valor):
        uid = pd.to_numeric(valor, errors='coerce')
        if pd.notna(uid):
            uid = int(uid)
            if uid in usuarios_map and usuarios_map[uid]:
                return usuarios_map[uid]
            return f"Usuario #{uid}"
        return str(valor) if str(valor).strip() else 'N/A'

    productos_map = {}
    for _, producto in productos.iterrows():
        pid = pd.to_numeric(producto.get('id_producto'), errors='coerce')
        if pd.notna(pid):
            productos_map[int(pid)] = str(producto.get('nombre', '')).strip()

    productos_por_pedido = {}
    for id_pedido, grupo in detalle.groupby('id_pedido'):
        if pd.isna(id_pedido):
            continue

        items = []
        for _, item in grupo.iterrows():
            pid = pd.to_numeric(item.get('id_producto'), errors='coerce')
            cantidad = pd.to_numeric(item.get('cantidad'), errors='coerce')
            nombre_producto = ''

            if pd.notna(pid):
                nombre_producto = productos_map.get(int(pid), f"Producto #{int(pid)}")
            if not nombre_producto:
                nombre_producto = 'Producto sin nombre'

            if pd.notna(cantidad) and int(cantidad) > 1:
                items.append(f"{nombre_producto} x{int(cantidad)}")
            else:
                items.append(nombre_producto)

        vistos = []
        for item in items:
            if item not in vistos:
                vistos.append(item)
        productos_por_pedido[int(id_pedido)] = ', '.join(vistos) if vistos else 'Sin productos'

    pedidos_view['usuario_nombre'] = pedidos_view['id_usuario'].apply(resolver_usuario)
    pedidos_view['productos_pedido'] = pedidos_view['id_pedido'].apply(
        lambda valor: productos_por_pedido.get(int(valor), 'Sin productos') if pd.notna(valor) else 'Sin productos'
    )

    filtro_q = str(request.args.get('q', '')).strip()
    filtro_estado = str(request.args.get('estado', 'todos')).strip().lower()
    filtro_fecha_desde = str(request.args.get('fecha_desde', '')).strip()
    filtro_fecha_hasta = str(request.args.get('fecha_hasta', '')).strip()
    pago_filtro_q = str(request.args.get('pago_q', '')).strip()
    pago_filtro_metodo = str(request.args.get('pago_metodo', 'todos')).strip().lower()
    pago_filtro_estado = str(request.args.get('pago_estado', 'todos')).strip().lower()
    pago_filtro_fecha_desde = str(request.args.get('pago_fecha_desde', '')).strip()
    pago_filtro_fecha_hasta = str(request.args.get('pago_fecha_hasta', '')).strip()

    estados_validos = {'pendiente', 'enviado', 'entregado', 'cancelado'}
    if filtro_estado not in estados_validos:
        filtro_estado = 'todos'

    pedidos_view['estado'] = pedidos_view['estado'].fillna('pendiente').astype(str).str.strip().str.lower()
    pedidos_view['fecha_pedido'] = pedidos_view['fecha_pedido'].fillna('').astype(str)
    pedidos_view['fecha_pedido_dt'] = pd.to_datetime(pedidos_view['fecha_pedido'], errors='coerce')
    pedidos_view['id_pedido_txt'] = pedidos_view['id_pedido'].apply(
        lambda valor: str(int(valor)) if pd.notna(valor) else ''
    )

    if filtro_estado != 'todos':
        pedidos_view = pedidos_view[pedidos_view['estado'] == filtro_estado]

    fecha_desde_dt = pd.to_datetime(filtro_fecha_desde, errors='coerce')
    if pd.notna(fecha_desde_dt):
        pedidos_view = pedidos_view[pedidos_view['fecha_pedido_dt'].dt.date >= fecha_desde_dt.date()]
    else:
        filtro_fecha_desde = ''

    fecha_hasta_dt = pd.to_datetime(filtro_fecha_hasta, errors='coerce')
    if pd.notna(fecha_hasta_dt):
        pedidos_view = pedidos_view[pedidos_view['fecha_pedido_dt'].dt.date <= fecha_hasta_dt.date()]
    else:
        filtro_fecha_hasta = ''

    if filtro_q:
        texto = filtro_q.lower()
        pedidos_view = pedidos_view[
            pedidos_view['id_pedido_txt'].str.contains(texto, na=False) |
            pedidos_view['usuario_nombre'].fillna('').astype(str).str.lower().str.contains(texto, na=False) |
            pedidos_view['productos_pedido'].fillna('').astype(str).str.lower().str.contains(texto, na=False) |
            pedidos_view['fecha_pedido'].str.lower().str.contains(texto, na=False)
        ]

    pedidos_view = pedidos_view.sort_values(by='id_pedido', ascending=False, na_position='last')

    pedidos_por_pagina = 10
    pagina_raw = str(request.args.get('page', '1')).strip()
    try:
        pagina_actual = int(pagina_raw)
    except ValueError:
        pagina_actual = 1
    pagina_actual = max(1, pagina_actual)

    total_filtrados = int(len(pedidos_view.index))
    total_paginas = max(1, (total_filtrados + pedidos_por_pagina - 1) // pedidos_por_pagina)
    if pagina_actual > total_paginas:
        pagina_actual = total_paginas

    if total_paginas <= 7:
        botones_paginacion = list(range(1, total_paginas + 1))
    else:
        botones_paginacion = [1]
        inicio = max(2, pagina_actual - 1)
        fin = min(total_paginas - 1, pagina_actual + 1)
        if inicio > 2:
            botones_paginacion.append('...')
        botones_paginacion.extend(range(inicio, fin + 1))
        if fin < total_paginas - 1:
            botones_paginacion.append('...')
        botones_paginacion.append(total_paginas)

    inicio = (pagina_actual - 1) * pedidos_por_pagina
    fin = inicio + pedidos_por_pagina
    pedidos_view = pedidos_view.iloc[inicio:fin].copy()

    pagos_view = pagos.copy()
    pagos_view['metodo_pago'] = pagos_view['metodo_pago'].fillna('').astype(str).str.strip().str.lower()
    pagos_view['estado_pago'] = pagos_view['estado_pago'].fillna('').astype(str).str.strip().str.lower()
    pagos_view['fecha_pago'] = pagos_view['fecha_pago'].fillna('').astype(str)
    pagos_view['fecha_pago_dt'] = pd.to_datetime(pagos_view['fecha_pago'], errors='coerce')
    pagos_view['id_pago_txt'] = pagos_view['id_pago'].apply(lambda valor: str(int(valor)) if pd.notna(valor) else '')
    pagos_view['id_pedido_txt'] = pagos_view['id_pedido'].apply(lambda valor: str(int(valor)) if pd.notna(valor) else '')
    pagos_view['monto_txt'] = pagos_view['monto'].apply(
        lambda valor: f"{float(valor):.2f}" if pd.notna(valor) else ''
    )

    metodos_pago_opciones = sorted([m for m in pagos_view['metodo_pago'].unique().tolist() if m])
    estados_pago_opciones = sorted([e for e in pagos_view['estado_pago'].unique().tolist() if e])

    if pago_filtro_metodo != 'todos' and pago_filtro_metodo not in metodos_pago_opciones:
        pago_filtro_metodo = 'todos'
    if pago_filtro_estado != 'todos' and pago_filtro_estado not in estados_pago_opciones:
        pago_filtro_estado = 'todos'

    if pago_filtro_metodo != 'todos':
        pagos_view = pagos_view[pagos_view['metodo_pago'] == pago_filtro_metodo]
    if pago_filtro_estado != 'todos':
        pagos_view = pagos_view[pagos_view['estado_pago'] == pago_filtro_estado]

    pago_fecha_desde_dt = pd.to_datetime(pago_filtro_fecha_desde, errors='coerce')
    if pd.notna(pago_fecha_desde_dt):
        pagos_view = pagos_view[pagos_view['fecha_pago_dt'].dt.date >= pago_fecha_desde_dt.date()]
    else:
        pago_filtro_fecha_desde = ''

    pago_fecha_hasta_dt = pd.to_datetime(pago_filtro_fecha_hasta, errors='coerce')
    if pd.notna(pago_fecha_hasta_dt):
        pagos_view = pagos_view[pagos_view['fecha_pago_dt'].dt.date <= pago_fecha_hasta_dt.date()]
    else:
        pago_filtro_fecha_hasta = ''

    if pago_filtro_q:
        pago_texto = pago_filtro_q.lower()
        pagos_view = pagos_view[
            pagos_view['id_pago_txt'].str.contains(pago_texto, na=False) |
            pagos_view['id_pedido_txt'].str.contains(pago_texto, na=False) |
            pagos_view['metodo_pago'].str.contains(pago_texto, na=False) |
            pagos_view['estado_pago'].str.contains(pago_texto, na=False) |
            pagos_view['fecha_pago'].str.lower().str.contains(pago_texto, na=False) |
            pagos_view['monto_txt'].str.contains(pago_texto, na=False)
        ]

    pagos_view = pagos_view.sort_values(by='id_pago', ascending=False, na_position='last')

    pagos_por_pagina = 10
    pago_pagina_raw = str(request.args.get('pago_page', '1')).strip()
    try:
        pago_pagina_actual = int(pago_pagina_raw)
    except ValueError:
        pago_pagina_actual = 1
    pago_pagina_actual = max(1, pago_pagina_actual)

    pago_total_filtrados = int(len(pagos_view.index))
    pago_total_paginas = max(1, (pago_total_filtrados + pagos_por_pagina - 1) // pagos_por_pagina)
    if pago_pagina_actual > pago_total_paginas:
        pago_pagina_actual = pago_total_paginas

    if pago_total_paginas <= 7:
        pago_botones_paginacion = list(range(1, pago_total_paginas + 1))
    else:
        pago_botones_paginacion = [1]
        pago_inicio_botones = max(2, pago_pagina_actual - 1)
        pago_fin_botones = min(pago_total_paginas - 1, pago_pagina_actual + 1)
        if pago_inicio_botones > 2:
            pago_botones_paginacion.append('...')
        pago_botones_paginacion.extend(range(pago_inicio_botones, pago_fin_botones + 1))
        if pago_fin_botones < pago_total_paginas - 1:
            pago_botones_paginacion.append('...')
        pago_botones_paginacion.append(pago_total_paginas)

    pago_inicio = (pago_pagina_actual - 1) * pagos_por_pagina
    pago_fin = pago_inicio + pagos_por_pagina
    pagos_view = pagos_view.iloc[pago_inicio:pago_fin].copy()

    lista_pedidos = pedidos_view.fillna('').to_dict(orient='records')
    lista_pagos = pagos_view.fillna('').to_dict(orient='records')

    for p in lista_pedidos:
        if p.get('id_pedido') != '':
            p['id_pedido'] = int(p['id_pedido'])
        p['estado'] = str(p.get('estado', 'pendiente')).strip().lower() or 'pendiente'

    for p in lista_pagos:
        if p.get('id_pago') != '':
            p['id_pago'] = int(p['id_pago'])
        if p.get('id_pedido') != '':
            p['id_pedido'] = int(p['id_pedido'])
        p['metodo_pago'] = str(p.get('metodo_pago', '')).strip().lower()
        p['estado_pago'] = str(p.get('estado_pago', '')).strip().lower()

    return render_template(
        'Administrador/Gestion pedidos/admin_orders.html',
        pedidos=lista_pedidos,
        pagos=lista_pagos,
        filtros={
            'q': filtro_q,
            'estado': filtro_estado,
            'fecha_desde': filtro_fecha_desde,
            'fecha_hasta': filtro_fecha_hasta,
            'page': pagina_actual
        },
        pago_filtros={
            'q': pago_filtro_q,
            'metodo': pago_filtro_metodo,
            'estado': pago_filtro_estado,
            'fecha_desde': pago_filtro_fecha_desde,
            'fecha_hasta': pago_filtro_fecha_hasta,
            'page': pago_pagina_actual
        },
        paginacion={
            'page': pagina_actual,
            'per_page': pedidos_por_pagina,
            'total': total_filtrados,
            'total_paginas': total_paginas,
            'desde': (inicio + 1) if total_filtrados > 0 else 0,
            'hasta': min(fin, total_filtrados),
            'opciones': list(range(1, total_paginas + 1)),
            'botones': botones_paginacion
        },
        paginacion_pagos={
            'page': pago_pagina_actual,
            'per_page': pagos_por_pagina,
            'total': pago_total_filtrados,
            'total_paginas': pago_total_paginas,
            'desde': (pago_inicio + 1) if pago_total_filtrados > 0 else 0,
            'hasta': min(pago_fin, pago_total_filtrados),
            'botones': pago_botones_paginacion
        },
        metodos_pago_opciones=metodos_pago_opciones,
        estados_pago_opciones=estados_pago_opciones,
        hay_filtros_activos=bool(
            filtro_q or filtro_fecha_desde or filtro_fecha_hasta or filtro_estado != 'todos'
        ),
        hay_filtros_pagos_activos=bool(
            pago_filtro_q or pago_filtro_fecha_desde or pago_filtro_fecha_hasta or
            pago_filtro_metodo != 'todos' or pago_filtro_estado != 'todos'
        )
    )


@app.route('/admin/pedidos/estado/<int:id_pedido>', methods=['POST'])
def admin_pedidos_estado(id_pedido):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    filtro_q = str(request.form.get('f_q', '')).strip()
    filtro_estado = str(request.form.get('f_estado', 'todos')).strip().lower()
    filtro_fecha_desde = str(request.form.get('f_fecha_desde', '')).strip()
    filtro_fecha_hasta = str(request.form.get('f_fecha_hasta', '')).strip()
    filtro_page = str(request.form.get('f_page', '1')).strip()
    pago_filtro_q = str(request.form.get('f_pago_q', '')).strip()
    pago_filtro_metodo = str(request.form.get('f_pago_metodo', 'todos')).strip().lower()
    pago_filtro_estado = str(request.form.get('f_pago_estado', 'todos')).strip().lower()
    pago_filtro_fecha_desde = str(request.form.get('f_pago_fecha_desde', '')).strip()
    pago_filtro_fecha_hasta = str(request.form.get('f_pago_fecha_hasta', '')).strip()
    pago_filtro_page = str(request.form.get('f_pago_page', '1')).strip()

    def redirigir_a_pedidos_con_filtros():
        params = {}
        if filtro_q:
            params['q'] = filtro_q
        if filtro_estado and filtro_estado != 'todos':
            params['estado'] = filtro_estado
        if filtro_fecha_desde:
            params['fecha_desde'] = filtro_fecha_desde
        if filtro_fecha_hasta:
            params['fecha_hasta'] = filtro_fecha_hasta
        try:
            page_int = int(filtro_page)
            if page_int > 1:
                params['page'] = page_int
        except ValueError:
            pass
        if pago_filtro_q:
            params['pago_q'] = pago_filtro_q
        if pago_filtro_metodo and pago_filtro_metodo != 'todos':
            params['pago_metodo'] = pago_filtro_metodo
        if pago_filtro_estado and pago_filtro_estado != 'todos':
            params['pago_estado'] = pago_filtro_estado
        if pago_filtro_fecha_desde:
            params['pago_fecha_desde'] = pago_filtro_fecha_desde
        if pago_filtro_fecha_hasta:
            params['pago_fecha_hasta'] = pago_filtro_fecha_hasta
        try:
            pago_page_int = int(pago_filtro_page)
            if pago_page_int > 1:
                params['pago_page'] = pago_page_int
        except ValueError:
            pass
        return redirect(url_for('admin_pedidos', **params))

    estado_nuevo = request.form.get('estado', '').strip().lower()
    estados_validos = {'pendiente', 'enviado', 'entregado', 'cancelado'}
    if estado_nuevo not in estados_validos:
        flash('Estado de pedido inválido.', 'danger')
        return redirigir_a_pedidos_con_filtros()

    pedidos = cargar_pedidos_df()
    if 'id_pedido' not in pedidos.columns:
        flash('Estructura de pedidos inválida.', 'danger')
        return redirigir_a_pedidos_con_filtros()
    if 'estado' not in pedidos.columns:
        pedidos['estado'] = 'pendiente'

    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    idx = pedidos[pedidos['id_pedido'] == id_pedido].index
    if idx.empty:
        flash('Pedido no encontrado.', 'warning')
        return redirigir_a_pedidos_con_filtros()

    estado_anterior = str(pedidos.at[idx[0], 'estado']).strip().lower()
    pedidos.at[idx[0], 'estado'] = estado_nuevo
    guardar_pedidos_df(pedidos)

    if estado_anterior != estado_nuevo:
        registrar_actividad(f"Actualizo estado de pedido #{id_pedido}: {estado_anterior} -> {estado_nuevo}")
        flash(f'Pedido #{id_pedido} actualizado a "{estado_nuevo}".', 'success')
    else:
        flash(f'El pedido #{id_pedido} ya estaba en "{estado_nuevo}".', 'info')

    return redirigir_a_pedidos_con_filtros()


@app.route('/admin/pos/checkout', methods=['POST'])
def admin_pos_checkout():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    cliente_nombre = request.form.get('cliente_nombre', '').strip()
    cliente_correo = request.form.get('cliente_correo', '').strip().lower()
    cliente_documento = request.form.get('cliente_documento', '').strip()
    cliente_telefono = request.form.get('cliente_telefono', '').strip()
    if not cliente_nombre or not cliente_correo or not cliente_documento or not cliente_telefono:
        flash('Debes completar todos los datos del cliente para registrar la venta.', 'warning')
        return redirect(url_for('admin_pos'))
    if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+', cliente_nombre):
        flash('El nombre del cliente solo puede contener letras y espacios.', 'warning')
        return redirect(url_for('admin_pos'))
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', cliente_correo):
        flash('Debes ingresar un correo electrónico válido.', 'warning')
        return redirect(url_for('admin_pos'))
    if not cliente_documento.isdigit():
        flash('La cédula solo puede contener números.', 'warning')
        return redirect(url_for('admin_pos'))
    if not cliente_telefono.isdigit() or len(cliente_telefono) > 10:
        flash('El teléfono solo puede contener números y máximo 10 dígitos.', 'warning')
        return redirect(url_for('admin_pos'))

    items_raw = request.form.get('items_json', '[]')
    metodo_pago = request.form.get('metodo_pago', 'efectivo').strip().lower()
    metodos_validos = {'efectivo', 'tarjeta', 'transferencia', 'qr'}
    if metodo_pago not in metodos_validos:
        metodo_pago = 'efectivo'

    try:
        items = json.loads(items_raw)
    except json.JSONDecodeError:
        flash('No se pudo procesar el carrito POS.', 'danger')
        return redirect(url_for('admin_pos'))

    if not isinstance(items, list) or not items:
        flash('Agrega al menos un producto para cobrar.', 'warning')
        return redirect(url_for('admin_pos'))

    productos = cargar_productos_df()
    if productos.empty:
        flash('No existe el catálogo de productos.', 'danger')
        return redirect(url_for('admin_pos'))

    promos = cargar_promociones_df()
    hoy = datetime.now().date()
    mejor_promo_por_producto = {}
    mejor_descuento_por_producto = {}
    for _, row in promos.iterrows():
        promo = row.to_dict()
        if not promocion_esta_aplicable(promo, hoy):
            continue

        id_producto_promo = pd.to_numeric(promo.get('id_producto'), errors='coerce')
        if pd.isna(id_producto_promo):
            continue
        id_prod_int = int(id_producto_promo)

        producto_df = productos[productos['id_producto'] == id_prod_int]
        if producto_df.empty:
            continue

        precio_ref = float(pd.to_numeric(producto_df.iloc[0].get('precio', 0), errors='coerce') or 0)
        descuento_actual = calcular_descuento_promocion(precio_ref, promo)
        if descuento_actual > mejor_descuento_por_producto.get(id_prod_int, -1):
            mejor_descuento_por_producto[id_prod_int] = descuento_actual
            mejor_promo_por_producto[id_prod_int] = promo

    carrito_validado = []
    total_bruto = 0.0
    total_descuento = 0.0
    total = 0.0

    for item in items:
        try:
            id_producto = int(item.get('id_producto', 0))
            cantidad = int(item.get('cantidad', 0))
        except (TypeError, ValueError):
            flash('Hay productos inválidos en el carrito POS.', 'danger')
            return redirect(url_for('admin_pos'))

        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero.', 'danger')
            return redirect(url_for('admin_pos'))

        idx = productos[productos['id_producto'] == id_producto].index
        if idx.empty:
            flash(f'El producto con ID {id_producto} ya no existe.', 'danger')
            return redirect(url_for('admin_pos'))

        row_idx = idx[0]
        if bool(productos.at[row_idx, 'eliminado']):
            flash(f'El producto ID {id_producto} está eliminado.', 'danger')
            return redirect(url_for('admin_pos'))

        stock_actual = int(pd.to_numeric(productos.at[row_idx, 'stock'], errors='coerce') or 0)
        if cantidad > stock_actual:
            nombre = str(productos.at[row_idx, 'nombre'])
            flash(f'Stock insuficiente para "{nombre}". Disponible: {stock_actual}.', 'warning')
            return redirect(url_for('admin_pos'))

        precio_base = float(pd.to_numeric(productos.at[row_idx, 'precio'], errors='coerce') or 0)
        promo = mejor_promo_por_producto.get(id_producto)
        descuento_unitario = calcular_descuento_promocion(precio_base, promo) if promo else 0.0
        precio_final = max(0.0, precio_base - descuento_unitario)

        subtotal_bruto = precio_base * cantidad
        subtotal_descuento = descuento_unitario * cantidad
        subtotal_final = max(0.0, subtotal_bruto - subtotal_descuento)

        total_bruto += subtotal_bruto
        total_descuento += subtotal_descuento
        total += subtotal_final

        productos.at[row_idx, 'stock'] = stock_actual - cantidad
        carrito_validado.append({
            'id_producto': id_producto,
            'cantidad': cantidad,
            'subtotal': subtotal_final,
            'subtotal_bruto': subtotal_bruto,
            'monto_descuento': subtotal_descuento,
            'promo_id': promo.get('id_promo', '') if promo else '',
            'promo_codigo': promo.get('codigo', '') if promo else '',
            'promo_tipo_descuento': promo.get('tipo_descuento', '') if promo else '',
            'promo_valor_descuento': float(pd.to_numeric(promo.get('valor_descuento', 0), errors='coerce') or 0) if promo else 0.0
        })

    guardar_productos_df(productos)

    pedidos = cargar_pedidos_df()
    detalle_pedido = cargar_detalle_pedido_df()
    pagos = cargar_pagos_df()

    next_pedido_id = next_id('pedidos', 'id_pedido')
    nuevo_pedido = {
        'id_pedido': next_pedido_id,
        'id_usuario': session.get('usuario', 'admin_pos'),
        'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'estado': 'completado'
    }
    pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
    guardar_pedidos_df(pedidos)

    next_detalle_id = next_id('detalle_pedido', 'id_detalle')
    nuevos_detalles = []
    for item in carrito_validado:
        nuevos_detalles.append({
            'id_detalle': next_detalle_id,
            'id_pedido': next_pedido_id,
            'id_producto': item['id_producto'],
            'cantidad': item['cantidad'],
            'subtotal': item['subtotal']
        })
        next_detalle_id += 1
    detalle_pedido = pd.concat([detalle_pedido, pd.DataFrame(nuevos_detalles)], ignore_index=True)
    guardar_detalle_pedido_df(detalle_pedido)

    promo_ids = []
    promo_codigos = []
    promo_tipos = []
    promo_valores = []
    for item in carrito_validado:
        promo_id = str(item.get('promo_id', '')).strip()
        promo_codigo = str(item.get('promo_codigo', '')).strip()
        promo_tipo = str(item.get('promo_tipo_descuento', '')).strip()
        promo_valor = float(pd.to_numeric(item.get('promo_valor_descuento', 0), errors='coerce') or 0)

        if promo_id and promo_id not in promo_ids:
            promo_ids.append(promo_id)
        if promo_codigo and promo_codigo not in promo_codigos:
            promo_codigos.append(promo_codigo)
        if promo_tipo and promo_tipo not in promo_tipos:
            promo_tipos.append(promo_tipo)
        if promo_valor and promo_valor not in promo_valores:
            promo_valores.append(promo_valor)

    if not promo_ids:
        pago_id_promo = ''
        pago_codigo_promo = ''
        pago_tipo_descuento = ''
        pago_valor_descuento = 0.0
    elif len(promo_ids) == 1:
        pago_id_promo = promo_ids[0]
        pago_codigo_promo = promo_codigos[0] if promo_codigos else ''
        pago_tipo_descuento = promo_tipos[0] if promo_tipos else ''
        pago_valor_descuento = float(promo_valores[0]) if promo_valores else 0.0
    else:
        pago_id_promo = 'multi'
        pago_codigo_promo = ','.join(promo_codigos)
        pago_tipo_descuento = 'multi'
        pago_valor_descuento = 0.0

    next_pago_id = next_id('pagos', 'id_pago')
    nuevo_pago = {
        'id_pago': next_pago_id,
        'id_pedido': next_pedido_id,
        'monto': round(total, 2),
        'metodo_pago': metodo_pago,
        'fecha_pago': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'estado_pago': 'aprobado',
        'id_promo': pago_id_promo,
        'codigo_promo': pago_codigo_promo,
        'tipo_descuento': pago_tipo_descuento,
        'valor_descuento': round(pago_valor_descuento, 2),
        'monto_descuento': round(total_descuento, 2)
    }
    pagos = pd.concat([pagos, pd.DataFrame([nuevo_pago])], ignore_index=True)
    guardar_pagos_df(pagos)

    total_bruto = round(total_bruto, 2)
    total_descuento = round(total_descuento, 2)
    total = round(total, 2)
    total_cop = formatear_cop(total)
    total_bruto_cop = formatear_cop(total_bruto)
    descuento_cop = formatear_cop(total_descuento)
    registrar_actividad(
        f"POS registro venta #{next_pedido_id} por {total_cop} ({len(carrito_validado)} producto(s))\n"
        f"- total bruto: {total_bruto_cop}\n"
        f"- descuento aplicado: {descuento_cop}\n"
        f"- cliente: {cliente_nombre}\n"
        f"- correo: {cliente_correo}\n"
        f"- documento: {cliente_documento}\n"
        f"- teléfono: {cliente_telefono}"
    )
    if total_descuento > 0:
        flash(
            f'Venta POS registrada. Pedido #{next_pedido_id} por {total_cop}. '
            f'Descuento aplicado: {descuento_cop}.',
            'success'
        )
    else:
        flash(f'Venta POS registrada. Pedido #{next_pedido_id} por {total_cop}.', 'success')

    session['ultimo_recibo_pos'] = {
        'id_pedido': int(next_pedido_id),
        'cliente_nombre': cliente_nombre,
        'cliente_correo': cliente_correo,
        'cliente_documento': cliente_documento,
        'cliente_telefono': cliente_telefono
    }
    session.modified = True
    return redirect(url_for('admin_pos', descargar_recibo=next_pedido_id))


@app.route('/admin/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = cargar_productos_df()
    producto = productos[productos['id_producto'] == id_producto]

    if producto.empty:
        return "Producto no encontrado."

    if request.method == 'POST':
        idx = producto.index[0]

        anterior = {
            'nombre': str(productos.at[idx, 'nombre']) if 'nombre' in productos.columns else '',
            'descripcion': str(productos.at[idx, 'descripcion']) if 'descripcion' in productos.columns else '',
            'precio': float(pd.to_numeric(productos.at[idx, 'precio'], errors='coerce')) if 'precio' in productos.columns else 0.0,
            'stock': int(pd.to_numeric(productos.at[idx, 'stock'], errors='coerce')) if 'stock' in productos.columns else 0,
            'id_categoria': str(productos.at[idx, 'id_categoria']) if 'id_categoria' in productos.columns else '',
            'fuerza': str(productos.at[idx, 'fuerza']) if 'fuerza' in productos.columns else '',
            'intendencia': str(productos.at[idx, 'intendencia']) if 'intendencia' in productos.columns else ''
        }

        nuevo_nombre = request.form['nombre'].strip()
        nueva_descripcion = request.form['descripcion'].strip()
        nuevo_precio = float(request.form['precio'])
        nuevo_stock = int(request.form['stock'])
        nueva_fuerza = request.form.get('fuerza', anterior['fuerza']).strip()
        nueva_intendencia = request.form.get('intendencia', anterior['intendencia']).strip()
        if nueva_fuerza not in FUERZAS_OPCIONES or nueva_intendencia not in INTENDENCIAS_OPCIONES:
            flash('Selecciona una fuerza e intendencia validas.', 'danger')
            return redirect(url_for('admin_productos'))

        nueva_categoria = anterior['id_categoria']
        if 'id_categoria' in productos.columns:
            categoria_form = request.form.get('id_categoria', '').strip()
            if categoria_form:
                try:
                    nueva_categoria = int(float(categoria_form))
                except ValueError:
                    nueva_categoria = anterior['id_categoria']
            # Evitar errores de tipo en pandas (int64): asegurar valor numerico
            nueva_categoria_num = pd.to_numeric(nueva_categoria, errors='coerce')
            if pd.isna(nueva_categoria_num):
                nueva_categoria_num = pd.to_numeric(productos.at[idx, 'id_categoria'], errors='coerce')
            nueva_categoria = int(nueva_categoria_num) if pd.notna(nueva_categoria_num) else 0

        productos.at[idx, 'nombre'] = nuevo_nombre
        productos.at[idx, 'descripcion'] = nueva_descripcion
        productos.at[idx, 'precio'] = nuevo_precio
        productos.at[idx, 'stock'] = nuevo_stock
        productos.at[idx, 'fuerza'] = nueva_fuerza
        productos.at[idx, 'intendencia'] = nueva_intendencia
        if 'id_categoria' in productos.columns:
            productos.at[idx, 'id_categoria'] = nueva_categoria

        guardar_productos_df(productos)

        cambios = []
        if anterior['nombre'] != nuevo_nombre:
            cambios.append(f"- nombre: '{anterior['nombre']}' -> '{nuevo_nombre}'")
        if anterior['descripcion'] != nueva_descripcion:
            cambios.append(f"- descripcion: '{anterior['descripcion']}' -> '{nueva_descripcion}'")
        if round(float(anterior['precio']), 2) != round(float(nuevo_precio), 2):
            cambios.append(f"- precio: {formatear_cop(anterior['precio'])} -> {formatear_cop(nuevo_precio)}")
        if int(anterior['stock']) != int(nuevo_stock):
            cambios.append(f"- stock: {anterior['stock']} -> {nuevo_stock}")
        if anterior['fuerza'] != nueva_fuerza:
            cambios.append(f"- fuerza: {anterior['fuerza']} -> {nueva_fuerza}")
        if anterior['intendencia'] != nueva_intendencia:
            cambios.append(f"- intendencia: {anterior['intendencia']} -> {nueva_intendencia}")
        if str(anterior['id_categoria']) != str(nueva_categoria):
            cambios.append(f"- categoria: {anterior['id_categoria']} -> {nueva_categoria}")

        encabezado = f"Actualizo producto '{nuevo_nombre}' (ID {id_producto})"
        if cambios:
            registrar_actividad(encabezado + "\n" + "\n".join(cambios))
        else:
            registrar_actividad(encabezado + "\n- sin cambios detectados")

        return redirect(url_for('admin_productos'))

    # Render formulario de edición (plantilla propia en Gestion productos)
    return render_template(
        'Administrador/Gestion productos/editar_producto.html',
        producto=producto.iloc[0],
        fuerzas=FUERZAS_OPCIONES,
        intendencias=INTENDENCIAS_OPCIONES
    )

    

@app.route('/user')
def user_dashboard():
    if session.get('rol') == 'normal':
        productos = cargar_productos_activos_df()
        lista_productos = productos.to_dict(orient='records')

        # Promoción vigente por producto para mostrar en catálogo
        promos = cargar_promociones_df()
        hoy = datetime.now().date()
        mejor_promo_por_producto = {}
        mejor_descuento_por_producto = {}
        for _, row in promos.iterrows():
            promo = row.to_dict()
            if not promocion_esta_aplicable(promo, hoy):
                continue
            id_producto_promo = pd.to_numeric(promo.get('id_producto'), errors='coerce')
            if pd.isna(id_producto_promo):
                continue
            id_prod_int = int(id_producto_promo)
            precio_ref = float(pd.to_numeric(
                productos.loc[productos['id_producto'] == id_prod_int, 'precio'].iloc[0]
                if not productos[productos['id_producto'] == id_prod_int].empty else 0,
                errors='coerce'
            ) or 0)
            descuento_actual = calcular_descuento_promocion(precio_ref, promo)
            if descuento_actual > mejor_descuento_por_producto.get(id_prod_int, -1):
                mejor_descuento_por_producto[id_prod_int] = descuento_actual
                mejor_promo_por_producto[id_prod_int] = promo

        for producto in lista_productos:
            precio_base = float(pd.to_numeric(producto.get('precio', 0), errors='coerce') or 0)
            promo = mejor_promo_por_producto.get(int(producto.get('id_producto', 0)))
            if promo:
                descuento = calcular_descuento_promocion(precio_base, promo)
                producto['precio_original'] = precio_base
                producto['precio_con_descuento'] = max(0.0, precio_base - descuento)
                producto['promo_activa'] = True
                producto['promo_nombre'] = promo.get('nombre', '')
                if promo.get('tipo_descuento') == 'valor_fijo':
                    producto['promo_etiqueta'] = f"-{formatear_cop(promo.get('valor_descuento', 0))}"
                else:
                    valor_pct = float(pd.to_numeric(promo.get('valor_descuento', 0), errors='coerce') or 0)
                    producto['promo_etiqueta'] = f"-{valor_pct:g}%"
            else:
                producto['precio_original'] = precio_base
                producto['precio_con_descuento'] = precio_base
                producto['promo_activa'] = False
                producto['promo_nombre'] = ''
                producto['promo_etiqueta'] = ''
        
        # Obtener el contador del carrito
        carrito = session.get('carrito', [])
        cart_count = len(carrito)
        
        return render_template('Usuarios/user_dashboard.html', productos=lista_productos, cart_count=cart_count)
    return "Acceso denegado"


@app.route('/product/<int:id_producto>')
def product_detail(id_producto):
    if session.get('rol') == 'normal':
        productos = cargar_productos_activos_df()
        producto = productos[productos['id_producto'] == id_producto]
        
        if producto.empty:
            return "Producto no encontrado"
        
        producto_dict = producto.iloc[0].to_dict()
        galeria = obtener_galeria_producto(id_producto, producto_dict.get('imagen_url', ''))[:MAX_IMAGES_PER_PRODUCT]
        producto_dict['imagenes'] = galeria
        if galeria:
            producto_dict['imagen_url'] = galeria[0]
        
        # Obtener el contador del carrito
        carrito = session.get('carrito', [])
        cart_count = len(carrito)
        
        return render_template('Usuarios/Detalle pedido/product_detail.html', producto=producto_dict, cart_count=cart_count)
    return "Acceso denegado"


@app.route('/add_to_cart/<int:id_producto>', methods=['POST'])
def add_to_cart(id_producto):
    if session.get('rol') != 'normal':
        return "Acceso denegado"

    if 'carrito' not in session:
        session['carrito'] = []

    productos = cargar_productos_activos_df()

    try:
        cantidad = int(request.form.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1

    if cantidad <= 0:
        flash('Cantidad inválida.', 'warning')
        return redirect(url_for('user_dashboard'))

    producto_df = productos[productos['id_producto'] == id_producto]
    if producto_df.empty:
        flash('El producto no existe o ya no está disponible.', 'warning')
        return redirect(url_for('user_dashboard'))

    producto = producto_df.iloc[0]
    stock_actual = int(producto.get('stock', 0))
    if stock_actual <= 0:
        flash(f'El producto "{producto["nombre"]}" está agotado.', 'warning')
        return redirect(url_for('user_dashboard'))
    if cantidad > stock_actual:
        flash(f'Solo hay {stock_actual} unidad(es) disponibles de "{producto["nombre"]}".', 'warning')
        return redirect(url_for('user_dashboard'))

    carrito = session.get('carrito', [])
    item_existente = next((item for item in carrito if int(item.get('id_producto', 0)) == int(id_producto)), None)
    if item_existente:
        nueva_cantidad = int(item_existente.get('cantidad', 0)) + cantidad
        if nueva_cantidad > stock_actual:
            flash(f'No puedes agregar mas de {stock_actual} unidad(es) de "{producto["nombre"]}".', 'warning')
            return redirect(url_for('cart'))
        item_existente['cantidad'] = nueva_cantidad
        item_existente['subtotal'] = float(item_existente['precio']) * nueva_cantidad
    else:
        item_carrito = {
            'id_producto': int(id_producto),
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio': float(producto['precio']),
            'subtotal': float(producto['precio']) * cantidad
        }
        carrito.append(item_carrito)

    session['carrito'] = carrito
    session.modified = True

    flash(f'¡{producto["nombre"]} agregado al carrito exitosamente!', 'success')

    referer = request.referrer
    if referer and 'product' in referer:
        return redirect(url_for('product_detail', id_producto=id_producto))

    return redirect(url_for('user_dashboard'))

@app.route('/cart')
def cart():
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
        carrito_limpio, cambios = normalizar_carrito_por_stock(carrito)
        if carrito_limpio != carrito:
            session['carrito'] = carrito_limpio
            session.modified = True
        for cambio in cambios[:3]:
            flash(cambio, 'warning')
        if len(cambios) > 3:
            flash(f'Se aplicaron {len(cambios)} ajustes de stock en tu carrito.', 'warning')
        carrito = carrito_limpio
        total = sum(item['subtotal'] for item in carrito)
        return render_template('Usuarios/Carrito/cart.html', carrito=carrito, total=total)
    return "Acceso denegado"

@app.route('/get_cart_count')
def get_cart_count():
    carrito = session.get('carrito', [])
    count = len(carrito)
    return {'count': count}

@app.route('/cart/remove/<int:index>', methods=['POST'])
def remove_from_cart(index):
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
        if 0 <= index < len(carrito):
            carrito.pop(index)
            session['carrito'] = carrito
            session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
        if not carrito:
            flash('No hay productos en el carrito.', 'warning')
            return redirect(url_for('cart'))
        
        carrito_limpio, cambios = normalizar_carrito_por_stock(carrito)
        if carrito_limpio != carrito:
            session['carrito'] = carrito_limpio
            session.modified = True
        for cambio in cambios[:3]:
            flash(cambio, 'warning')
        if len(cambios) > 3:
            flash(f'Se aplicaron {len(cambios)} ajustes de stock en tu carrito.', 'warning')
        carrito = carrito_limpio
        total = sum(item['subtotal'] for item in carrito)
        return render_template('Usuarios/Carrito/checkout.html', carrito=carrito, total=total)
    return "Acceso denegado"

@app.route('/pay', methods=['POST'])
def pay():
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
        carrito_limpio, cambios = normalizar_carrito_por_stock(carrito)
        if carrito_limpio != carrito:
            session['carrito'] = carrito_limpio
            session.modified = True
        if cambios:
            flash('Actualizamos tu carrito por cambios de stock. Revisa antes de pagar.', 'warning')
            return redirect(url_for('cart'))
        carrito = carrito_limpio
        
        if not carrito:
            flash('No hay productos en el carrito.', 'warning')
            return redirect(url_for('cart'))
        
        total = sum(item['subtotal'] for item in carrito)
        codigo_promo = request.form.get('codigo_promo', '').strip().upper()
        promo_aplicada = None
        descuento_promo = 0.0

        pagos = cargar_pagos_df()

        if 'id_promo' not in pagos.columns:
            pagos['id_promo'] = pd.Series(dtype='float')
        if 'codigo_promo' not in pagos.columns:
            pagos['codigo_promo'] = ''
        if 'tipo_descuento' not in pagos.columns:
            pagos['tipo_descuento'] = ''
        if 'valor_descuento' not in pagos.columns:
            pagos['valor_descuento'] = 0.0
        if 'monto_descuento' not in pagos.columns:
            pagos['monto_descuento'] = 0.0

        pedidos = cargar_pedidos_df()
        detalle_pedido = cargar_detalle_pedido_df()

        productos = cargar_productos_df()
        if productos.empty:
            flash('No existe la base de productos.', 'danger')
            return redirect(url_for('cart'))

        promos = cargar_promociones_df()
        if codigo_promo:
            promo_aplicada = buscar_promocion_por_codigo(promos, codigo_promo, datetime.now().date())
            if promo_aplicada is None:
                flash('El código promocional no es válido o no está vigente.', 'warning')
                return redirect(url_for('cart'))
            descuento_promo = calcular_descuento_promocion(total, promo_aplicada)

        total_final = max(0.0, float(total) - float(descuento_promo))

        for item in carrito:
            id_producto = int(item.get('id_producto', 0))
            cantidad = int(item.get('cantidad', 0))
            fila = productos[(productos['id_producto'] == id_producto) & (productos['eliminado'] == False)]
            if fila.empty:
                flash(f'El producto "{item.get("nombre", id_producto)}" ya no está disponible.', 'warning')
                return redirect(url_for('cart'))
            stock_actual = int(fila.iloc[0].get('stock', 0))
            if cantidad > stock_actual:
                nombre = str(fila.iloc[0].get('nombre', item.get('nombre', id_producto)))
                flash(f'Stock insuficiente para "{nombre}". Disponible: {stock_actual}.', 'warning')
                return redirect(url_for('cart'))

        agotados_en_compra = []
        for item in carrito:
            id_producto = int(item.get('id_producto', 0))
            cantidad = int(item.get('cantidad', 0))
            idx = productos[productos['id_producto'] == id_producto].index[0]
            stock_anterior = int(productos.at[idx, 'stock'])
            nuevo_stock = stock_anterior - cantidad
            productos.at[idx, 'stock'] = nuevo_stock
            if stock_anterior > 0 and nuevo_stock == 0:
                agotados_en_compra.append(str(productos.at[idx, 'nombre']))

        guardar_productos_df(productos)

        # Crear nuevo pedido
        nuevo_id_pedido = next_id('pedidos', 'id_pedido')
        nuevo_pedido = {
            'id_pedido': nuevo_id_pedido,
            'id_usuario': session.get('id_usuario', session['usuario']),
            'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estado': 'pendiente'
        }
        pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
        guardar_pedidos_df(pedidos)
        
        # Guardar detalles del pedido
        next_detalle_id = next_id('detalle_pedido', 'id_detalle')
        for item in carrito:
            nuevo_detalle = {
                'id_detalle': next_detalle_id,
                'id_pedido': nuevo_id_pedido,
                'id_producto': item['id_producto'],
                'cantidad': item['cantidad'],
                'subtotal': item['subtotal']
            }
            detalle_pedido = pd.concat([detalle_pedido, pd.DataFrame([nuevo_detalle])], ignore_index=True)
            next_detalle_id += 1
        
        guardar_detalle_pedido_df(detalle_pedido)

        # Registrar pago
        nuevo_id_pago = next_id('pagos', 'id_pago')
        nuevo_pago = {
            'id_pago': nuevo_id_pago,
            'id_pedido': nuevo_id_pedido,
            'monto': total_final,
            'metodo_pago': request.form['metodo_pago'],
            'fecha_pago': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estado_pago': 'aprobado',
            'id_promo': int(pd.to_numeric(promo_aplicada.get('id_promo'), errors='coerce')) if promo_aplicada else '',
            'codigo_promo': promo_aplicada.get('codigo', '') if promo_aplicada else '',
            'tipo_descuento': promo_aplicada.get('tipo_descuento', '') if promo_aplicada else '',
            'valor_descuento': float(pd.to_numeric(promo_aplicada.get('valor_descuento', 0), errors='coerce')) if promo_aplicada else 0.0,
            'monto_descuento': float(descuento_promo)
        }
        pagos = pd.concat([pagos, pd.DataFrame([nuevo_pago])], ignore_index=True)
        guardar_pagos_df(pagos)
        
        # Registrar accion
        registrar_actividad(f"Creo pedido #{nuevo_id_pedido} con {len(carrito)} producto(s) por {formatear_cop(total_final)}")

        if agotados_en_compra:
            registrar_actividad("Stock agotado por pedido: " + ", ".join(agotados_en_compra))
        
        # Limpiar carrito
        session['carrito'] = []
        session.modified = True

        # Preparar datos para la pagina de confirmacion
        metodo_pago_nombres = {
            'tarjeta': 'Tarjeta de Credito/Debito',
            'transferencia': 'Transferencia Bancaria',
            'efectivo': 'Efectivo',
            'paypal': 'PayPal'
        }
        
        return render_template('Usuarios/Carrito/order_confirmation.html',
            pedido_id=nuevo_id_pedido,
            metodo_pago=metodo_pago_nombres.get(request.form['metodo_pago'], request.form['metodo_pago']),
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
            total=total_final,
            promo_codigo=promo_aplicada.get('codigo', '') if promo_aplicada else None,
            descuento=descuento_promo if promo_aplicada else 0
        )
    return "Acceso denegado"

@app.route('/user/orders')
def user_orders():
    if session.get('rol') != 'normal':
        return "Acceso denegado"
    
    pedidos = cargar_pedidos_df()
    id_usuario = session.get('id_usuario')
    pedidos_usuario = pedidos[pedidos['id_usuario'] == id_usuario] if not pedidos.empty else pd.DataFrame(columns=PEDIDO_COLUMNS)
    
    # Obtener montos de pagos
    if not pedidos_usuario.empty:
        pagos = cargar_pagos_df()
        pedidos_usuario = pd.merge(pedidos_usuario, pagos[['id_pedido', 'monto', 'metodo_pago']], 
                                   on='id_pedido', how='left')
    
    lista_pedidos = pedidos_usuario.to_dict(orient='records')
    return render_template('Usuarios/Carrito/user_orders.html', pedidos=lista_pedidos)

@app.route('/user/orders/details/<int:id_pedido>')
def user_order_details(id_pedido):
    if session.get('rol') != 'normal':
        return "Acceso denegado"
    
    # Verificar que el pedido pertenece al usuario
    pedidos = cargar_pedidos_df()
    pedido = pedidos[(pedidos['id_pedido'] == id_pedido) & 
                     (pedidos['id_usuario'] == session.get('id_usuario'))]
    
    if pedido.empty:
        return "Pedido no encontrado o no tienes permiso para verlo"
    
    detalle_pedido = cargar_detalle_pedido_df()
    detalles = detalle_pedido[detalle_pedido['id_pedido'] == id_pedido]
    
    productos = cargar_productos_df()
    detalles = pd.merge(detalles, productos[['id_producto', 'nombre', 'precio']], on='id_producto')
    
    return render_template('Usuarios/Informacion compras pedido/user_order_details.html',
                          pedido=pedido.iloc[0].to_dict(),
                          detalles=detalles.to_dict(orient='records'))

@app.route('/user/profile')
def user_profile():
    if session.get('rol') != 'normal':
        return "Acceso denegado"
    
    # Cargar informacion del usuario
    usuarios = cargar_usuarios_df()
    usuario_email = session.get('usuario')
    usuario = usuarios[usuarios['email'] == usuario_email]
    
    if usuario.empty:
        return "Usuario no encontrado"
    
    usuario_dict = usuario.iloc[0].to_dict()
    
    # Asegurar que existan las columnas telefono y direccion
    if 'telefono' not in usuario_dict:
        usuario_dict['telefono'] = ''
    if 'direccion' not in usuario_dict:
        usuario_dict['direccion'] = ''
    
    # Asegurar que existan las columnas de verificación
    if 'email_verified' not in usuario_dict:
        usuario_dict['email_verified'] = False
    
    # Asegurar que existan las columnas de configuracion con valores por defecto
    config_defaults = {
        'notif_email': True,
        'notif_pedidos': True,
        'notif_promociones': True,
        'perfil_publico': False,
        'mostrar_historial': False,
        'idioma': 'es',
        'moneda': 'COP'
    }
    for key, default_value in config_defaults.items():
        if key not in usuario_dict or pd.isna(usuario_dict[key]):
            usuario_dict[key] = default_value
    
    # Obtener estadísticas del usuario
    pedidos_total = 0
    gasto_total = 0.0
    
    pedidos = cargar_pedidos_df()
    if not pedidos.empty:
        id_usuario = session.get('id_usuario', usuario_email)
        pedidos_usuario = pedidos[pedidos['id_usuario'] == id_usuario]
        pedidos_total = len(pedidos_usuario)
        
        if not pedidos_usuario.empty:
            pagos = cargar_pagos_df()
            pagos_usuario = pagos[pagos['id_pedido'].isin(pedidos_usuario['id_pedido'])]
            gasto_total = pagos_usuario['monto'].sum() if not pagos_usuario.empty else 0.0
    
    return render_template('Usuarios/Ajustes/user_profile.html', 
                          usuario=usuario_dict,
                          pedidos_total=pedidos_total,
                          gasto_total=gasto_total)

@app.route('/user/profile/update', methods=['POST'])
def update_profile():
    if session.get('rol') != 'normal':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))
    
    # Obtener datos del formulario
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono', '')
    direccion = request.form.get('direccion', '')
    
    # Cargar usuarios
    usuarios = cargar_usuarios_df()
    usuario_email = session.get('usuario')
    
    # Asegurar que existan las columnas
    if 'telefono' not in usuarios.columns:
        usuarios['telefono'] = ''
    if 'direccion' not in usuarios.columns:
        usuarios['direccion'] = ''
    
    # Actualizar informacion
    idx = usuarios[usuarios['email'] == usuario_email].index
    if not idx.empty:
        usuarios.loc[idx, 'nombre'] = nombre
        usuarios.loc[idx, 'telefono'] = telefono
        usuarios.loc[idx, 'direccion'] = direccion
        
        guardar_usuarios_df(usuarios)
        registrar_actividad(f"Usuario {usuario_email} actualizo su perfil")
        flash('Perfil actualizado correctamente', 'success')
    else:
        flash('Error al actualizar el perfil', 'danger')
    
    return redirect(url_for('user_profile'))

@app.route('/user/profile/change-password', methods=['POST'])
def change_password():
    if session.get('rol') != 'normal':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))
    
    # Obtener datos del formulario
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validar que las contraseñas coincidan
    if new_password != confirm_password:
        flash('Las contraseñas nuevas no coinciden', 'danger')
        return redirect(url_for('user_profile'))
    
    # Cargar usuarios
    usuarios = cargar_usuarios_df()
    usuario_email = session.get('usuario')
    usuario = usuarios[usuarios['email'] == usuario_email]
    
    if usuario.empty:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('user_profile'))
    
    # Verificar contraseña actual
    if usuario.iloc[0]['password_hash'] != current_password:
        flash('La contraseña actual es incorrecta', 'danger')
        return redirect(url_for('user_profile'))
    
    # Actualizar contraseña
    idx = usuarios[usuarios['email'] == usuario_email].index
    usuarios.loc[idx, 'password_hash'] = new_password
    
    guardar_usuarios_df(usuarios)
    registrar_actividad(f"Usuario {usuario_email} cambió su contraseña")
    flash('Contraseña cambiada correctamente', 'success')
    
    return redirect(url_for('user_profile'))

@app.route('/user/profile/settings', methods=['POST'])
def update_settings():
    if session.get('rol') != 'normal':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))
    
    # Obtener datos del formulario
    notif_email = request.form.get('notif_email') == 'on'
    notif_pedidos = request.form.get('notif_pedidos') == 'on'
    notif_promociones = request.form.get('notif_promociones') == 'on'
    perfil_publico = request.form.get('perfil_publico') == 'on'
    mostrar_historial = request.form.get('mostrar_historial') == 'on'
    idioma = request.form.get('idioma', 'es')
    moneda = request.form.get('moneda', 'COP')
    
    # Cargar usuarios
    usuarios = cargar_usuarios_df()
    usuario_email = session.get('usuario')
    
    # Asegurar que existan las columnas de configuracion
    columnas_config = ['notif_email', 'notif_pedidos', 'notif_promociones', 
                       'perfil_publico', 'mostrar_historial', 'idioma', 'moneda']
    for col in columnas_config:
        if col not in usuarios.columns:
            usuarios[col] = '' if col in ['idioma', 'moneda'] else False
    
    # Actualizar configuracion
    idx = usuarios[usuarios['email'] == usuario_email].index
    if not idx.empty:
        usuarios.loc[idx, 'notif_email'] = notif_email
        usuarios.loc[idx, 'notif_pedidos'] = notif_pedidos
        usuarios.loc[idx, 'notif_promociones'] = notif_promociones
        usuarios.loc[idx, 'perfil_publico'] = perfil_publico
        usuarios.loc[idx, 'mostrar_historial'] = mostrar_historial
        usuarios.loc[idx, 'idioma'] = idioma
        usuarios.loc[idx, 'moneda'] = moneda
        
        guardar_usuarios_df(usuarios)
        registrar_actividad(f"Usuario {usuario_email} actualizo sus ajustes")
        flash('Ajustes guardados correctamente', 'success')
    else:
        flash('Error al guardar los ajustes', 'danger')
    
    return redirect(url_for('user_profile'))

@app.route('/user/send-verification-code', methods=['POST'])
def send_verification_code():
    """Envía un código de verificación al correo del usuario (funciona siempre)."""
    if session.get('rol') != 'normal':
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    
    try:
        # Verificar si está en modo desarrollo (sin configuración de Gmail)
        modo_desarrollo = (config_email.MAIL_USERNAME == 'tu_correo@gmail.com' or 
                          'xxxx' in config_email.MAIL_PASSWORD)
        
        # Cargar usuarios
        usuarios = cargar_usuarios_df()
        usuario_email = session.get('usuario')
        
        # Asegurar que existan las columnas de verificación
        if 'email_verified' not in usuarios.columns:
            usuarios['email_verified'] = False
        if 'verification_code' not in usuarios.columns:
            usuarios['verification_code'] = ''
        if 'verification_code_expiry' not in usuarios.columns:
            usuarios['verification_code_expiry'] = ''
        
        # Verificar si el usuario existe
        usuario_idx = usuarios[usuarios['email'] == usuario_email].index
        if usuario_idx.empty:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Generar código de verificación (sin importar si ya está verificado)
        codigo = generar_codigo_verificacion()
        expiry = datetime.now() + timedelta(minutes=10)
        
        # Guardar código en la base de datos (forzar como string)
        usuarios.loc[usuario_idx, 'verification_code'] = str(codigo)
        usuarios.loc[usuario_idx, 'verification_code_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
        
        # Asegurar que la columna sea tipo string
        usuarios['verification_code'] = usuarios['verification_code'].astype(str).str.replace('.0', '', regex=False).replace('nan', '')
        
        guardar_usuarios_df(usuarios)
        
        # MODO DESARROLLO: Mostrar código en consola sin enviar email
        if modo_desarrollo:
            print("\n" + "="*60)
            print("MODO DESARROLLO - CÓDIGO DE VERIFICACIÓN")
            print("="*60)
            print(f"Usuario: {usuario_email}")
            print(f"Código: {codigo}")
            print(f"Válido hasta: {expiry.strftime('%H:%M:%S')}")
            print("="*60 + "\n")
            
            registrar_actividad(f"Código de autenticación generado para {usuario_email} (modo desarrollo)")
            return jsonify({
                'success': True, 
                'message': f'Código generado: {codigo} (revisa la consola del servidor)'
            })
        
        # MODO PRODUCCIÓN: Enviar email real
        if enviar_codigo_verificacion(usuario_email, codigo):
            registrar_actividad(f"Código de autenticación enviado a {usuario_email}")
            return jsonify({
                'success': True, 
                'message': 'Código enviado correctamente. Revisa tu correo.'
            })
        else:
            # Si falla el envío, mostrar en consola como fallback
            print("\nERROR AL ENVIAR EMAIL - MOSTRANDO CÓDIGO EN CONSOLA:")
            print(f"Código para {usuario_email}: {codigo}\n")
            return jsonify({
                'success': True, 
                'message': f'Email no configurado. Tu código es: {codigo}'
            })
            
    except Exception as e:
        print(f"Error al enviar código: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/user/verify-email', methods=['POST'])
def verify_email():
    """Verifica el código ingresado por el usuario (funciona siempre)."""
    if session.get('rol') != 'normal':
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    
    try:
        codigo_ingresado = request.json.get('code', '').strip()
        
        if not codigo_ingresado:
            return jsonify({'success': False, 'message': 'Debe ingresar un código'}), 400
        
        # Cargar usuarios
        usuarios = cargar_usuarios_df()
        usuario_email = session.get('usuario')
        
        # Asegurar que existan las columnas
        if 'email_verified' not in usuarios.columns:
            usuarios['email_verified'] = False
        if 'verification_code' not in usuarios.columns:
            usuarios['verification_code'] = ''
        if 'verification_code_expiry' not in usuarios.columns:
            usuarios['verification_code_expiry'] = ''
        
        usuario_idx = usuarios[usuarios['email'] == usuario_email].index
        if usuario_idx.empty:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        usuario = usuarios.loc[usuario_idx[0]]
        
        # Verificar si existe un código
        if not usuario['verification_code']:
            return jsonify({'success': False, 'message': 'No hay código de verificación. Solicita uno nuevo.'}), 400
        
        # Verificar si el código expiró
        try:
            expiry = pd.to_datetime(usuario['verification_code_expiry'])
            if pd.Timestamp.now() > expiry:
                return jsonify({'success': False, 'message': 'El código ha expirado. Solicita uno nuevo.'}), 400
        except:
            return jsonify({'success': False, 'message': 'Error al verificar la fecha de expiración'}), 500
        
        # Verificar el código (limpiar .0 por si acaso)
        codigo_guardado = str(usuario['verification_code']).replace('.0', '').strip()
        if codigo_guardado == str(codigo_ingresado):
            # Código correcto
            # Marcar como verificado si no lo estaba
            if not usuario['email_verified']:
                usuarios.loc[usuario_idx, 'email_verified'] = True
                mensaje_exito = '¡Correo verificado exitosamente!'
                actividad = f"Usuario {usuario_email} verificó su correo electrónico"
            else:
                mensaje_exito = '¡Autenticación exitosa!'
                actividad = f"Usuario {usuario_email} se autenticó correctamente"
            
            # Limpiar código usado
            usuarios.loc[usuario_idx, 'verification_code'] = ''
            usuarios.loc[usuario_idx, 'verification_code_expiry'] = ''
            guardar_usuarios_df(usuarios)
            
            registrar_actividad(actividad)
            return jsonify({
                'success': True, 
                'message': mensaje_exito
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Código incorrecto. Verifica e intenta nuevamente.'
            }), 400
            
    except Exception as e:
        print(f"Error al verificar código: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Error interno del servidor'
        }), 500

# Ruta para el redireccionamiento para ver el catálogo
@app.route('/armada')
def armada():
    productos = cargar_productos_por_fuerza('Armada')
    return render_template('Usuarios/catalogo/armada.html', productos=productos)


@app.route('/policia')
def policia():
    productos = cargar_productos_por_fuerza('Policia')
    return render_template('Usuarios/catalogo/policia.html', productos=productos)


@app.route('/gaula')
def gaula():
    productos = cargar_productos_por_fuerza('Gaula')
    return render_template('Usuarios/catalogo/gaula.html', productos=productos)


@app.route('/ejercito')
def ejercito():
    productos = cargar_productos_por_fuerza('Ejercito')
    return render_template('Usuarios/catalogo/ejercito.html', productos=productos)

@app.route('/producto/<int:id_producto>')
def producto_detalle(id_producto):
    productos = cargar_productos_activos_df()

    producto = productos[productos['id_producto'] == id_producto]
    if producto.empty:
        return "Producto no encontrado"

    producto_dict = producto.iloc[0].to_dict()
    galeria = obtener_galeria_producto(id_producto, producto_dict.get('imagen_url', ''))[:MAX_IMAGES_PER_PRODUCT]
    producto_dict['imagenes'] = galeria
    if galeria:
        producto_dict['imagen_url'] = galeria[0]

    carrito = session.get('carrito', [])
    cart_count = len(carrito)
    return render_template('Usuarios/Detalle pedido/product_detail.html', producto=producto_dict, cart_count=cart_count)

@app.route('/admin/promo', methods=['GET','POST'])
def admin_promo():
    # Página de gestión de promociones para administradores
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    if request.method == 'POST':
        id_producto = pd.to_numeric(request.form.get('id_producto', ''), errors='coerce')
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        tipo_descuento = request.form.get('tipo_descuento', 'porcentaje').strip().lower()
        if tipo_descuento not in ['porcentaje', 'valor_fijo']:
            tipo_descuento = 'porcentaje'
        try:
            valor_descuento = float(request.form.get('valor_descuento', 0))
        except ValueError:
            valor_descuento = 0
        if valor_descuento < 0:
            valor_descuento = 0
        if tipo_descuento == 'porcentaje':
            valor_descuento = min(valor_descuento, 100)

        codigo = request.form.get('codigo', '').strip().upper()
        fecha_inicio = request.form.get('fecha_inicio', '')
        fecha_fin = request.form.get('fecha_fin', '')
        activo = request.form.get('activo') == 'on'
        inicio_date = parsear_fecha_promocion(fecha_inicio)
        fin_date = parsear_fecha_promocion(fecha_fin)
        if inicio_date and fin_date and inicio_date > fin_date:
            flash('La fecha de inicio no puede ser mayor que la fecha fin.', 'warning')
            return redirect(url_for('admin_promo'))
        if pd.isna(id_producto):
            flash('Debes seleccionar un producto para la promocion.', 'warning')
            return redirect(url_for('admin_promo'))
        productos_ref = cargar_productos_activos_df()
        id_producto_num = int(id_producto)
        existe_producto = not productos_ref[
            pd.to_numeric(productos_ref.get('id_producto', 0), errors='coerce') == id_producto_num
        ].empty
        if not existe_producto:
            flash('El producto seleccionado no existe o está inactivo.', 'warning')
            return redirect(url_for('admin_promo'))

        promos = cargar_promociones_df()
        if codigo:
            existe_codigo = promos[promos['codigo'].astype(str).str.upper() == codigo]
            if not existe_codigo.empty:
                flash('El código promocional ya existe. Usa otro.', 'warning')
                return redirect(url_for('admin_promo'))
        next_id = int(pd.to_numeric(promos['id_promo'], errors='coerce').max() + 1) if not promos.empty else 1
        nuevo = {
            'id_promo': next_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'tipo_descuento': tipo_descuento,
            'valor_descuento': valor_descuento,
            'id_producto': int(id_producto),
            'codigo': codigo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'activo': activo
        }
        promos = pd.concat([promos, pd.DataFrame([nuevo])], ignore_index=True)
        guardar_promociones_df(promos)
        detalle_desc = formatear_cop(valor_descuento) if tipo_descuento == 'valor_fijo' else f"{valor_descuento:.2f}%"
        registrar_actividad(
            f"Promocion creada: {nombre}\n"
            f"- producto ID: {int(id_producto)}\n"
            f"- descuento: {detalle_desc}\n"
            f"- codigo: {codigo or 'N/A'}"
        )
        return redirect(url_for('admin_promo'))

    promos = cargar_promociones_df()
    hoy = datetime.now().date()
    productos = cargar_productos_activos_df()
    productos['id_producto'] = pd.to_numeric(productos.get('id_producto', 0), errors='coerce').fillna(0).astype(int)
    lista_productos = productos.to_dict(orient='records')
    productos_por_fuerza = {fuerza: [] for fuerza in FUERZAS_OPCIONES}

    for producto in lista_productos:
        imagen_principal = str(producto.get('imagen_url', '')).strip()
        galeria = obtener_galeria_producto(producto.get('id_producto'), imagen_principal)
        producto['imagenes'] = galeria
        if galeria:
            producto['imagen_url'] = galeria[0]

        fuerza_producto = str(producto.get('fuerza', '')).strip().lower()
        for fuerza in FUERZAS_OPCIONES:
            if fuerza_producto == fuerza.lower():
                productos_por_fuerza[fuerza].append(producto)
                break

    pagos = cargar_pagos_df()
    if not pagos.empty:
        if 'id_promo' not in pagos.columns:
            pagos['id_promo'] = pd.Series(dtype='float')
        if 'monto_descuento' not in pagos.columns:
            pagos['monto_descuento'] = 0.0
        pagos['id_promo'] = pd.to_numeric(pagos['id_promo'], errors='coerce')
        pagos['monto_descuento'] = pd.to_numeric(pagos['monto_descuento'], errors='coerce').fillna(0.0)
        impacto = pagos.dropna(subset=['id_promo']).groupby('id_promo', as_index=False).agg(
            usos=('id_pago', 'count'),
            descuento_total=('monto_descuento', 'sum')
        )
    else:
        impacto = pd.DataFrame(columns=['id_promo', 'usos', 'descuento_total'])

    lista_promos = promos.to_dict(orient='records')
    impacto_map = {}
    for _, row in impacto.iterrows():
        impacto_map[int(row['id_promo'])] = {
            'usos': int(row['usos']),
            'descuento_total': float(row['descuento_total'])
        }
    for p in lista_promos:
        p['estado_vigencia'] = estado_vigencia_promocion(p, hoy)
        p['es_aplicable'] = promocion_esta_aplicable(p, hoy)
        p['id_producto'] = int(pd.to_numeric(p.get('id_producto'), errors='coerce') or 0)
        key = int(pd.to_numeric(p.get('id_promo'), errors='coerce') or 0)
        metrica = impacto_map.get(key, {'usos': 0, 'descuento_total': 0.0})
        p['usos'] = metrica['usos']
        p['descuento_total'] = metrica['descuento_total']
    nombre_producto = {int(row['id_producto']): str(row.get('nombre', 'Producto')) for _, row in productos.iterrows()}
    for p in lista_promos:
        p['producto_nombre'] = nombre_producto.get(p['id_producto'], 'Producto no encontrado')
    return render_template(
        'Administrador/Promociones/adim_promo.html',
        promos=lista_promos,
        productos=lista_productos,
        productos_por_fuerza=productos_por_fuerza,
        fuerzas=FUERZAS_OPCIONES
    )


@app.route('/admin/promo/toggle/<int:id_promo>', methods=['POST'])
def admin_promo_toggle(id_promo):
    if session.get('rol') != 'admin':
        return "Acceso denegado"
    promos = cargar_promociones_df()
    idx = promos[promos['id_promo'] == id_promo].index
    if not idx.empty:
        promos.loc[idx, 'activo'] = ~promos.loc[idx, 'activo']
        guardar_promociones_df(promos)
        registrar_actividad(f"Promocion {'activada' if promos.loc[idx, 'activo'].iloc[0] else 'desactivada'}: {promos.loc[idx, 'nombre'].iloc[0]}")
    return redirect(url_for('admin_promo'))


@app.route('/promociones')
def promociones():
    # Página pública que muestra promociones activas y vigentes
    promos = cargar_promociones_df()
    hoy = datetime.now().date()
    productos = cargar_productos_activos_df()
    productos['id_producto'] = pd.to_numeric(productos.get('id_producto', 0), errors='coerce')

    productos_map = {}
    for _, row in productos.iterrows():
        id_producto = pd.to_numeric(row.get('id_producto'), errors='coerce')
        if pd.notna(id_producto):
            productos_map[int(id_producto)] = {
                'nombre': str(row.get('nombre', '')).strip(),
                'imagen_url': str(row.get('imagen_url', '')).strip(),
                'precio': float(pd.to_numeric(row.get('precio', 0), errors='coerce') or 0),
                'descripcion': str(row.get('descripcion', '')).strip()
            }

    lista_promos = []
    for _, row in promos.iterrows():
        p = row.to_dict()
        if promocion_esta_aplicable(p, hoy):
            id_producto = pd.to_numeric(p.get('id_producto'), errors='coerce')
            producto = productos_map.get(int(id_producto), None) if pd.notna(id_producto) else None
            if producto:
                p['producto_nombre'] = producto['nombre'] or p.get('nombre', 'Producto')
                p['producto_imagen_url'] = producto['imagen_url']
                p['producto_precio'] = producto['precio']
                if not str(p.get('descripcion', '')).strip() and producto['descripcion']:
                    p['descripcion'] = producto['descripcion']
            else:
                p['producto_nombre'] = 'Producto no disponible'
                p['producto_imagen_url'] = ''
                p['producto_precio'] = 0.0
            p['estado_vigencia'] = estado_vigencia_promocion(p, hoy)
            lista_promos.append(p)
    return render_template('Usuarios/Promociones/promociones.html', promos=lista_promos)


@app.route('/admin/charts')
def admin_charts():
    if session.get('rol') == 'admin':
        periodo = request.args.get('periodo', 'all').strip().lower()
        fecha_desde_raw = request.args.get('fecha_desde', '').strip()
        fecha_hasta_raw = request.args.get('fecha_hasta', '').strip()
        datos = obtener_datos_charts(periodo, fecha_desde_raw, fecha_hasta_raw)

        return render_template(
            'Administrador/Informes/admin_charts_dashboard.html',
            ventas_producto=datos['ventas_producto'],
            ventas_mes=datos['ventas_mes'],
            metodos_pago=datos['metodos_pago'],
            top_productos=datos['top_productos'],
            kpis=datos['kpis'],
            kpi_variaciones=datos['kpi_variaciones'],
            filtros=datos['filtros'],
            rango_texto=datos['rango_texto'],
            comparacion_texto=datos['comparacion_texto']
        )
    return "Acceso denegado"


def obtener_datos_charts(periodo, fecha_desde_raw, fecha_hasta_raw):
    detalle = cargar_detalle_pedido_df()
    productos = cargar_productos_df()
    pedidos = cargar_pedidos_df()
    pagos = cargar_pagos_df()

    if 'id_producto' not in detalle.columns:
        detalle['id_producto'] = pd.Series(dtype='int')
    if 'cantidad' not in detalle.columns:
        detalle['cantidad'] = 0
    if 'subtotal' not in detalle.columns:
        detalle['subtotal'] = 0
    if 'id_pedido' not in detalle.columns:
        detalle['id_pedido'] = pd.Series(dtype='int')

    detalle['cantidad'] = pd.to_numeric(detalle['cantidad'], errors='coerce').fillna(0)
    detalle['subtotal'] = pd.to_numeric(detalle['subtotal'], errors='coerce').fillna(0)

    if 'id_producto' not in productos.columns:
        productos['id_producto'] = pd.Series(dtype='int')
    if 'nombre' not in productos.columns:
        productos['nombre'] = ''
    if 'precio' not in productos.columns:
        productos['precio'] = 0
    productos['precio'] = pd.to_numeric(productos['precio'], errors='coerce').fillna(0)

    if 'id_pedido' not in pedidos.columns:
        pedidos['id_pedido'] = pd.Series(dtype='int')
    if 'fecha_pedido' not in pedidos.columns:
        pedidos['fecha_pedido'] = ''
    pedidos['fecha_pedido'] = pd.to_datetime(pedidos['fecha_pedido'], errors='coerce')

    if 'monto' not in pagos.columns:
        pagos['monto'] = 0
    if 'metodo_pago' not in pagos.columns:
        pagos['metodo_pago'] = ''
    pagos['monto'] = pd.to_numeric(pagos['monto'], errors='coerce').fillna(0)
    pagos['metodo_pago'] = pagos['metodo_pago'].fillna('').astype(str)

    def filtrar_pedidos_por_rango(df_pedidos, desde=None, hasta=None):
        filtrado = df_pedidos.copy().dropna(subset=['fecha_pedido'])
        if desde is not None:
            filtrado = filtrado[filtrado['fecha_pedido'].dt.date >= desde]
        if hasta is not None:
            filtrado = filtrado[filtrado['fecha_pedido'].dt.date <= hasta]
        return filtrado

    def calcular_kpis_desde_pedidos(pedidos_base):
        ids = pedidos_base['id_pedido'].tolist()
        detalle_base = detalle[detalle['id_pedido'].isin(ids)].copy()
        pagos_base = pagos[pagos['id_pedido'].isin(ids)].copy()
        total_ventas_base = float(pagos_base['monto'].sum()) if not pagos_base.empty else float(detalle_base['subtotal'].sum())
        total_pedidos_base = int(len(pedidos_base))
        total_items_base = int(detalle_base['cantidad'].sum()) if not detalle_base.empty else 0
        ticket_promedio_base = (total_ventas_base / total_pedidos_base) if total_pedidos_base > 0 else 0
        return {
            'total_ventas': total_ventas_base,
            'total_pedidos': total_pedidos_base,
            'ticket_promedio': ticket_promedio_base,
            'total_items': total_items_base
        }

    def variacion_kpi(valor_actual, valor_anterior):
        if valor_anterior == 0:
            if valor_actual == 0:
                return {'trend': 'flat', 'texto': '0.0% vs periodo anterior'}
            return {'trend': 'up', 'texto': 'Nuevo vs periodo anterior'}

        delta_pct = ((valor_actual - valor_anterior) / abs(valor_anterior)) * 100
        trend = 'up' if delta_pct > 0 else 'down' if delta_pct < 0 else 'flat'
        return {'trend': trend, 'texto': f"{delta_pct:+.1f}% vs periodo anterior"}

    hoy = datetime.now().date()
    fecha_desde = None
    fecha_hasta = None

    if periodo == 'today':
        fecha_desde = hoy
        fecha_hasta = hoy
    elif periodo == 'week':
        fecha_desde = hoy - timedelta(days=6)
        fecha_hasta = hoy
    elif periodo == 'month':
        fecha_desde = hoy.replace(day=1)
        fecha_hasta = hoy
    elif periodo == 'range':
        if fecha_desde_raw:
            try:
                fecha_desde = datetime.strptime(fecha_desde_raw, '%Y-%m-%d').date()
            except ValueError:
                fecha_desde = None
        if fecha_hasta_raw:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_raw, '%Y-%m-%d').date()
            except ValueError:
                fecha_hasta = None
        if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    pedidos_filtrados = filtrar_pedidos_por_rango(pedidos, fecha_desde, fecha_hasta)
    ids_pedidos = pedidos_filtrados['id_pedido'].tolist()
    detalle_filtrado = detalle[detalle['id_pedido'].isin(ids_pedidos)].copy()
    pagos_filtrados = pagos[pagos['id_pedido'].isin(ids_pedidos)].copy()

    ventas_por_producto_df = detalle_filtrado.groupby('id_producto', as_index=False)['cantidad'].sum()
    ventas_por_producto_df = pd.merge(
        ventas_por_producto_df,
        productos[['id_producto', 'nombre']],
        on='id_producto',
        how='left'
    )
    ventas_por_producto_df['nombre'] = ventas_por_producto_df['nombre'].fillna('Producto sin nombre')

    pedidos_fechas = pedidos_filtrados.copy()
    pedidos_fechas['mes'] = pedidos_fechas['fecha_pedido'].dt.to_period('M').astype(str)

    ventas_por_mes_df = detalle_filtrado.groupby('id_pedido', as_index=False)['subtotal'].sum()
    ventas_por_mes_df = pd.merge(ventas_por_mes_df, pedidos_fechas[['id_pedido', 'mes']], on='id_pedido', how='left')
    ventas_por_mes_df = ventas_por_mes_df.dropna(subset=['mes'])
    ventas_por_mes_df = ventas_por_mes_df.groupby('mes', as_index=False)['subtotal'].sum().sort_values('mes')

    metodos_pago_df = pagos_filtrados.groupby('metodo_pago', as_index=False)['monto'].sum()
    metodos_pago_df = metodos_pago_df[metodos_pago_df['metodo_pago'].str.strip() != '']

    kpis = calcular_kpis_desde_pedidos(pedidos_filtrados)

    top_productos_df = ventas_por_producto_df.sort_values('cantidad', ascending=False).head(5).copy()
    top_productos_df = pd.merge(
        top_productos_df,
        productos[['id_producto', 'precio']],
        on='id_producto',
        how='left'
    )
    top_productos_df['precio'] = pd.to_numeric(top_productos_df['precio'], errors='coerce').fillna(0)

    kpis_anterior = {'total_ventas': 0, 'total_pedidos': 0, 'ticket_promedio': 0, 'total_items': 0}
    comparacion_texto = 'Sin comparacion de periodo'
    if fecha_desde is not None and fecha_hasta is not None:
        dias_periodo = max(1, (fecha_hasta - fecha_desde).days + 1)
        anterior_hasta = fecha_desde - timedelta(days=1)
        anterior_desde = anterior_hasta - timedelta(days=dias_periodo - 1)
        pedidos_anterior = filtrar_pedidos_por_rango(pedidos, anterior_desde, anterior_hasta)
        kpis_anterior = calcular_kpis_desde_pedidos(pedidos_anterior)
        comparacion_texto = (
            f"Comparando contra {anterior_desde.strftime('%Y-%m-%d')} a "
            f"{anterior_hasta.strftime('%Y-%m-%d')}"
        )
    elif periodo == 'all':
        comparacion_texto = 'Selecciona un periodo para activar comparacion'

    kpi_variaciones = {
        'total_ventas': variacion_kpi(kpis['total_ventas'], kpis_anterior['total_ventas']),
        'total_pedidos': variacion_kpi(kpis['total_pedidos'], kpis_anterior['total_pedidos']),
        'ticket_promedio': variacion_kpi(kpis['ticket_promedio'], kpis_anterior['ticket_promedio']),
        'total_items': variacion_kpi(kpis['total_items'], kpis_anterior['total_items'])
    }

    rango_texto = 'Todo el historial'
    if fecha_desde is not None and fecha_hasta is not None:
        rango_texto = f"{fecha_desde.strftime('%Y-%m-%d')} a {fecha_hasta.strftime('%Y-%m-%d')}"
    elif fecha_desde is not None:
        rango_texto = f"Desde {fecha_desde.strftime('%Y-%m-%d')}"
    elif fecha_hasta is not None:
        rango_texto = f"Hasta {fecha_hasta.strftime('%Y-%m-%d')}"

    filtros = {
        'periodo': periodo if periodo in {'all', 'today', 'week', 'month', 'range'} else 'all',
        'fecha_desde': fecha_desde_raw,
        'fecha_hasta': fecha_hasta_raw
    }

    return {
        'ventas_producto': ventas_por_producto_df.to_dict(orient='records'),
        'ventas_mes': ventas_por_mes_df.to_dict(orient='records'),
        'metodos_pago': metodos_pago_df.to_dict(orient='records'),
        'top_productos': top_productos_df.to_dict(orient='records'),
        'kpis': kpis,
        'kpi_variaciones': kpi_variaciones,
        'filtros': filtros,
        'rango_texto': rango_texto,
        'comparacion_texto': comparacion_texto,
        'ventas_producto_df': ventas_por_producto_df,
        'ventas_mes_df': ventas_por_mes_df,
        'metodos_pago_df': metodos_pago_df,
        'top_productos_df': top_productos_df
    }


@app.route('/admin/charts/export_excel')
def admin_charts_export_excel():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    periodo = request.args.get('periodo', 'all').strip().lower()
    fecha_desde_raw = request.args.get('fecha_desde', '').strip()
    fecha_hasta_raw = request.args.get('fecha_hasta', '').strip()
    datos = obtener_datos_charts(periodo, fecha_desde_raw, fecha_hasta_raw)

    resumen_df = pd.DataFrame([
        {'metrica': 'Ventas totales', 'valor': formatear_cop(datos['kpis']['total_ventas'])},
        {'metrica': 'Pedidos', 'valor': datos['kpis']['total_pedidos']},
        {'metrica': 'Ticket promedio', 'valor': formatear_cop(datos['kpis']['ticket_promedio'])},
        {'metrica': 'Items vendidos', 'valor': datos['kpis']['total_items']},
        {'metrica': 'Rango aplicado', 'valor': datos['rango_texto']},
        {'metrica': 'Comparacion', 'valor': datos['comparacion_texto']}
    ])

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
        datos['ventas_producto_df'].to_excel(writer, sheet_name='Ventas por producto', index=False)
        datos['ventas_mes_df'].to_excel(writer, sheet_name='Ventas por mes', index=False)
        datos['metodos_pago_df'].to_excel(writer, sheet_name='Metodos de pago', index=False)
        datos['top_productos_df'].to_excel(writer, sheet_name='Top productos', index=False)

        wb = writer.book
        ws_producto = wb['Ventas por producto']
        ws_mes = wb['Ventas por mes']
        ws_metodos = wb['Metodos de pago']
        ws_top = wb['Top productos']
        formato_cop = '[>=1000]#,##0.00 "COP";0.00 "COP"'

        # Formatos numericos COP en columnas monetarias
        for row in range(2, ws_mes.max_row + 1):
            ws_mes.cell(row=row, column=2).number_format = formato_cop  # subtotal
        for row in range(2, ws_metodos.max_row + 1):
            ws_metodos.cell(row=row, column=2).number_format = formato_cop  # monto
        for row in range(2, ws_top.max_row + 1):
            ws_top.cell(row=row, column=4).number_format = formato_cop  # precio

        if ws_producto.max_row > 1:
            chart_prod = BarChart()
            chart_prod.title = 'Cantidad vendida por producto'
            chart_prod.y_axis.title = 'Cantidad'
            chart_prod.x_axis.title = 'Producto'
            data_prod = Reference(ws_producto, min_col=3, min_row=1, max_row=ws_producto.max_row)
            cats_prod = Reference(ws_producto, min_col=2, min_row=2, max_row=ws_producto.max_row)
            chart_prod.add_data(data_prod, titles_from_data=True)
            chart_prod.set_categories(cats_prod)
            chart_prod.height = 8
            chart_prod.width = 14
            if chart_prod.series:
                chart_prod.series[0].graphicalProperties.solidFill = "1882A9"
            ws_producto.add_chart(chart_prod, 'E2')

        if ws_mes.max_row > 1:
            chart_mes = LineChart()
            chart_mes.title = 'Ventas por mes'
            chart_mes.y_axis.title = 'Subtotal'
            chart_mes.x_axis.title = 'Mes'
            data_mes = Reference(ws_mes, min_col=2, min_row=1, max_row=ws_mes.max_row)
            cats_mes = Reference(ws_mes, min_col=1, min_row=2, max_row=ws_mes.max_row)
            chart_mes.add_data(data_mes, titles_from_data=True)
            chart_mes.set_categories(cats_mes)
            chart_mes.height = 8
            chart_mes.width = 14
            if chart_mes.series:
                chart_mes.series[0].graphicalProperties.line.solidFill = "0A2962"
            ws_mes.add_chart(chart_mes, 'D2')

        if ws_metodos.max_row > 1:
            chart_met = PieChart()
            chart_met.title = 'Distribucion por metodo de pago'
            data_met = Reference(ws_metodos, min_col=2, min_row=1, max_row=ws_metodos.max_row)
            cats_met = Reference(ws_metodos, min_col=1, min_row=2, max_row=ws_metodos.max_row)
            chart_met.add_data(data_met, titles_from_data=True)
            chart_met.set_categories(cats_met)
            chart_met.height = 8
            chart_met.width = 12
            if chart_met.series:
                colores = ["0A2962", "1882A9", "1ABC9C", "F1C40F", "E74C3C", "6C5CE7"]
                points = []
                num_points = max(0, ws_metodos.max_row - 1)
                for i in range(num_points):
                    pt = DataPoint(idx=i)
                    pt.graphicalProperties.solidFill = colores[i % len(colores)]
                    points.append(pt)
                chart_met.series[0].dPt = points
            ws_metodos.add_chart(chart_met, 'D2')

        if ws_top.max_row > 1:
            chart_top = BarChart()
            chart_top.title = 'Top productos vendidos'
            chart_top.y_axis.title = 'Cantidad'
            chart_top.x_axis.title = 'Producto'
            data_top = Reference(ws_top, min_col=3, min_row=1, max_row=ws_top.max_row)
            cats_top = Reference(ws_top, min_col=2, min_row=2, max_row=ws_top.max_row)
            chart_top.add_data(data_top, titles_from_data=True)
            chart_top.set_categories(cats_top)
            chart_top.height = 8
            chart_top.width = 14
            if chart_top.series:
                chart_top.series[0].graphicalProperties.solidFill = "0A2962"
            ws_top.add_chart(chart_top, 'F2')
    buffer.seek(0)

    nombre_archivo = f"graficas_informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
#orden personalizada
@app.route('/orden-personalizada')
def orden_personalizada():
    return render_template('Usuarios/orden_personalizada/orden.html')

#sobre nosotros
@app.route('/sobre-nosotros')
def sobre_nosotros():
    return render_template('Usuarios/Informacion empresa/sobre_nosotros.html')

if __name__ == '__main__':
    app.run(debug=True)




