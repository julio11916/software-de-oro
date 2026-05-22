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
import unicodedata


PRODUCT_IMAGE_ROOT = os.path.join("static", "img", "catalogo")
LEGACY_PRODUCT_IMAGE_ROOT = os.path.join("static", "img", "Empresa")


def _slug_carpeta(valor):
    texto = str(valor or "").strip()
    if not texto:
        return "variado"
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9_-]+", "_", texto).strip("_").lower()
    return texto or "variado"


def _carpeta_catalogo_fuerza(fuerza=""):
    base = Path(PRODUCT_IMAGE_ROOT)
    slug = _slug_carpeta(fuerza)
    if base.is_dir():
        for carpeta in base.iterdir():
            if carpeta.is_dir() and carpeta.name.lower() == slug:
                return str(carpeta)
    return str(base / slug)


def _carpetas_catalogo_producto(fuerza="", incluir_legacy=False):
    carpetas = []
    if fuerza:
        carpetas.append(_carpeta_catalogo_fuerza(fuerza))
    base = Path(PRODUCT_IMAGE_ROOT)
    if base.is_dir():
        carpetas.extend(str(carpeta) for carpeta in base.iterdir() if carpeta.is_dir())
    if incluir_legacy:
        carpetas.append(LEGACY_PRODUCT_IMAGE_ROOT)

    unicas = []
    vistos = set()
    for carpeta in carpetas:
        normalizada = os.path.abspath(carpeta).lower()
        if normalizada in vistos:
            continue
        vistos.add(normalizada)
        unicas.append(carpeta)
    return unicas


def _es_imagen_generada_producto(nombre_archivo):
    return bool(re.match(r"^producto_\d+(?:_[^.]+)?\.[a-z0-9]+$", str(nombre_archivo or ""), flags=re.IGNORECASE))


def _nombre_imagen_producto(id_producto, indice, extension):
    marca = datetime.now().strftime("%Y%m%d%H%M%S%f")
    token = secrets.token_hex(3)
    return f"producto_{id_producto}_{indice}_{marca}_{token}.{extension}"


def _leer_archivo_subido(archivo):
    try:
        archivo.seek(0)
        contenido = archivo.read()
        archivo.seek(0)
        return contenido
    except Exception:
        try:
            archivo.seek(0)
        except Exception:
            pass
        return b""


def buscar_imagen_catalogo_existente(archivo, allowed_image_extensions, fuerza=""):
    nombre_original = os.path.basename(str(getattr(archivo, "filename", "") or "")).strip()
    extension = extension_imagen(nombre_original)
    if not nombre_original or extension not in allowed_image_extensions:
        return ""
    if _es_imagen_generada_producto(nombre_original):
        return ""

    contenido_subido = _leer_archivo_subido(archivo)
    if not contenido_subido:
        return ""

    nombre_normalizado = nombre_original.lower()
    for carpeta_catalogo in _carpetas_catalogo_producto(fuerza):
        carpeta = Path(carpeta_catalogo)
        if not carpeta.is_dir():
            continue

        for candidata in carpeta.rglob("*"):
            if not candidata.is_file():
                continue
            if candidata.name.lower() != nombre_normalizado:
                continue
            if _es_imagen_generada_producto(candidata.name):
                continue
            if extension_imagen(candidata.name) not in allowed_image_extensions:
                continue
            try:
                if candidata.read_bytes() != contenido_subido:
                    continue
            except OSError:
                continue

            return os.path.relpath(str(candidata), "static").replace("\\", "/")

    return ""


def resolver_imagen_catalogo_existente(ruta_relativa, allowed_image_extensions):
    ruta = normalizar_imagen_url(ruta_relativa)
    if not ruta.startswith("img/catalogo/"):
        return ""
    if extension_imagen(ruta) not in allowed_image_extensions:
        return ""

    base = os.path.abspath(PRODUCT_IMAGE_ROOT)
    candidata = os.path.abspath(os.path.join("static", ruta))
    if os.path.commonpath([base, candidata]) != base:
        return ""
    if not os.path.isfile(candidata):
        return ""
    return os.path.relpath(candidata, "static").replace("\\", "/")


def listar_imagenes_catalogo_disponibles(allowed_image_extensions):
    base = Path(PRODUCT_IMAGE_ROOT)
    if not base.is_dir():
        return []

    imagenes = []
    for archivo in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not archivo.is_file():
            continue
        if extension_imagen(archivo.name) not in allowed_image_extensions:
            continue
        if _es_imagen_generada_producto(archivo.name):
            continue

        ruta = os.path.relpath(str(archivo), "static").replace("\\", "/")
        carpeta = archivo.parent.name
        imagenes.append(
            {
                "ruta": ruta,
                "nombre": archivo.stem.replace("_", " ").replace("-", " ").strip() or archivo.name,
                "carpeta": carpeta,
            }
        )
    return imagenes


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


def guardar_documento_identidad_personalizada_desde_data_url(data_url, max_image_size_bytes, usuario_email=""):
    raw = str(data_url or "").strip()
    if not raw:
        return {}, "Debes adjuntar una foto legible de tu libreta militar, carné o documento institucional."

    match = re.match(r"^data:image/(png|jpe?g|webp|gif);base64,(.+)$", raw, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return {}, "El documento de validación debe ser una imagen JPG, PNG, GIF o WEBP."

    ext = match.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    payload_b64 = match.group(2)

    try:
        contenido = base64.b64decode(payload_b64, validate=True)
    except Exception:
        return {}, "No se pudo procesar la imagen del documento de validación."

    if not contenido:
        return {}, "La imagen del documento de validación está vacía."
    if len(contenido) > max_image_size_bytes:
        return {}, "La imagen del documento de validación supera el tamaño permitido (3MB)."

    usuario_slug = _slug_carpeta(str(usuario_email or "usuario").split("@", 1)[0])
    carpeta_relativa = Path("validaciones_identidad") / usuario_slug
    carpeta_destino = Path("instance") / carpeta_relativa
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    nombre_archivo = f"validacion_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{secrets.token_hex(4)}.{ext}"
    ruta_absoluta = carpeta_destino / nombre_archivo
    ruta_absoluta.write_bytes(contenido)

    ruta_privada = (carpeta_relativa / nombre_archivo).as_posix()
    return {
        "path": ruta_privada,
        "filename": nombre_archivo,
        "content_type": f"image/{'jpeg' if ext == 'jpg' else ext}",
        "size": len(contenido),
    }, ""


def ruta_imagen_producto_absoluta(ruta_relativa):
    ruta = str(ruta_relativa or "").strip().replace("\\", "/").lstrip("/")
    if not (ruta.startswith("img/catalogo/") or ruta.startswith("img/Empresa/")):
        return ""

    bases = [
        os.path.abspath(PRODUCT_IMAGE_ROOT),
        os.path.abspath(LEGACY_PRODUCT_IMAGE_ROOT),
    ]
    candidata = os.path.abspath(os.path.join("static", ruta))
    if not any(os.path.commonpath([base, candidata]) == base for base in bases):
        return ""
    return candidata


def listar_archivos_galeria_producto(id_producto, allowed_image_extensions, fuerza=""):
    prefijo = f"producto_{id_producto}_"
    resultados = []

    for carpeta_destino in _carpetas_catalogo_producto(fuerza):
        if not os.path.isdir(carpeta_destino):
            continue
        for nombre in os.listdir(carpeta_destino):
            if not nombre.lower().startswith(prefijo.lower()):
                continue
            if extension_imagen(nombre) not in allowed_image_extensions:
                continue
            sufijo = nombre[len(prefijo) :]
            posicion = sufijo.rsplit(".", 1)[0].split("_", 1)[0]
            if not posicion.isdigit():
                continue
            ruta_relativa = os.path.relpath(os.path.join(carpeta_destino, nombre), "static").replace("\\", "/")
            resultados.append((int(posicion), ruta_relativa))

    resultados.sort(key=lambda item: item[0])
    return resultados


def migrar_legacy_a_galeria(id_producto, allowed_image_extensions, fuerza=""):
    if listar_archivos_galeria_producto(id_producto, allowed_image_extensions, fuerza=fuerza):
        return

    carpeta_origen = LEGACY_PRODUCT_IMAGE_ROOT
    carpeta_destino = _carpeta_catalogo_fuerza(fuerza)
    if not os.path.isdir(carpeta_origen):
        return
    os.makedirs(carpeta_destino, exist_ok=True)

    for extension in sorted(allowed_image_extensions):
        legacy_name = f"producto_{id_producto}.{extension}"
        legacy_path = os.path.join(carpeta_origen, legacy_name)
        if not os.path.exists(legacy_path):
            continue
        nuevo_nombre = f"producto_{id_producto}_1.{extension}"
        nuevo_path = os.path.join(carpeta_destino, nuevo_nombre)
        os.replace(legacy_path, nuevo_path)
        break


def limpiar_imagenes_producto(id_producto, allowed_image_extensions, fuerza=""):
    prefijo_galeria = f"producto_{id_producto}_".lower()
    prefijo_legacy = f"producto_{id_producto}.".lower()
    for carpeta_destino in _carpetas_catalogo_producto(fuerza, incluir_legacy=True):
        if not os.path.isdir(carpeta_destino):
            continue
        for nombre in os.listdir(carpeta_destino):
            nombre_lower = nombre.lower()
            if not (nombre_lower.startswith(prefijo_galeria) or nombre_lower.startswith(prefijo_legacy)):
                continue
            if extension_imagen(nombre_lower) not in allowed_image_extensions:
                continue
            ruta = os.path.join(carpeta_destino, nombre)
            if os.path.isfile(ruta):
                os.remove(ruta)


def guardar_galeria_producto(id_producto, imagenes, allowed_image_extensions, reemplazar=True, fuerza="", intendencia=""):
    carpeta_destino = _carpeta_catalogo_fuerza(fuerza)
    os.makedirs(carpeta_destino, exist_ok=True)

    imagenes_validas = [img for img in imagenes if img and str(getattr(img, "filename", "")).strip()]
    if reemplazar:
        limpiar_imagenes_producto(id_producto, allowed_image_extensions, fuerza=fuerza)
        indice_inicial = 1
    else:
        migrar_legacy_a_galeria(id_producto, allowed_image_extensions, fuerza=fuerza)
        existentes = listar_archivos_galeria_producto(id_producto, allowed_image_extensions, fuerza=fuerza)
        indice_inicial = (existentes[-1][0] + 1) if existentes else 1

    if reemplazar and len(imagenes_validas) == 1:
        ruta_existente = buscar_imagen_catalogo_existente(imagenes_validas[0], allowed_image_extensions, fuerza=fuerza)
        if ruta_existente:
            return [ruta_existente]

    rutas_guardadas = []
    for indice, imagen in enumerate(imagenes_validas, start=indice_inicial):
        extension = extension_imagen(imagen.filename)
        nombre_archivo = _nombre_imagen_producto(id_producto, indice, extension)
        ruta_absoluta = os.path.join(carpeta_destino, nombre_archivo)
        imagen.save(ruta_absoluta)
        ruta_relativa = os.path.relpath(ruta_absoluta, "static").replace("\\", "/")
        rutas_guardadas.append(ruta_relativa)
    return rutas_guardadas


def obtener_galeria_producto(id_producto, allowed_image_extensions, imagen_principal=""):
    try:
        id_producto_int = int(float(id_producto))
    except (TypeError, ValueError):
        return [normalizar_imagen_url(imagen_principal)] if str(imagen_principal).strip() else []

    galeria = listar_archivos_galeria_producto(id_producto_int, allowed_image_extensions)
    rutas = []
    imagen_principal_norm = normalizar_imagen_url(imagen_principal)
    if imagen_principal_norm:
        rutas.append(imagen_principal_norm)

    for _, ruta in galeria:
        ruta_norm = normalizar_imagen_url(ruta)
        if ruta_norm and ruta_norm not in rutas:
            rutas.append(ruta_norm)

    if not rutas:
        for extension in sorted(allowed_image_extensions):
            legacy_name = f"producto_{id_producto_int}.{extension}"
            legacy_path = os.path.join(LEGACY_PRODUCT_IMAGE_ROOT, legacy_name)
            if os.path.exists(legacy_path):
                rutas.append(f"img/Empresa/{legacy_name}")
                break
    return rutas
