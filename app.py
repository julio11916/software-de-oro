import os
import pandas as pd
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash, send_file
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave"  # Necesario para manejar sesiones

USUARIO_COLUMNS = ['id_usuario', 'nombre', 'email', 'password_hash', 'rol', 'fecha_registro']
REGISTRO_COLUMNS = ['id_registro', 'id_usuario', 'accion', 'fecha_accion']

# Si no existe detalle_pedido.xlsx, crear uno vacío
if not os.path.exists('bd/detalle_pedido.xlsx'):
    detalle_pedido = pd.DataFrame(columns=['id_detalle','id_pedido','id_producto','cantidad','subtotal'])
    detalle_pedido.to_excel('bd/detalle_pedido.xlsx', index=False)


def cargar_usuarios_df():
    if os.path.exists('bd/usuarios.xlsx'):
        usuarios = pd.read_excel('bd/usuarios.xlsx')
    else:
        usuarios = pd.DataFrame(columns=USUARIO_COLUMNS)

    for col in USUARIO_COLUMNS:
        if col not in usuarios.columns:
            usuarios[col] = ''
    return usuarios[USUARIO_COLUMNS]


def guardar_usuarios_df(usuarios):
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


@app.context_processor
def inyectar_nombre_admin():
    if session.get('rol') == 'admin':
        return {'admin_nombre': obtener_nombre_sesion()}
    return {'admin_nombre': ''}

@app.route('/')
def home():
    productos = pd.read_excel('bd/producto.xlsx')
    lista_productos = productos.to_dict(orient='records')
    return render_template('Usuarios/Autenticacion/login.html', productos=lista_productos)

@app.route('/login', methods=['POST'])
def login():
    usuarios = pd.read_excel('bd/usuarios.xlsx')  # leer cada vez
    email = request.form['email']
    password = request.form['password']

    usuario = usuarios[(usuarios['email'] == email) & (usuarios['password_hash'] == password)]

    if not usuario.empty:
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
            usuarios = pd.DataFrame(columns=['id_usuario', 'nombre', 'email', 'password_hash', 'rol', 'fecha_registro'])

        if email in usuarios['email'].values:
            return "Este correo ya está registrado."

        nuevo_id = len(usuarios) + 1
        nuevo_usuario = {
            'id_usuario': nuevo_id,
            'nombre': nombre,
            'email': email,
            'password_hash': password,
            'rol': rol,
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

        # Asegurar que la columna 'eliminado' existe y es booleana
        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

        productos = productos[productos['eliminado'] == False]
        lista_productos = productos.to_dict(orient='records')
        admin_nombre = obtener_nombre_sesion()
        # plantilla actual en el proyecto
        return render_template(
            'Administrador/admin_dashboard_principal.html',
            productos=lista_productos,
            admin_nombre=admin_nombre
        )
    return "Acceso denegado"


@app.route('/admin/productos')
def admin_productos():
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    if 'eliminado' not in productos.columns:
        productos['eliminado'] = False
    productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

    productos = productos[productos['eliminado'] == False]
    lista_productos = productos.to_dict(orient='records')
    return render_template('Administrador/Gestion productos/admin_prod_dashboard.html', productos=lista_productos)


@app.route('/admin/agregar_producto', methods=['POST'])
def agregar_producto():
    if session.get('rol') == 'admin':
        productos = pd.read_excel('bd/producto.xlsx')

        nuevo_id = len(productos) + 1
        nuevo_producto = {
            'id_producto': nuevo_id,
            'nombre': request.form['nombre'],
            'descripcion': request.form['descripcion'],
            'precio': float(request.form['precio']),
            'stock': int(request.form['stock']),
            'id_categoria': 1  # Puedes ajustar esto si manejas categorías
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
            'accion': f"Agregó producto: {request.form['nombre']}",
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


#admin dashboard
from flask import flash

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

        # Validar tamaño (máx. 2MB)
        imagen.seek(0, os.SEEK_END)
        tamaño = imagen.tell()
        imagen.seek(0)
        if tamaño > 2 * 1024 * 1024:
            flash("La imagen excede el tamaño máximo permitido (2MB).")
            return redirect(url_for('admin_productos'))

        # Guardar imagen
        carpeta_destino = os.path.join('static', 'img')
        os.makedirs(carpeta_destino, exist_ok=True)
        ruta = os.path.join(carpeta_destino, f'producto_{id_producto}.jpg')
        imagen.save(ruta)

        # Registrar ruta en el Excel
        productos = pd.read_excel('bd/producto.xlsx')
        idx = productos[productos['id_producto'] == id_producto].index
        if not idx.empty:
            productos.at[idx[0], 'imagen_url'] = f'img/producto_{id_producto}.jpg'
            productos.to_excel('bd/producto.xlsx', index=False)

        flash("Imagen subida correctamente.")

    else:
        flash("No se seleccionó ninguna imagen.")

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
            'accion': f"Eliminó producto: {nombre} (ID {id_producto})",
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
            'accion': f"Eliminó definitivamente el producto: {nombre} (ID {id_producto})",
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
            'accion': f"Restauró producto: {nombre} (ID {id_producto})",
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

    lista_usuarios = filtrados.fillna('').to_dict(orient='records')
    for usuario in lista_usuarios:
        if usuario.get('id_usuario') != '':
            usuario['id_usuario'] = int(usuario['id_usuario'])

    filtros = {'buscar': buscar, 'rol': rol, 'orden': orden}
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

    if rol not in ['admin', 'normal']:
        rol = 'normal'

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
        if password:
            usuarios.at[idx[0], 'password_hash'] = password

        guardar_usuarios_df(usuarios[USUARIO_COLUMNS])
        registrar_actividad(f"Actualizo usuario {email} (ID {edit_id})")
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
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        guardar_usuarios_df(usuarios[USUARIO_COLUMNS])
        registrar_actividad(f"Creo usuario {email} (ID {nuevo_id})")
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
    return render_template('Administrador/Sistema POS/admin_pos_dashboard.html')


@app.route('/admin/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    if session.get('rol') != 'admin':
        return "Acceso denegado"

    productos = pd.read_excel('bd/producto.xlsx')
    producto = productos[productos['id_producto'] == id_producto]

    if producto.empty:
        return "Producto no encontrado."

    if request.method == 'POST':
        idx = producto.index[0]
        productos.at[idx, 'nombre'] = request.form['nombre']
        productos.at[idx, 'descripcion'] = request.form['descripcion']
        productos.at[idx, 'precio'] = float(request.form['precio'])
        productos.at[idx, 'stock'] = int(request.form['stock'])
        productos.to_excel('bd/producto.xlsx', index=False)
        return redirect(url_for('admin_productos'))

    # Render formulario de edición (plantilla propia en Gestion productos)
    return render_template('Administrador/Gestion productos/editar_producto.html', producto=producto.iloc[0])

    

@app.route('/user')
def user_dashboard():
    if session.get('rol') == 'normal':
        productos = pd.read_excel('bd/producto.xlsx')

        if 'eliminado' not in productos.columns:
            productos['eliminado'] = False
        productos['eliminado'] = productos['eliminado'].fillna(False).astype(bool)

        productos = productos[productos['eliminado'] == False]
        lista_productos = productos.to_dict(orient='records')
        
        # Obtener el contador del carrito
        carrito = session.get('carrito', [])
        cart_count = len(carrito)
        
        return render_template('Usuarios/user_dashboard.html', productos=lista_productos, cart_count=cart_count)
    return "Acceso denegado"


@app.route('/product/<int:id_producto>')
def product_detail(id_producto):
    if session.get('rol') == 'normal':
        productos = pd.read_excel('bd/producto.xlsx')
        producto = productos[productos['id_producto'] == id_producto]
        
        if producto.empty:
            return "Producto no encontrado"
        
        producto_dict = producto.iloc[0].to_dict()
        
        # Obtener el contador del carrito
        carrito = session.get('carrito', [])
        cart_count = len(carrito)
        
        return render_template('Usuarios/product_detail.html', producto=producto_dict, cart_count=cart_count)
    return "Acceso denegado"


@app.route('/add_to_cart/<int:id_producto>', methods=['POST'])
def add_to_cart(id_producto):
    if 'carrito' not in session:
        session['carrito'] = []
    
    productos = pd.read_excel('bd/producto.xlsx')
    cantidad = int(request.form['cantidad'])
    producto = productos[productos['id_producto'] == id_producto].iloc[0]
    
    subtotal = producto['precio'] * cantidad
    
    # Agregar al carrito en sesión
    item_carrito = {
        'id_producto': int(id_producto),
        'nombre': producto['nombre'],
        'cantidad': cantidad,
        'precio': float(producto['precio']),
        'subtotal': float(subtotal)
    }
    
    session['carrito'].append(item_carrito)
    session.modified = True
    
    # Mensaje de éxito
    flash(f'¡{producto["nombre"]} agregado al carrito exitosamente!', 'success')
    
    # Verificar si viene de la página de detalles
    referer = request.referrer
    if referer and 'product' in referer:
        return redirect(url_for('product_detail', id_producto=id_producto))
    
    return redirect(url_for('user_dashboard'))

@app.route('/cart')
def cart():
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
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

@app.route('/pay', methods=['POST'])
def pay():
    if session.get('rol') == 'normal':
        carrito = session.get('carrito', [])
        
        if not carrito:
            return "No hay productos en el carrito."
        
        total = sum(item['subtotal'] for item in carrito)

        if os.path.exists('bd/pagos.xlsx'):
            pagos = pd.read_excel('bd/pagos.xlsx')
        else:
            pagos = pd.DataFrame(columns=['id_pago','id_pedido','monto','metodo_pago','fecha_pago','estado_pago'])

        if os.path.exists('bd/pedidos.xlsx'):
            pedidos = pd.read_excel('bd/pedidos.xlsx')
        else:
            pedidos = pd.DataFrame(columns=['id_pedido','id_usuario','fecha_pedido','estado'])
        
        if os.path.exists('bd/detalle_pedido.xlsx'):
            detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
        else:
            detalle_pedido = pd.DataFrame(columns=['id_detalle','id_pedido','id_producto','cantidad','subtotal'])

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
            'monto': total,
            'metodo_pago': request.form['metodo_pago'],
            'fecha_pago': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estado_pago': 'aprobado'
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
            'accion': f"Creó pedido #{nuevo_id_pedido} con {len(carrito)} producto(s) por ${total}",
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        registros.to_excel('bd/registros.xlsx', index=False)
        
        # Limpiar carrito
        session['carrito'] = []
        session.modified = True

        return f"Pedido #{nuevo_id_pedido} creado y pago registrado con éxito. Total: ${total}"
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
    
    return render_template('Usuarios/user_order_details.html',
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
    
    return render_template('Usuarios/user_profile.html', 
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
        registrar_actividad(f"Usuario {usuario_email} actualizó su perfil")
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

@app.route('/producto/<int:id_producto>')
def producto_detalle(id_producto):
    productos = pd.read_excel('bd/producto.xlsx') if os.path.exists('bd/producto.xlsx') else pd.DataFrame()
    producto = productos[productos['id_producto'] == id_producto]
    if producto.empty:
        return "Producto no encontrado"
    return render_template('Usuarios/product_detail.html', producto=producto.iloc[0].to_dict())

@app.route('/admin/charts')
def admin_charts():
    if session.get('rol') == 'admin':
        detalle = pd.read_excel('bd/detalle_pedido.xlsx')
        productos = pd.read_excel('bd/producto.xlsx')
        pedidos = pd.read_excel('bd/pedidos.xlsx')

        ventas_por_producto = detalle.groupby('id_producto')['cantidad'].sum().reset_index()
        ventas_por_producto = pd.merge(ventas_por_producto, productos[['id_producto','nombre']], on='id_producto')

        pedidos['fecha_pedido'] = pd.to_datetime(pedidos['fecha_pedido'])
        pedidos['mes'] = pedidos['fecha_pedido'].dt.to_period('M').astype(str)
        ventas_por_mes = detalle.groupby('id_pedido')['subtotal'].sum().reset_index()
        ventas_por_mes = pd.merge(ventas_por_mes, pedidos[['id_pedido','mes']], on='id_pedido')
        ventas_por_mes = ventas_por_mes.groupby('mes')['subtotal'].sum().reset_index()

        return render_template('Administrador/Informes/admin_charts_dashboard.html',
                       ventas_producto=ventas_por_producto.to_dict(orient='records'),
                       ventas_mes=ventas_por_mes.to_dict(orient='records'))
    return "Acceso denegado"
#orden personalizada
@app.route('/orden-personalizada')
def orden_personalizada():
    return render_template('Usuarios/orden_personalizada/orden.html')

if __name__ == '__main__':
    app.run(debug=True)



###hhdyjdjtrdytdfy###
