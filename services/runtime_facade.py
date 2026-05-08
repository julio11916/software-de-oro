"""Fachada de helpers runtime legacy usados por app.py."""

from datetime import datetime

import pandas as pd


def build_runtime_bindings(
    *,
    session_obj,
    cargar_registros_df_fn,
    guardar_registros_df_fn,
    cargar_usuarios_df_fn,
    currency_code,
    currency_name,
):
    def registrar_actividad(accion, forzar=False):
        rol_actual = str(session_obj.get('rol', '') or '').strip().lower()
        if not forzar and rol_actual != 'admin':
            return False

        registros = cargar_registros_df_fn()
        nuevo_id = int(pd.to_numeric(registros['id_registro'], errors='coerce').max() + 1) if not registros.empty else 1
        actor = session_obj.get('usuario', 'admin')
        nuevo_registro = {
            'id_registro': nuevo_id,
            'id_usuario': actor,
            'accion': accion,
            'fecha_accion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        registros = pd.concat([registros, pd.DataFrame([nuevo_registro])], ignore_index=True)
        guardar_registros_df_fn(registros)
        return True

    def obtener_nombre_sesion():
        nombre = str(session_obj.get('nombre', '')).strip()
        if nombre:
            return nombre

        email = str(session_obj.get('usuario', '')).strip()
        if not email:
            return 'Administrador'

        usuarios = cargar_usuarios_df_fn()
        if {'email', 'nombre'}.issubset(usuarios.columns):
            coincidencia = usuarios[usuarios['email'].astype(str).str.lower() == email.lower()]
            if not coincidencia.empty:
                nombre_excel = str(coincidencia.iloc[0].get('nombre', '')).strip()
                if nombre_excel:
                    session_obj['nombre'] = nombre_excel
                    return nombre_excel

        return email.split('@')[0] if '@' in email else email

    def formatear_cop(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            numero = 0.0
        valor_formateado = f"{numero:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"{currency_code} {valor_formateado}"

    def inyectar_nombre_admin_context():
        admin_nombre = ''
        if session_obj.get('rol') == 'admin':
            admin_nombre = obtener_nombre_sesion()
        return {
            'admin_nombre': admin_nombre,
            'currency_code': currency_code,
            'currency_name': currency_name,
        }

    return {
        'registrar_actividad': registrar_actividad,
        'obtener_nombre_sesion': obtener_nombre_sesion,
        'formatear_cop': formatear_cop,
        'inyectar_nombre_admin_context': inyectar_nombre_admin_context,
    }
