"""Constantes compartidas del proyecto."""

CURRENCY_CODE = "COP"
CURRENCY_NAME = "Peso colombiano"

USUARIO_COLUMNS = [
    'id_usuario',
    'nombre',
    'email',
    'password_hash',
    'rol',
    'estado',
    'fecha_registro',
    'telefono',
    'direccion',
    'email_verified',
    'verification_code',
    'verification_code_expiry',
    'reset_token',
    'reset_token_expiry',
    'password_change_code',
    'password_change_code_expiry',
]
REGISTRO_COLUMNS = ['id_registro', 'id_usuario', 'accion', 'fecha_accion']
PRODUCTO_COLUMNS = [
    'id_producto', 'nombre', 'descripcion', 'precio', 'stock',
    'id_categoria', 'fuerza', 'intendencia', 'imagen_url',
    'eliminado', 'destacado_dashboard'
]
PEDIDO_COLUMNS = ['id_pedido', 'id_usuario', 'fecha_pedido', 'estado', 'cliente_telefono', 'cliente_direccion']
DETALLE_PEDIDO_COLUMNS = ['id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'subtotal', 'talla']
PAGO_COLUMNS = ['id_pago', 'id_pedido', 'monto', 'metodo_pago', 'fecha_pago', 'estado_pago', 'comprobante_url', 'id_promo', 'codigo_promo', 'tipo_descuento', 'valor_descuento', 'monto_descuento']
ORDEN_PERSONALIZADA_COLUMNS = [
    'id_orden_personalizada', 'usuario_email', 'cliente_nombre', 'cliente_correo',
    'cliente_telefono', 'cliente_direccion', 'rango', 'fecha_contingencia',
    'identidad', 'producto', 'tecnica', 'color', 'estampado', 'talla',
    'modelo_rh', 'modelo_presilla', 'cantidad', 'imagen_url', 'precio',
    'estado', 'datos_json', 'fecha_creacion'
]
ORDEN_PERSONALIZADA_PRECIO_COLUMNS = ['producto', 'nombre', 'precio']
ORDEN_PERSONALIZADA_PRECIOS_DEFAULT = [
    {'producto': 'guerrera', 'nombre': 'Guerrera', 'precio': 160000},
    {'producto': 'buso_tactico', 'nombre': 'Buso tactico', 'precio': 95000},
    {'producto': 'buso', 'nombre': 'Buso', 'precio': 78000},
    {'producto': 'gorra', 'nombre': 'Gorra', 'precio': 35000},
    {'producto': 'pa\u00f1oleta', 'nombre': 'Pa\u00f1oleta', 'precio': 28000},
    {'producto': 'buso-manga-larga', 'nombre': 'Buso manga larga', 'precio': 85000},
    {'producto': 'presillas', 'nombre': 'Presillas', 'precio': 15000},
    {'producto': 'rh', 'nombre': 'RH', 'precio': 12000},
    {'producto': 'gafete del nombre o apellido', 'nombre': 'Gafete de nombre o apellido', 'precio': 12000},
]
ORDEN_PERSONALIZADA_PRODUCTO_ALIAS = {
    'buso tactico': 'buso_tactico',
    'buso-tactico': 'buso_tactico',
    'buso manga larga': 'buso-manga-larga',
    'buso_manga_larga': 'buso-manga-larga',
    'pa\u00f1oleta': 'pa\u00f1oleta',
    'paoleta': 'pa\u00f1oleta',
    'panoleta': 'pa\u00f1oleta',
}
PEDIDO_STATUS_FLOW = [
    ('confirmado', 'Confirmado'),
    ('empaquetado', 'Empaquetado'),
    ('enviado', 'Enviado'),
    ('entregado', 'Entregado'),
]
PEDIDO_STATUS_EXTRA = {
    'pago_en_revision': 'Pago en revisión',
    'cancelado': 'Cancelado',
    'pendiente_revision': 'Pendiente de revisión',
    'completado': 'Completado',
}
ORDEN_PERSONALIZADA_ESTADOS_PAGO = {
    'pendiente_pago': 'Pendiente de pago',
    'pendiente': 'Pendiente',
    'en_revision': 'En revisión',
    'cotizada': 'Cotizada',
    'completada': 'Completada',
    'cancelada': 'Cancelada',
}
PEDIDO_STATUS_ALIAS = {
    'pendiente': 'confirmado',
    'en_preparacion': 'confirmado',
    'pendiente_revision': 'confirmado',
    'completado': 'entregado',
}
PEDIDO_STATUS_LABELS = {
    **{clave: etiqueta for clave, etiqueta in PEDIDO_STATUS_FLOW},
    **PEDIDO_STATUS_EXTRA,
}
PAGO_STATUS_LABELS = {
    'pendiente_comprobante': 'Pendiente de comprobante',
    'en_revision': 'En revisión',
    'aprobado': 'Aprobado',
    'rechazado': 'Rechazado',
}

PROMO_COLUMNS = [
    'id_promo', 'nombre', 'descripcion',
    'tipo_descuento', 'valor_descuento',
    'id_producto',
    'codigo',
    'fecha_inicio', 'fecha_fin',
    'activo'
]

FUERZAS_OPCIONES = ["Policia", "Ejercito", "Armada", "Gaula", "Variado", "Accesorios"]
INTENDENCIAS_OPCIONES = [
    "Busos", "Camibusos", "Gorras", "Pa\u00f1oletas", "Sudaderas",
    "Pantalonetas", "Colchas", "Tendidos", "Chuspas para ropa sucia",
    "Fundas para almohadas", "Camuflados", "Accesorios", "Presillas"
]
TALLAS_OPCIONES = ["XS", "S", "M", "L", "XL", "XXL"]
INTENDENCIAS_SIN_TALLA = {
    "pa\u00f1oleta", "pa\u00f1oletas",
    "panoleta", "panoletas",
    "gorra", "gorras",
    "colcha", "colchas",
    "tendido", "tendidos",
    "chuspa para ropa sucia", "chuspas para ropa sucia",
    "funda para almohadas", "fundas para almohadas",
    "accesorio", "accesorios",
    "presilla", "presillas",
}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_SIZE_BYTES = 3 * 1024 * 1024
MAX_IMAGES_PER_PRODUCT = 5
REGISTER_CODE_EXP_MINUTES = 7
PASSWORD_RESET_EXP_MINUTES = 30
PASSWORD_CHANGE_CODE_EXP_MINUTES = 7
