import pandas as pd
import os

os.makedirs('bd', exist_ok=True)

tablas = {
    'usuarios.xlsx': ['id_usuario', 'nombre', 'email', 'password_hash', 'rol', 'fecha_registro'],
    'registros.xlsx': ['id_registro', 'id_usuario', 'accion', 'fecha_accion'],
    'categoria_producto.xlsx': ['id_categoria', 'nombre_categoria', 'descripcion'],
    'producto.xlsx': ['id_producto', 'nombre', 'descripcion', 'precio', 'stock', 'id_categoria'],
    'pedidos.xlsx': ['id_pedido', 'id_usuario', 'fecha_pedido', 'estado'],
    'detalle_pedido.xlsx': ['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal'],
    'pagos.xlsx': ['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago']
}

for archivo, columnas in tablas.items():
    df = pd.DataFrame(columns=columnas)
    df.to_excel(f'bd/{archivo}', index=False)

print("Archivos Excel creados en la carpeta bd/")