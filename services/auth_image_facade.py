"""Fachada de helpers legacy para auth e imagenes."""

import re


def build_auth_image_legacy_bindings(
    *,
    app_auth_service,
    app_image_service,
    pending_registrations,
    register_code_exp_minutes,
    allowed_image_extensions,
    max_image_size_bytes,
    generate_password_hash_fn,
    check_password_hash_fn,
    enviar_codigo_verificacion_fn,
):
    def normalizar_imagen_url(valor):
        return app_image_service.normalizar_imagen_url(valor)

    def normalizar_imagenes_productos(productos):
        return app_image_service.normalizar_imagenes_productos(productos)

    def extension_imagen(nombre_archivo):
        return app_image_service.extension_imagen(nombre_archivo)

    def normalizar_email(valor):
        return app_auth_service.normalizar_email(valor)

    def email_es_valido(email):
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(email or "").strip()))

    def limpiar_registros_pendientes():
        return app_auth_service.limpiar_registros_pendientes(pending_registrations)

    def obtener_registro_pendiente(email):
        return app_auth_service.obtener_registro_pendiente(email, pending_registrations)

    def guardar_registro_pendiente(email, codigo, nombre="", password=""):
        return app_auth_service.guardar_registro_pendiente(
            email,
            codigo,
            pending_registrations,
            register_code_exp_minutes,
            nombre=nombre,
            password=password,
        )

    def password_esta_hasheado(valor):
        return app_auth_service.password_esta_hasheado(valor)

    def crear_hash_password(password):
        return app_auth_service.crear_hash_password(password, generate_password_hash_fn=generate_password_hash_fn)

    def password_coincide(password_guardado, password_plano):
        return app_auth_service.password_coincide(
            password_guardado,
            password_plano,
            check_password_hash_fn=check_password_hash_fn,
        )

    def password_cumple_estandares(password):
        return app_auth_service.password_cumple_estandares(password)

    def timestamp_expirado(valor_expiry):
        return app_auth_service.timestamp_expirado(valor_expiry)

    def asegurar_columnas_cambio_password(usuarios):
        return app_auth_service.asegurar_columnas_cambio_password(usuarios)

    def codigo_cambio_password_expirado(usuario):
        return app_auth_service.codigo_cambio_password_expirado(usuario)

    def limpiar_codigo_cambio_password(usuarios, idx_usuario):
        return app_auth_service.limpiar_codigo_cambio_password(usuarios, idx_usuario)

    def generar_token_recuperacion():
        return app_auth_service.generar_token_recuperacion()

    def obtener_usuario_por_token_recuperacion(usuarios, token):
        return app_auth_service.obtener_usuario_por_token_recuperacion(usuarios, token)

    def token_recuperacion_expirado(usuario):
        return app_auth_service.token_recuperacion_expirado(usuario)

    def limpiar_token_recuperacion(usuarios, idx_usuario):
        return app_auth_service.limpiar_token_recuperacion(usuarios, idx_usuario)

    def enviar_codigo_registro(email, codigo):
        return app_auth_service.enviar_codigo_registro(
            email,
            codigo,
            enviar_codigo_verificacion_fn=enviar_codigo_verificacion_fn,
            register_code_exp_minutes=register_code_exp_minutes,
        )

    def validar_archivo_imagen(archivo):
        return app_image_service.validar_archivo_imagen(
            archivo,
            allowed_image_extensions=allowed_image_extensions,
            max_image_size_bytes=max_image_size_bytes,
        )

    def guardar_comprobante_transferencia(archivo, id_pedido):
        return app_image_service.guardar_comprobante_transferencia(
            archivo,
            id_pedido,
            allowed_image_extensions=allowed_image_extensions,
            max_image_size_bytes=max_image_size_bytes,
        )

    def guardar_preview_personalizado_desde_data_url(data_url, prefijo="personalizada"):
        return app_image_service.guardar_preview_personalizado_desde_data_url(
            data_url,
            max_image_size_bytes=max_image_size_bytes,
            prefijo=prefijo,
        )

    def guardar_documento_identidad_personalizada_desde_data_url(data_url, usuario_email=""):
        return app_image_service.guardar_documento_identidad_personalizada_desde_data_url(
            data_url,
            max_image_size_bytes=max_image_size_bytes,
            usuario_email=usuario_email,
        )

    def ruta_imagen_producto_absoluta(ruta_relativa):
        return app_image_service.ruta_imagen_producto_absoluta(ruta_relativa)

    def listar_archivos_galeria_producto(id_producto, fuerza=""):
        return app_image_service.listar_archivos_galeria_producto(
            id_producto,
            allowed_image_extensions=allowed_image_extensions,
            fuerza=fuerza,
        )

    def migrar_legacy_a_galeria(id_producto, fuerza=""):
        return app_image_service.migrar_legacy_a_galeria(
            id_producto,
            allowed_image_extensions=allowed_image_extensions,
            fuerza=fuerza,
        )

    def limpiar_imagenes_producto(id_producto, fuerza=""):
        return app_image_service.limpiar_imagenes_producto(
            id_producto,
            allowed_image_extensions=allowed_image_extensions,
            fuerza=fuerza,
        )

    def resolver_imagen_catalogo_existente(ruta_relativa):
        return app_image_service.resolver_imagen_catalogo_existente(
            ruta_relativa,
            allowed_image_extensions=allowed_image_extensions,
        )

    def listar_imagenes_catalogo_disponibles():
        return app_image_service.listar_imagenes_catalogo_disponibles(
            allowed_image_extensions=allowed_image_extensions,
        )

    def guardar_galeria_producto(id_producto, imagenes, reemplazar=True, fuerza="", intendencia=""):
        return app_image_service.guardar_galeria_producto(
            id_producto,
            imagenes,
            allowed_image_extensions=allowed_image_extensions,
            reemplazar=reemplazar,
            fuerza=fuerza,
            intendencia=intendencia,
        )

    def obtener_galeria_producto(id_producto, imagen_principal=""):
        return app_image_service.obtener_galeria_producto(
            id_producto,
            allowed_image_extensions=allowed_image_extensions,
            imagen_principal=imagen_principal,
        )

    return {
        "normalizar_imagen_url": normalizar_imagen_url,
        "normalizar_imagenes_productos": normalizar_imagenes_productos,
        "extension_imagen": extension_imagen,
        "normalizar_email": normalizar_email,
        "email_es_valido": email_es_valido,
        "limpiar_registros_pendientes": limpiar_registros_pendientes,
        "obtener_registro_pendiente": obtener_registro_pendiente,
        "guardar_registro_pendiente": guardar_registro_pendiente,
        "password_esta_hasheado": password_esta_hasheado,
        "crear_hash_password": crear_hash_password,
        "password_coincide": password_coincide,
        "password_cumple_estandares": password_cumple_estandares,
        "timestamp_expirado": timestamp_expirado,
        "asegurar_columnas_cambio_password": asegurar_columnas_cambio_password,
        "codigo_cambio_password_expirado": codigo_cambio_password_expirado,
        "limpiar_codigo_cambio_password": limpiar_codigo_cambio_password,
        "generar_token_recuperacion": generar_token_recuperacion,
        "obtener_usuario_por_token_recuperacion": obtener_usuario_por_token_recuperacion,
        "token_recuperacion_expirado": token_recuperacion_expirado,
        "limpiar_token_recuperacion": limpiar_token_recuperacion,
        "enviar_codigo_registro": enviar_codigo_registro,
        "validar_archivo_imagen": validar_archivo_imagen,
        "guardar_comprobante_transferencia": guardar_comprobante_transferencia,
        "guardar_preview_personalizado_desde_data_url": guardar_preview_personalizado_desde_data_url,
        "guardar_documento_identidad_personalizada_desde_data_url": guardar_documento_identidad_personalizada_desde_data_url,
        "ruta_imagen_producto_absoluta": ruta_imagen_producto_absoluta,
        "listar_archivos_galeria_producto": listar_archivos_galeria_producto,
        "migrar_legacy_a_galeria": migrar_legacy_a_galeria,
        "limpiar_imagenes_producto": limpiar_imagenes_producto,
        "resolver_imagen_catalogo_existente": resolver_imagen_catalogo_existente,
        "listar_imagenes_catalogo_disponibles": listar_imagenes_catalogo_disponibles,
        "guardar_galeria_producto": guardar_galeria_producto,
        "obtener_galeria_producto": obtener_galeria_producto,
    }
