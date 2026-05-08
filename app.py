import os
import sys
from functools import partial

from flask import Flask, render_template, request, session
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash

from core.config import get_config
from core.db_utils import engine, next_id  # Inicializa DB y proxys al importar
from core.extensions import init_extensions
from services.email_service import (
    enviar_actualizacion_pedido,
    enviar_codigo_verificacion,
    enviar_notificacion_pago_personalizado_admin,
    enviar_notificacion_transferencia_admin,
    enviar_recuperacion_password,
    generar_codigo_verificacion,
)
from models.constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    CURRENCY_CODE,
    CURRENCY_NAME,
    DETALLE_PEDIDO_COLUMNS,
    FUERZAS_OPCIONES,
    INTENDENCIAS_OPCIONES,
    INTENDENCIAS_SIN_TALLA,
    MAX_IMAGES_PER_PRODUCT,
    MAX_IMAGE_SIZE_BYTES,
    ORDEN_PERSONALIZADA_COLUMNS,
    ORDEN_PERSONALIZADA_ESTADOS_PAGO,
    ORDEN_PERSONALIZADA_PRECIO_COLUMNS,
    ORDEN_PERSONALIZADA_PRECIOS_DEFAULT,
    ORDEN_PERSONALIZADA_PRODUCTO_ALIAS,
    PAGO_COLUMNS,
    PAGO_STATUS_LABELS,
    PASSWORD_CHANGE_CODE_EXP_MINUTES,
    PASSWORD_RESET_EXP_MINUTES,
    PEDIDO_COLUMNS,
    PEDIDO_STATUS_ALIAS,
    PEDIDO_STATUS_FLOW,
    PEDIDO_STATUS_LABELS,
    PRODUCTO_COLUMNS,
    PROMO_COLUMNS,
    REGISTER_CODE_EXP_MINUTES,
    REGISTRO_COLUMNS,
    TALLAS_OPCIONES,
    USUARIO_COLUMNS,
)
from routes.admin import register_admin_legacy_routes
from routes.auth import register_auth_legacy_routes
from routes.checkout import register_checkout_legacy_routes
from routes.custom_orders import register_custom_orders_legacy_routes
from routes.user import register_user_legacy_routes
from services import auth_service as app_auth_service
from services import dashboard_service as app_dashboard_service
from services import image_service as app_image_service
from services import mail_service as app_mail_service
from services import order_service
from services import promo_service as app_promo_service
from services import receipt_service as app_receipt_service
from services import storage_service as app_storage_service
from services import user_orders_service
from services.auth_image_facade import build_auth_image_legacy_bindings
from services.cart_facade import build_cart_legacy_bindings
from services.receipt_facade import build_receipt_legacy_bindings
from services.runtime_facade import build_runtime_bindings
from services.workflow_facade import build_workflow_legacy_bindings
from services.stripe_service import (
    crear_checkout_sesion_tarjeta,
    obtener_checkout_sesion,
    stripe_estado_configuracion,
)

app = Flask(__name__)
app.config.from_object(get_config())
app.jinja_env.auto_reload = True
app.secret_key = str(app.config.get("SECRET_KEY", "")).strip()
if not app.secret_key:
    app.secret_key = os.urandom(32)
    print(
        "ADVERTENCIA: SECRET_KEY no est\u00e1 configurada en el entorno. "
        "Usando una clave temporal para esta ejecuci\u00f3n."
    )

init_extensions(app)

PENDING_REGISTRATIONS = {}

# DB init y proxys se hacen al importar db_utils

normalizar_intendencia = app_storage_service.normalizar_intendencia
producto_requiere_talla = app_storage_service.producto_requiere_talla
cargar_usuarios_df = app_storage_service.cargar_usuarios_df
guardar_usuarios_df = app_storage_service.guardar_usuarios_df
cargar_registros_df = app_storage_service.cargar_registros_df
guardar_registros_df = app_storage_service.guardar_registros_df
cargar_promociones_df = app_storage_service.cargar_promociones_df
guardar_promociones_df = app_storage_service.guardar_promociones_df
normalizar_producto_personalizado = app_storage_service.normalizar_producto_personalizado
producto_personalizado_canonico = app_storage_service.producto_personalizado_canonico
asegurar_tablas_orden_personalizada = app_storage_service.asegurar_tablas_orden_personalizada
cargar_precios_orden_personalizada_df = app_storage_service.cargar_precios_orden_personalizada_df
precios_orden_personalizada_mapa = app_storage_service.precios_orden_personalizada_mapa
cargar_ordenes_personalizadas_df = app_storage_service.cargar_ordenes_personalizadas_df
actualizar_precio_orden_personalizada = app_storage_service.actualizar_precio_orden_personalizada
actualizar_estado_ordenes_personalizadas_carrito = app_storage_service.actualizar_estado_ordenes_personalizadas_carrito
cargar_productos_df = app_storage_service.cargar_productos_df
guardar_productos_df = app_storage_service.guardar_productos_df
cargar_productos_activos_df = app_storage_service.cargar_productos_activos_df
cargar_pedidos_df = app_storage_service.cargar_pedidos_df
guardar_pedidos_df = app_storage_service.guardar_pedidos_df
cargar_detalle_pedido_df = app_storage_service.cargar_detalle_pedido_df
guardar_detalle_pedido_df = app_storage_service.guardar_detalle_pedido_df
cargar_pagos_df = app_storage_service.cargar_pagos_df
guardar_pagos_df = app_storage_service.guardar_pagos_df
cargar_productos_por_fuerza = app_storage_service.cargar_productos_por_fuerza
cargar_productos_por_intendencia = app_storage_service.cargar_productos_por_intendencia

globals().update(
    build_auth_image_legacy_bindings(
        app_auth_service=app_auth_service,
        app_image_service=app_image_service,
        pending_registrations=PENDING_REGISTRATIONS,
        register_code_exp_minutes=REGISTER_CODE_EXP_MINUTES,
        allowed_image_extensions=ALLOWED_IMAGE_EXTENSIONS,
        max_image_size_bytes=MAX_IMAGE_SIZE_BYTES,
        generate_password_hash_fn=generate_password_hash,
        check_password_hash_fn=check_password_hash,
        enviar_codigo_verificacion_fn=enviar_codigo_verificacion,
    )
)

parsear_fecha_promocion = app_promo_service.parsear_fecha_promocion
estado_vigencia_promocion = app_promo_service.estado_vigencia_promocion
promocion_esta_aplicable = app_promo_service.promocion_esta_aplicable
calcular_descuento_promocion = app_promo_service.calcular_descuento_promocion
obtener_mejor_promocion_por_producto = app_promo_service.obtener_mejor_promocion_por_producto
buscar_promocion_por_codigo = app_promo_service.buscar_promocion_por_codigo

globals().update(
    build_runtime_bindings(
        session_obj=session,
        cargar_registros_df_fn=cargar_registros_df,
        guardar_registros_df_fn=guardar_registros_df,
        cargar_usuarios_df_fn=cargar_usuarios_df,
        currency_code=CURRENCY_CODE,
        currency_name=CURRENCY_NAME,
    )
)

globals().update(
    build_receipt_legacy_bindings(
        app_receipt_service=app_receipt_service,
        session_obj=session,
        cargar_detalle_pedido_df_fn=cargar_detalle_pedido_df,
        cargar_productos_df_fn=cargar_productos_df,
        cargar_pagos_df_fn=cargar_pagos_df,
        cargar_pedidos_df_fn=cargar_pedidos_df,
        tallas_opciones=TALLAS_OPCIONES,
        formatear_cop_fn=formatear_cop,
        app_root_path=app.root_path,
        render_template_fn=render_template,
        edge_path_env=os.environ.get('EDGE_PATH', ''),
    )
)

globals().update(
    build_cart_legacy_bindings(
        order_service=order_service,
        session_obj=session,
        cargar_productos_df_fn=cargar_productos_df,
        obtener_galeria_producto_fn=obtener_galeria_producto,
        normalizar_imagen_url_fn=normalizar_imagen_url,
        normalizar_email_fn=normalizar_email,
        engine=engine,
        sa_module=sa,
    )
)

app.add_template_filter(formatear_cop, 'cop')
cop_filter = formatear_cop

app.context_processor(inyectar_nombre_admin_context)
inyectar_nombre_admin = inyectar_nombre_admin_context

register_auth_legacy_routes(app, legacy=sys.modules[__name__])
register_user_legacy_routes(app, legacy=sys.modules[__name__])
register_admin_legacy_routes(app, legacy=sys.modules[__name__])
register_checkout_legacy_routes(app, legacy=sys.modules[__name__])
register_custom_orders_legacy_routes(app, legacy=sys.modules[__name__])

globals().update(
    build_workflow_legacy_bindings(
        app_dashboard_service=app_dashboard_service,
        app_mail_service=app_mail_service,
        order_service=order_service,
        request_obj=request,
        session_obj=session,
        app_obj=app,
        stripe_estado_configuracion=stripe_estado_configuracion,
        crear_checkout_sesion_tarjeta=crear_checkout_sesion_tarjeta,
        cargar_productos_activos_df_fn=cargar_productos_activos_df,
        cargar_promociones_df_fn=cargar_promociones_df,
        obtener_mejor_promocion_por_producto_fn=obtener_mejor_promocion_por_producto,
        calcular_descuento_promocion_fn=calcular_descuento_promocion,
        formatear_cop_fn=formatear_cop,
        obtener_galeria_producto_fn=obtener_galeria_producto,
        cargar_productos_df_fn=cargar_productos_df,
        guardar_productos_df_fn=guardar_productos_df,
        fuerzas_opciones=FUERZAS_OPCIONES,
        intendencias_opciones=INTENDENCIAS_OPCIONES,
        obtener_productos_agotados_fn=obtener_productos_agotados,
        obtener_nombre_sesion_fn=obtener_nombre_sesion,
        cargar_usuarios_df_fn=cargar_usuarios_df,
        guardar_usuarios_df_fn=guardar_usuarios_df,
        cargar_pedidos_df_fn=cargar_pedidos_df,
        cargar_detalle_pedido_df_fn=cargar_detalle_pedido_df,
        cargar_pagos_df_fn=cargar_pagos_df,
        pago_status_labels=PAGO_STATUS_LABELS,
        pedido_status_alias=PEDIDO_STATUS_ALIAS,
        pedido_status_labels=PEDIDO_STATUS_LABELS,
        pedido_status_flow=PEDIDO_STATUS_FLOW,
        normalizar_email_fn=normalizar_email,
        email_es_valido_fn=email_es_valido,
        enviar_actualizacion_pedido_fn=enviar_actualizacion_pedido,
        enviar_notificacion_pago_personalizado_admin_fn=enviar_notificacion_pago_personalizado_admin,
        enviar_notificacion_transferencia_admin_fn=enviar_notificacion_transferencia_admin,
        next_id_fn=next_id,
        guardar_pagos_df_fn=guardar_pagos_df,
        guardar_detalle_pedido_df_fn=guardar_detalle_pedido_df,
        guardar_pedidos_df_fn=guardar_pedidos_df,
        tallas_opciones=TALLAS_OPCIONES,
        producto_requiere_talla_fn=producto_requiere_talla,
        buscar_promocion_por_codigo_fn=buscar_promocion_por_codigo,
        hash_carrito_checkout_fn=_hash_carrito_checkout,
        stripe_obj_get_fn=_stripe_obj_get,
        stripe_checkout_guardar_creado_fn=_stripe_checkout_guardar_creado,
        logger_obj=app.logger,
        obtener_items_personalizados_carrito_fn=app_mail_service.obtener_items_personalizados_carrito,
    )
)

_obtener_pedidos_usuario_actual = partial(
    user_orders_service.obtener_pedidos_usuario_actual,
    session_obj=session,
    cargar_pedidos_df_fn=cargar_pedidos_df,
    cargar_pagos_df_fn=cargar_pagos_df,
    pedido_columns=PEDIDO_COLUMNS,
    enriquecer_pedidos_con_tracking_fn=_enriquecer_pedidos_con_tracking,
)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
