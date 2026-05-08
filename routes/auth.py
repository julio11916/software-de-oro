from datetime import datetime, timedelta

import pandas as pd
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def register_auth_legacy_routes(app, legacy):
    """
    Registro incremental de rutas legacy de autenticacion.
    Fase 2: primera migracion real desde app.py sin romper endpoints existentes.
    """

    def logout():
        if session.get("rol") == "normal":
            legacy._guardar_carrito_guardado_usuario(
                session.get("usuario", ""),
                legacy._obtener_carrito_sesion_usuario(),
            )
        session.clear()
        return redirect(url_for("home"))

    def login():
        if request.method == "GET":
            return render_template("Usuarios/Autenticacion/login_form.html")
        usuarios = legacy.cargar_usuarios_df()  # leer cada vez
        email = legacy.normalizar_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        usuarios["email"] = usuarios["email"].astype(str).str.strip()
        candidatos = usuarios[usuarios["email"].str.lower() == email]
        if candidatos.empty:
            flash("Correo equivocado.", "email_error")
            return render_template("Usuarios/Autenticacion/login_form.html"), 401

        idx_usuario = candidatos.index[0]
        usuario = candidatos.loc[idx_usuario]

        if not legacy.password_coincide(usuario.get("password_hash", ""), password):
            flash("Contraseña incorrecta.", "password_error")
            return render_template("Usuarios/Autenticacion/login_form.html"), 401

        password_guardado = str(usuario.get("password_hash", "") or "")
        if not legacy.password_esta_hasheado(password_guardado):
            usuarios.at[idx_usuario, "password_hash"] = legacy.crear_hash_password(password)
            legacy.guardar_usuarios_df(usuarios)

        estado = str(usuario.get("estado", "activo")).strip().lower()
        if estado != "activo":
            return "Tu usuario está inactivo. Contacta al administrador."

        rol = usuario["rol"]
        id_usuario = usuario["id_usuario"]
        nombre = str(usuario.get("nombre", "")).strip()
        email_sesion = str(usuario.get("email", email)).strip() or email

        session.permanent = True
        session["usuario"] = email_sesion
        session["id_usuario"] = int(id_usuario)
        session["rol"] = rol
        session["nombre"] = nombre

        if rol == "normal":
            session["carrito"] = legacy._obtener_carrito_guardado_usuario(email_sesion)
        else:
            session.pop("carrito", None)

        legacy.registrar_actividad("Inicio de sesión exitoso")

        if rol == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("user_dashboard"))

    def forgot_password():
        if request.method == "GET":
            return render_template(
                "Usuarios/Autenticacion/forgot_password.html",
                reset_minutes=legacy.PASSWORD_RESET_EXP_MINUTES,
            )

        email = legacy.normalizar_email(request.form.get("email", ""))
        if not legacy.email_es_valido(email):
            flash("Debes ingresar un correo electrónico válido.", "danger")
            return render_template(
                "Usuarios/Autenticacion/forgot_password.html",
                reset_minutes=legacy.PASSWORD_RESET_EXP_MINUTES,
            ), 400

        usuarios = legacy.cargar_usuarios_df()
        usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()
        candidatos = usuarios[usuarios["email"] == email]

        if not candidatos.empty:
            idx_usuario = candidatos.index[0]
            token = legacy.generar_token_recuperacion()
            expiry_at = datetime.now() + timedelta(minutes=legacy.PASSWORD_RESET_EXP_MINUTES)

            usuarios.at[idx_usuario, "reset_token"] = token
            usuarios.at[idx_usuario, "reset_token_expiry"] = expiry_at.strftime("%Y-%m-%d %H:%M:%S")
            legacy.guardar_usuarios_df(usuarios)

            enlace = url_for("reset_password", token=token, _external=True)
            envio_ok = legacy.enviar_recuperacion_password(
                email=email,
                enlace_recuperacion=enlace,
                minutos_expiracion=legacy.PASSWORD_RESET_EXP_MINUTES,
            )

            if envio_ok:
                legacy.registrar_actividad(f"Enlace de recuperación enviado a {email}")
            else:
                legacy.limpiar_token_recuperacion(usuarios, idx_usuario)
                legacy.guardar_usuarios_df(usuarios)
                print(f"No fue posible enviar el correo de recuperación para: {email}")

        flash(
            "Si el correo existe en el sistema, te enviamos un enlace para restablecer tu contraseña.",
            "info",
        )
        return redirect(url_for("forgot_password"))

    def reset_password(token):
        token = str(token or "").strip()
        usuarios = legacy.cargar_usuarios_df()

        encontrado = legacy.obtener_usuario_por_token_recuperacion(usuarios, token)
        if not encontrado:
            flash("El enlace de recuperación no es válido o ya fue utilizado.", "danger")
            return redirect(url_for("forgot_password"))

        idx_usuario, usuario = encontrado
        if legacy.token_recuperacion_expirado(usuario):
            legacy.limpiar_token_recuperacion(usuarios, idx_usuario)
            legacy.guardar_usuarios_df(usuarios)
            flash("El enlace de recuperación expiró. Solicita uno nuevo.", "warning")
            return redirect(url_for("forgot_password"))

        if request.method == "GET":
            return render_template("Usuarios/Autenticacion/reset_password.html", token=token)

        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not new_password or not confirm_password:
            flash("Debes completar todos los campos.", "danger")
            return render_template("Usuarios/Autenticacion/reset_password.html", token=token), 400

        if new_password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("Usuarios/Autenticacion/reset_password.html", token=token), 400

        if not legacy.password_cumple_estandares(new_password):
            flash(
                "La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial.",
                "danger",
            )
            return render_template("Usuarios/Autenticacion/reset_password.html", token=token), 400

        usuarios.at[idx_usuario, "password_hash"] = legacy.crear_hash_password(new_password)
        legacy.limpiar_token_recuperacion(usuarios, idx_usuario)
        legacy.guardar_usuarios_df(usuarios)

        email_usuario = str(usuario.get("email", "")).strip()
        legacy.registrar_actividad(f"Contraseña restablecida por recuperación para {email_usuario}")
        flash("Contraseña actualizada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    def registro():
        def _render_registro(nombre="", email=""):
            return render_template(
                "Usuarios/Autenticacion/registro.html",
                nombre_registro=nombre,
                email_registro=email,
                registro_code_minutes=legacy.REGISTER_CODE_EXP_MINUTES,
            )

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = legacy.normalizar_email(request.form.get("email", ""))
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not nombre or not email or not password or not confirm_password:
                flash("Debes completar todos los campos del formulario.", "danger")
                return _render_registro(nombre, email), 400

            if not legacy.email_es_valido(email):
                flash("Debes ingresar un correo electrónico válido.", "danger")
                return _render_registro(nombre, email), 400

            if password != confirm_password:
                flash("Las contraseñas no coinciden.", "danger")
                return _render_registro(nombre, email), 400

            if not legacy.password_cumple_estandares(password):
                flash(
                    "La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial.",
                    "danger",
                )
                return _render_registro(nombre, email), 400

            usuarios = legacy.cargar_usuarios_df()
            usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()

            if email in usuarios["email"].values:
                flash(
                    "El correo electrónico ya está registrado con otra cuenta. "
                    "Por favor, utiliza otro correo electrónico válido.",
                    "warning",
                )
                return _render_registro(nombre, email), 409

            codigo = legacy.generar_codigo_verificacion()
            password_hash = legacy.crear_hash_password(password)
            legacy.guardar_registro_pendiente(email, codigo, nombre=nombre, password=password_hash)
            session["registro_pendiente_email"] = email

            envio_ok, mensaje_envio = legacy.enviar_codigo_registro(email, codigo)
            if not envio_ok:
                legacy.PENDING_REGISTRATIONS.pop(email, None)
                session.pop("registro_pendiente_email", None)
                flash(mensaje_envio, "danger")
                return _render_registro(nombre, email), 500

            flash(mensaje_envio, "success")
            flash("Ingresa el código de verificación para activar tu cuenta.", "info")
            return redirect(url_for("registro_verificacion"))

        return _render_registro()

    def registro_check_email():
        try:
            payload = request.get_json(silent=True) or request.form
            email = legacy.normalizar_email(payload.get("email", ""))

            if not email:
                return jsonify({"success": False, "exists": False, "message": "Debes ingresar un correo electrónico."}), 400

            if not legacy.email_es_valido(email):
                return jsonify({"success": False, "exists": False, "message": "El correo electrónico no es válido."}), 400

            usuarios = legacy.cargar_usuarios_df()
            usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()
            email_existente = email in usuarios["email"].values

            if email_existente:
                return jsonify(
                    {
                        "success": True,
                        "exists": True,
                        "message": (
                            "El correo electrónico ya está registrado con otra cuenta. "
                            "Por favor, utiliza otro correo electrónico válido."
                        ),
                    }
                )

            return jsonify({"success": True, "exists": False, "message": "Correo electrónico disponible."})
        except Exception as e:
            print(f"Error validando correo de registro: {str(e)}")
            return jsonify({"success": False, "exists": False, "message": "Error interno validando el correo."}), 500

    def registro_send_code():
        try:
            payload = request.get_json(silent=True) or request.form
            email = legacy.normalizar_email(payload.get("email", ""))

            if not email:
                return jsonify({"success": False, "message": "Debes ingresar un correo electrónico."}), 400

            if not legacy.email_es_valido(email):
                return jsonify({"success": False, "message": "El correo electrónico no es válido."}), 400

            usuarios = legacy.cargar_usuarios_df()
            usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()
            if email in usuarios["email"].values:
                return jsonify(
                    {
                        "success": False,
                        "message": (
                            "El correo electrónico ya está registrado con otra cuenta. "
                            "Por favor, utiliza otro correo electrónico válido."
                        ),
                    }
                ), 409

            pendiente_actual = legacy.obtener_registro_pendiente(email) or {}
            nombre = str(pendiente_actual.get("nombre", "")).strip()
            password = str(pendiente_actual.get("password", ""))

            codigo = legacy.generar_codigo_verificacion()
            legacy.guardar_registro_pendiente(email, codigo, nombre=nombre, password=password)
            envio_ok, mensaje_envio = legacy.enviar_codigo_registro(email, codigo)

            if not envio_ok:
                legacy.PENDING_REGISTRATIONS.pop(email, None)
                session.pop("registro_pendiente_email", None)
                return jsonify({"success": False, "message": mensaje_envio}), 500

            session["registro_pendiente_email"] = email
            return jsonify({"success": True, "message": mensaje_envio})
        except Exception as e:
            print(f"Error al enviar código de registro: {str(e)}")
            return jsonify({"success": False, "message": "Error interno enviando el código."}), 500

    def registro_verificacion():
        def _render_verificacion(email=""):
            return render_template(
                "Usuarios/Autenticacion/registro_verificacion.html",
                email_registro=email,
                registro_code_minutes=legacy.REGISTER_CODE_EXP_MINUTES,
            )

        email = legacy.normalizar_email(session.get("registro_pendiente_email", ""))
        if not email:
            flash("Primero debes completar el formulario de registro.", "warning")
            return redirect(url_for("registro"))

        registro_pendiente = legacy.obtener_registro_pendiente(email)
        if not registro_pendiente:
            session.pop("registro_pendiente_email", None)
            flash("No hay un registro pendiente o el código ya expiró. Registra tus datos nuevamente.", "warning")
            return redirect(url_for("registro"))

        if request.method == "POST":
            accion = request.form.get("action", "verify")
            if accion == "resend":
                codigo_nuevo = legacy.generar_codigo_verificacion()
                nombre = str(registro_pendiente.get("nombre", "")).strip()
                password = str(registro_pendiente.get("password", ""))
                legacy.guardar_registro_pendiente(email, codigo_nuevo, nombre=nombre, password=password)
                envio_ok, mensaje_envio = legacy.enviar_codigo_registro(email, codigo_nuevo)
                flash(mensaje_envio, "success" if envio_ok else "danger")
                if not envio_ok:
                    legacy.PENDING_REGISTRATIONS.pop(email, None)
                    session.pop("registro_pendiente_email", None)
                    return redirect(url_for("registro"))
                return _render_verificacion(email)

            codigo_ingresado = request.form.get("verification_code", "").strip()
            if not codigo_ingresado:
                flash("Debes ingresar el código de verificación.", "danger")
                return _render_verificacion(email), 400

            registro_pendiente = legacy.obtener_registro_pendiente(email)
            if not registro_pendiente:
                session.pop("registro_pendiente_email", None)
                flash("El código expiró. Debes iniciar el registro nuevamente.", "warning")
                return redirect(url_for("registro"))

            if str(codigo_ingresado) != str(registro_pendiente.get("code", "")).strip():
                flash("Código de verificación incorrecto.", "danger")
                return _render_verificacion(email), 400

            usuarios = legacy.cargar_usuarios_df()
            usuarios["email"] = usuarios["email"].astype(str).str.strip().str.lower()
            if email in usuarios["email"].values:
                legacy.PENDING_REGISTRATIONS.pop(email, None)
                session.pop("registro_pendiente_email", None)
                flash(
                    "El correo electrónico ya está registrado con otra cuenta. "
                    "Por favor, utiliza otro correo electrónico válido.",
                    "warning",
                )
                return redirect(url_for("registro"))

            nombre = str(registro_pendiente.get("nombre", "")).strip()
            password_guardado = str(registro_pendiente.get("password", ""))
            if not nombre or not password_guardado:
                legacy.PENDING_REGISTRATIONS.pop(email, None)
                session.pop("registro_pendiente_email", None)
                flash("No se encontraron los datos del registro pendiente. Intenta nuevamente.", "warning")
                return redirect(url_for("registro"))

            if not legacy.password_esta_hasheado(password_guardado):
                password_guardado = legacy.crear_hash_password(password_guardado)

            ultimo_id = pd.to_numeric(usuarios["id_usuario"], errors="coerce").max()
            nuevo_id = int(ultimo_id + 1) if pd.notna(ultimo_id) else 1
            nuevo_usuario = {
                "id_usuario": nuevo_id,
                "nombre": nombre,
                "email": email,
                "password_hash": password_guardado,
                "rol": "normal",
                "estado": "activo",
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "email_verified": True,
                "verification_code": "",
                "verification_code_expiry": "",
                "reset_token": "",
                "reset_token_expiry": "",
            }

            usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
            legacy.guardar_usuarios_df(usuarios)
            legacy.PENDING_REGISTRATIONS.pop(email, None)
            session.pop("registro_pendiente_email", None)

            legacy.registrar_actividad(f"Nuevo usuario registrado y verificado: {nombre}")
            session["usuario"] = email
            session["id_usuario"] = int(nuevo_id)
            session["rol"] = "normal"
            session["nombre"] = nombre
            flash("Cuenta creada correctamente. Correo verificado.", "success")
            return redirect(url_for("user_dashboard"))

        return _render_verificacion(email)

    app.add_url_rule("/login", endpoint="login", view_func=login, methods=["GET", "POST"])
    app.add_url_rule(
        "/forgot-password",
        endpoint="forgot_password",
        view_func=forgot_password,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/reset-password/<token>",
        endpoint="reset_password",
        view_func=reset_password,
        methods=["GET", "POST"],
    )
    app.add_url_rule("/registro", endpoint="registro", view_func=registro, methods=["GET", "POST"])
    app.add_url_rule("/registro/check-email", endpoint="registro_check_email", view_func=registro_check_email, methods=["POST"])
    app.add_url_rule("/registro/send-code", endpoint="registro_send_code", view_func=registro_send_code, methods=["POST"])
    app.add_url_rule(
        "/registro/verificacion",
        endpoint="registro_verificacion",
        view_func=registro_verificacion,
        methods=["GET", "POST"],
    )
    app.add_url_rule("/logout", endpoint="logout", view_func=logout)
