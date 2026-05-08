"""
Servicio de autenticacion y registro.
Extrae helpers legacy de auth para reducir app.py.
"""

from datetime import datetime, timedelta
import re
import secrets

import pandas as pd


def normalizar_email(valor):
    return str(valor or "").strip().lower()


def limpiar_registros_pendientes(pending_registrations):
    ahora = datetime.now()
    expirados = []
    for email, data in pending_registrations.items():
        expiry_at = data.get("expiry_at")
        if not expiry_at or ahora > expiry_at:
            expirados.append(email)
    for email in expirados:
        pending_registrations.pop(email, None)


def obtener_registro_pendiente(email, pending_registrations):
    limpiar_registros_pendientes(pending_registrations)
    return pending_registrations.get(normalizar_email(email))


def guardar_registro_pendiente(email, codigo, pending_registrations, register_code_exp_minutes, nombre="", password=""):
    expiry_at = datetime.now() + timedelta(minutes=register_code_exp_minutes)
    pending_registrations[normalizar_email(email)] = {
        "code": str(codigo).strip(),
        "expiry_at": expiry_at,
        "nombre": str(nombre).strip(),
        "password": str(password),
    }
    return expiry_at


def password_esta_hasheado(valor):
    texto = str(valor or "").strip()
    return texto.startswith("pbkdf2:") or texto.startswith("scrypt:")


def crear_hash_password(password, generate_password_hash_fn):
    return generate_password_hash_fn(str(password or ""))


def password_coincide(password_guardado, password_plano, check_password_hash_fn):
    guardado = str(password_guardado or "")
    plano = str(password_plano or "")
    if not guardado or not plano:
        return False

    if password_esta_hasheado(guardado):
        try:
            return check_password_hash_fn(guardado, plano)
        except Exception:
            return False

    return guardado == plano


def password_cumple_estandares(password):
    patron = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}"
    return bool(re.fullmatch(patron, str(password or "")))


def timestamp_expirado(valor_expiry):
    expiry_dt = pd.to_datetime(valor_expiry, errors="coerce")
    if pd.isna(expiry_dt):
        return True

    tz = getattr(expiry_dt, "tz", None)
    if tz is not None:
        ahora = pd.Timestamp.now(tz=tz)
    else:
        ahora = pd.Timestamp.now()
    return ahora > expiry_dt


def asegurar_columnas_cambio_password(usuarios):
    if "password_change_code" not in usuarios.columns:
        usuarios["password_change_code"] = ""
    if "password_change_code_expiry" not in usuarios.columns:
        usuarios["password_change_code_expiry"] = ""
    usuarios["password_change_code"] = usuarios["password_change_code"].fillna("").astype(str)
    usuarios["password_change_code_expiry"] = usuarios["password_change_code_expiry"].fillna("").astype(str)
    return usuarios


def codigo_cambio_password_expirado(usuario):
    expiry_raw = str(usuario.get("password_change_code_expiry", "") or "").strip()
    if not expiry_raw:
        return True

    return timestamp_expirado(expiry_raw)


def limpiar_codigo_cambio_password(usuarios, idx_usuario):
    usuarios.at[idx_usuario, "password_change_code"] = ""
    usuarios.at[idx_usuario, "password_change_code_expiry"] = ""


def generar_token_recuperacion():
    return secrets.token_urlsafe(32)


def obtener_usuario_por_token_recuperacion(usuarios, token):
    token = str(token or "").strip()
    if not token:
        return None

    usuarios["reset_token"] = usuarios["reset_token"].fillna("").astype(str)
    candidatos = usuarios[usuarios["reset_token"] == token]
    if candidatos.empty:
        return None

    idx = candidatos.index[0]
    return idx, candidatos.loc[idx]


def token_recuperacion_expirado(usuario):
    expiry_raw = str(usuario.get("reset_token_expiry", "") or "").strip()
    if not expiry_raw:
        return True

    return timestamp_expirado(expiry_raw)


def limpiar_token_recuperacion(usuarios, idx_usuario):
    usuarios.at[idx_usuario, "reset_token"] = ""
    usuarios.at[idx_usuario, "reset_token_expiry"] = ""


def enviar_codigo_registro(email, codigo, enviar_codigo_verificacion_fn, register_code_exp_minutes):
    envio_ok = enviar_codigo_verificacion_fn(
        email,
        codigo,
        tipo="registro",
        minutos_expiracion=register_code_exp_minutes,
    )
    if envio_ok:
        return True, "Codigo enviado correctamente. Revisa tu correo."
    return False, (
        "No fue posible enviar el codigo de verificacion al correo indicado. "
        "Verifica la configuracion SMTP del sistema e intenta nuevamente."
    )
