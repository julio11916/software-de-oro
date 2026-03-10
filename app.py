import os
import json
import pandas as pd
from io import BytesIO
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash, send_file, jsonify
from datetime import datetime, timedelta, date
from typing import Any, Mapping, Optional
from email_service import mail, generar_codigo_verificacion, enviar_codigo_verificacion
import config_email
from db_utils import engine  # Inicializa DB y proxys al importar

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
    "Fundas para almohadas", "Camuflados"
]

# DB init y proxys se hacen al importar db_utils


def cargar_usuarios_df():
    if os.path.exists('bd/usuarios.xlsx'):
        usuarios = pd.read_excel('bd/usuarios.xlsx')
    else:
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
    usuarios.to_excel('bd/usuarios.xlsx', index=False)


def cargar_registros_df():
    if os.path.exists('bd/registros.xlsx'):
        registros = pd.read_excel('bd/registros.xlsx')
    else:
        registros = pd.DataFrame(columns=REGISTRO_COLUMNS)

    for col in REGISTRO_COLUMNS:
        if col not in registros.columns:
            registros[col] = ''
    return registros[REGISTRO_COLUMNS]


def cargar_promociones_df():
    """Carga el DataFrame de promociones desde bd/promociones.xlsx.
    Si el archivo no existe se crea con columnas definidas.
    """
    if os.path.exists('bd/promociones.xlsx'):
        promos = pd.read_excel('bd/promociones.xlsx')
    else:
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
    """Guarda las promociones en bd/promociones.xlsx"""
    promos.to_excel('bd/promociones.xlsx', index=False)


def normalizar_imagen_url(valor):
    ruta = str(valor or '').strip().replace('\\', '/')
    if not ruta or ruta.lower() == 'nan':
        return ''
    if ruta.startswith('img/Empresa/') or ruta.startswith('img/Pagina/'):
        return ruta
    if ruta.startswith('img/'):
        return f"img/Empresa/{ruta.split('/')[-1]}"
    return ruta


def normalizar_imagenes_productos(productos):
    if 'imagen_url' not in productos.columns:
        productos['imagen_url'] = ''
    productos['imagen_url'] = productos['imagen_url'].apply(normalizar_imagen_url)
    return productos


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
    registros.to_excel('bd/registros.xlsx', index=False)


def obtener_nombre_sesion():
    nombre = str(session.get('nombre', '')).strip()
    if nombre:
        return nombre

    email = str(session.get('usuario', '')).strip()
    if not email:
        return 'Administrador'

    if os.path.exists('bd/usuarios.xlsx'):
        usuarios = pd.read_excel('bd/usuarios.xlsx')
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


def obtener_productos_agotados():
    if not os.path.exists('bd/producto.xlsx'):
        return []

    productos = pd.read_excel('bd/producto.xlsx')
    if productos.empty:
        return []

    if 'stock' not in productos.columns:
        productos['stock'] = 0
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    if 'nombre' not in productos.columns:
        productos['nombre'] = ''
    if 'id_producto' not in productos.columns:
        productos['id_producto'] = 0

    productos['stock'] = pd.to_numeric(productos['stock'], errors='coerce').fillna(0).astype(int)
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

    agotados = productos[(productos['eliminado'] == False) & (productos['stock'] <= 0)].copy()
    if agotados.empty:
        return []

    agotados = agotados.sort_values(by='nombre', na_position='last')
    return agotados[['id_producto', 'nombre', 'stock']].to_dict(orient='records')


def normalizar_carrito_por_stock(carrito):
    if not carrito:
        return [], []

    if not os.path.exists('bd/producto.xlsx'):
        return carrito, []

    productos = pd.read_excel('bd/producto.xlsx')
    if 'id_producto' not in productos.columns:
        return carrito, []
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    if 'stock' not in productos.columns:
        productos['stock'] = 0
    if 'precio' not in productos.columns:
        productos['precio'] = 0
    if 'nombre' not in productos.columns:
        productos['nombre'] = ''

    productos['id_producto'] = pd.to_numeric(productos['id_producto'], errors='coerce')
    productos['stock'] = pd.to_numeric(productos['stock'], errors='coerce').fillna(0).astype(int)
    productos['precio'] = pd.to_numeric(productos['precio'], errors='coerce').fillna(0.0).astype(float)
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

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
    if os.path.exists('bd/producto.xlsx'):
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)
    else:
        productos = pd.DataFrame(columns=['id_producto', 'nombre', 'precio', 'stock', 'eliminado'])

    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos = productos[productos['eliminado'] == False]

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
            return "Tu usuario est? inactivo. Contacta al administrador."

        rol = usuario.iloc[0]['rol']
        id_usuario = usuario.iloc[0]['id_usuario']
        nombre = str(usuario.iloc[0].get('nombre', '')).strip()
        session['usuario'] = email
        session['id_usuario'] = int(id_usuario)
        session['rol'] = rol
        session['nombre'] = nombre

        # Registrar el login
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': email,
            'accion': f"Inicio de sesión exitoso",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

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

        if os.path.exists('bd/usuarios.xlsx'):
            usuarios = pd.read_excel('bd/usuarios.xlsx')
        else:
            usuarios = pd.DataFrame(columns=['id_usuario', 'nombre', 'email', 'password_hash', 'rol', 'estado', 'fecha_registro'])

        if email in usuarios['email'].values:
            return "Este correo ya est? registrado."

        nuevo_id = len(usuarios) + 1
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
        usuarios.to_excel('bd/usuarios.xlsx', index=False)

        # Registrar el nuevo usuario en registros
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': email,
            'accion': f"Nuevo usuario registrado: {nombre}",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

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
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)

        # Asegurar que la columna 'eliminado' existe y es booleana
        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

        productos = productos[productos['eliminado'] == False]
        lista_productos = productos.to_dict(orient='records')
        productos_agotados = obtener_productos_agotados()
        admin_nombre = obtener_nombre_sesion()
        # plantilla actual en el proyecto
        return render_template(
            'Administrador/admin_dashboard_principal.html',
            productos=lista_productos,
            admin_nombre=admin_nombre,
            productos_agotados=productos_agotados
        )
    return "Acceso denegado"


@app.route('/admin/productos')
def admin_productos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    productos = normalizar_imagenes_productos(productos)
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    if 'fuerza' not in productos.columns:
        productos['fuerza'] = ''
    if 'intendencia' not in productos.columns:
        productos['intendencia'] = ''
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

    productos = productos[productos['eliminado'] == False]
    lista_productos = productos.to_dict(orient='records')
    return render_template(
        'Administrador/Gestion productos/admin_prod_dashboard.html',
        productos=lista_productos,
        fuerzas=FUERZAS_OPCIONES,
        intendencias=INTENDENCIAS_OPCIONES
    )


@app.route('/admin/agregar_producto', methods=['POST'])
def agregar_producto():
    if session.get('rol') == 'admin':
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)
        if 'fuerza' not in productos.columns:
            productos['fuerza'] = ''
        if 'intendencia' not in productos.columns:
            productos['intendencia'] = ''
        if 'imagen_url' not in productos.columns:
            productos['imagen_url'] = ''

        nuevo_id = len(productos) + 1
        fuerza = request.form.get('fuerza', '').strip()
        intendencia = request.form.get('intendencia', '').strip()
        if fuerza not in FUERZAS_OPCIONES or intendencia not in INTENDENCIAS_OPCIONES:
            flash('Selecciona una fuerza e intendencia validas.', 'danger')
            return redirect(url_for('admin_productos'))

        imagen_url = ''
        imagen = request.files.get('imagen')
        if imagen and imagen.filename:
            extensiones_permitidas = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            extension = imagen.filename.rsplit('.', 1)[-1].lower() if '.' in imagen.filename else ''
            if extension not in extensiones_permitidas:
                flash("Formato de imagen no permitido. Usa .jpg, .jpeg, .png, .gif o .webp.", 'danger')
                return redirect(url_for('admin_productos'))

            imagen.seek(0, os.SEEK_END)
            tamano = imagen.tell()
            imagen.seek(0)
            if tamano > 2 * 1024 * 1024:
                flash("La imagen excede el tamano maximo permitido (2MB).", 'danger')
                return redirect(url_for('admin_productos'))

            carpeta_destino = os.path.join('static', 'img', 'Empresa')
            os.makedirs(carpeta_destino, exist_ok=True)
            ruta = os.path.join(carpeta_destino, f'producto_{nuevo_id}.jpg')
            imagen.save(ruta)
            imagen_url = f'img/Empresa/producto_{nuevo_id}.jpg'

        nuevo_producto = {
            'id_producto': nuevo_id,
            'nombre': request.form['nombre'],
            'descripcion': request.form['descripcion'],
            'precio': float(request.form['precio']),
            'stock': int(request.form['stock']),
            'id_categoria': 1,  # Se conserva por compatibilidad
            'fuerza': fuerza,
            'intendencia': intendencia,
            'imagen_url': imagen_url
        }

        productos = pd.concat([productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
        productos.to_excel('bd/producto.xlsx', index=False)

        # Registrar acción en registros.xlsx
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': session['usuario'],
            'accion': (
                f"Creo producto '{request.form['nombre']}' (ID {nuevo_id})\n"
                f"- precio: {formatear_cop(float(request.form['precio']))}\n"
                f"- stock: {int(request.form['stock'])}\n"
                f"- fuerza: {fuerza}\n"
                f"- intendencia: {intendencia}"
            ),
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

        return redirect(url_for('admin_productos'))
    return "Acceso denegado"

@app.route('/admin/sales/export')
def export_sales():
    if session.get('rol') != 'admin':
        return "Acceso denegado"
    
    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
    else:
        pedidos = pd.DataFrame(columns=['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'])
    
    if os.path.exists('bd/pagos.xlsx'):
        pagos = pd.read_excel('bd/pagos.xlsx')
    else:
        pagos = pd.DataFrame(columns=['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago'])
    
    if os.path.exists('bd/detalle_pedido.xlsx'):
        detalle = pd.read_excel('bd/detalle_pedido.xlsx')
    else:
        detalle = pd.DataFrame(columns=['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal'])
    
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

    imagen = request.files.get('imagen')
    if imagen:
        # Validar extensión
        extensiones_permitidas = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        extension = imagen.filename.rsplit('.', 1)[-1].lower()
        if extension not in extensiones_permitidas:
            flash("Formato de imagen no permitido. Usa .jpg, .jpeg, .png, .gif o .webp.")
            return redirect(url_for('admin_productos'))

        # Validar tamano (max. 2MB)
        imagen.seek(0, os.SEEK_END)
        tamano = imagen.tell()
        imagen.seek(0)
        if tamano > 2 * 1024 * 1024:
            flash("La imagen excede el tamano maximo permitido (2MB).")
            return redirect(url_for('admin_productos'))

        # Guardar imagen
        carpeta_destino = os.path.join('static', 'img', 'Empresa')
        os.makedirs(carpeta_destino, exist_ok=True)
        ruta = os.path.join(carpeta_destino, f'producto_{id_producto}.jpg')
        imagen.save(ruta)

        # Registrar ruta en el Excel
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)
        idx = productos[productos['id_producto'] == id_producto].index
        if not idx.empty:
            productos.at[idx[0], 'imagen_url'] = f'img/Empresa/producto_{id_producto}.jpg'
            productos.to_excel('bd/producto.xlsx', index=False)

        flash("Imagen subida correctamente.")

    else:
        flash("No se seleccion? ninguna imagen.")

    return redirect(url_for('admin_productos'))



@app.route('/admin/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')

    # Asegurar que la columna 'eliminado' existe y es del tipo correcto
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].astype(object)

    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        productos.at[idx[0], 'eliminado'] = True
        productos.to_excel('bd/producto.xlsx', index=False)

        # Registrar acción
        nombre = productos.at[idx[0], 'nombre']
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': session['usuario'],
            'accion': f"Elimin? producto: {nombre} (ID {id_producto})",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

    return redirect(url_for('admin_productos'))

@app.route('/admin/eliminar_definitivo/<int:id_producto>', methods=['POST'])
def eliminar_definitivo(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        nombre = productos.at[idx[0], 'nombre']
        productos = productos.drop(index=idx)
        productos.to_excel('bd/producto.xlsx', index=False)

        # Registrar acción
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': session['usuario'],
            'accion': f"Elimin? definitivamente el producto: {nombre} (ID {id_producto})",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

    return redirect(url_for('admin_papelera'))

@app.route('/admin/restaurar/<int:id_producto>', methods=['POST'])
def restaurar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    idx = productos[productos['id_producto'] == id_producto].index

    if not idx.empty:
        productos['eliminado'] = productos['eliminado'].astype(object)
        productos.at[idx[0], 'eliminado'] = False
        productos.to_excel('bd/producto.xlsx', index=False)

        # Registrar restauración
        nombre = productos.at[idx[0], 'nombre']
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])

        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': session['usuario'],
            'accion': f"Restaur? producto: {nombre} (ID {id_producto})",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

    return redirect(url_for('admin_papelera'))


@app.route('/admin/papelera')
def admin_papelera():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')

    # Asegurar que la columna 'eliminado' existe y es del tipo correcto
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].astype(object)

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
            flash('ID de usuario invalido.', 'danger')
            return redirect(url_for('admin_usuarios'))

    if edit_id is None and not password:
        flash('La contrasena es obligatoria para crear usuarios.', 'danger')
        return redirect(url_for('admin_usuarios'))

    existe_email = usuarios[usuarios['email'].str.lower() == email.lower()]
    if edit_id is not None:
        existe_email = existe_email[existe_email['id_usuario'] != edit_id]
    if not existe_email.empty:
        flash('Ese email ya esta registrado por otro usuario.', 'danger')
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

    if os.path.exists('bd/producto.xlsx'):
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)
    else:
        productos = pd.DataFrame(columns=['id_producto', 'nombre', 'precio', 'stock', 'eliminado'])

    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0)
    productos['precio'] = pd.to_numeric(productos.get('precio', 0), errors='coerce').fillna(0)

    productos_activos = productos[productos['eliminado'] == False].copy()
    lista_productos = productos_activos.to_dict(orient='records')
    return render_template('Administrador/Sistema POS/admin_pos_dashboard.html', productos=lista_productos)


@app.route('/admin/pedidos')
def admin_pedidos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
    else:
        pedidos = pd.DataFrame(columns=['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'])

    if os.path.exists('bd/pagos.xlsx'):
        pagos = pd.read_excel('bd/pagos.xlsx')
    else:
        pagos = pd.DataFrame(columns=['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago'])

    if os.path.exists('bd/detalle_pedido.xlsx'):
        detalle = pd.read_excel('bd/detalle_pedido.xlsx')
    else:
        detalle = pd.DataFrame(columns=['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal'])

    if os.path.exists('bd/producto.xlsx'):
        productos = pd.read_excel('bd/producto.xlsx')
    else:
        productos = pd.DataFrame(columns=['id_producto', 'nombre'])

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
    pedidos_view = pedidos_view.sort_values(by='id_pedido', ascending=False, na_position='last')

    pagos_view = pagos.sort_values(by='id_pago', ascending=False, na_position='last')

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

    return render_template(
        'Administrador/Gestion pedidos/admin_orders.html',
        pedidos=lista_pedidos,
        pagos=lista_pagos
    )


@app.route('/admin/pedidos/estado/<int:id_pedido>', methods=['POST'])
def admin_pedidos_estado(id_pedido):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    estado_nuevo = request.form.get('estado', '').strip().lower()
    estados_validos = {'pendiente', 'enviado', 'entregado', 'cancelado'}
    if estado_nuevo not in estados_validos:
        flash('Estado de pedido invalido.', 'danger')
        return redirect(url_for('admin_pedidos'))

    if not os.path.exists('bd/pedidos.xlsx'):
        flash('No existe la base de pedidos.', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedidos = pd.read_excel('bd/pedidos.xlsx')
    if 'id_pedido' not in pedidos.columns:
        flash('Estructura de pedidos invalida.', 'danger')
        return redirect(url_for('admin_pedidos'))
    if 'estado' not in pedidos.columns:
        pedidos['estado'] = 'pendiente'

    pedidos['id_pedido'] = pd.to_numeric(pedidos['id_pedido'], errors='coerce')
    idx = pedidos[pedidos['id_pedido'] == id_pedido].index
    if idx.empty:
        flash('Pedido no encontrado.', 'warning')
        return redirect(url_for('admin_pedidos'))

    estado_anterior = str(pedidos.at[idx[0], 'estado']).strip().lower()
    pedidos.at[idx[0], 'estado'] = estado_nuevo
    pedidos.to_excel('bd/pedidos.xlsx', index=False)

    if estado_anterior != estado_nuevo:
        registrar_actividad(f"Actualizo estado de pedido #{id_pedido}: {estado_anterior} -> {estado_nuevo}")
        flash(f'Pedido #{id_pedido} actualizado a "{estado_nuevo}".', 'success')
    else:
        flash(f'El pedido #{id_pedido} ya estaba en "{estado_nuevo}".', 'info')

    return redirect(url_for('admin_pedidos'))


@app.route('/admin/pos/checkout', methods=['POST'])
def admin_pos_checkout():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

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

    if os.path.exists('bd/producto.xlsx'):
        productos = pd.read_excel('bd/producto.xlsx')
    else:
        flash('No existe el catalogo de productos.', 'danger')
        return redirect(url_for('admin_pos'))

    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0)
    productos['precio'] = pd.to_numeric(productos.get('precio', 0), errors='coerce').fillna(0)
    productos['id_producto'] = pd.to_numeric(productos.get('id_producto', 0), errors='coerce')

    carrito_validado = []
    total = 0.0

    for item in items:
        try:
            id_producto = int(item.get('id_producto', 0))
            cantidad = int(item.get('cantidad', 0))
        except (TypeError, ValueError):
            flash('Hay productos invalidos en el carrito POS.', 'danger')
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
            flash(f'El producto ID {id_producto} esta eliminado.', 'danger')
            return redirect(url_for('admin_pos'))

        stock_actual = int(productos.at[row_idx, 'stock'])
        if cantidad > stock_actual:
            nombre = str(productos.at[row_idx, 'nombre'])
            flash(f'Stock insuficiente para "{nombre}". Disponible: {stock_actual}.', 'warning')
            return redirect(url_for('admin_pos'))

        precio = float(productos.at[row_idx, 'precio'])
        subtotal = precio * cantidad
        total += subtotal

        productos.at[row_idx, 'stock'] = stock_actual - cantidad
        carrito_validado.append({
            'id_producto': id_producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })

    productos.to_excel('bd/producto.xlsx', index=False)

    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
    else:
        pedidos = pd.DataFrame(columns=['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'])

    if os.path.exists('bd/detalle_pedido.xlsx'):
        detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
    else:
        detalle_pedido = pd.DataFrame(columns=['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal'])

    if os.path.exists('bd/pagos.xlsx'):
        pagos = pd.read_excel('bd/pagos.xlsx')
    else:
        pagos = pd.DataFrame(columns=['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago'])

    next_pedido_id = int(pd.to_numeric(pedidos.get('id_pedido', pd.Series(dtype='float')), errors='coerce').max() + 1) if not pedidos.empty else 1
    nuevo_pedido = {
        'id_pedido': next_pedido_id,
        'id_usuario': session.get('usuario', 'admin_pos'),
        'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'estado': 'completado'
    }
    pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
    pedidos.to_excel('bd/pedidos.xlsx', index=False)

    next_detalle_id = int(pd.to_numeric(detalle_pedido.get('id_detalle', pd.Series(dtype='float')), errors='coerce').max() + 1) if not detalle_pedido.empty else 1
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
    detalle_pedido.to_excel('bd/detalle_pedido.xlsx', index=False)

    next_pago_id = int(pd.to_numeric(pagos.get('id_pago', pd.Series(dtype='float')), errors='coerce').max() + 1) if not pagos.empty else 1
    nuevo_pago = {
        'id_pago': next_pago_id,
        'id_pedido': next_pedido_id,
        'monto': round(total, 2),
        'metodo_pago': metodo_pago,
        'fecha_pago': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'estado_pago': 'aprobado'
    }
    pagos = pd.concat([pagos, pd.DataFrame([nuevo_pago])], ignore_index=True)
    pagos.to_excel('bd/pagos.xlsx', index=False)
    total_cop = formatear_cop(round(total, 2))
    registrar_actividad(f"POS registro venta #{next_pedido_id} por {total_cop} ({len(carrito_validado)} producto(s))")
    flash(f'Venta POS registrada. Pedido #{next_pedido_id} por {total_cop}.', 'success')
    return redirect(url_for('admin_pos'))


@app.route('/admin/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    if 'fuerza' not in productos.columns:
        productos['fuerza'] = ''
    if 'intendencia' not in productos.columns:
        productos['intendencia'] = ''
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

        productos.to_excel('bd/producto.xlsx', index=False)

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
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)

        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
        productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0).astype(int)

        productos = productos[productos['eliminado'] == False]
        lista_productos = productos.to_dict(orient='records')

        # Promocion vigente por producto para mostrar en catalogo
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
        productos = pd.read_excel('bd/producto.xlsx')
        productos = normalizar_imagenes_productos(productos)
        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
        productos = productos[productos['eliminado'] == False]
        productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0).astype(int)
        producto = productos[productos['id_producto'] == id_producto]
        
        if producto.empty:
            return "Producto no encontrado"
        
        producto_dict = producto.iloc[0].to_dict()
        
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

    productos = pd.read_excel('bd/producto.xlsx')
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos = productos[productos['eliminado'] == False].copy()
    productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0).astype(int)

    try:
        cantidad = int(request.form.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1

    if cantidad <= 0:
        flash('Cantidad invalida.', 'warning')
        return redirect(url_for('user_dashboard'))

    producto_df = productos[productos['id_producto'] == id_producto]
    if producto_df.empty:
        flash('El producto no existe o ya no esta disponible.', 'warning')
        return redirect(url_for('user_dashboard'))

    producto = producto_df.iloc[0]
    stock_actual = int(producto.get('stock', 0))
    if stock_actual <= 0:
        flash(f'El producto "{producto["nombre"]}" esta agotado.', 'warning')
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

        if os.path.exists('bd/pagos.xlsx'):
            pagos = pd.read_excel('bd/pagos.xlsx')
        else:
            pagos = pd.DataFrame(columns=['id_pago','id_pedido','monto','metodo_pago','fecha_pago','estado_pago'])

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

        if os.path.exists('bd/pedidos.xlsx'):
            pedidos = pd.read_excel('bd/pedidos.xlsx')
        else:
            pedidos = pd.DataFrame(columns=['id_pedido','id_usuario','fecha_pedido','estado'])
        
        if os.path.exists('bd/detalle_pedido.xlsx'):
            detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
        else:
            detalle_pedido = pd.DataFrame(columns=['id_detalle','id_pedido','id_producto','cantidad','subtotal'])

        if os.path.exists('bd/producto.xlsx'):
            productos = pd.read_excel('bd/producto.xlsx')
        else:
            flash('No existe la base de productos.', 'danger')
            return redirect(url_for('cart'))

        promos = cargar_promociones_df()
        if codigo_promo:
            promo_aplicada = buscar_promocion_por_codigo(promos, codigo_promo, datetime.now().date())
            if promo_aplicada is None:
                flash('El codigo promocional no es valido o no esta vigente.', 'warning')
                return redirect(url_for('cart'))
            descuento_promo = calcular_descuento_promocion(total, promo_aplicada)

        total_final = max(0.0, float(total) - float(descuento_promo))

        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
        productos['stock'] = pd.to_numeric(productos.get('stock', 0), errors='coerce').fillna(0).astype(int)

        for item in carrito:
            id_producto = int(item.get('id_producto', 0))
            cantidad = int(item.get('cantidad', 0))
            fila = productos[(productos['id_producto'] == id_producto) & (productos['eliminado'] == False)]
            if fila.empty:
                flash(f'El producto "{item.get("nombre", id_producto)}" ya no esta disponible.', 'warning')
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

        productos.to_excel('bd/producto.xlsx', index=False)

        # Crear nuevo pedido
        nuevo_id_pedido = len(pedidos) + 1 if not pedidos.empty else 1
        nuevo_pedido = {
            'id_pedido': nuevo_id_pedido,
            'id_usuario': session.get('id_usuario', session['usuario']),
            'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estado': 'pendiente'
        }
        pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
        pedidos.to_excel('bd/pedidos.xlsx', index=False)
        
        # Guardar detalles del pedido
        for item in carrito:
            nuevo_id_detalle = len(detalle_pedido) + 1 if not detalle_pedido.empty else 1
            nuevo_detalle = {
                'id_detalle': nuevo_id_detalle,
                'id_pedido': nuevo_id_pedido,
                'id_producto': item['id_producto'],
                'cantidad': item['cantidad'],
                'subtotal': item['subtotal']
            }
            detalle_pedido = pd.concat([detalle_pedido, pd.DataFrame([nuevo_detalle])], ignore_index=True)
        
        detalle_pedido.to_excel('bd/detalle_pedido.xlsx', index=False)

        # Registrar pago
        nuevo_id_pago = len(pagos) + 1 if not pagos.empty else 1
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
        pagos.to_excel('bd/pagos.xlsx', index=False)
        
        # Registrar acción
        if os.path.exists('bd/registros.xlsx'):
            registros = pd.read_excel('bd/registros.xlsx')
        else:
            registros = pd.DataFrame(columns=['id_registro', 'id_usuario', 'accion', 'fecha_accion'])
        
        nuevo_registro = {
            'id_registro': len(registros) + 1,
            'id_usuario': session['usuario'],
            'accion': f"Cre? pedido #{nuevo_id_pedido} con {len(carrito)} producto(s) por {formatear_cop(total_final)}",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)

        if agotados_en_compra:
            registrar_actividad("Stock agotado por pedido: " + ", ".join(agotados_en_compra))
        
        # Limpiar carrito
        session['carrito'] = []
        session.modified = True

        # Preparar datos para la página de confirmación
        metodo_pago_nombres = {
            'tarjeta': 'Tarjeta de Crédito/Débito',
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
    
    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
        id_usuario = session.get('id_usuario')
        pedidos_usuario = pedidos[pedidos['id_usuario'] == id_usuario]
    else:
        pedidos_usuario = pd.DataFrame(columns=['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'])
    
    # Obtener montos de pagos
    if os.path.exists('bd/pagos.xlsx'):
        pagos = pd.read_excel('bd/pagos.xlsx')
        pedidos_usuario = pd.merge(pedidos_usuario, pagos[['id_pedido', 'monto', 'metodo_pago']], 
                                   on='id_pedido', how='left')
    
    lista_pedidos = pedidos_usuario.to_dict(orient='records')
    return render_template('Usuarios/Carrito/user_orders.html', pedidos=lista_pedidos)

@app.route('/user/orders/details/<int:id_pedido>')
def user_order_details(id_pedido):
    if session.get('rol') != 'normal':
        return "Acceso denegado"
    
    # Verificar que el pedido pertenece al usuario
    pedidos = pd.read_excel('bd/pedidos.xlsx')
    pedido = pedidos[(pedidos['id_pedido'] == id_pedido) & 
                     (pedidos['id_usuario'] == session.get('id_usuario'))]
    
    if pedido.empty:
        return "Pedido no encontrado o no tienes permiso para verlo"
    
    detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
    detalles = detalle_pedido[detalle_pedido['id_pedido'] == id_pedido]
    
    productos = pd.read_excel('bd/producto.xlsx')
    detalles = pd.merge(detalles, productos[['id_producto', 'nombre', 'precio']], on='id_producto')
    
    return render_template('Usuarios/Informacion compras pedido/user_order_details.html',
                          pedido=pedido.iloc[0].to_dict(),
                          detalles=detalles.to_dict(orient='records'))

@app.route('/user/profile')
def user_profile():
    if session.get('rol') != 'normal':
        return "Acceso denegado"
    
    # Cargar información del usuario
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
    
    # Asegurar que existan las columnas de configuración con valores por defecto
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
    
    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
        id_usuario = session.get('id_usuario', usuario_email)
        pedidos_usuario = pedidos[pedidos['id_usuario'] == id_usuario]
        pedidos_total = len(pedidos_usuario)
        
        if os.path.exists('bd/pagos.xlsx') and not pedidos_usuario.empty:
            pagos = pd.read_excel('bd/pagos.xlsx')
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
    
    # Actualizar información
    idx = usuarios[usuarios['email'] == usuario_email].index
    if not idx.empty:
        usuarios.loc[idx, 'nombre'] = nombre
        usuarios.loc[idx, 'telefono'] = telefono
        usuarios.loc[idx, 'direccion'] = direccion
        
        guardar_usuarios_df(usuarios)
        registrar_actividad(f"Usuario {usuario_email} actualiz? su perfil")
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
    
    # Asegurar que existan las columnas de configuración
    columnas_config = ['notif_email', 'notif_pedidos', 'notif_promociones', 
                       'perfil_publico', 'mostrar_historial', 'idioma', 'moneda']
    for col in columnas_config:
        if col not in usuarios.columns:
            usuarios[col] = '' if col in ['idioma', 'moneda'] else False
    
    # Actualizar configuración
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
        registrar_actividad(f"Usuario {usuario_email} actualizó sus ajustes")
        flash('Ajustes guardados correctamente', 'success')
    else:
        flash('Error al guardar los ajustes', 'danger')
    
    return redirect(url_for('user_profile'))

@app.route('/user/send-verification-code', methods=['POST'])
def send_verification_code():
    """Envía un código de verificación al correo del usuario (funciona siempre)"""
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
            print("🔐 MODO DESARROLLO - CÓDIGO DE VERIFICACIÓN")
            print("="*60)
            print(f"📧 Usuario: {usuario_email}")
            print(f"🔢 Código: {codigo}")
            print(f"⏰ Válido hasta: {expiry.strftime('%H:%M:%S')}")
            print("="*60 + "\n")
            
            registrar_actividad(f"Código de autenticación generado para {usuario_email} (modo desarrollo)")
            return jsonify({
                'success': True, 
                'message': f'✅ Código generado: {codigo} (revisa la consola del servidor)'
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
            print("\n⚠️ ERROR AL ENVIAR EMAIL - MOSTRANDO CÓDIGO EN CONSOLA:")
            print(f"Código para {usuario_email}: {codigo}\n")
            return jsonify({
                'success': True, 
                'message': f'⚠️ Email no configurado. Tu código es: {codigo}'
            })
            
    except Exception as e:
        print(f"Error al enviar código: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/user/verify-email', methods=['POST'])
def verify_email():
    """Verifica el código ingresado por el usuario (funciona siempre)"""
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

@app.route('/producto/<int:id_producto>')
def producto_detalle(id_producto):
    productos = pd.read_excel('bd/producto.xlsx') if os.path.exists('bd/producto.xlsx') else pd.DataFrame()
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos = productos[productos['eliminado'] == False]

    producto = productos[productos['id_producto'] == id_producto]
    if producto.empty:
        return "Producto no encontrado"

    carrito = session.get('carrito', [])
    cart_count = len(carrito)
    return render_template('Usuarios/Detalle pedido/product_detail.html', producto=producto.iloc[0].to_dict(), cart_count=cart_count)

@app.route('/admin/promo', methods=['GET','POST'])
def admin_promo():
    # pagina de gestion de promociones para administradores
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
        if os.path.exists('bd/producto.xlsx'):
            productos_ref = pd.read_excel('bd/producto.xlsx')
            if 'eliminado' not in productos_ref.columns:
                productos_ref['eliminado'] = False
            productos_ref['eliminado'] = productos_ref['eliminado'].fillna(False).astype(bool)
            id_producto_num = int(id_producto)
            existe_producto = not productos_ref[
                (pd.to_numeric(productos_ref.get('id_producto', 0), errors='coerce') == id_producto_num)
                & (productos_ref['eliminado'] == False)
            ].empty
            if not existe_producto:
                flash('El producto seleccionado no existe o esta inactivo.', 'warning')
                return redirect(url_for('admin_promo'))

        promos = cargar_promociones_df()
        if codigo:
            existe_codigo = promos[promos['codigo'].astype(str).str.upper() == codigo]
            if not existe_codigo.empty:
                flash('El codigo promocional ya existe. Usa otro.', 'warning')
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
    productos = pd.read_excel('bd/producto.xlsx') if os.path.exists('bd/producto.xlsx') else pd.DataFrame()
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos = productos[productos['eliminado'] == False].copy()
    productos = normalizar_imagenes_productos(productos)
    productos['id_producto'] = pd.to_numeric(productos.get('id_producto', 0), errors='coerce').fillna(0).astype(int)
    productos['precio'] = pd.to_numeric(productos.get('precio', 0), errors='coerce').fillna(0)
    lista_productos = productos.to_dict(orient='records')
    pagos = pd.read_excel('bd/pagos.xlsx') if os.path.exists('bd/pagos.xlsx') else pd.DataFrame()
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
        productos=lista_productos
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
    # pagina publica que muestra promociones activas y vigentes
    promos = cargar_promociones_df()
    hoy = datetime.now().date()
    productos = pd.read_excel('bd/producto.xlsx') if os.path.exists('bd/producto.xlsx') else pd.DataFrame()
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)
    productos = productos[productos['eliminado'] == False].copy()
    productos = normalizar_imagenes_productos(productos)
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
    if os.path.exists('bd/detalle_pedido.xlsx'):
        detalle = pd.read_excel('bd/detalle_pedido.xlsx')
    else:
        detalle = pd.DataFrame(columns=['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal'])

    if os.path.exists('bd/producto.xlsx'):
        productos = pd.read_excel('bd/producto.xlsx')
    else:
        productos = pd.DataFrame(columns=['id_producto', 'nombre', 'precio'])

    if os.path.exists('bd/pedidos.xlsx'):
        pedidos = pd.read_excel('bd/pedidos.xlsx')
    else:
        pedidos = pd.DataFrame(columns=['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'])

    if os.path.exists('bd/pagos.xlsx'):
        pagos = pd.read_excel('bd/pagos.xlsx')
    else:
        pagos = pd.DataFrame(columns=['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago'])

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
