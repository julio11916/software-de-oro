"""
Servicio para validacion y gestion de imagenes.
Extrae logica de imagenes para reducir app.py.
"""

import base64
from datetime import datetime
import os
from pathlib import Path
import re
import secrets


def normalizar_imagen_url(valor):
    ruta = str(valor or "").strip().replace("\\", "/")
    if not ruta or ruta.lower() == "nan":
        return ""
    ruta = re.sub(r"^https?://[^/]+", "", ruta, flags=re.IGNORECASE)
    if ruta.startswith("/static/"):
        ruta = ruta[len("/static/") :]
    elif ruta.startswith("static/"):
        ruta = ruta[len("static/") :]
    if ruta.startswith("/img/"):
        ruta = ruta[1:]
    ruta = ruta.lstrip()
    if (
        ruta.startswith("img/Empresa/")
        or ruta.startswith("img/Pagina/")
        or ruta.startswith("img/catalogo/")
        or ruta.startswith("img/prendas/")
        or ruta.startswith("img/estampados/")
        or ruta.startswith("img/personalizadas/")
        or ruta.startswith("img/comprobantes/")
    ):
        return ruta
    if ruta.startswith("img/"):
        return f"img/Empresa/{ruta.split('/')[-1]}"
    return ruta


def normalizar_imagenes_productos(productos):
    if "imagen_url" not in productos.columns:
        productos["imagen_url"] = ""
    productos["imagen_url"] = productos["imagen_url"].apply(normalizar_imagen_url)
    return productos


def extension_imagen(nombre_archivo):
    if not nombre_archivo or "." not in nombre_archivo:
        return ""
    return nombre_archivo.rsplit(".", 1)[-1].lower()


def validar_archivo_imagen(archivo, allowed_image_extensions, max_image_size_bytes):
    extension = extension_imagen(getattr(archivo, "filename", ""))
    if extension not in allowed_image_extensions:
        return "Formato de imagen no permitido. Usa .jpg, .jpeg, .png, .gif o .webp."

    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > max_image_size_bytes:
        return "La imagen excede el tamano maximo permitido (3MB)."
    return None


def guardar_comprobante_transferencia(archivo, id_pedido, allowed_image_extensions, max_image_size_bytes):
    error_validacion = validar_archivo_imagen(
        archivo,
        allowed_image_extensions=allowed_image_extensions,
        max_image_size_bytes=max_image_size_bytes,
    )
    if error_validacion:
        return "", error_validacion

    carpeta_destino = os.path.join("static", "img", "comprobantes")
    os.makedirs(carpeta_destino, exist_ok=True)

    extension = extension_imagen(getattr(archivo, "filename", "")) or "jpg"
    nombre_archivo = f"comprobante_pedido_{int(id_pedido)}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.{extension}"
    ruta_absoluta = os.path.join(carpeta_destino, nombre_archivo)
    archivo.save(ruta_absoluta)
    return f"img/comprobantes/{nombre_archivo}".replace("\\", "/"), ""


def guardar_preview_personalizado_desde_data_url(data_url, max_image_size_bytes, prefijo="personalizada"):
    raw = str(data_url or "").strip()
    if not raw:
        return "", "No se recibio imagen de vista previa."

    match = re.match(r"^data:image/(png|jpe?g|webp);base64,(.+)$", raw, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return "", "El formato de la vista previa no es valido."

    ext = match.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    payload_b64 = match.group(2)

    try:
        contenido = base64.b64decode(payload_b64, validate=True)
    except Exception:
        return "", "No se pudo procesar la imagen de vista previa."

    if not contenido:
        return "", "La imagen de vista previa esta vacia."
    if len(contenido) > max_image_size_bytes:
        return "", "La imagen de vista previa supera el tamano permitido (3MB)."

    carpeta_destino = os.path.join("static", "img", "personalizadas")
    os.makedirs(carpeta_destino, exist_ok=True)

    nombre_archivo = f"{prefijo}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{secrets.token_hex(4)}.{ext}"
    ruta_absoluta = os.path.join(carpeta_destino, nombre_archivo)
    with open(ruta_absoluta, "wb") as fh:
        fh.write(contenido)

    return f"/static/img/personalizadas/{nombre_archivo}".replace("\\", "/"), ""


def ruta_imagen_producto_absoluta(ruta_relativa):
    ruta = str(ruta_relativa or "").strip().replace("\\", "/").lstrip("/")
    if not ruta.startswith("img/Empresa/"):
        return ""

    base = os.path.abspath(os.path.join("static", "img", "Empresa"))
    candidata = os.path.abspath(os.path.join("static", ruta))
    if os.path.commonpath([base, candidata]) != base:
        return ""
    return candidata


def listar_archivos_galeria_producto(id_producto, allowed_image_extensions):
    carpeta_destino = os.path.join("static", "img", "Empresa")
    prefijo = f"producto_{id_producto}_"
    resultados = []

    if not os.path.isdir(carpeta_destino):
        return resultados

    for nombre in os.listdir(carpeta_destino):
        if not nombre.lower().startswith(prefijo.lower()):
            continue
        if extension_imagen(nombre) not in allowed_image_extensions:
            continue
        sufijo = nombre[len(prefijo) :]
        posicion = sufijo.split(".", 1)[0]
        if not posicion.isdigit():
            continue
        resultados.append((int(posicion), nombre))

    resultados.sort(key=lambda item: item[0])
    return resultados


def migrar_legacy_a_galeria(id_producto, allowed_image_extensions):
    if listar_archivos_galeria_producto(id_producto, allowed_image_extensions):
        return

    carpeta_destino = os.path.join("static", "img", "Empresa")
    if not os.path.isdir(carpeta_destino):
        return

    for extension in sorted(allowed_image_extensions):
        legacy_name = f"producto_{id_producto}.{extension}"
        legacy_path = os.path.join(carpeta_destino, legacy_name)
        if not os.path.exists(legacy_path):
            continue
        nuevo_nombre = f"producto_{id_producto}_1.{extension}"
        nuevo_path = os.path.join(carpeta_destino, nuevo_nombre)
        os.replace(legacy_path, nuevo_path)
        break


def limpiar_imagenes_producto(id_producto, allowed_image_extensions):
    carpeta_destino = os.path.join("static", "img", "Empresa")
    if not os.path.isdir(carpeta_destino):
        return

    prefijo_galeria = f"producto_{id_producto}_".lower()
    prefijo_legacy = f"producto_{id_producto}.".lower()
    for nombre in os.listdir(carpeta_destino):
        nombre_lower = nombre.lower()
        if not (nombre_lower.startswith(prefijo_galeria) or nombre_lower.startswith(prefijo_legacy)):
            continue
        if extension_imagen(nombre_lower) not in allowed_image_extensions:
            continue
        ruta = os.path.join(carpeta_destino, nombre)
        if os.path.isfile(ruta):
            os.remove(ruta)


def guardar_galeria_producto(id_producto, imagenes, allowed_image_extensions, reemplazar=True):
    carpeta_destino = os.path.join("static", "img", "Empresa")
    os.makedirs(carpeta_destino, exist_ok=True)

    imagenes_validas = [img for img in imagenes if img and str(getattr(img, "filename", "")).strip()]
    if reemplazar:
        limpiar_imagenes_producto(id_producto, allowed_image_extensions)
        indice_inicial = 1
    else:
        migrar_legacy_a_galeria(id_producto, allowed_image_extensions)
        existentes = listar_archivos_galeria_producto(id_producto, allowed_image_extensions)
        indice_inicial = (existentes[-1][0] + 1) if existentes else 1

    rutas_guardadas = []
    for indice, imagen in enumerate(imagenes_validas, start=indice_inicial):
        extension = extension_imagen(imagen.filename)
        nombre_archivo = f"producto_{id_producto}_{indice}.{extension}"
        ruta_absoluta = os.path.join(carpeta_destino, nombre_archivo)
        imagen.save(ruta_absoluta)
        rutas_guardadas.append(f"img/Empresa/{nombre_archivo}".replace("\\", "/"))
    return rutas_guardadas


def obtener_galeria_producto(id_producto, allowed_image_extensions, imagen_principal=""):
    try:
        id_producto_int = int(float(id_producto))
    except (TypeError, ValueError):
        return [normalizar_imagen_url(imagen_principal)] if str(imagen_principal).strip() else []

    galeria = listar_archivos_galeria_producto(id_producto_int, allowed_image_extensions)
    rutas = [f"img/Empresa/{nombre}".replace("\\", "/") for _, nombre in galeria]

    if not rutas:
        carpeta_destino = os.path.join("static", "img", "Empresa")
        if str(imagen_principal).strip():
            rutas.append(normalizar_imagen_url(imagen_principal))
        else:
            for extension in sorted(allowed_image_extensions):
                legacy_name = f"producto_{id_producto_int}.{extension}"
                legacy_path = os.path.join(carpeta_destino, legacy_name)
                if os.path.exists(legacy_path):
                    rutas.append(f"img/Empresa/{legacy_name}")
                    break
    return rutas
