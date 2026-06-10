from datetime import datetime
import base64
import os
from pathlib import Path
import shutil
import subprocess

import pandas as pd


def construir_datos_recibo_pos(
    id_pedido,
    *,
    cargar_detalle_pedido_df_fn,
    cargar_productos_df_fn,
    cargar_pagos_df_fn,
    cargar_pedidos_df_fn,
    tallas_opciones,
    ultimo_recibo_pos=None,
):
    detalle = cargar_detalle_pedido_df_fn()
    if detalle.empty:
        raise ValueError(f"No existe detalle para el pedido #{id_pedido}.")

    detalle = detalle.copy()
    detalle["id_pedido"] = pd.to_numeric(detalle["id_pedido"], errors="coerce")
    detalle = detalle[detalle["id_pedido"] == int(id_pedido)]
    if detalle.empty:
        raise ValueError(f"No existe detalle para el pedido #{id_pedido}.")

    if "id_detalle" in detalle.columns:
        detalle = detalle.sort_values(by="id_detalle", ascending=True, na_position="last")

    productos_df = cargar_productos_df_fn()
    productos_df["id_producto"] = pd.to_numeric(productos_df["id_producto"], errors="coerce")
    productos_map = {}
    for _, row in productos_df.iterrows():
        if pd.notna(row.get("id_producto")):
            productos_map[int(row["id_producto"])] = str(row.get("nombre", "")).strip()

    items = []
    for _, row in detalle.iterrows():
        id_producto = int(pd.to_numeric(row.get("id_producto"), errors="coerce") or 0)
        cantidad = int(pd.to_numeric(row.get("cantidad", 0), errors="coerce") or 0)
        subtotal = float(pd.to_numeric(row.get("subtotal", 0), errors="coerce") or 0)
        talla = str(row.get("talla", "") or "").strip().upper()
        if talla not in tallas_opciones:
            talla = "-"
        if cantidad <= 0:
            cantidad = 1
        valor_unitario = subtotal / cantidad if cantidad else subtotal
        descripcion = productos_map.get(id_producto, f"Producto #{id_producto}")
        items.append(
            {
                "cantidad": cantidad,
                "talla": talla,
                "descripcion": descripcion,
                "valor_unitario": float(valor_unitario),
                "total": float(subtotal),
            }
        )

    pagos = cargar_pagos_df_fn()
    pagos["id_pedido"] = pd.to_numeric(pagos["id_pedido"], errors="coerce")
    pago_pedido = pagos[pagos["id_pedido"] == int(id_pedido)].copy()
    pago_row = None
    if not pago_pedido.empty:
        pago_pedido["id_pago"] = pd.to_numeric(pago_pedido["id_pago"], errors="coerce")
        pago_pedido = pago_pedido.sort_values(by="id_pago", ascending=False, na_position="last")
        pago_row = pago_pedido.iloc[0]

    metodo_pago = ""
    monto_total = float(sum(item["total"] for item in items))
    descuento_total = 0.0
    if pago_row is not None:
        metodo_pago = str(pago_row.get("metodo_pago", "")).strip().lower()
        monto_total = float(pd.to_numeric(pago_row.get("monto", monto_total), errors="coerce") or monto_total)
        descuento_total = float(pd.to_numeric(pago_row.get("monto_descuento", 0), errors="coerce") or 0)

    metodo_label = {
        "efectivo": "Efectivo",
        "tarjeta": "Tarjeta",
        "transferencia": "Transferencia",
        "qr": "QR",
    }.get(metodo_pago, metodo_pago.title() if metodo_pago else "No especificado")

    pedidos = cargar_pedidos_df_fn()
    pedidos["id_pedido"] = pd.to_numeric(pedidos["id_pedido"], errors="coerce")
    pedido_row = pedidos[pedidos["id_pedido"] == int(id_pedido)]
    fecha_compra = datetime.now()
    if not pedido_row.empty:
        fecha_raw = pedido_row.iloc[0].get("fecha_pedido", "")
        fecha_parseada = pd.to_datetime(fecha_raw, errors="coerce")
        if pd.notna(fecha_parseada):
            fecha_compra = fecha_parseada.to_pydatetime()

    ultimo_recibo = ultimo_recibo_pos or {}
    cliente_nombre = ""
    cliente_correo = ""
    cliente_documento = ""
    cliente_telefono = ""
    if str(ultimo_recibo.get("id_pedido", "")) == str(id_pedido):
        cliente_nombre = str(ultimo_recibo.get("cliente_nombre", "")).strip()
        cliente_correo = str(ultimo_recibo.get("cliente_correo", "")).strip()
        cliente_documento = str(ultimo_recibo.get("cliente_documento", "")).strip()
        cliente_telefono = str(ultimo_recibo.get("cliente_telefono", "")).strip()

    subtotal_bruto = max(0.0, monto_total + descuento_total)
    return {
        "id_pedido": int(id_pedido),
        "fecha_compra": fecha_compra,
        "metodo_pago": metodo_label,
        "items": items,
        "subtotal_bruto": float(subtotal_bruto),
        "descuento_total": float(descuento_total),
        "total": float(monto_total),
        "cliente_nombre": cliente_nombre,
        "cliente_correo": cliente_correo,
        "cliente_documento": cliente_documento,
        "cliente_telefono": cliente_telefono,
    }


def particionar_items_recibo(items, max_items_por_pagina=8):
    items = list(items or [])
    if not items:
        return [[]]
    return [items[i : i + max_items_por_pagina] for i in range(0, len(items), max_items_por_pagina)]


def construir_contexto_recibo_pos(
    id_pedido,
    *,
    construir_datos_recibo_pos_fn,
    formatear_cop_fn,
    particionar_items_recibo_fn=particionar_items_recibo,
):
    datos = construir_datos_recibo_pos_fn(id_pedido)
    fecha_txt = datos["fecha_compra"].strftime("%d / %m / %Y")
    hora_txt = datos["fecha_compra"].strftime("%H:%M:%S")

    items_formateados = []
    for item in datos.get("items", []):
        items_formateados.append(
            {
                "cantidad": int(pd.to_numeric(item.get("cantidad", 0), errors="coerce") or 0),
                "talla": str(item.get("talla", "-") or "-").strip().upper() or "-",
                "descripcion": str(item.get("descripcion", "") or "").strip(),
                "valor_unitario": formatear_cop_fn(item.get("valor_unitario", 0)),
                "total": formatear_cop_fn(item.get("total", 0)),
            }
        )

    paginas_items = particionar_items_recibo_fn(items_formateados, max_items_por_pagina=8)
    total_paginas = len(paginas_items)
    paginas = []
    for i, items_pagina in enumerate(paginas_items, start=1):
        paginas.append({"numero": i, "detalle_items": items_pagina, "es_ultima": i == total_paginas})

    cliente_campos = []
    cliente_nombre = str(datos.get("cliente_nombre", "") or "").strip()
    cliente_doc = str(datos.get("cliente_documento", "") or "").strip()
    cliente_tel = str(datos.get("cliente_telefono", "") or "").strip()
    cliente_mail = str(datos.get("cliente_correo", "") or "").strip()
    if cliente_nombre:
        cliente_campos.append({"label": "Nombre", "valor": cliente_nombre})
    if cliente_doc:
        cliente_campos.append({"label": "Documento", "valor": cliente_doc})
    if cliente_tel:
        cliente_campos.append({"label": "Telefono", "valor": cliente_tel})
    if cliente_mail:
        cliente_campos.append({"label": "Correo", "valor": cliente_mail})

    return {
        "id_pedido": int(datos["id_pedido"]),
        "codigo_recibo": f"POS-{int(datos['id_pedido']):06d}",
        "fecha_txt": fecha_txt,
        "hora_txt": hora_txt,
        "paginas": paginas,
        "total_paginas": total_paginas,
        "cliente_campos": cliente_campos,
        "cantidad_items": len(items_formateados),
        "metodo_pago": str(datos.get("metodo_pago", "No especificado") or "No especificado"),
        "subtotal_txt": formatear_cop_fn(datos.get("subtotal_bruto", 0)),
        "descuento_txt": formatear_cop_fn(datos.get("descuento_total", 0)),
        "total_txt": formatear_cop_fn(datos.get("total", 0)),
        "observaciones": (
            "Prendas confeccionadas bajo estandares de resistencia, "
            "durabilidad y ergonomia para uso tactico y operativo."
        ),
    }


def cargar_css_recibo_pos(app_root_path):
    ruta_css = os.path.join(app_root_path, "static", "css", "administrador", "admin_pos_recibo.css")
    if not os.path.exists(ruta_css):
        return ""
    try:
        with open(ruta_css, "r", encoding="utf-8") as f_css:
            return f_css.read()
    except UnicodeDecodeError:
        with open(ruta_css, "r", encoding="latin-1") as f_css:
            return f_css.read()


def cargar_marca_agua_recibo_src(app_root_path):
    carpeta = os.path.join(app_root_path, "static", "img", "Pagina")
    candidatos = ("recibo.png", "nachoher_fondo_logo.jpg", "logo.jpeg")
    mime_por_ext = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
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
        mime = mime_por_ext.get(ext, "application/octet-stream")
        with open(ruta, "rb") as f_img:
            contenido_b64 = base64.b64encode(f_img.read()).decode("ascii")
        return f"data:{mime};base64,{contenido_b64}"
    return ""


def render_html_recibo_pos(
    id_pedido,
    *,
    construir_contexto_recibo_pos_fn,
    cargar_css_recibo_pos_fn,
    cargar_marca_agua_recibo_src_fn,
    render_template_fn,
):
    contexto = construir_contexto_recibo_pos_fn(id_pedido)
    css_content = cargar_css_recibo_pos_fn()
    return render_template_fn(
        "Administrador/Sistema POS/recibo_pos_pdf.html",
        css_content=css_content,
        watermark_image_src=cargar_marca_agua_recibo_src_fn(),
        **contexto,
    )


def buscar_msedge(edge_path_env=""):
    candidatos = []

    edge_env = str(edge_path_env or "").strip()
    if edge_env:
        candidatos.append(edge_env)

    for exe in ("msedge.exe", "msedge"):
        encontrado = shutil.which(exe)
        if encontrado:
            candidatos.append(encontrado)

    candidatos.extend(
        [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    )

    for ruta in candidatos:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


def generar_pdf_recibo_pos(
    id_pedido,
    *,
    render_html_recibo_pos_fn,
    buscar_msedge_fn,
    app_root_path,
):
    html = render_html_recibo_pos_fn(id_pedido)
    ruta_edge = buscar_msedge_fn()
    if not ruta_edge:
        raise RuntimeError(
            "No se encontro Microsoft Edge para convertir el recibo a PDF. "
            "Configura EDGE_PATH o instala Edge."
        )

    tmp_path = Path(app_root_path) / f"recibo_pos_tmp_{id_pedido}_{os.getpid()}_{int(datetime.now().timestamp() * 1000)}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    try:
        html_path = tmp_path / f"recibo_pos_{id_pedido}.html"
        pdf_path = tmp_path / f"recibo_pos_{id_pedido}.pdf"
        user_data_dir = tmp_path

        html_path.write_text(html, encoding="utf-8")

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
            html_path.resolve().as_uri(),
        ]

        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=90)

        if resultado.returncode != 0 or not pdf_path.exists():
            detalle_error = (resultado.stderr or resultado.stdout or "").strip()
            if detalle_error:
                detalle_error = detalle_error.splitlines()[0]
            raise RuntimeError(f"No se pudo convertir el recibo a PDF. {detalle_error}")

        return pdf_path.read_bytes()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
