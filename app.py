import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, Response
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave"  # Necesario para manejar sesiones

# Si no existe detalle_pedido.xlsx, crear uno vacío
if not os.path.exists('bd/detalle_pedido.xlsx'):
    detalle_pedido = pd.DataFrame(columns=['id_detalle','id_pedido','id_producto','cantidad','subtotal'])
    detalle_pedido.to_excel('bd/detalle_pedido.xlsx', index=False)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuarios = pd.read_excel('bd/usuarios.xlsx')  # leer cada vez
    email = request.form['email']
    password = request.form['password']

    usuario = usuarios[(usuarios['email'] == email) & (usuarios['password_hash'] == password)]

    if not usuario.empty:
        rol = usuario.iloc[0]['rol']
        session['usuario'] = email
        session['rol'] = rol

        if rol == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    else:
        return "Credenciales inválidas. Intenta de nuevo."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if session.get('rol') == 'admin':
        return render_template('admin_dashboard.html')
    return "Acceso denegado"

@app.route('/admin/orders')
def admin_orders():
    if session.get('rol') == 'admin':
        pedidos = pd.read_excel('bd/pedidos.xlsx')
        pagos = pd.read_excel('bd/pagos.xlsx')

        lista_pedidos = pedidos.to_dict(orient='records')
        lista_pagos = pagos.to_dict(orient='records')

        return render_template('admin_orders.html',
                               pedidos=lista_pedidos,
                               pagos=lista_pagos)
    return "Acceso denegado"

@app.route('/user')
def user_dashboard():
    if session.get('rol') == 'normal':
        productos = pd.read_excel('bd/producto.xlsx')
        lista_productos = productos.to_dict(orient='records')
        return render_template('user_dashboard.html', productos=lista_productos)
    return "Acceso denegado"

@app.route('/add_to_cart/<int:id_producto>', methods=['POST'])
def add_to_cart(id_producto):
    productos = pd.read_excel('bd/producto.xlsx')
    detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')

    cantidad = int(request.form['cantidad'])
    producto = productos[productos['id_producto'] == id_producto].iloc[0]

    subtotal = producto['precio'] * cantidad

    nuevo_id = len(detalle_pedido) + 1
    nuevo_pedido = {
        'id_detalle': nuevo_id,
        'id_pedido': 1,  # por ahora pedido fijo
        'id_producto': id_producto,
        'cantidad': cantidad,
        'subtotal': subtotal
    }

    detalle_pedido = pd.concat([detalle_pedido, pd.DataFrame([nuevo_pedido])], ignore_index=True)
    detalle_pedido.to_excel('bd/detalle_pedido.xlsx', index=False)

    return redirect(url_for('user_dashboard'))

@app.route('/cart')
def cart():
    if session.get('rol') == 'normal':
        detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
        carrito = detalle_pedido.to_dict(orient='records')
        total = detalle_pedido['subtotal'].sum() if not detalle_pedido.empty else 0
        return render_template('cart.html', carrito=carrito, total=total)
    return "Acceso denegado"

@app.route('/pay', methods=['POST'])
def pay():
    if session.get('rol') == 'normal':
        detalle_pedido = pd.read_excel('bd/detalle_pedido.xlsx')
        total = detalle_pedido['subtotal'].sum() if not detalle_pedido.empty else 0

        if total == 0:
            return "No hay productos en el carrito."

        if os.path.exists('bd/pagos.xlsx'):
            pagos = pd.read_excel('bd/pagos.xlsx')
        else:
            pagos = pd.DataFrame(columns=['id_pago','id_pedido','monto','metodo_pago','fecha_pago','estado_pago'])

        if os.path.exists('bd/pedidos.xlsx'):
            pedidos = pd.read_excel('bd/pedidos.xlsx')
        else:
            pedidos = pd.DataFrame(columns=['id_pedido','id_usuario','fecha_pedido','estado'])

        nuevo_id_pedido = len(pedidos) + 1
        nuevo_pedido = {
            'id_pedido': nuevo_id_pedido,
            'id_usuario': session['usuario'],
            'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estado': 'pagado'
        }
        pedidos = pd.concat([pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
        pedidos.to_excel('bd/pedidos.xlsx', index=False)

        nuevo_id_pago = len(pagos) + 1
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

        return f"Pedido #{nuevo_id_pedido} creado y pago registrado con éxito. Total: {total}"
    return "Acceso denegado"

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

        return render_template('admin_charts.html',
                               ventas_producto=ventas_por_producto.to_dict(orient='records'),
                               ventas_mes=ventas_por_mes.to_dict(orient='records'))
    return "Acceso denegado"

if __name__ == '__main__':
    app.run(debug=True)