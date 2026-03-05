# ========================================
# GUÍA RÁPIDA: Configurar Gmail para Autenticación por Correo
# ========================================

## 📧 Paso 1: Obtener Contraseña de Aplicación de Gmail

### Opción A: Usando el enlace directo
1. Ve a: https://myaccount.google.com/apppasswords
2. Es posible que te pida iniciar sesión
3. Si ves "Las contraseñas de aplicaciones no están disponibles", primero debes activar la verificación en dos pasos

### Opción B: Paso por paso
1. Ve a: https://myaccount.google.com/
2. En el menú izquierdo, haz clic en **"Seguridad"**
3. Busca **"Verificación en dos pasos"** y actívala si no lo está
4. Una vez activada, busca **"Contraseñas de aplicaciones"**
5. Selecciona:
   - **Aplicación**: "Correo"
   - **Dispositivo**: "Otro (nombre personalizado)" → Escribe "Flask Nachoher"
6. Haz clic en **"Generar"**
7. Google te mostrará una contraseña de 16 caracteres como: `abcd efgh ijkl mnop`
8. **COPIA ESTA CONTRASEÑA** (no podrás verla de nuevo)

## ⚙️ Paso 2: Configurar el Archivo

1. Abre el archivo: `config_email.py`
2. Modifica estas 3 líneas:

```python
MAIL_USERNAME = 'tu_correo@gmail.com'  # ← CAMBIA ESTO
MAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'  # ← PEGA LA CONTRASEÑA DE APLICACIÓN AQUÍ
MAIL_DEFAULT_SENDER = 'tu_correo@gmail.com'  # ← CAMBIA ESTO (mismo que USERNAME)
```

### Ejemplo Real:
Si tu correo es: `davidshop@gmail.com`
Y tu contraseña de aplicación es: `abcd efgh ijkl mnop`

Entonces el archivo quedaría:
```python
MAIL_USERNAME = 'davidshop@gmail.com'
MAIL_PASSWORD = 'abcd efgh ijkl mnop'
MAIL_DEFAULT_SENDER = 'davidshop@gmail.com'
```

## ✅ Paso 3: Guardar y Probar

1. **Guarda** el archivo `config_email.py`
2. **Reinicia** el servidor Flask (Ctrl+C y luego `python app.py`)
3. **Ve al perfil** del usuario en: http://localhost:5000/user/profile
4. **Haz clic** en el botón "Autenticar" o "Validar"
5. **Haz clic** en "Enviar Código"
6. **Revisa tu correo** (puede tardar unos segundos)
7. **Ingresa el código** de 6 dígitos que recibiste
8. **¡Listo!** ✨

## 🔒 Notas de Seguridad

- **NUNCA** compartas tu contraseña de aplicación con nadie
- **NO** subas el archivo `config_email.py` a GitHub o repositorios públicos
- Si crees que tu contraseña fue comprometida, revócala desde Google y genera una nueva
- La contraseña de aplicación es DIFERENTE a tu contraseña normal de Gmail

## ❌ Problemas Comunes

### "Username and Password not accepted"
- Verifica que la verificación en dos pasos esté activada
- Asegúrate de usar la contraseña de aplicación, no tu contraseña normal
- Verifica que no haya espacios extra en el correo o contraseña

### "SMTPAuthenticationError"
- La contraseña de aplicación es incorrecta
- Genera una nueva contraseña de aplicación

### No llega el correo
- Revisa la carpeta de **Spam**
- Espera hasta 1 minuto (puede haber retraso)
- Verifica que el correo esté bien escrito en config_email.py
- Revisa la consola del servidor Flask para ver errores

### "Connection refused" o "Connection timed out"
- Verifica tu conexión a Internet
- Algunos antivirus o firewalls bloquean el puerto 587
- Intenta desactivar temporalmente el firewall

## 🎯 ¿Funciona?

Una vez configurado correctamente, deberías:
1. Ver un correo hermoso con tu código de 6 dígitos
2. Poder ingresar el código y autenticarte
3. Ver el mensaje de éxito

---

**¿Necesitas ayuda?** Revisa los logs de la consola donde corre Flask para ver mensajes de error detallados.
